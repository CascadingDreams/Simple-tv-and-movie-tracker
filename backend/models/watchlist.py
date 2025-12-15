from datetime import datetime
from . import db


class Watchlist(db.Model):
    """Watchlist model - tracks user's media list with status"""

    __tablename__ = "watchlist"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    media_id = db.Column(
        db.Integer, db.ForeignKey("media.id"), nullable=False, index=True
    )

    status = db.Column(db.String(50), nullable=False, default="plan_to_watch")
    added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "media_id", name="unique_user_media"),
    )

    user = db.relationship("User", back_populates="watchlist")
    media = db.relationship("Media", back_populates="watchlist_entries")

    def __repr__(self):
        return f"<Watchlist user_id={self.user_id} media_id={self.media_id} status={self.status}>"
