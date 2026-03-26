from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.rating import Rating
from routes.media import get_or_create_media, media_to_dict

bp = Blueprint("ratings", __name__, url_prefix="/api/ratings")


@bp.route("", methods=["GET"])
@jwt_required()
def get_ratings():
    user_id = int(get_jwt_identity())
    entries = (
        Rating.query.filter_by(user_id=user_id)
        .order_by(Rating.created_at.desc())
        .all()
    )
    return jsonify([
        {
            "id": e.id,
            "rating": e.rating,
            "review": e.review,
            "created_at": e.created_at.isoformat(),
            "media": media_to_dict(e.media),
        }
        for e in entries
    ]), 200


@bp.route("", methods=["POST"])
@jwt_required()
def add_rating():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    tmdb_id = data.get("tmdb_id")
    media_type = data.get("media_type")
    rating_value = data.get("rating")
    review = data.get("review") or ""

    if not tmdb_id or media_type not in ("movie", "tv"):
        return jsonify({"error": "tmdb_id and valid media_type required"}), 400
    if not isinstance(rating_value, int) or not (1 <= rating_value <= 5):
        return jsonify({"error": "Rating must be 1–5"}), 400

    media = get_or_create_media(tmdb_id, media_type)

    if Rating.query.filter_by(user_id=user_id, media_id=media.id).first():
        return jsonify({"error": "Already rated — use PUT to update"}), 409

    entry = Rating(user_id=user_id, media_id=media.id, rating=rating_value, review=review)
    db.session.add(entry)
    db.session.commit()

    return jsonify({
        "id": entry.id,
        "rating": entry.rating,
        "review": entry.review,
        "media": media_to_dict(media),
    }), 201


@bp.route("/<int:entry_id>", methods=["PUT"])
@jwt_required()
def update_rating(entry_id):
    user_id = int(get_jwt_identity())
    entry = Rating.query.filter_by(id=entry_id, user_id=user_id).first_or_404()

    data = request.get_json()
    rating_value = data.get("rating")
    if rating_value is not None:
        if not isinstance(rating_value, int) or not (1 <= rating_value <= 5):
            return jsonify({"error": "Rating must be 1–5"}), 400
        entry.rating = rating_value

    review = data.get("review")
    if review is not None:
        entry.review = review

    db.session.commit()
    return jsonify({"id": entry.id, "rating": entry.rating, "review": entry.review}), 200


@bp.route("/<int:entry_id>", methods=["DELETE"])
@jwt_required()
def delete_rating(entry_id):
    user_id = int(get_jwt_identity())
    entry = Rating.query.filter_by(id=entry_id, user_id=user_id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200
