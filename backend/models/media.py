from .associations import media_genres
from datetime import datetime
from . import db


class Media(db.Model):
    """Media model"""

    __tablename__ = "media"
    id = db.Column(db.Integer, primary_key=True)

    tmdb_id = db.Column(db.Integer, unique=True, nullable=False)
    media_type = db.Column(db.String(10), nullable=False)

    title = db.Column(db.String(255), nullable=False, index=True)
    overview = db.Column(db.Text)
    original_language = db.Column(db.String(10))

    poster_path = db.Column(db.String(255))
    backdrop_path = db.Column(db.String(255))

    release_date = db.Column(db.Date, nullable=True)
    runtime = db.Column(db.Integer)

    number_of_seasons = db.Column(db.Integer, nullable=True)
    number_of_episodes = db.Column(db.Integer, nullable=True)

    status = db.Column(db.String(50))
    rating_avg = db.Column(db.Float)
    rating_count = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # to add relationships
    # watchlist
    # history
    # ratings

    # Media can have multiple genres
    genres = db.relationship("Genre", secondary="media_genres", back_populates="media")

    watchlist_entries = db.relationship(
        "Watchlist",
        back_populates="media",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    history_entries = db.relationship(
        "History", back_populates="media", cascade="all, delete-orphan", lazy="dynamic"
    )
    ratings = db.relationship(
        "Rating", back_populates="media", cascade="all, delete-orphan", lazy="dynamic"
    )
    people = db.relationship(
        "Person", secondary="media_people", back_populates="media_credits"
    )

    def __repr__(self):
        return f"<Media {self.title} ({self.media_type})>"
