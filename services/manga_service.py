from services.scraping.sources_manager import MangaSourceManager

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

