from flask import Flask
# Import the database defined in the models folder
from app.models.user import db 

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # --- Configuration ---
    # Secret key is required for security and tokens
    app.config['SECRET_KEY'] = 'super-secret-hackathon-key' 
    # Tell Flask where to save the SQLite database file
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sih_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Initialize Database ---
    db.init_app(app)
    
    # This automatically creates database tables if they don't exist yet
    with app.app_context():
        db.create_all()

    # --- Register Blueprints ---
    
    # The existing Search routes
    from app.api.search_routes import search_bp
    app.register_blueprint(search_bp)

    # The new Auth routes
    from app.api.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    return app