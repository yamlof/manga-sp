import requests
from bs4 import BeautifulSoup
import certifi
from models.models import MangaSource


# Import Manga class with a delayed import to avoid circular dependency

class MangakakalotSource(MangaSource):
    """Mangakakalot.to implementation"""

    def __init__(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0',
            'Accept': 'image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Connection': 'keep-alive',
            'Referer': 'https://chapmanganelo.com/',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
            'Priority': 'u=5, i',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        super().__init__("https://mangakakalot.to", headers)

    def get_popular_manga(self):
        url = f"{self.base_url}/hot?sort=default&page=1"
        response = requests.get(url, headers=self.headers, verify=False)
        soup = BeautifulSoup(response.content, "html.parser")

        hot_manga = soup.select_one(
            "html body div#wrapper div#main div.container div.main_inner.is-single div.manga-list.is-big-sbs div.inner")
        manga_items = hot_manga.find_all("div", class_="item")

        popular = []
        for item in manga_items:
            manga_item_cover = item.select_one("div.item-poster a.manga-poster img.manga-poster-img")['src']
            manga_item_title = item.select_one("div.item-info h3.manga-name a")['title']
            manga_url = item.select_one("div.item-info .manga-name a")["href"]
            manga_url = self.base_url + manga_url

            hot_manga = {
                "title": manga_item_title,
                "cover": manga_item_cover,
                "manga_url": manga_url
            }
            popular.append(hot_manga)

        return popular

    def search_manga(self, manga_name: str):
        manga_name = manga_name.replace(" ", "+")
        manga_url = f"{self.base_url}/search?keyword={manga_name}"

        response = requests.get(manga_url, verify=certifi.where())
        soup = BeautifulSoup(response.content, "html.parser")

        manga_src = soup.select_one(
            "html body div#wrapper div#main div.container div.main_inner.is-single div.manga-list.is-big-sbs")
        manga_item = manga_src.find_all("div", class_="item")

        manga_choices = []
        for manga in manga_item:
            title = manga.select_one("div.item-info h3.manga-name a")['title']
            link = manga.select_one("div.item-info .manga-name a")['href']
            cover = manga.select_one("img")['src']
            link = self.base_url + link

            api = {
                "title": title,
                "cover": cover,
                "manga_url": link
            }
            manga_choices.append(api)

        return manga_choices

    def get_manga_info(self, url: str):
        # Import here to avoid circular import

        from models.models import Manga

        response = requests.get(url, headers=self.headers, verify=False)
        soup = BeautifulSoup(response.content, "html.parser")

        manga_details = soup.select("div.detail-box")
        id = soup.select_one("html body div#wrapper div#main")["data-id"]

        # Get cover images
        cover = manga_details[0].select_one("div.db-poster")
        cover = cover.find("img")
        cover = cover.get("src") # pyright: ignore[reportAttributeAccessIssue]

        # Get title of manga
        details = manga_details[0].select_one("div.db-info")
        title = details.select_one("div.line.line-top div.line-content")
        title = title.find('h3').text

        # Get author, status and genres
        author = manga_details[0].select_one("div.line:nth-child(2) span.result")
        author_list = []
        author = author.find_all('a')
        for a in author:
            author_list.append(a.text)
        author_list = " ".join(author_list)

        status = manga_details[0].select_one("div.line:nth-child(3) div.line-content span.result")
        genres = manga_details[0].select_one("div.line:nth-child(6) div.line-content span.result")
        genres = genres.find_all("a")

        response = requests.get(f"{self.base_url}/ajax/manga/list-chapter-volume?id={id}")
        chapters_soup = BeautifulSoup(response.content, "html.parser")

        # Get chapters of manga
        chapters = chapters_soup.select_one("#list-chapter-en")
        if not chapters:
            raise requests.HTTPError(f"Error response returned. {response.status_code} {id}: {response.reason}")

        chapters = chapters.find_all("a")
        chapters_list = []

        for chapter in chapters:
            chapter_title = chapter.text
            chapter_link = chapter["href"]

            chapter_js = {
                "chapterTitle": chapter_title,
                "chapterLink": self.base_url + chapter_link,
                "mangaUrl": url
            }
            chapters_list.append(chapter_js)

        manga = Manga(title, author_list, cover, status.text, genres, chapters_list)
        return manga

    def get_chapter_images(self, chapter_url: str):
        response = requests.get(chapter_url)
        soup = BeautifulSoup(response.content, "html.parser")

        reading_id = soup.select_one("html body.reading div#wrapper div#reading")['data-reading-id']
        reading_type = soup.select_one("html body.reading div#wrapper div#reading")['data-reading-type']

        img_request = requests.get(f"{self.base_url}/ajax/manga/images?id={reading_id}&type={reading_type}")
        soup = BeautifulSoup(img_request.content, "html.parser")

        list_of_images = []
        manga_images = soup.find_all('div', class_='card-wrap')

        for idx, img in enumerate(manga_images):
            img_name = f"image{idx + 1}"
            img_link = img.get('data-url')

            img_list = {
                "imgTitle": img_name,
                "imgLink": img_link
            }
            list_of_images.append(img_list)

        return list_of_images

    def get_latest_updates(self):
        url = f"{self.base_url}/latest?sort=default&page=1"
        response = requests.get(url, headers=self.headers, verify=False)
        soup = BeautifulSoup(response.content, "html.parser")

        latest = soup.select_one(
            "html body div#wrapper div#main div.container div.main_inner.is-single div.manga-list.is-big-sbs div.inner")
        manga_items = latest.find_all("div", class_="item")

        list_of_latest = []
        for item in manga_items:
            manga_item_cover = item.select_one("div.item-poster a.manga-poster img.manga-poster-img")['src']
            manga_item_title = item.select_one("div.item-info h3.manga-name a")['title']
            manga_url = item.select_one("div.item-info .manga-name a")["href"]
            manga_url = self.base_url + manga_url

            api = {
                "title": manga_item_title,
                "cover": manga_item_cover,
                "manga_url": manga_url
            }
            list_of_latest.append(api)

        return list_of_latest