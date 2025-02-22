import requests,os
from bs4 import BeautifulSoup
from .manga import Manga
from pprint import pprint
import inquirer,certifi

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

def clear_console():
    # Clear command for Windows
    if os.name == 'nt':
        os.system('cls')
    # Clear command for Unix/Linux/Mac
    else:
        os.system('clear')


def get_popular_manga():

    hot_manga_page = 1
    url = f'https://m.manganelo.com/genre-all/{hot_manga_page}?type=topview'

    response = requests.get(url,verify=certifi.where())
    soup = BeautifulSoup(response.content,"html.parser")

    hot_manga = soup.find_all("div",class_="content-genres-item")
    

    popular = []

    for manga in hot_manga:

        title = manga.select_one(".genres-item-img.bookmark_check ")['title']
        link = manga.select_one(".genres-item-img.bookmark_check")['href']
        cover = manga.select_one("img")['src']

        hot_manga = {
                "cover" : cover,
                "manga_url" : link,
                "title" : title
                }

        popular.append(hot_manga)

    return popular



def search_manga(manga_name):

    # Format manga name for URL
    manga_name = manga_name.replace(" ", "_")
    base_url = "https://m.manganelo.com/search/story/"
    manga_url = base_url + manga_name

    # Make request and parse content
    response = requests.get(manga_url,verify=certifi.where())
    soup = BeautifulSoup(response.content, "html.parser")

    # Find manga items
    manga_item = soup.find_all("div",class_="search-story-item")
    manga_choices = []

    for manga in manga_item:


        title = manga.select_one(".item-img.bookmark_check ")['title']
        link = manga.select_one(".item-img.bookmark_check")['href']
        cover = manga.select_one("img")['src']
        api = {
                "title" : title ,
                "cover" : cover ,
                "manga_url" : link
                }

        manga_choices.append(api)


    return manga_choices

       

def get_manga_info(url):

    response = requests.get(url,headers = headers,verify = False)
    soup = BeautifulSoup(response.content, "html.parser")

    # Get manga details

    manga_details = soup.select_one("html body div.body-site div.container.container-main div.container-main-left")

    # Get cover images

    cover = manga_details.select_one(".story-info-left")
    cover = cover.find("img")
    cover = cover.get("src")

    # Get title of manga

    details = manga_details.select_one(".story-info-right")
    title = details.find("h1")
    
    # Get author , status and genres

    table = manga_details.select_one(".story-info-right")
    author = table.select_one(".variations-tableInfo > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) ")
    status = table.select_one(".variations-tableInfo > tbody:nth-child(1) > tr:nth-child(3) > td:nth-child(2)")
    genres = table.select_one(".variations-tableInfo > tbody:nth-child(1) > tr:nth-child(4) > td:nth-child(2)")
    genres = genres.find_all("a")
    print(author)

    #Get chapters of manga

    chapters = manga_details.select_one(".panel-story-chapter-list")
    chapters = chapters.select_one(".row-content-chapter")
    chapters = chapters.find_all("a")
    
    chapters_list = []

    for chapter in chapters:
        chapter_title = chapter.text
        chapter_link = chapter["href"]

        chapter_js = {
                "chapterTitle" : chapter_title,
                "chapterLink" : chapter_link
                }

        chapters_list.append(chapter_js)
    
    manga = Manga(title.text,author.text,cover,status.text,genres,chapters_list)

    return manga

def download_chapters(chapter_links,title):
    save_directory = title
    os.makedirs(save_directory, exist_ok=True)

    links = []

    for chapter_index, chapter in enumerate(chapter_links):

        chapter_link = chapter["chapterLink"]
        chapter_name = chapter["chapterTitle"]
        chapter_directory = os.path.join(save_directory,chapter_name)
        os.makedirs(chapter_directory,exist_ok=True)


        print(f"Downloading images for chapter {chapter_index + 1}: {chapter_link}")
        response = requests.get(chapter_link)
        soup = BeautifulSoup(response.content, "html.parser")
        manga_images = soup.select_one("html body div.body-site div.container-chapter-reader")
        manga_images = manga_images.find_all("img")
        for img_index,img in enumerate(manga_images):
            url = img.get("src")
            filename = f"{img['alt']}.jpg"  # Change extension as needed
            save_as = os.path.join(chapter_directory, filename)

            # Download the image
            img_response = requests.get(url,headers=headers)
            if img_response.status_code == 200:  # Check if the request was successful
                with open(save_as, 'wb') as file:
                    file.write(img_response.content)
                    print(f"Saved {filename}")
            else:
                    print(f"Failed to download image: {url}")



def latest_updates():

    url = "https://m.manganelo.com/genre-all-update-latest"
    response = requests.get(url,headers = headers,verify = False)
    soup = BeautifulSoup(response.content,"html.parser")

    manga_items = soup.find_all("div",class_="content-genres-item")

    list_of_latest = []

    for item in manga_items:

        manga_item_cover = item.select_one("img")['src']
        manga_item_title = item.select_one(".genres-item-info h3 a")
        manga_url = item.select_one(".genres-item-info h3 a")["href"]

        api = {
                "title" : manga_item_title.text ,
                "cover" : manga_item_cover ,
                "manga_url" : manga_url
                }

        list_of_latest.append(api)


    return list_of_latest

def get_chapter(chapter_url):
    response = requests.get(chapter_url)
    soup = BeautifulSoup(response.content, "html.parser")
    manga_images = soup.select_one("html body div.body-site div.container-chapter-reader")
    manga_images = manga_images.find_all("img")
    list_of_images = []
    for img in manga_images:
        img_name = img['alt']
        img_link = img['src']

        img_list = {
                "imgTitle" : img_name,
                "imgLink" : img_link
                }

        list_of_images.append(img_list)

    return list_of_images
        

#manga = input("enter manga to download (ensure it is writen well and with spaces) ")

if __name__ == '__main__':
    import argparse
    import inquirer

    parser = argparse.ArgumentParser(description="downloads for manga pages")
    parser.add_argument('--link',type=str,default=None,help="Link of the manga")
    parser.add_argument('--title',)
    args = parser.parse_args()

    if args.link is None:
        print("Please provide a manga link using --link")
    else:
        manga_data = search_manga(args.link)
        choices = []
        for i in manga_data:
            choices.append(f"{i['title']} ")
        manga = choices.index(inquirer.prompt([inquirer.List('_',message='choose a manga',choices=choices)])['_'])
        manga_info = get_manga_info(manga_data[manga]['manga_url'])
        download_chapters(manga_info.chapters,manga_info.title)
        

latest_updates()
