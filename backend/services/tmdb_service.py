import requests
from flask import current_app

TMDB_BASE_URL = "https://api.themoviedb.org/3"


def _get(endpoint, params=None):
    params = params or {}
    params["api_key"] = current_app.config["TMDB_API_KEY"]
    r = requests.get(f"{TMDB_BASE_URL}{endpoint}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def search(query, media_type="multi"):
    """Search TMDB. media_type: multi, movie, tv"""
    data = _get(f"/search/{media_type}", {"query": query, "include_adult": False})
    results = data.get("results", [])
    if media_type == "multi":
        results = [r for r in results if r.get("media_type") in ("movie", "tv")]
    return results


def get_details(tmdb_id, media_type):
    """Get full details for a movie or TV show, including credits"""
    return _get(f"/{media_type}/{tmdb_id}", {"append_to_response": "credits"})
