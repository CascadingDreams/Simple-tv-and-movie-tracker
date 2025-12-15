from .associations import media_people
from . import db


class Person(db.Model):
    """Person (actors and directors) model"""

    __tablename__ = "people"
    id = db.Column(db.Integer, primary_key=True)

    tmdb_person_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False, index=True)
    profile_path = db.Column(db.String(255), nullable=True)
    known_for_department = db.Column(db.String(50), nullable=True)

    # people can be associated with many media
    media_credits = db.relationship(
        "Person", secondary=media_people, back_populates="people"
    )

    def __repr__(self):
        return f"<Person {self.name} ({self.known_for_department})>"
