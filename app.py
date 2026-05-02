import os
import uuid
from flask import Flask, request
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

    # Feature toggles
    app.config["FEATURE_PRODUCTS"] = os.getenv("FEATURE_PRODUCTS", "true")
    app.config["FEATURE_CLIENTS"] = os.getenv("FEATURE_CLIENTS", "true")
    app.config["FEATURE_TASKS"] = os.getenv("FEATURE_TASKS", "true")
    app.config["FEATURE_EMAIL"] = os.getenv("FEATURE_EMAIL", "true")
    app.config["FEATURE_ANALYTICS"] = os.getenv("FEATURE_ANALYTICS", "true")

    # Stripe keys (optional — mock mode if unset)
    app.config["STRIPE_SECRET_KEY"] = os.getenv("STRIPE_SECRET_KEY", "")
    app.config["STRIPE_PUBLISHABLE_KEY"] = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

    # Resend key (optional — mock mode if unset)
    app.config["RESEND_API_KEY"] = os.getenv("RESEND_API_KEY", "")
    app.config["RESEND_FROM_EMAIL"] = os.getenv("RESEND_FROM_EMAIL", "hello@yourdomain.com")

    # Init extensions
    db.init_app(app)

    # Register core blueprints
    from blueprints.public import public_bp
    from blueprints.admin import admin_bp
    from blueprints.api import api_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Register feature blueprints (only if enabled)
    if app.config["FEATURE_PRODUCTS"] == "true":
        from blueprints.products import products_bp
        app.register_blueprint(products_bp)

    if app.config["FEATURE_CLIENTS"] == "true":
        from blueprints.clients import clients_bp
        app.register_blueprint(clients_bp)

    if app.config["FEATURE_TASKS"] == "true":
        from blueprints.tasks import tasks_bp
        app.register_blueprint(tasks_bp)

    if app.config["FEATURE_EMAIL"] == "true":
        from blueprints.email import email_bp
        app.register_blueprint(email_bp)

    # Inject business name and feature flags into all templates
    @app.context_processor
    def inject_globals():
        return {
            "business_name": app.config["BUSINESS_NAME"],
            "stripe_checkout_url": app.config["STRIPE_CHECKOUT_URL"],
            "lead_magnet_url": app.config["LEAD_MAGNET_URL"],
        }

    # Analytics middleware — track page views on public pages
    if app.config["FEATURE_ANALYTICS"] == "true":
        @app.before_request
        def track_page_view():
            if request.endpoint in ("public.landing", "public.sales", "products.store"):
                from models import PageView
                visitor_id = request.cookies.get("visitor_id")
                if not visitor_id:
                    visitor_id = str(uuid.uuid4())
                page_view = PageView(
                    page=request.path,
                    visitor_id=visitor_id,
                    referrer=request.referrer,
                )
                db.session.add(page_view)
                db.session.commit()

        @app.after_request
        def set_visitor_cookie(response):
            if not request.cookies.get("visitor_id"):
                response.set_cookie("visitor_id", str(uuid.uuid4()), max_age=60*60*24*365)
            return response

    # Create tables on startup
    with app.app_context():
        import models  # noqa: F401
        db.create_all()

    return app


# For gunicorn: `gunicorn app:app`
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=8000)
