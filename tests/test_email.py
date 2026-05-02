"""Tests for Email Triggers features."""
import json


# --- Email Template API ---

def test_email_templates_page(auth_client):
    r = auth_client.get("/admin/email-templates")
    assert r.status_code == 200


def test_email_log_page(auth_client):
    r = auth_client.get("/admin/email-log")
    assert r.status_code == 200


def test_update_email_template(auth_client):
    # Create a template directly
    from models import EmailTemplate
    from extensions import db
    template = EmailTemplate(
        name="Test Template",
        subject="Original Subject",
        body_html="<p>Hello</p>",
        trigger_type="lead_magnet",
        active=True,
    )
    db.session.add(template)
    db.session.commit()

    r = auth_client.put(f"/api/email-templates/{template.id}",
        data=json.dumps({"subject": "Updated Subject", "active": False}),
        content_type="application/json")
    assert r.status_code == 200
    assert r.json["subject"] == "Updated Subject"
    assert r.json["active"] is False


def test_update_nonexistent_template(auth_client):
    r = auth_client.put("/api/email-templates/9999",
        data=json.dumps({"subject": "No Such Template"}),
        content_type="application/json")
    assert r.status_code == 404


# --- Email Trigger (mock mode) ---

def test_send_trigger_email_mock(auth_client, app):
    """Test that send_trigger_email creates a mock log entry."""
    from models import EmailTemplate, Contact, EmailLog
    from extensions import db
    from blueprints.email import send_trigger_email

    with app.app_context():
        template = EmailTemplate(
            name="Trigger Test",
            subject="Hello {{name}}",
            body_html="<p>Welcome {{name}}</p>",
            trigger_type="lead_magnet",
            active=True,
        )
        db.session.add(template)
        contact = Contact(name="Trigger User", email="trigger@test.com", status="Lead")
        db.session.add(contact)
        db.session.commit()

        log = send_trigger_email("lead_magnet", contact)
        assert log is not None
        assert log.status == "mock"
        assert log.to_email == "trigger@test.com"
        assert "Trigger User" in log.subject


def test_send_trigger_no_template(auth_client, app):
    """Test that send_trigger_email returns None when no matching template exists."""
    from models import Contact
    from extensions import db
    from blueprints.email import send_trigger_email

    with app.app_context():
        contact = Contact(name="No Template", email="notemplate@test.com", status="Lead")
        db.session.add(contact)
        db.session.commit()

        log = send_trigger_email("nonexistent_trigger", contact)
        assert log is None
