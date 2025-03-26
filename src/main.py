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
    

    url = "https://mangakakalot.to/hot?sort=default&page=1"
    response = requests.get(url,headers = headers,verify = False)
    soup = BeautifulSoup(response.content,"html.parser")
    
    
    hot_manga = soup.select_one("html body div#wrapper div#main div.container div.main_inner.is-single div.manga-list.is-big-sbs div.inner")
    

    manga_items = hot_manga.find_all("div", class_="item")
    #print(manga_items)

    popular = []

    for item in manga_items:

        manga_item_cover = item.select_one("div.item-poster a.manga-poster img.manga-poster-img")['src']
        manga_item_title = item.select_one("div.item-info h3.manga-name a")['title']
        manga_url = item.select_one("div.item-info .manga-name a")["href"]
        
        base_url = "https://mangakakalot.to"
        
        manga_url = base_url+ manga_url

        hot_manga = {
                "title" : manga_item_title ,
                "cover" : manga_item_cover ,
                "manga_url" : manga_url
                }

        popular.append(hot_manga)

    return popular

def search_manga(manga_name):

    # Format manga name for URL
    manga_name = manga_name.replace(" ", "+")
    base_url = "https://mangakakalot.to/search?keyword="
    manga_url = base_url + manga_name

    # Make request and parse content
    response = requests.get(manga_url,verify=certifi.where())
    soup = BeautifulSoup(response.content, "html.parser")

    manga_src = soup.select_one("html body div#wrapper div#main div.container div.main_inner.is-single div.manga-list.is-big-sbs")
    # Find manga items
    manga_item = manga_src.find_all("div",class_="item")
    
    manga_choices = []

    for manga in manga_item:


        title = manga.select_one("div.item-info h3.manga-name a")['title']
        link = manga.select_one("div.item-info .manga-name a")['href']
        cover = manga.select_one("img")['src']
        
        base_url = "https://mangakakalot.to"
        
        link = base_url+ link
        
        api = {
                "title" : title ,
                "cover" : cover ,
                "manga_url" : link
                }

        manga_choices.append(api)

    #print(manga_choices)
    return manga_choices

       

def get_manga_info(url):

    response = requests.get(url,headers = headers,verify = False)
    soup = BeautifulSoup(response.content, "html.parser")

    #print(soup)

    # Get manga details

    manga_details = soup.select("div.detail-box")

    id = soup.select_one("html body div#wrapper div#main")["data-id"]

    print(id)

#    print(manga_details)

    # Get cover images

    cover = manga_details[0].select_one("div.db-poster")
    cover = cover.find("img")
    cover = cover.get("src")

    print(cover)

    # Get title of manga

    details = manga_details[0].select_one("div.db-info")
    #details = details[0].select("div.line_content")
    title = details.select_one("div.line.line-top div.line-content")
    title = title.find('h3').text
    

    print(title)
    
    # Get author , status and genres

    #table = manga_details[0].select_one(".story-info-right")
    author = manga_details[0].select_one("div.line:nth-child(2) span.result")
    author_list = []
    author = author.find_all('a')
    for a in author:
        author_list.append(a.text)
        
    author_list = " ".join(author_list)

    status = manga_details[0].select_one("div.line:nth-child(3) div.line-content span.result")
    print(author_list)
    print(status)
    genres = manga_details[0].select_one("div.line:nth-child(6) div.line-content span.result")
    genres = genres.find_all("a")
#    print(genres)

    response = requests.get(f"https://mangakakalot.to/ajax/manga/list-chapter-volume?id={id}")
    chapters_soup = BeautifulSoup(response.content, "html.parser")

    #Get chapters of manga

    chapters = chapters_soup.select_one("#list-chapter-en")
    if chapters:
        print(id)
    else:
        print(requests.HTTPError(f"Error response returned. {response.status_code} {id}: {response.reason}"))
    #    print(soup)
    #chapters = chapters.select_one(".row-content-chapter")
    chapters = chapters.find_all("a")
    
    chapters_list = []
    
    base_url = "https://mangakakalot.to"
        
    link = base_url+ url


    for chapter in chapters:
        chapter_title = chapter.text
        chapter_link = chapter["href"]

        chapter_js = {
                "chapterTitle" : chapter_title,
                "chapterLink" : base_url+chapter_link,
                "mangaUrl" : link
                }

        chapters_list.append(chapter_js)

    #print(chapters_list)
    
    manga = Manga(title,author_list,cover,status.text,genres,chapters_list)

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

    url = "https://mangakakalot.to/latest?sort=default&page=1"
    response = requests.get(url,headers = headers,verify = False)
    soup = BeautifulSoup(response.content,"html.parser")
    
    
    latest = soup.select_one("html body div#wrapper div#main div.container div.main_inner.is-single div.manga-list.is-big-sbs div.inner")
    

    manga_items = latest.find_all("div", class_="item")
    #print(manga_items)

    list_of_latest = []
    
    base_url = "https://mangakakalot.to"
        
        

    for item in manga_items:

        manga_item_cover = item.select_one("div.item-poster a.manga-poster img.manga-poster-img")['src']
        manga_item_title = item.select_one("div.item-info h3.manga-name a")['title']
        manga_url = item.select_one("div.item-info .manga-name a")["href"]
        
        manga_url = base_url+ manga_url 

        api = {
                "title" : manga_item_title ,
                "cover" : manga_item_cover ,
                "manga_url" : manga_url
                }

        list_of_latest.append(api)

    #print(list_of_latest)


    return list_of_latest

def get_chapter(chapter_url):
    response = requests.get(chapter_url)
    soup = BeautifulSoup(response.content, "html.parser")
    manga_images = soup.select_one("html body.reading div#wrapper div#reading div.reading-inner div#list-image.container-chapter-reader")
    #print(manga_images)
    reading_id = soup.select_one("html body.reading div#wrapper div#reading")['data-reading-id']
    reading_type = soup.select_one("html body.reading div#wrapper div#reading")['data-reading-type']
    
    img_request = requests.get(f"https://mangakakalot.to/ajax/manga/images?id={reading_id}&type={reading_type}")
    soup = BeautifulSoup(img_request.content, "html.parser")
    print(soup)
    
    
    list_of_images = []
    manga_images = soup.find_all('div',class_='card-wrap')
    print(manga_images)
    for idx,img in enumerate(manga_images):
        img_name = f"image{idx+1}"
        img_link = img.get('data-url')

        img_list = {
                "imgTitle" : img_name,
                "imgLink" : img_link
                }

        list_of_images.append(img_list)

    
    print(list_of_images)
    return list_of_images
        
#get_manga_info("https://mangakakalot.to/onepunch-man-40")
#manga = input("enter manga to download (ensure it is writen well and with spaces) ")
"""
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
        
"""
#get_chapter("https://mangakakalot.to/read/blue-lock-225/en/chapter-295")
#search_manga("one piece")

get_manga_info("https://mangakakalot.to/blue-lock-225")