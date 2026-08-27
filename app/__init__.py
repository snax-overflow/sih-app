from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    from app.api.search_routes import search_bp
    app.register_blueprint(search_bp)

    return app