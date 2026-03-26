from pathlib import Path

from flask import Flask, jsonify, render_template

from models import db
from routes.calculator import calculator_bp
from routes.provisions import provisions_bp


def create_app() -> Flask:
    app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

    database_path = Path(app.root_path) / "survival_provisions.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(provisions_bp)
    app.register_blueprint(calculator_bp)

    @app.get("/")
    def index():
        return render_template("menu.html")

    @app.get("/proviant")
    def provisions_dashboard():
        return render_template("provisions.html")

    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(_error):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def handle_server_error(_error):
        return jsonify({"error": "Internal server error"}), 500

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
