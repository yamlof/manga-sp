# Example of how to add a new source
from typing import List

from src.main import MangaSource, MangaDict


class MangareadSource(MangaSource):
    """Example implementation for another manga site"""

    def __init__(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            # ... other headers specific to this site
        }
        super().__init__("https://example-manga-site.com", headers)

    def get_popular_manga(self) -> List[MangaDict]:
        # Implementation specific to this site's HTML structure
        url = f"{self.base_url}/popular"
        # ... scraping logic for this site
        pass

    def search_manga(self, manga_name: str) -> List[MangaDict]:
        # Implementation specific to this site's search
        pass

    def get_manga_info(self, url: str):
        # Implementation specific to this site's manga info page
        pass

    def get_chapter_images(self, chapter_url: str) -> List[ImageDict]:
        # Implementation specific to this site's chapter pages
        pass

    def get_latest_updates(self) -> List[MangaDict]:
        # Implementation specific to this site's latest updates
        pass
