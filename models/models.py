from abc import ABC, abstractmethod
from typing import Dict, List
from config.db import db
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship

MangaDict = Dict[str, str]
ChapterDict = Dict[str, str]
ImageDict = Dict[str, str]
Headers = Dict[str, str]

class Manga(db.Model):
    __tablename__ = "manga"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255))
    author = db.Column(db.String(255))
    cover = db.Column(db.String(500))
    status = db.Column(db.String(50))
    genres = db.Column(db.String(500))

    chapters : Mapped[List["Chapter"]]  = relationship("Chapter", back_populates="manga")

    def __repr__(self):
        return f"<Manga {self.title}>"

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "cover": self.cover,
            "status": self.status,
            "genres": self.genres.split(",") if self.genres else [],
            "chapters": [c.serialize() for c in self.chapters]
        }
        
    
        
class Chapter(db.Model):
    __tablename__ = "chapters"

    id = db.Column(db.Integer, primary_key=True)
    manga_id = db.Column(db.Integer, db.ForeignKey("manga.id"), nullable=False)
    title = db.Column(db.String(255))
    number = db.Column(db.String(50))
    url = db.Column(db.String(500))
    
    manga = db.relationship("Manga", back_populates="chapters")


    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "number": self.number,
            "url": self.url,
        }

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

