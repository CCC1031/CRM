import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db

load_dotenv()


def create_app():
    app = Flask(__name__)

    # Config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///crm.db"
    )
    # Railway uses postgres:// but SQLAlchemy needs postgresql://
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
        app.config["SQLALCHEMY_DATABASE_URI"] = app.config[
            "SQLALCHEMY_DATABASE_URI"
        ].replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Store business config
    app.config["ADMIN_USER"] = os.getenv("ADMIN_USER", "admin")
    app.config["ADMIN_PASS"] = os.getenv("ADMIN_PASS", "admin")
    app.config["BUSINESS_NAME"] = os.getenv("BUSINESS_NAME", "Command Center CRM")
    app.config["STRIPE_CHECKOUT_URL"] = os.getenv("STRIPE_CHECKOUT_URL", "#")
    app.config["LEAD_MAGNET_URL"] = os.getenv("LEAD_MAGNET_URL", "#")
    app.config["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY", "")

    # Init extensions
    db.init_app(app)

    # Register blueprints
    from blueprints.public import public_bp
    from blueprints.admin import admin_bp
    from blueprints.api import api_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Inject business name into all templates
    @app.context_processor
    def inject_globals():
        return {
            "business_name": app.config["BUSINESS_NAME"],
            "stripe_checkout_url": app.config["STRIPE_CHECKOUT_URL"],
            "lead_magnet_url": app.config["LEAD_MAGNET_URL"],
        }

    # Create tables on startup
    with app.app_context():
        import models  # noqa: F401
        db.create_all()

    return app


# For gunicorn: `gunicorn app:app`
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=8000)
