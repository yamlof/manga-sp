from services.scraping.sources_manager import MangaSourceManager

def get_popular_manga(source: str = None, source_manager: MangaSourceManager = None):
    if source_manager is None:
        source_manager = MangaSourceManager()
    source_obj = source_manager.get_current_source(source)
    return source_obj.get_popular_manga()

def search_manga(manga_name: str, source: str = None, source_manager: MangaSourceManager = None):
    if source_manager is None:
        source_manager = MangaSourceManager()
    source_obj = source_manager.get_current_source(source)
    return source_obj.search_manga(manga_name)

def get_manga_info(url: str, source: str = "mangabat", source_manager: MangaSourceManager = None):
    if source_manager is None:
        source_manager = MangaSourceManager()
    source_obj = source_manager.get_current_source(source)
    return source_obj.get_manga_info(url)

def get_chapter(chapter_url: str, source: str = None, source_manager: MangaSourceManager = None):
    if source_manager is None:
        source_manager = MangaSourceManager()
    source_obj = source_manager.get_current_source(source)
    return source_obj.get_chapter_images(chapter_url)

def latest_updates(source: str = "mangabat", source_manager: MangaSourceManager = None):
    if source_manager is None:
        source_manager = MangaSourceManager()
    source_obj = source_manager.get_current_source(source)
    return source_obj.get_latest_updates()


