from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.watchlist import Watchlist
from routes.media import get_or_create_media, media_to_dict

bp = Blueprint("watchlist", __name__, url_prefix="/api/watchlist")

VALID_STATUSES = {"plan_to_watch", "watching", "completed", "on_hold", "dropped"}


@bp.route("", methods=["GET"])
@jwt_required()
def get_watchlist():
    user_id = int(get_jwt_identity())
    entries = (
        Watchlist.query.filter_by(user_id=user_id)
        .order_by(Watchlist.updated_at.desc())
        .all()
    )
    return jsonify([
        {
            "id": e.id,
            "status": e.status,
            "added_at": e.added_at.isoformat(),
            "media": media_to_dict(e.media),
        }
        for e in entries
    ]), 200


@bp.route("", methods=["POST"])
@jwt_required()
def add_to_watchlist():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    tmdb_id = data.get("tmdb_id")
    media_type = data.get("media_type")
    status = data.get("status", "plan_to_watch")

    if not tmdb_id or media_type not in ("movie", "tv"):
        return jsonify({"error": "tmdb_id and valid media_type required"}), 400
    if status not in VALID_STATUSES:
        return jsonify({"error": "Invalid status"}), 400

    media = get_or_create_media(tmdb_id, media_type)

    if Watchlist.query.filter_by(user_id=user_id, media_id=media.id).first():
        return jsonify({"error": "Already in watchlist"}), 409

    entry = Watchlist(user_id=user_id, media_id=media.id, status=status)
    db.session.add(entry)
    db.session.commit()

    return jsonify({"id": entry.id, "status": entry.status, "media": media_to_dict(media)}), 201


@bp.route("/<int:entry_id>", methods=["PUT"])
@jwt_required()
def update_watchlist(entry_id):
    user_id = int(get_jwt_identity())
    entry = Watchlist.query.filter_by(id=entry_id, user_id=user_id).first_or_404()

    data = request.get_json()
    status = data.get("status")
    if status:
        if status not in VALID_STATUSES:
            return jsonify({"error": "Invalid status"}), 400
        entry.status = status

    db.session.commit()
    return jsonify({"id": entry.id, "status": entry.status}), 200


@bp.route("/<int:entry_id>", methods=["DELETE"])
@jwt_required()
def remove_from_watchlist(entry_id):
    user_id = int(get_jwt_identity())
    entry = Watchlist.query.filter_by(id=entry_id, user_id=user_id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Removed"}), 200
