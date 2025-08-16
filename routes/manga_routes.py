from flask import Blueprint, request,jsonify
from services.manga_service import get_popular_manga, search_manga,latest_updates,get_manga_info,get_chapter

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


    print("received ",manga_url)
   
    manga = get_manga_info(manga_url)
    
    if manga is None:
        return jsonify({"error": "Manga not found"}), 404

    return jsonify({
        "title" : manga.title ,
        "cover" : manga.cover,
        "status" : manga.status,
        "author" : manga.author,
        "chapters" :manga.chapters
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