from flask import Blueprint, request,jsonify
from services.manga_service import get_popular_manga, search_manga,latest_updates,get_manga_info,get_chapter
from models.models import Manga ,db

manga_bp = Blueprint("manga", __name__)

@manga_bp.route('/hello',methods=['GET'])
def test():
    return jsonify("connected")

@manga_bp.route('/latest',methods=['GET'])
def latest():
    api = latest_updates()
    print("API data:",api)
    return jsonify(api)

@manga_bp.route('/manga_info',methods=['GET','POST'])
def manga_info():
    manga_url = request.args.get('mangaInfo')
    
    if not manga_url:
        return jsonify({"error": "mangainfo parameter is missingo"}),400
    
    manga_from_db = Manga.query.filter_by(url=manga_url).first()
    
    if manga_from_db:
        print("manga in db")
        return {
            "title" : manga_from_db.title ,
            "url" : manga_from_db.url,
            "cover" : manga_from_db.cover,
            "status" : manga_from_db.status,
            "author" : manga_from_db.author,
            "chapters" :[c.serialize() for c in list(manga_from_db.chapters)] 
        }


    print("scraping from website ",manga_url)
   
    manga = get_manga_info(manga_url)
    
    if manga is None:
        return jsonify({"error": "Manga not found"}), 404

    return jsonify({
        "title" : manga.title ,
        "url" : manga.url,
        "cover" : manga.cover,
        "status" : manga.status,
        "author" : manga.author,
        "chapters" :[c.serialize() for c in list(manga.chapters)]
        })


@manga_bp.route('/chapter',methods=['GET'])
def chapter():
    chapterUrl = request.args.get('chapterUrl')
    
    if chapterUrl is None:
        return jsonify({"error": "Missing mangaString parameter"}), 400

    chapter = get_chapter(chapterUrl)

    return jsonify(chapter)

@manga_bp.route('/popular', methods=['GET'])
def popular():

    popular = get_popular_manga()

    return jsonify(popular)

@manga_bp.route('/search', methods=['GET'])
def search():
    mangaString = request.args.get('mangaString')
    
    if mangaString is None:
        return jsonify({"error": "Missing mangaString parameter"}), 400

    mangas = search_manga(mangaString)

    return jsonify(mangas)