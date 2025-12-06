from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    """Initilises the db with flask"""
    db.init_app(app)
    migrate.init_app(app, db)

    from . import user, media, genre, watchlist, history, rating
