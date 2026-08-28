"""
Search Routes Module
Handles API endpoints and view routes related to destination searching.
Uses a Blueprint to keep route definitions modular and separated from the main app.
"""

from flask import Blueprint, jsonify, render_template, request
from app.services.geocoding import SearchService

# Initialize the Blueprint. 
# 'search' is the name of the blueprint, and __name__ helps Flask locate associated resources.
search_bp = Blueprint("search", __name__)


@search_bp.route("/")
def index():
    """
    Renders the main landing page of the application.
    
    Returns:
        HTML template for the index page.
    """
    return render_template("index.html")


@search_bp.route("/api/v1/search", methods=["GET"])
def search_api():
    """
    API endpoint to search for a destination and its nearby places.
    Expects a query parameter: ?destination=<location_name>
    
    Returns:
        JSON response containing the destination data, or a JSON error message with 
        the appropriate HTTP status code.
    """
    # 1. Extract the 'destination' parameter from the URL (e.g., ?destination=Paris)
    # .strip() removes any accidental leading/trailing spaces from the user's input.
    query = request.args.get("destination", "").strip()
    
    # 2. Pass the clean query to our service layer to do the actual data fetching
    data, error = SearchService.find_destination_and_nearby(query)
    
    # 3. Handle any errors returned by the service layer
    if error:
        # Default to 404 (Not Found), but switch to 400 (Bad Request) if the user left it blank
        status_code = 400 if error == "Destination query is required" else 404
        
        # If the external geocoding API crashed, return a 502 (Bad Gateway)
        if error.startswith("Unable to contact"):
            status_code = 502
            
        return jsonify({"error": error}), status_code
        
    # 4. If everything went perfectly, return the data as JSON with a default 200 OK status
    return jsonify(data)