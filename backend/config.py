import os
from datetime import timedelta


class Config:
    _db_url = os.getenv("DATABASE_URL", "")
    # Render provides postgres:// but SQLAlchemy requires postgresql://
    SQLALCHEMY_DATABASE_URI = _db_url.replace("postgres://", "postgresql://", 1) if _db_url else None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
