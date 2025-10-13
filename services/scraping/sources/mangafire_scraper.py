import requests,re,quickjs
from bs4 import BeautifulSoup
from services.scraping.base import MangaSource
from typing import Dict, List
from services.scraping.base import MangaDict,ImageDict
from urllib.parse import urlencode


class MangaFire(MangaSource):
    def __init__(self, lang_code="en"):
        self.base_url = "https://mangafire.to"
        self.ctx = quickjs.Context()
        self.lang_code = lang_code

        self._load_vrf_script()
        
        self.headers = { 
                        "User-Agent" : (
                            "Mozilla/5.0 (X11; Linux x86_64) " 
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/114.0.0.0 Safari/537.36" 
                            ),
                        "Referer": "https://www.mangafire.to/"
                        }

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.mangafire.to/",
        })
        #super().__init__("https://mangafire.to",headers)
        
        
    def _load_vrf_script(self):
        with open("services/scraping/sources/vrf.js", "r", encoding="utf-8") as f:
            vrf_js = f.read()
        self.ctx.eval(vrf_js)   
        
    def _generate_vrf(self, keyword: str) -> str:
        js_call = f'crc_vrf("{keyword}")'
        return self.ctx.eval(js_call)
    
    def _get(self, path: str, params: dict = None):
        """Helper method for GET requests using a persistent session."""
        url = f"{self.base_url}{path}"
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response
    
    def search_manga(self, manga_name: str,page: int = 1) -> List[MangaDict]:
        params = {
            "keyword": manga_name,
            "vrf": self._generate_vrf(manga_name),
            "language[]": self.lang_code,
            "page": str(page)
        }
        print(f"Fetching {self.base_url}/filter?{urlencode(params)}")
        response = self._get("/filter", params=params)
        soup = BeautifulSoup(response.text, "lxml")

        results = []
        for element in soup.select(".original.card-lg .unit .inner"):
            info = element.select_one(".info > a")
            if info:
                title = info.text.strip()
                href = info["href"]
                img_tag = element.select_one("img")
                poster = img_tag["src"] if img_tag else None
                results.append({
                    "title": title,
                    "cover": poster,
                    "manga_url": f"{self.base_url}{href}",
                })
        return results

    
    def get_latest_updates(self):
        url = f"{self.base_url}/updated?page=1"
        response = requests.get(url, headers=self.headers,verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        latest = soup.select_one("html body div.wrapper main div section div.original.card-lg")
        manga_items = latest.select('div.inner')
        list_of_latest = []
        
        for item in manga_items:
            #print(item)
            manga_item_cover = item.select('div.inner a.poster img')
            img = manga_item_cover[0]['src'] # becausee select gets a list that why [0]
            
            title_link = item.select_one('div.info a').text.strip()
            
            manga_url = item.select_one('a.poster')['href']

            api = {
                "title": title_link,
                "cover": img,
                "manga_url": f"{self.base_url}{manga_url}"
            }
            list_of_latest.append(api) 
            
        return list_of_latest
    
    def get_popular_manga(self):
        url = f"{self.base_url}/filter?keyword=&sort=total_views&page=1"
        response = requests.get(url, headers=self.headers,verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        latest = soup.select_one("html body div.wrapper main div section div.original.card-lg")
        manga_items = latest.select('div.inner')
        list_of_latest = []
        
        for item in manga_items:
            #print(item)
            manga_item_cover = item.select('div.inner a.poster img')
            img = manga_item_cover[0]['src'] # becausee select gets a list that why [0]
            
            title_link = item.select_one('div.info a').text.strip()
            
            manga_url = item.select_one('a.poster')['href']

            api = {
                "title": title_link,
                "cover": img,
                "manga_url": f"{self.base_url}{manga_url}"
            }
            list_of_latest.append(api) 
            
        return list_of_latest

    def get_manga_info(self,url):
        
        from models.models import Manga,Chapter
        from config.db import db
        
        print(f"Scraping URL: {url} from source:")

        
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")
        
        manga_details = soup.select("#manga-page > div.manga-detail > div.container > div")
        
        title = manga_details[0].select_one("div.main-inner aside.content div.info h1").text
    
        url = f"{self.base_url}{url}"
        
        cover = manga_details[0].select_one("div.main-inner aside.content div.poster div img")['src']
        
        status = manga_details[0].select_one("div.main-inner aside.content div.info p").text
        
        #document.querySelector("#info-rating > div.meta > div:nth-child(1) > span:nth-child(2)")
        
        author = manga_details[0].select_one("aside.sidebar div.collapse div.meta div:nth-child(1) span:nth-child(2)").text
        #print(soup)
        chapters = soup.select("#manga-page > div.container > div > aside.content > section.m-list > div:nth-child(2) > div.list-body > ul")
       # print(chapters)
        #document.querySelector("#manga-page > div.container > div > aside.content > section.m-list > div:nth-child(2) > div.list-body > ul")
        chapters_list = chapters[0].find_all('li')
        
        chapters_list_api = []

        genre_span = manga_details[0].select_one("#info-rating > div.meta > div:nth-child(3) > span:nth-child(2)")
        
        genres = [a.get_text(strip=True) for a in genre_span.find_all("a")]

        print(genres)
        
        #document.querySelector("#info-rating > div.meta > div:nth-child(3) > span:nth-child(2  
        manga = Manga()
        manga.title = title
        manga.url = url
        manga.author = author
        manga.cover = cover
        manga.status = status
        manga.genres = genres
        manga.chapters = chapters_list_api
        
        for chapter in chapters_list:
            chapter_title = chapter.select_one("a span").text
            #print(chapter_title)
            chapter_link = chapter.select_one("a")['href']
            #print(chapter_link)
            
            match = re.search(r'Chapter\s+(\d+)', chapter_title, re.IGNORECASE)
            chapter_number = int(match.group(1)) if match else None

            chapter_js = {
                "chapterTitle": chapter_title,
                "chapterLink":  f"{self.base_url}{chapter_link}",
                "mangaUrl": url
            }
            
            chapter_obj = Chapter(
            title=chapter_title,
            url=f"{self.base_url}{chapter_link}",
            number=chapter_number # You can parse number if needed
            )
            
            chapters_list_api.append(chapter_obj)
            
            """"
            
            chapter = Chapter()  # no arguments
            chapter.title = chapter_title
            chapter.number = None  # optional: extract number if needed
            chapter.url = f"{self.base_url}{chapter_link}"
            manga.chapters.append(chapter)"""
            
            #chapters_list_api.append(chapter_js)
        
        #print(title)
        manga.chapters = chapters_list_api
        #document.querySelector("#manga-page > div.manga-detail > div.container > div")
        return manga

    def get_chapter_images(self, chapters_url: str) -> List[ImageDict]:
        return []
        
if __name__ == '__main__':
    service = MangaFire()
    soup = service.get_manga_info(url="https://mangafire.to/manga/one-piecee.dkw")
    print(soup)