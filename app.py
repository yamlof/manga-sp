from flask import Flask
from flask import Flask
from flask_cors import CORS
from routes.manga_routes import manga_bp
from config.db import init_db

def create_app():
    app = Flask(__name__)
    
    #app.config.from_object("config_settings")
    
    CORS(app)
    
    init_db(app)
    
    
    #app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(manga_bp, url_prefix="/manga")
    #app.register_blueprint(user_bp, url_prefix="/user")
    
    @app.route("/")
    def home():
        return {"message": "Welcome to the Manga Server API"}
    
    return app


app = Flask(__name__)

CORS(app)



if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0',port=5000)

