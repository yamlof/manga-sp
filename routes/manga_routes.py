from flask import Blueprint, request,jsonify
from services.manga_service import get_popular_manga, search_manga,latest_updates,get_manga_info,get_chapter
from models.models import Manga ,db  

manga_bp = Blueprint("manga", __name__)

@manga_bp.route('/hello',methods=['GET'])
def test():
    return jsonify("connected")

@manga_bp.route('/latest',methods=['GET'])
def latest():
    
    source = request.args.get('source','mangabat')
    
    api = latest_updates(source)
    print("API data:",api)
    return jsonify(api)

@manga_bp.route('/manga_info',methods=['GET','POST'])
def manga_info():
    manga_url = request.args.get('mangaInfo')
    source_name = request.args.get('source', 'mangabat')

    
    if not manga_url:
        return jsonify({"error": "mangainfo parameter is missingo"}),400

    print("scraping from website ",manga_url)
   
    manga = get_manga_info(url=manga_url,source=source_name)
    
    if manga is None:
        return jsonify({"error": "Manga not found"}), 404

    return jsonify({
        "title" : manga.title ,
        "url" : manga.url,
        "cover" : manga.cover,
        "status" : manga.status,
        "author" : manga.author,
        "genres" : [str(g) for g in getattr(manga, "genres", [])],
        "chapters" :[c.serialize() for c in sorted(manga.chapters, key=lambda c: c.number or 0)]
        })


@manga_bp.route('/chapter',methods=['GET'])
def chapter():
    chapterUrl = request.args.get('chapterUrl')
    
    if chapterUrl is None:
        return jsonify({"error": "Missing mangaString parameter"}), 400

    chapter = get_chapter(chapterUrl)

    return jsonify(chapter)

@manga_bp.route('/popular', methods=['GET','POST'])
def popular():
    
    source = request.args.get('source','mangabat')

    popular = get_popular_manga(source)

    return jsonify(popular)

@manga_bp.route('/search', methods=['GET','POST'])
def search():
    mangaString = request.args.get('mangaString')
    source_name = request.args.get('source', 'mangabat')

    if mangaString is None:
        return jsonify({"error": "Missing mangaString parameter"}), 400

    mangas = search_manga(mangaString,source=source_name)

    return jsonify(mangas)