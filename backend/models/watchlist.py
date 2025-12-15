''' from datetime import datetime
from . import db


class Watchlist(db.Model):
    """Watchlist model"""

    __tablename__ = "watchlist"
    id = db.Column(db.Integer, primary_key=True)

    user_id = 
    media_id =
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    Unique constraint on user_id, media_id - can only have one of each