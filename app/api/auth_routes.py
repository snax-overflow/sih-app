"""
Authentication Routes Module.
Handles all API endpoints related to user registration and login.
Connects the frontend JSON requests to the backend authentication logic.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from app.services.auth_services import AuthService

auth_bp = Blueprint("auth", __name__)


# ---------------------------
# VIEW ROUTES (Pages)
# ---------------------------

@auth_bp.route("/login", methods=["GET"])
@auth_bp.route("/auth", methods=["GET"])
def auth_page():
    """
    Renders the frontend authentication page.
    Supports both /login and /auth paths.
    """
    return render_template("auth.html")


# ---------------------------
# API ENDPOINTS
# ---------------------------

@auth_bp.route("/api/v1/register", methods=["POST"])
def register():
    data = request.get_json()
    result, error = AuthService.register_user(data.get("email"), data.get("password"))
    
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify(result), 201


@auth_bp.route("/api/v1/login", methods=["POST"])
def login():
    data = request.get_json()
    result, error = AuthService.login_user(data.get("email"), data.get("password"))
    
    if error:
        return jsonify({"error": error}), 401
    session["user_id"] = data.get("email")  # or result.get("user_id")
        
    # If using Flask sessions alongside JWT, store a flag or identifier:
    # session["user"] = data.get("email")

    return jsonify(result), 200


@auth_bp.route("/logout", methods=["GET"])
def logout():
    """
    Clears the server-side session and redirects back to the login page.
    """
    session.clear()
    return redirect(url_for("auth.auth_page"))