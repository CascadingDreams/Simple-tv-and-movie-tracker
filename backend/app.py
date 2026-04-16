import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from models import init_db

app = Flask(__name__)
app.config.from_object(Config)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "https://stream-tracker-sh.vercel.app").split(",")
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
JWTManager(app)
init_db(app)

from routes.auth import bp as auth_bp
from routes.media import bp as media_bp
from routes.watchlist import bp as watchlist_bp
from routes.ratings import bp as ratings_bp

app.register_blueprint(auth_bp)
app.register_blueprint(media_bp)
app.register_blueprint(watchlist_bp)
app.register_blueprint(ratings_bp)


@app.route("/")
def home():
    return {"message": "API is running!"}


@app.route("/health")
def health():
    from models import db
    try:
        db.session.execute(db.text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}, 200
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
