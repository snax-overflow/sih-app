"""
Authentication Routes Module.
Handles all API endpoints related to user registration and login.
Connects the frontend JSON requests to the backend authentication logic.
"""

from flask import Blueprint, request, jsonify, render_template
# Importing from auth_services file to handle the actual logic
from app.services.auth_services import AuthService

# Initialize the Blueprint.
# 'auth' is the blueprint name, which we registered in __init__.py
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/v1/register", methods=["POST"])
def register():
    """
    API endpoint to register a new user.
    Expects a JSON body containing 'email' and 'password'.
    
    Returns:
        JSON response with a success message (201 Created) or error (400 Bad Request).
    """
    # 1. Parse the incoming JSON data from the frontend fetch() request
    data = request.get_json()
    
    # 2. Pass the extracted email and password to the service layer for processing
    # .get() is safer than data['email'] because it won't crash if the frontend forgot to send it
    result, error = AuthService.register_user(data.get("email"), data.get("password"))
    
    # 3. Handle errors (e.g., if the email already exists in the database)
    if error:
        # 400 Bad Request: The server cannot process the request due to a client error
        return jsonify({"error": error}), 400
        
    # 4. Success! Return the result message with a 201 status code
    # 201 Created: Standard response when a new resource is successfully created
    return jsonify(result), 201


@auth_bp.route("/api/v1/login", methods=["POST"])
def login():
    """
    API endpoint to log in an existing user.
    Expects a JSON body containing 'email' and 'password'.
    
    Returns:
        JSON response with a JWT token (200 OK) or error (401 Unauthorized).
    """
    # 1. Parse the incoming JSON data
    data = request.get_json()
    
    # 2. Ask the service layer to verify the credentials and generate a token
    result, error = AuthService.login_user(data.get("email"), data.get("password"))
    
    # 3. Handle login failures (wrong password, user doesn't exist, etc.)
    if error:
        # 401 Unauthorized: Standard response when authentication fails
        return jsonify({"error": error}), 401
        
    # 4. Success! Return the JWT token to the frontend
    # 200 OK: Standard response for a successful request
    return jsonify(result), 200

@auth_bp.route("/auth", methods=["GET"])
def auth_page():
    """
    Renders the frontend authentication page.
    """
    return render_template("auth.html")