from datetime import datetime
from flask import Blueprint, request, jsonify
from models import db
from models.media import Media
from models.genre import Genre
from services.tmdb_service import search as tmdb_search, get_details

bp = Blueprint("media", __name__, url_prefix="/api/media")


def media_to_dict(media):
    return {
        "id": media.id,
        "tmdb_id": media.tmdb_id,
        "media_type": media.media_type,
        "title": media.title,
        "overview": media.overview,
        "poster_path": media.poster_path,
        "release_date": media.release_date.isoformat() if media.release_date else None,
        "rating_avg": media.rating_avg,
        "number_of_seasons": media.number_of_seasons,
        "status": media.status,
    }


def get_or_create_media(tmdb_id, media_type):
    """Return existing media row or fetch from TMDB and create it."""
    media = Media.query.filter_by(tmdb_id=tmdb_id, media_type=media_type).first()
    if media:
        return media

    details = get_details(tmdb_id, media_type)

    if media_type == "movie":
        title = details.get("title", "")
        release_date_str = details.get("release_date")
        runtime = details.get("runtime")
        num_seasons = None
        num_episodes = None
    else:
        title = details.get("name", "")
        release_date_str = details.get("first_air_date")
        runtime = None
        num_seasons = details.get("number_of_seasons")
        num_episodes = details.get("number_of_episodes")

    release_date = None
    if release_date_str:
        try:
            release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    media = Media(
        tmdb_id=tmdb_id,
        media_type=media_type,
        title=title,
        overview=details.get("overview"),
        original_language=details.get("original_language"),
        poster_path=details.get("poster_path"),
        backdrop_path=details.get("backdrop_path"),
        release_date=release_date,
        runtime=runtime,
        number_of_seasons=num_seasons,
        number_of_episodes=num_episodes,
        status=details.get("status"),
        rating_avg=details.get("vote_average"),
        rating_count=details.get("vote_count"),
    )

    for g in details.get("genres", []):
        genre = Genre.query.filter_by(tmdb_genre_id=g["id"]).first()
        if not genre:
            genre = Genre(tmdb_genre_id=g["id"], name=g["name"])
            db.session.add(genre)
        media.genres.append(genre)

    db.session.add(media)
    db.session.commit()
    return media


@bp.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Query required"}), 400

    results = tmdb_search(query)
    simplified = []
    for r in results[:20]:
        media_type = r.get("media_type", "movie")
        simplified.append({
            "tmdb_id": r["id"],
            "media_type": media_type,
            "title": r.get("title") or r.get("name", ""),
            "overview": r.get("overview", ""),
            "poster_path": r.get("poster_path"),
            "release_date": r.get("release_date") or r.get("first_air_date"),
            "rating_avg": r.get("vote_average"),
        })

    return jsonify(simplified), 200
