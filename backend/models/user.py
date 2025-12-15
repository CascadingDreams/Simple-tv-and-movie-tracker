from datetime import datetime
from . import db


class User(db.Model):
    """User model for auth and user data"""

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)

    # user auth fields
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # other fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    watchlist = db.relationship(
        "Watchlist",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",  # returns query object instead of list - can filter
    )

    history = db.relationship(
        "History", back_populates="user", cascade="all, delete-orphan", lazy="dynamic"
    )

    ratings = db.relationship(
        "Rating", back_populates="user", cascade="all, delete-orphan", lazy="dynamic"
    )

    def __repr__(self):
        """displays user as username not object"""
        return f"<User {self.username}>"
