from datetime import datetime
from . import db


class History(db.Model):
    """History model tracks when users watch media"""

    __tablename__ = "history"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    media_id = db.Column(
        db.Integer, db.ForeignKey("media.id"), nullable=False, index=True
    )

    watched_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    user = db.relationship("User", back_populates="history")
    media = db.relationship("Media", back_populates="history_entries")

    def __repr__(self):
        return f"<History user_id={self.user_id} media_id={self.media_id} watched_at={self.watched_at}>"
