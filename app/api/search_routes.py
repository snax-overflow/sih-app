from flask import Blueprint, jsonify, render_template, request

from app.services.geocoding import SearchService

search_bp = Blueprint("search", __name__)


@search_bp.route("/")
def index():
    return render_template("index.html")


@search_bp.route("/api/v1/search", methods=["GET"])
def search_api():
    query = request.args.get("destination", "").strip()
    data, error = SearchService.find_destination_and_nearby(query)
    if error:
        status_code = 400 if error == "Destination query is required" else 404
        if error.startswith("Unable to contact"):
            status_code = 502
        return jsonify({"error": error}), status_code
    return jsonify(data)
