from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    """Initilises the db with flask"""
    db.init_app(app)
    migrate.init_app(app, db)

    from . import associations
    from . import user, media, genre, watchlist, rating, people

    from .user import User
    from .media import Media
    from .genre import Genre
    from .watchlist import Watchlist
    from .rating import Rating
    from .people import Person

    __all__ = [
        "db",
        "migrate",
        "init_db",
        "User",
        "Media",
        "Genre",
        "Watchlist",
        "Rating",
        "Person",
    ]
