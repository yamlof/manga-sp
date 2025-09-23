import requests
from bs4 import BeautifulSoup
from services.scraping.base import MangaSource
from models.models import Manga


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
        response = requests.get(url, headers=self.headers,verify=False)
        soup = BeautifulSoup(response.content, "html.parser")

        latest = soup.select_one("html body div.container div.main-wrapper div.leftCol.listCol div.comic-list")
        manga_items = latest.find_all("div", class_="list-comic-item-wrap")
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
        # Import here to avoid circular import

        from models.models import Manga,Chapter
        from config.db import db

        #body > div.container > div.main-wrapper > div.leftCol

        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")

        manga_details = soup.select("body div.container div.main-wrapper div.leftCol")

        # Get title of manga
        details = manga_details[0].select_one("div.manga-info-top div.manga-info-content ul.manga-info-text")
        title = details.select_one("li h1").text.strip() # type: ignore
        print(title)

        # Get cover images
        cover = manga_details[0].select_one("div.manga-info-top div.manga-info-pic img")['src']

        # Get author, status and genres
        author_tags = manga_details[0].select_one("li:nth-of-type(2)").find_all('a')
        author_str = ", ".join([a.text.strip() for a in author_tags])

        status = manga_details[0].select_one("li:nth-of-type(3)").text.replace("Status :", "").strip()
        genre_tags = manga_details[0].select_one("li.genres").select("a")
        genres_str = ", ".join([g.text.strip() for g in genre_tags])
        

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

        manga = Manga()
        manga.title = title
        manga.url = url
        manga.author = author_str
        manga.cover = cover
        manga.status = status
        manga.genres = genres_str
        
        chapters_html = manga_details[0].select("div.chapter div.manga-info-chapter div.chapter-list div.row")
        for ch_html in chapters_html:
            chapter_title = ch_html.select_one("span a").text.strip()
            chapter_link = ch_html.select_one("span a")['href']

            chapter = Chapter()  # no arguments
            chapter.title = chapter_title
            chapter.number = None  # optional: extract number if needed
            chapter.url = chapter_link
            manga.chapters.append(chapter)
            
            
        db.session.add(manga)
        db.session.commit()
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

        # Check if Cloudflare blocked us
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
