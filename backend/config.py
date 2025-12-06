import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://streamtracker:streamtracker123@db:5432/streamtracker",
    )

    SQL_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-later")

    TMDB_API_KEY = os.getenv("TMDB_API_KEY", "cecc549a14310092d5250896ffb47b6e")
