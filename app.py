from flask import Flask
from flask import Flask,jsonify,request
import urllib.parse
import requests,json
from flask_cors import CORS
from services.manga_service import latest_updates,get_manga_info,get_chapter,get_popular_manga,search_manga
from models.models import Manga

app = Flask(__name__)

CORS(app)

@app.route('/hello',methods=['GET'])
def test():
    return jsonify("connected")

@app.route('/latest',methods=['GET'])
def latest():
    api = latest_updates()
    print("API data:",api)
    return jsonify(api)

@app.route('/manga_info',methods=['GET','POST'])
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

@app.route('/chapter',methods=['GET'])
def chapter():
    chapterUrl = request.args.get('chapterUrl')
    
    if chapterUrl is None:
        return jsonify({"error": "Missing mangaString parameter"}), 400

    chapter = get_chapter(chapterUrl)

    return jsonify(chapter)

@app.route('/popular', methods=['GET'])
def popular():

    popular = get_popular_manga()

    return jsonify(popular)

@app.route('/search', methods=['GET'])
def search():
    mangaString = request.args.get('mangaString')
    
    if mangaString is None:
        return jsonify({"error": "Missing mangaString parameter"}), 400

    mangas = search_manga(mangaString)

    return jsonify(mangas)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)

