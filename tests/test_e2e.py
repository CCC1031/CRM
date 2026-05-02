"""Playwright E2E browser tests for all CRM features.

Run with: python3 -m pytest tests/test_e2e.py -v --headed (to watch)
       or: python3 -m pytest tests/test_e2e.py -v (headless)

Requires: pip install pytest-playwright && playwright install chromium
"""
import pytest
import threading
import time
import socket
from app import create_app
from extensions import db as _db
import os


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


TEST_PORT = find_free_port()
BASE = f"http://127.0.0.1:{TEST_PORT}"


@pytest.fixture(scope="module")
def live_app():
    os.environ["DATABASE_URL"] = "sqlite:///test_e2e.db"
    os.environ["SECRET_KEY"] = "e2e-test-secret"
    os.environ["ADMIN_USER"] = "admin"
    os.environ["ADMIN_PASS"] = "admin"
    os.environ["BUSINESS_NAME"] = "Test CRM"
    os.environ["FEATURE_PRODUCTS"] = "true"
    os.environ["FEATURE_CLIENTS"] = "true"
    os.environ["FEATURE_TASKS"] = "true"
    os.environ["FEATURE_EMAIL"] = "true"
    os.environ["FEATURE_ANALYTICS"] = "true"

    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        _db.create_all()
        from models import Contact, Deal, Product, Task, EmailTemplate, ClientNote
        from datetime import datetime, timedelta

        c1 = Contact(name="E2E Client", email="e2e@test.com", status="Client", company="E2E Corp")
        c2 = Contact(name="E2E Lead", email="lead@test.com", status="Lead")
        _db.session.add_all([c1, c2])
        _db.session.flush()

        _db.session.add(Deal(title="E2E Deal", contact_id=c1.id, value=50000, stage="Proposal"))
        _db.session.add(Product(name="E2E Product", price=47, product_type="paid", active=True))
        _db.session.add(Product(name="E2E Free", price=0, product_type="free", active=True))
        _db.session.add(Task(title="E2E Todo", status="todo", priority="high"))
        _db.session.add(Task(title="E2E In Progress", status="in_progress", priority="medium"))
        _db.session.add(Task(title="E2E Done", status="done", priority="low"))
        _db.session.add(EmailTemplate(name="Lead Magnet", subject="Welcome", body_html="<p>Hi</p>", trigger_type="lead_magnet", active=True))
        _db.session.add(ClientNote(contact_id=c1.id, title="Onboarding", content="Welcome"))
        _db.session.commit()

    server = threading.Thread(target=lambda: app.run(port=TEST_PORT, use_reloader=False), daemon=True)
    server.start()
    time.sleep(1.5)
    yield app

    with app.app_context():
        _db.drop_all()
    for p in ["test_e2e.db", "instance/test_e2e.db"]:
        try:
            os.remove(p)
        except FileNotFoundError:
            pass


def login(page):
    page.goto(f"{BASE}/admin/login")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "admin")
    page.click('button[type="submit"]')
    page.wait_for_url("**/admin/dashboard**")


# ===================== PUBLIC PAGES =====================

def test_landing_page(live_app, page):
    page.goto(f"{BASE}/lp")
    assert page.title()


def test_sales_page(live_app, page):
    page.goto(f"{BASE}/sales")
    assert page.title()


def test_store_page(live_app, page):
    page.goto(f"{BASE}/store")
    assert page.locator("text=E2E Product").count() > 0


def test_landing_form(live_app, page):
    page.goto(f"{BASE}/lp")
    page.fill('input[name="name"]', "Playwright Lead")
    page.fill('input[name="email"]', "playwright@test.com")
    page.click('button[type="submit"]')
    page.wait_for_url("**/thank-you**")


# ===================== AUTH =====================

def test_login(live_app, page):
    login(page)
    assert "dashboard" in page.url


def test_auth_redirect(live_app, page):
    page.goto(f"{BASE}/admin/dashboard")
    assert "login" in page.url


# ===================== DASHBOARD =====================

def test_dashboard_stats(live_app, page):
    login(page)
    assert page.locator("text=Total Contacts").count() > 0
    assert page.locator("text=Pipeline Value").count() > 0


def test_dashboard_funnel(live_app, page):
    login(page)
    funnel_visible = page.locator("text=Conversion Funnel").count() > 0 or page.locator("text=Page Views").count() > 0
    assert funnel_visible


# ===================== CONTACTS =====================

def test_contacts_page(live_app, page):
    login(page)
    page.goto(f"{BASE}/admin/contacts")
    assert page.locator("text=E2E Client").count() > 0


def test_contact_detail(live_app, page):
    login(page)
    page.goto(f"{BASE}/admin/contacts")
    page.click("text=E2E Client")
    page.wait_for_load_state("networkidle")
    assert page.locator("text=e2e@test.com").count() > 0


# ===================== DEALS =====================

def test_deals_pipeline(live_app, page):
    login(page)
    page.goto(f"{BASE}/admin/deals")
    assert page.locator("text=E2E Deal").count() > 0


# ===================== CLIENTS =====================

def test_clients_page(live_app, page):
    login(page)
    page.goto(f"{BASE}/admin/clients")
    assert page.locator("text=E2E Client").count() > 0


def test_client_notes(live_app, page):
    login(page)
    page.goto(f"{BASE}/admin/clients")
    page.click("text=E2E Client")
    page.wait_for_load_state("networkidle")
    assert page.locator("text=Onboarding").count() > 0


# ===================== PRODUCTS =====================

def test_products_page(live_app, page):
    login(page)
    page.goto(f"{BASE}/admin/products")
    assert page.locator("text=E2E Product").count() > 0


def test_product_detail(live_app, page):
    login(page)
    page.goto(f"{BASE}/admin/products")
    page.click("text=E2E Product")
    page.wait_for_load_state("networkidle")
    assert page.locator("text=E2E Product").count() > 0


# ===================== TASKS =====================

def test_tasks_kanban(live_app, page):
    login(page)
    page.goto(f"{BASE}/admin/tasks")
    assert page.locator("text=To Do").count() > 0
    assert page.locator("text=In Progress").count() > 0
    assert page.locator("text=Done").count() > 0
    assert page.locator("text=E2E Todo").count() > 0


# ===================== EMAIL =====================

def test_email_templates(live_app, page):
    login(page)
    page.goto(f"{BASE}/admin/email-templates")
    assert page.locator("text=Lead Magnet").count() > 0


def test_email_log(live_app, page):
    login(page)
    page.goto(f"{BASE}/admin/email-log")
    assert page.locator("text=Email Log").first.count() > 0


# ===================== SIDEBAR =====================

def test_sidebar_links(live_app, page):
    login(page)
    sidebar = page.locator("aside.sidebar")
    for link in ["Dashboard", "Contacts", "Deals", "Clients", "Products", "Tasks", "Email", "Logout"]:
        assert sidebar.locator(f"text={link}").count() > 0, f"Missing sidebar link: {link}"


# ===================== CHATBOT (bug fix verification) =====================

def test_chatbot_on_dashboard(live_app, page):
    login(page)
    page.click(".chat-toggle")
    page.wait_for_timeout(500)
    assert page.locator(".chat-panel").is_visible()
    assert page.locator("text=AI Assistant").count() > 0


def test_chatbot_on_contacts(live_app, page):
    """Verify chatbot bug fix — must work on contacts page."""
    login(page)
    page.goto(f"{BASE}/admin/contacts")
    page.wait_for_load_state("networkidle")
    page.click(".chat-toggle")
    page.wait_for_timeout(500)
    assert page.locator(".chat-panel").is_visible()


def test_chatbot_on_deals(live_app, page):
    """Verify chatbot bug fix — must work on deals page."""
    login(page)
    page.goto(f"{BASE}/admin/deals")
    page.wait_for_load_state("networkidle")
    page.click(".chat-toggle")
    page.wait_for_timeout(500)
    assert page.locator(".chat-panel").is_visible()


def test_chatbot_on_tasks(live_app, page):
    login(page)
    page.goto(f"{BASE}/admin/tasks")
    page.wait_for_load_state("networkidle")
    page.click(".chat-toggle")
    page.wait_for_timeout(500)
    assert page.locator(".chat-panel").is_visible()


def test_chatbot_on_products(live_app, page):
    login(page)
    page.goto(f"{BASE}/admin/products")
    page.wait_for_load_state("networkidle")
    page.click(".chat-toggle")
    page.wait_for_timeout(500)
    assert page.locator(".chat-panel").is_visible()
