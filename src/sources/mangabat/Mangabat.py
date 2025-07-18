from abc import ABC

import certifi
import requests
from bs4 import BeautifulSoup
from flask import session

from src.models import MangaSource


class Mangabat(MangaSource):
    def __init__(self):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.mangabats.com/"
        }
        super().__init__("https://mangabats.com",headers)

    def get_popular_manga(self):
        url = f"{self.base_url}/manga-list/hot-manga?page=1"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")

        hot_manga = soup.select_one(
            "body > div.container > div.main-wrapper > div > div")
        manga_items = hot_manga.find_all("div", class_="list-truyen-item-wrap")

        print(manga_items[0])

        popular = []
        for item in manga_items:
            manga_item_cover = item.select_one("a.list-story-item.bookmark_check.cover img")['src']
            manga_item_title = item.select_one("a.list-story-item.bookmark_check.cover")['title']
            manga_url = item.select_one("a.list-story-item.bookmark_check.cover")["href"]
            manga_url = manga_url

            hot_manga = {
                "title": manga_item_title,
                "cover": manga_item_cover,
                "manga_url": manga_url
            }
            popular.append(hot_manga)


        print(hot_manga)
        return popular

    def get_chapter_images(self, chapter_url: str):
        response = requests.get(chapter_url)
        soup = BeautifulSoup(response.content, "html.parser")

        manga_images_container = soup.select_one("html body div.container-chapter-reader")

        list_of_images = []
        manga_images = manga_images_container.find_all('img')

        for idx, img in enumerate(manga_images):
            img_name = f"image{idx}"
            img_link = img.get('src')

            img_list = {
                "imgTitle": img_name,
                "imgLink": img_link
            }
            list_of_images.append(img_list)

        return list_of_images

    def get_latest_updates(self):
        url = f"{self.base_url}/manga-list/latest-manga?page=1"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")

        latest = soup.select_one("html body div.container div.main-wrapper div.leftCol.listCol div.truyen-list")
        manga_items = latest.find_all("div", class_="list-truyen-item-wrap")
        #print(manga_items)
        list_of_latest = []
        for item in manga_items:
            manga_item_cover = item.select_one("a.list-story-item.bookmark_check.cover img")['src']
            manga_item_title = item.select_one("a.list-story-item.bookmark_check.cover")['title']
            manga_url = item.select_one("a.list-story-item.bookmark_check.cover")['href']

            api = {
                "title": manga_item_title,
                "cover": manga_item_cover,
                "manga_url": manga_url
            }
            list_of_latest.append(api)

        return list_of_latest

    def get_manga_info(self, url):
        from src.models import Manga

        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")

        manga_details = soup.select("body div.container div.main-wrapper div.leftCol")

        details = manga_details[0].select_one("div.manga-info-top div.manga-info-content ul.manga-info-text")
        title = details.select_one("li h1").text.strip()
        print(title)

        # Get cover images
        cover = manga_details[0].select_one("div.manga-info-top div.manga-info-pic img")['src']

        # Get author, status and genres
        author = manga_details[0].select_one("li:nth-of-type(2)")
        author_list = []
        author = author.find_all('a')
        for a in author:
            author_list.append(a.text)
        author_list = " ".join(author_list)
        #p#rint(author_list)

        status = manga_details[0].select_one("li:nth-of-type(3)").text.replace("Status :", "").strip()
        genre_tags = manga_details[0].select_one("li.genres").select("a")
        genres = [g.text.strip() for g in genre_tags]
        #print(status)
        #print(genres)

        # chapter > div > div.chapter-list

        # Get chapters of manga
        chapters = manga_details[0].select_one("div.chapter div.manga-info-chapter div.chapter-list")
        #print(chapters)

        chapters = chapters.find_all("div", class_="row")
        #print(chapters)
        chapters_list = []

        for chapter in chapters:
            chapter_title = chapter.select_one("span a").text
            chapter_link = chapter.select_one("span a")['href']

            chapter_js = {
                "chapterTitle": chapter_title,
                "chapterLink":  chapter_link,
                "mangaUrl": url
            }
            chapters_list.append(chapter_js)

        manga = Manga(title, author_list, cover, status, genres, chapters_list)
        return manga

    def search_manga(self, query):
        manga_name = query.replace(" ", "_")
        manga_url = f"{self.base_url}/search/story/{manga_name}"

        session = requests.Session()

        cookies = {
            'cf_clearence': 'W78LDaQlBSWM2bMqhfa0B5WPQYdYAmyZeMCTPtvDZpA-1748995952-1.2.1.1-QHl.UydtOjd6Kip78UKWPbq1I.eO7QpSJKQfso5TsbQfbEeO1goHSFpq9oQHI2k4LMOOMxb0uUkCb7PkUBUaqcDb4p4z6sJj5ZQLMeYCfWMlPZReDWR9x9J7imyFZwxdX0wG5LJ.oPmt1zu4oi.QSm2klO7oQdhRJ0FQuXufwhPXKhQuSDcM6tRAfHmba4p8mkW5u3tUy3zsP3NNhTvdIwHDVJsny7Dm6ICCNa90.w3WR4Rc6kTZK74N5Iyn4sqLI0bcP1sYwTRUHOliU5MXU.ZvJOqe.clIX1Tw_DOET60V4pNSpDzKpe5ECT8bo4jm_15DcsHevK99wpOyYGCwg2Codu2DtB6eK8cE5JLzkgl7yVJvulgFZnlAT3SkpQBn',
        }

        session.cookies.update(cookies)

        response = session.get(manga_url,headers=self.headers)

        if "Just a moment..." in response.text or "Enable JavaScript and cookies" in response.text:
            raise Exception("Blocked by Cloudflare. cloudscraper failed to bypass.")

        soup = BeautifulSoup(response.content, "html.parser")

        #body > div.container > div.main-wrapper > div.leftCol > div.daily-update > div
        manga_src = soup.select_one("html body div.container div.main-wrapper div.leftCol div.daily-update div")
        manga_item = manga_src.find_all("div", class_="story_item")

        manga_choices = []
        for manga in manga_item:
            title = manga.select_one("div.story_item_right h3 a").text
            link = manga.select_one("a")['href']
            cover = manga.select_one("a img")['src']

            api = {
                "title": title,
                "cover": cover,
                "manga_url": link
            }
            manga_choices.append(api)

        return manga_choices

if __name__ == "__main__":
    source = Mangabat()
    #results = source.get_popular_manga()
    #manga = source.get_manga_info("https://www.mangabats.com/manga/solo-leveling")
    #manga2 = source.get_manga_info("https://www.mangabats.com/manga/blue-lock")
    #manga_images = source.get_chapter_images("https://www.mangabats.com/manga/blue-lock/chapter-303")
    manga_images = source.get_latest_updates()
    #print(manga)
    #print(manga2)
    print(manga_images)
