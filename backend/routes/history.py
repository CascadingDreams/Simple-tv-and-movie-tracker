from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.history import History
from routes.media import get_or_create_media, media_to_dict

bp = Blueprint("history", __name__, url_prefix="/api/history")


@bp.route("", methods=["GET"])
@jwt_required()
def get_history():
    user_id = int(get_jwt_identity())
    entries = (
        History.query.filter_by(user_id=user_id)
        .order_by(History.watched_at.desc())
        .all()
    )
    return jsonify([
        {
            "id": e.id,
            "watched_at": e.watched_at.isoformat(),
            "media": media_to_dict(e.media),
        }
        for e in entries
    ]), 200


@bp.route("", methods=["POST"])
@jwt_required()
def add_to_history():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    tmdb_id = data.get("tmdb_id")
    media_type = data.get("media_type")

    if not tmdb_id or media_type not in ("movie", "tv"):
        return jsonify({"error": "tmdb_id and valid media_type required"}), 400

    media = get_or_create_media(tmdb_id, media_type)
    entry = History(user_id=user_id, media_id=media.id)
    db.session.add(entry)
    db.session.commit()

    return jsonify({
        "id": entry.id,
        "watched_at": entry.watched_at.isoformat(),
        "media": media_to_dict(media),
    }), 201


@bp.route("/<int:entry_id>", methods=["DELETE"])
@jwt_required()
def remove_from_history(entry_id):
    user_id = int(get_jwt_identity())
    entry = History.query.filter_by(id=entry_id, user_id=user_id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Removed"}), 200
