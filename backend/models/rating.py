from datetime import datetime
from . import db


class Rating(db.Model):
    """Rating model"""

    __tablename__ = "rating"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    media_id = db.Column(
        db.Integer, db.ForeignKey("media.id"), nullable=False, index=True
    )

    rating = db.Column(
        db.Integer,
        nullable=False,
    )
    review = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "media_id", name="unique_user_media_rating"),
        db.CheckConstraint("rating >= 1 AND rating <= 5", name="valid_rating_range"),
    )

    user = db.relationship("User", back_populates="ratings")
    media = db.relationship("Media", back_populates="ratings")

    def __repr__(self):
        return f"<Rating user_id={self.user_id} media_id={self.media_id} rating={self.rating}>"
