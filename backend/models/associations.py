from . import db

media_genres = db.Table(
    "media_genres",
    db.Column("media_id", db.Integer, db.ForeignKey("media.id"), primary_key=True),
    db.Column("genre_id", db.Integer, db.ForeignKey("genre.id"), primary_key=True),
)

media_people = db.Table(
    "media_people",
    db.Column("media_id", db.Integer, db.ForeignKey("media.id"), primary_key=True),
    db.Column("person_id", db.Integer, db.ForeignKey("people.id"), primary_key=True),
    db.Column("role", db.String(50)),
    db.Column("character", db.String(255), nullable=True),
)
