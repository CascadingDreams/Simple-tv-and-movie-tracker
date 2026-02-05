from .associations import media_genres
from . import db


class Genre(db.Model):
    """Genre model"""

    __tablename__ = "genre"
    id = db.Column(db.Integer, primary_key=True)

    tmdb_genre_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, index=True)

    # Genre can belong to many media
    media = db.relationship("Media", secondary="media_genres", back_populates="genres")

    def __repr__(self):
        return f"<Genre {self.name}>"
