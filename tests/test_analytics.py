"""Tests for Analytics features."""
import json


def test_dashboard_has_funnel(auth_client):
    """Dashboard should show conversion funnel when analytics enabled."""
    r = auth_client.get("/admin/dashboard")
    assert r.status_code == 200
    # The funnel HTML should be present (even if zero data)
    assert b"Conversion Funnel" in r.data or b"Page Views" in r.data


def test_page_view_tracking(client, app):
    """Landing page visits should create PageView records."""
    from models import PageView
    from extensions import db

    with app.app_context():
        initial_count = PageView.query.count()
        client.get("/lp")
        new_count = PageView.query.count()
        assert new_count > initial_count


def test_page_view_tracking_sales(client, app):
    """Sales page visits should create PageView records."""
    from models import PageView
    from extensions import db

    with app.app_context():
        initial_count = PageView.query.count()
        client.get("/sales")
        new_count = PageView.query.count()
        assert new_count > initial_count


def test_dashboard_stats_api(auth_client):
    """Dashboard stats API should still work."""
    r = auth_client.get("/api/dashboard-stats")
    assert r.status_code == 200
    data = r.json
    assert "total_contacts" in data
    assert "pipeline_value" in data


# --- Feature Toggle ---

def test_all_admin_pages_load(auth_client):
    """All admin pages should return 200."""
    pages = [
        "/admin/dashboard",
        "/admin/contacts",
        "/admin/deals",
        "/admin/clients",
        "/admin/products",
        "/admin/tasks",
        "/admin/email-templates",
        "/admin/email-log",
    ]
    for page in pages:
        r = auth_client.get(page)
        assert r.status_code == 200, f"Failed: {page} returned {r.status_code}"
