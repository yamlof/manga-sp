
from eta import ETA
import requests,os
from src.models import MangaSource
from src.sources.mangabat.Mangabat import Mangabat
from src.sources.mangakakalot.Mangakakalot import MangakakalotSource
from typing import List


class MangaSourceManager:
    def __init__(self):
        self.sources = {
            'mangakakalot': MangakakalotSource(),
            'mangabat': Mangabat(),  # Add new sources here
        }
        self.current_source = 'mangabat'  # Default source

    def set_source(self, source_name: str):
        if source_name in self.sources:
            self.current_source = source_name
        else:
            raise ValueError(f"Source {source_name} not available")

    def get_current_source(self) -> MangaSource:
        return self.sources[self.current_source]

    def list_sources(self) -> List[str]:
        return list(self.sources.keys())


title = r"""
  _____ _____    ____    _________              ____________  
 /     \\__  \  /    \  / ___\__  \    ______  /  ___/\____ \ 
|  Y Y  \/ __ \|   |  \/ /_/  > __ \_ /_____/  \___ \ |  |_> >
|__|_|  (____  /___|  /\___  (____  /         /____  >|   __/ 
      \/     \/     \//_____/     \/               \/ |__|  
"""



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

def get_popular_manga(source_manager: MangaSourceManager = None):
    if source_manager is None:
        source_manager = MangaSourceManager()
    return source_manager.get_current_source().get_popular_manga()

def search_manga(manga_name: str, source_manager: MangaSourceManager = None):
    if source_manager is None:
        source_manager = MangaSourceManager()
    return source_manager.get_current_source().search_manga(manga_name)

def get_manga_info(url: str, source_manager: MangaSourceManager = None):
    if source_manager is None:
        source_manager = MangaSourceManager()
    return source_manager.get_current_source().get_manga_info(url)

def get_chapter(chapter_url: str, source_manager: MangaSourceManager = None):
    if source_manager is None:
        source_manager = MangaSourceManager()
    return source_manager.get_current_source().get_chapter_images(chapter_url)

def latest_updates(source_manager: MangaSourceManager = None):
    if source_manager is None:
        source_manager = MangaSourceManager()
    return source_manager.get_current_source().get_latest_updates()


def download_chapters(chapter_links, title, source_manager=None):
    """Download all chapters of a manga"""
    if source_manager is None:
        source_manager = MangaSourceManager()

    save_directory = title
    os.makedirs(save_directory, exist_ok=True)

    total_chapters = len(chapter_links)
    eta = ETA(total=total_chapters)

    for chapter_index, chapter in enumerate(chapter_links):
        chapter_link = chapter["chapterLink"]
        chapter_name = chapter["chapterTitle"]
        chapter_directory = os.path.join(save_directory, chapter_name)
        os.makedirs(chapter_directory, exist_ok=True)

        eta.print_status(current=chapter_index, extra=f"Downloading chapter {chapter_index + 1}: {chapter_link}")

        # Use the source manager to get chapter images
        images = source_manager.get_current_source().get_chapter_images(chapter_link)

        if not images:
            print("⚠️ No images found.")
            eta.print_status(current=chapter_index + 1, extra="No images")
            continue

        for img in images:
            img_name = img["imgTitle"] + ".jpg"
            img_url = img["imgLink"]
            save_as = os.path.join(chapter_directory, img_name)

            try:
                # Use the source's headers
                headers = source_manager.get_current_source().headers
                img_response = requests.get(img_url, headers=headers)
                if img_response.status_code == 200:
                    with open(save_as, 'wb') as file:
                        file.write(img_response.content)
                    #print(f"✅ Saved {img_name}")
                else:
                    print(f"❌ Failed to download {img_url} (Status {img_response.status_code})")
            except Exception as e:
                print(f"❌ Exception occurred downloading {img_url}: {e}")

        eta.print_status(current=chapter_index + 1, extra=f"Chapter {chapter_index + 1} done")

    eta.done()  # Final message
    print(f"\n✅ Finished downloading all chapters of '{title}'.")

def download_manga(manga_name: str, source_name: str = 'mangakakalot', chapter_range=None):
    """
    High-level function to search and download a manga

    Args:
        manga_name: Name of the manga to search for
        source_name: Which source to use ('mangakakalot', etc.)
        chapter_range: Optional tuple (start, end) to download specific chapters
    """
    # Create source manager
    manager = MangaSourceManager()
    manager.set_source(source_name)

    # Search for manga
    search_results = search_manga(manga_name, manager)

    if not search_results:
        print(f"No manga found for '{manga_name}'")
        return

    # If multiple results, you might want to add selection logic here
    # For now, just take the first result
    selected_manga = search_results[0]
    print(f"Downloading: {selected_manga['title']}")

    # Get manga info
    manga_info = get_manga_info(selected_manga['manga_url'], manager)

    # Filter chapters if range specified
    chapters_to_download = manga_info.chapters
    if chapter_range:
        start, end = chapter_range
        chapters_to_download = manga_info.chapters[start:end]

    # Download chapters
    download_chapters(chapters_to_download, manga_info.title, manager)
    print(f"✅ Finished downloading {manga_info.title}")

def download_manga_chapters(manga_url: str, start_chapter: int = None, end_chapter: int = None,
                            source_name: str = 'mangakakalot'):
    """
    Download specific chapters from a manga URL

    Args:
        manga_url: Direct URL to the manga
        start_chapter: Starting chapter index (0-based)
        end_chapter: Ending chapter index (0-based, exclusive)
        source_name: Which source to use
    """
    manager = MangaSourceManager()
    manager.set_source(source_name)

    manga_info = get_manga_info(manga_url, manager)

    # Select chapter range
    chapters = manga_info.chapters
    if start_chapter is not None or end_chapter is not None:
        chapters = chapters[start_chapter:end_chapter]

    download_chapters(chapters, manga_info.title, manager)
    print(f"✅ Finished downloading chapters for {manga_info.title}")
