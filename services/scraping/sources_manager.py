from services.scraping.sources.mangabat_scraper import Mangabat
from services.scraping.sources.mangakakalot_scraper import MangakakalotSource
from services.scraping.sources.mangafire_scraper import MangaFire

from typing import List
from services.scraping.base import MangaSource

class MangaSourceManager:
    def __init__(self):
        self.sources = {
            'mangakakalot': MangakakalotSource(),
            'mangabat': Mangabat(),
            'mangafire' : MangaFire()
        }
        self.current_source = 'mangabat'

    def set_source(self, source_name: str):
        if source_name in self.sources:
            self.current_source = source_name
        else:
            raise ValueError(f"Source {source_name} not available")

    def get_current_source(self,source_name:str=None) -> MangaSource:
        
        if source_name:
            if source_name not in self.sources:
                raise ValueError(f"Source {source_name} not available")
            return self.sources[source_name]
        return self.sources[self.current_source]

    def list_sources(self) -> List[str]:
        return list(self.sources.keys())