from abc import ABC, abstractmethod
from typing import Dict, List

MangaDict = Dict[str, str]
ChapterDict = Dict[str, str]
ImageDict = Dict[str, str]
Headers = Dict[str, str]

class Manga:
    def __init__(self, title, author, cover, status, genres, chapters):
        self.title = title
        self.author = author
        self.cover = cover
        self.status = status
        self.genres = genres
        self.chapters = chapters

    def __repr__(self):
        return (
            f"Manga(title={self.title!r}, author={self.author!r}, "
            f"cover={self.cover!r}, status={self.status!r}, "
            f"genres={self.genres!r}, chapters={self.chapters!r})"
        )

class MangaSource(ABC):
    """ Abstract base class for manga sources """

    def __init__(self , base_url:str,headers:Headers):
        self.base_url = base_url
        self.headers = headers

    @abstractmethod
    def get_popular_manga(self) -> List[MangaDict]:
        """Get List of popular manga"""
        pass

    @abstractmethod
    def search_manga(self,manga_name:str) -> List[MangaDict]:
        """Search for manga by name"""
        pass

    @abstractmethod
    def get_manga_info(self,url:str):
        "Get detail manga information including chapters"
        pass

    @abstractmethod
    def get_chapter_images(self,chapters_url:str) -> List[ImageDict]:
        """Get images from a chapter"""
        pass

    @abstractmethod
    def get_latest_updates(self) -> List[MangaDict]:
        """Get latest manga updates"""
        pass
