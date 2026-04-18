import pytest
import os
from extensions import db as _db


@pytest.fixture
def app():
    os.environ["DATABASE_URL"] = "sqlite://"
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["ADMIN_USER"] = "testadmin"
    os.environ["ADMIN_PASS"] = "testpass"
    os.environ["BUSINESS_NAME"] = "Test CRM"

    from app import create_app
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """A client that's already logged in."""
    client.post("/admin/login", data={"username": "testadmin", "password": "testpass"}, follow_redirects=True)
    return client
