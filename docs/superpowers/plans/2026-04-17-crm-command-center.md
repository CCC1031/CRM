# CRM Command Center Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a premium, AI-powered CRM web app that workshop students can deploy to Railway and customize for their business.

**Architecture:** Flask monolith serving public pages + admin portal + JSON API + AI chatbot. Jinja2 templates with Tailwind CSS (CDN) and Alpine.js (CDN) for interactivity. SQLAlchemy ORM with PostgreSQL. OpenRouter API for AI chatbot routing to Gemini 2.5 Flash / Sonnet 4.

**Tech Stack:** Flask 3.x, SQLAlchemy 2.x, PostgreSQL, Tailwind CSS (CDN), Alpine.js (CDN), SortableJS (CDN), Chart.js (CDN), OpenRouter API, gunicorn, Railway

**Spec:** `docs/superpowers/specs/2026-04-17-crm-command-center-design.md`

---

## File Structure

```
crm-command-center/
  app.py                          # Flask app factory, config, db init, blueprint registration
  models.py                       # SQLAlchemy models: Contact, Deal, Note, ActivityLog
  auth.py                         # @login_required decorator, login/logout helpers
  seed.py                         # Demo data: 15 contacts, 8 deals, notes, activity
  requirements.txt                # Flask, SQLAlchemy, psycopg2-binary, gunicorn, python-dotenv, requests
  Procfile                        # web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
  .env.example                    # Template env vars
  .gitignore                      # Python defaults + .env
  blueprints/
    __init__.py                   # Empty
    public.py                     # Routes: /, /lp, /lp/submit, /lp/thank-you, /sales
    admin.py                      # Routes: /admin/login, logout, dashboard, contacts, deals
    api.py                        # JSON API: /api/contacts, /api/deals, /api/chat, /api/dashboard-stats
  templates/
    base.html                     # Root layout: Tailwind CDN, Alpine.js CDN, Inter font, PWA manifest link, body slot
    base_admin.html               # Extends base: sidebar nav + AI chat panel + main content area
    public/
      landing.html                # Lead magnet page with email capture form
      sales.html                  # Sales page with Stripe checkout link button
      thank_you.html              # Post-form thank you page
    admin/
      login.html                  # Login form (extends base.html directly)
      dashboard.html              # KPI cards + recent activity feed (extends base_admin)
      contacts.html               # Contact list table with search/filter (extends base_admin)
      contact_detail.html         # Contact info + notes + deals + activity timeline (extends base_admin)
      deals.html                  # Pipeline view — list grouped by stage, later Kanban (extends base_admin)
  static/
    css/
      custom.css                  # CAM 2.0 brand system: CSS variables, component classes, sidebar, cards, buttons, inputs, toasts, modals
    js/
      chat.js                     # Alpine.js chatbot component (Phase 3)
      pipeline.js                 # SortableJS Kanban logic (Phase 4)
    manifest.json                 # PWA manifest (Phase 5)
    icons/
      icon-192.png                # PWA icon (Phase 5)
      icon-512.png                # PWA icon (Phase 5)
  tests/
    conftest.py                   # Flask test client fixture, test database setup
    test_models.py                # Model creation, relationships, constraints
    test_api.py                   # API endpoint tests (CRUD, auth, validation)
    test_auth.py                  # Login, logout, protected routes
```

---

## PHASE 1: THE KITCHEN (MVP)

**Goal:** Deployable CRM with login, contacts, deals, dashboard, demo data, and premium dark gold UI.
**Restaurant analogy:** "Setting up your kitchen — every restaurant needs a place to prep before opening night."

---

### Task 1: Project Scaffold + Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `Procfile`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `blueprints/__init__.py`

- [ ] **Step 1: Initialize git repo**

```bash
cd "/Users/jonathanacuna/Documents/VS Code Programs/CRM Demo For Claude Workshop"
git init
```

- [ ] **Step 2: Create .gitignore**

```
__pycache__/
*.pyc
.env
*.db
.venv/
venv/
*.egg-info/
dist/
build/
.DS_Store
```

- [ ] **Step 3: Create requirements.txt**

```
flask>=3.1
flask-sqlalchemy>=3.1
sqlalchemy>=2.0
psycopg2-binary>=2.9
gunicorn>=22.0
python-dotenv>=1.0
requests>=2.32
```

- [ ] **Step 4: Create Procfile**

```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
```

- [ ] **Step 5: Create .env.example**

```env
# Database (Railway provides this automatically)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Admin Login
ADMIN_USER=admin
ADMIN_PASS=changeme

# Flask
SECRET_KEY=change-this-to-a-random-string
FLASK_ENV=development

# AI Chatbot (Phase 3)
OPENROUTER_API_KEY=sk-or-your-key-here

# Business Settings
BUSINESS_NAME=My Business CRM
STRIPE_CHECKOUT_URL=https://buy.stripe.com/your-link
LEAD_MAGNET_URL=https://your-lead-magnet-download-link
```

- [ ] **Step 6: Create empty blueprints/__init__.py**

Empty file.

- [ ] **Step 7: Create virtual environment and install deps**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- [ ] **Step 8: Commit**

```bash
git add .gitignore requirements.txt Procfile .env.example blueprints/__init__.py
git commit -m "feat: project scaffold with Flask dependencies and Railway config"
```

---

### Task 2: Flask App Factory + Config

**Files:**
- Create: `app.py`

- [ ] **Step 1: Create app.py with app factory**

```python
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


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
    app.config["BUSINESS_NAME"] = os.getenv("BUSINESS_NAME", "My Business CRM")
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

    # Create tables on first request
    with app.app_context():
        import models  # noqa: F401
        db.create_all()

    return app


# For gunicorn: `gunicorn app:app`
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

- [ ] **Step 2: Create minimal blueprint stubs so the app can start**

Create `blueprints/public.py`:
```python
from flask import Blueprint, redirect

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    return redirect("/lp")


@public_bp.route("/lp")
def landing():
    return "<h1>Landing Page — Coming Soon</h1>"
```

Create `blueprints/admin.py`:
```python
from flask import Blueprint

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/login")
def login():
    return "<h1>Login — Coming Soon</h1>"
```

Create `blueprints/api.py`:
```python
from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__)


@api_bp.route("/health")
def health():
    return jsonify({"status": "ok"})
```

- [ ] **Step 3: Run the app to verify it starts**

```bash
source .venv/bin/activate
python app.py
```

Expected: Server starts on `http://127.0.0.1:5000`. Visit `/` redirects to `/lp`. Visit `/api/health` returns `{"status": "ok"}`.

- [ ] **Step 4: Commit**

```bash
git add app.py blueprints/
git commit -m "feat: Flask app factory with config, blueprint stubs, and health endpoint"
```

---

### Task 3: SQLAlchemy Models

**Files:**
- Create: `models.py`

- [ ] **Step 1: Create models.py with all 4 models**

```python
from datetime import datetime, date
from app import db


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    company = db.Column(db.String(200))
    status = db.Column(db.String(20), default="Lead")  # Lead, Customer, VIP, Inactive
    lead_source = db.Column(db.String(30), default="Other")  # Website Form, TikTok, Referral, Workshop, Cold Outreach, Other
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    notes = db.relationship("Note", backref="contact", lazy=True, cascade="all, delete-orphan")
    deals = db.relationship("Deal", backref="contact", lazy=True)
    activities = db.relationship("ActivityLog", backref="contact", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "company": self.company,
            "status": self.status,
            "lead_source": self.lead_source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Deal(db.Model):
    __tablename__ = "deals"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    value = db.Column(db.Numeric(12, 2), default=0)
    stage = db.Column(db.String(30), default="New Lead")  # New Lead, Contacted, Proposal, Negotiation, Won, Lost
    expected_close_date = db.Column(db.Date, nullable=True)
    won_lost_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    activities = db.relationship("ActivityLog", backref="deal", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "contact_id": self.contact_id,
            "contact_name": self.contact.name if self.contact else None,
            "value": float(self.value) if self.value else 0,
            "stage": self.stage,
            "expected_close_date": self.expected_close_date.isoformat() if self.expected_close_date else None,
            "won_lost_reason": self.won_lost_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "contact_id": self.contact_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ActivityLog(db.Model):
    __tablename__ = "activity_log"

    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    deal_id = db.Column(db.Integer, db.ForeignKey("deals.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "action_type": self.action_type,
            "description": self.description,
            "contact_id": self.contact_id,
            "deal_id": self.deal_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def log_activity(action_type, description, contact_id=None, deal_id=None):
    """Helper to log an activity. Call BEFORE db.session.commit() — does NOT commit itself."""
    activity = ActivityLog(
        action_type=action_type,
        description=description,
        contact_id=contact_id,
        deal_id=deal_id,
    )
    db.session.add(activity)
    return activity
```

- [ ] **Step 2: Verify the app still starts (models are imported in app.py)**

```bash
python app.py
```

Expected: Server starts, `crm.db` SQLite file is created (local dev fallback).

- [ ] **Step 3: Commit**

```bash
git add models.py
git commit -m "feat: SQLAlchemy models for contacts, deals, notes, and activity log"
```

---

### Task 4: Authentication

**Files:**
- Create: `auth.py`
- Modify: `blueprints/admin.py`

- [ ] **Step 1: Create auth.py with login decorator**

```python
from functools import wraps
from flask import session, redirect, url_for, request, current_app


def login_required(f):
    """Decorator to protect admin routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def check_credentials(username, password):
    """Validate against env var credentials."""
    return (
        username == current_app.config["ADMIN_USER"]
        and password == current_app.config["ADMIN_PASS"]
    )
```

- [ ] **Step 2: Build login/logout routes in admin.py**

```python
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from auth import login_required, check_credentials

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if check_credentials(username, password):
            session["logged_in"] = True
            session.permanent = True
            next_url = request.args.get("next", url_for("admin.dashboard"))
            return redirect(next_url)
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("admin/dashboard.html")


@admin_bp.route("/contacts")
@login_required
def contacts():
    return render_template("admin/contacts.html")


@admin_bp.route("/contacts/<int:contact_id>")
@login_required
def contact_detail(contact_id):
    return render_template("admin/contact_detail.html", contact_id=contact_id)


@admin_bp.route("/deals")
@login_required
def deals():
    return render_template("admin/deals.html")
```

- [ ] **Step 3: Commit**

```bash
git add auth.py blueprints/admin.py
git commit -m "feat: session-based auth with login decorator and admin routes"
```

---

### Task 5: Brand System CSS

**Files:**
- Create: `static/css/custom.css`

- [ ] **Step 1: Create custom.css with full CAM 2.0 brand system**

This is the largest single file — it defines the entire visual identity. All CSS variables, component classes, sidebar, cards, buttons, inputs, toasts, modals, responsive breakpoints.

Key design tokens from spec:
- Backgrounds: `#0B0B0D`, `#111215`, `#17181C`, `#1E2025`
- Gold: `#C7A35A` (primary), `#B88933` (hover), `#E4D3A2` (champagne)
- Text: `#F5F0E8` (primary), `#C8C0B4` (muted), `#9E978C` (subtle)
- Border: `#31343C`
- Font: Inter, weights 400-700
- Radius: 8px (buttons/inputs), 12px (cards), 16px (modals)
- Card padding: 20px
- Sidebar: 200px fixed width

The CSS file should include these sections:
1. CSS custom properties (`:root`)
2. Base reset + body styles
3. Typography classes
4. Sidebar navigation (`.sidebar`, `.sidebar-brand`, `.sidebar-link`, `.sidebar-link.active`)
5. Main content area (`.main-content`)
6. Cards/widgets (`.card`, `.card-header`, `.card-title`)
7. Stat cards (`.stat-card`, `.stat-value`, `.stat-label`)
8. Buttons (`.btn`, `.btn-primary`, `.btn-secondary`, `.btn-outline`, `.btn-ghost`, `.btn-danger`, `.btn-sm`, `.btn-lg`)
9. Form inputs (`.form-group`, `.form-label`, `input`, `select`, `textarea`)
10. Tables (`.table`, `thead`, `tbody`, `tr`, `td`)
11. Badges/chips (`.badge`, `.badge-lead`, `.badge-customer`, `.badge-vip`)
12. Toasts (`.toast-container`, `.toast`, `.toast-success`, `.toast-error`)
13. Modals (`.modal-overlay`, `.modal`, `.modal-header`, `.modal-footer`)
14. Chat panel (`.chat-panel`, `.chat-messages`, `.chat-input`)
15. Pipeline/Kanban (`.pipeline-column`, `.deal-card`)
16. Activity timeline (`.timeline`, `.timeline-item`)
17. Responsive breakpoints (`@media` for mobile)
18. Utility classes (`.text-gold`, `.text-muted`, `.mt-4`, `.mb-4`, `.flex`, `.gap-4`)
19. Animations (`@keyframes slideIn`, `@keyframes fadeIn`)
20. Scrollbar styling (`::-webkit-scrollbar`)

Build this as one comprehensive file (~600-800 lines). Every component the app uses should be styled here so templates only need class names.

- [ ] **Step 2: Commit**

```bash
git add static/css/custom.css
git commit -m "feat: CAM 2.0 premium dark gold brand system CSS"
```

---

### Task 6: Base Templates

**Files:**
- Create: `templates/base.html`
- Create: `templates/base_admin.html`

- [ ] **Step 1: Create base.html — root layout**

Must include:
- `<!DOCTYPE html>` with `lang="en"`
- `<meta charset="UTF-8">` + viewport meta for mobile
- `<meta name="apple-mobile-web-app-capable" content="yes">`
- `<meta name="theme-color" content="#0B0B0D">`
- Google Fonts CDN link for Inter (weights 400,500,600,700)
- Tailwind CSS CDN: `<script src="https://cdn.tailwindcss.com"></script>`
- Alpine.js CDN: `<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>`
- Link to `/static/css/custom.css`
- `<title>{% block title %}{{ business_name }}{% endblock %}</title>`
- `{% block head %}{% endblock %}` for page-specific head content
- `<body class="bg-primary text-primary">` with dark background
- `{% block body %}{% endblock %}` — full body slot
- Toast container div at bottom
- `{% block scripts %}{% endblock %}` for page-specific JS

- [ ] **Step 2: Create base_admin.html — admin layout extending base**

Must include:
- `{% extends "base.html" %}`
- Override `{% block body %}` with:
  - Fixed sidebar (200px) with:
    - Brand area: icon + "{{ business_name }}" + tagline
    - Nav links: Dashboard, Contacts, Deals (with Lucide-style SVG icons inline)
    - Bottom: Logout link
    - Active state: highlight current page via `request.endpoint`
  - Main content area (`margin-left: 200px; padding: 24px 32px;`):
    - Page header: `{% block page_title %}{% endblock %}`
    - Content: `{% block content %}{% endblock %}`
  - AI Chat panel placeholder (hidden by default, Phase 3 activates it):
    - Toggle button (floating, bottom-right)
    - Slide-in panel (320px, right side)
  - Mobile: sidebar collapses, hamburger menu toggle via Alpine.js

- [ ] **Step 3: Verify templates render**

The admin routes already reference these templates. Start the app and visit `/admin/login`, then `/admin/dashboard` (after logging in).

- [ ] **Step 4: Commit**

```bash
git add templates/
git commit -m "feat: base templates with dark gold theme, sidebar nav, and admin layout"
```

---

### Task 7: Login Page

**Files:**
- Create: `templates/admin/login.html`

- [ ] **Step 1: Create login.html**

- Extends `base.html` (not base_admin — no sidebar on login)
- Centered card on dark background
- Brand icon + business name at top
- Username + password fields with gold-bordered inputs
- "Sign In" button (`.btn-primary`, full width)
- Flash message display for errors (red toast-style)
- Subtle tagline: "Your Command Center"
- Mobile responsive (card is full-width on small screens)

- [ ] **Step 2: Test login flow**

1. Visit `/admin/login` — see styled login page
2. Enter wrong credentials — see error flash
3. Enter correct credentials (from env/defaults: admin/admin) — redirect to dashboard

- [ ] **Step 3: Commit**

```bash
git add templates/admin/login.html
git commit -m "feat: premium login page with dark gold theme"
```

---

### Task 8: API Endpoints — Contacts CRUD

**Files:**
- Modify: `blueprints/api.py`

- [ ] **Step 1: Build contacts API endpoints**

Add to `blueprints/api.py`:

```python
from flask import Blueprint, jsonify, request
from app import db
from models import Contact, Deal, Note, ActivityLog, log_activity
from auth import login_required

api_bp = Blueprint("api", __name__)


@api_bp.route("/health")
def health():
    return jsonify({"status": "ok"})


# --- CONTACTS ---

@api_bp.route("/contacts", methods=["GET"])
@login_required
def list_contacts():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()

    query = Contact.query

    if q:
        search = f"%{q}%"
        query = query.filter(
            db.or_(
                Contact.name.ilike(search),
                Contact.email.ilike(search),
                Contact.company.ilike(search),
                Contact.phone.ilike(search),
            )
        )

    if status:
        query = query.filter(Contact.status == status)

    contacts = query.order_by(Contact.created_at.desc()).all()
    return jsonify([c.to_dict() for c in contacts])


@api_bp.route("/contacts", methods=["POST"])
@login_required
def create_contact():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    contact = Contact(
        name=data["name"],
        email=data.get("email"),
        phone=data.get("phone"),
        company=data.get("company"),
        status=data.get("status", "Lead"),
        lead_source=data.get("lead_source", "Other"),
    )
    db.session.add(contact)
    db.session.commit()

    log_activity("contact_created", f"Created contact: {contact.name}", contact_id=contact.id)

    return jsonify(contact.to_dict()), 201


@api_bp.route("/contacts/<int:contact_id>", methods=["GET"])
@login_required
def get_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    data = contact.to_dict()
    data["notes"] = [n.to_dict() for n in contact.notes]
    data["deals"] = [d.to_dict() for d in contact.deals]
    return jsonify(data)


@api_bp.route("/contacts/<int:contact_id>", methods=["PUT"])
@login_required
def update_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    data = request.get_json()

    if "name" in data:
        contact.name = data["name"]
    if "email" in data:
        contact.email = data["email"]
    if "phone" in data:
        contact.phone = data["phone"]
    if "company" in data:
        contact.company = data["company"]
    if "status" in data:
        contact.status = data["status"]
    if "lead_source" in data:
        contact.lead_source = data["lead_source"]

    db.session.commit()

    log_activity("contact_updated", f"Updated contact: {contact.name}", contact_id=contact.id)

    return jsonify(contact.to_dict())


@api_bp.route("/contacts/<int:contact_id>", methods=["DELETE"])
@login_required
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    name = contact.name
    db.session.delete(contact)
    db.session.commit()

    log_activity("contact_deleted", f"Deleted contact: {name}")

    return jsonify({"message": f"Contact '{name}' deleted"})


# --- NOTES ---

@api_bp.route("/contacts/<int:contact_id>/notes", methods=["GET"])
@login_required
def list_notes(contact_id):
    Contact.query.get_or_404(contact_id)
    notes = Note.query.filter_by(contact_id=contact_id).order_by(Note.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notes])


@api_bp.route("/contacts/<int:contact_id>/notes", methods=["POST"])
@login_required
def create_note(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    data = request.get_json()
    if not data or not data.get("content"):
        return jsonify({"error": "Content is required"}), 400

    note = Note(contact_id=contact_id, content=data["content"])
    db.session.add(note)
    db.session.commit()

    log_activity("note_added", f"Added note to {contact.name}", contact_id=contact_id)

    return jsonify(note.to_dict()), 201


# --- DEALS ---

@api_bp.route("/deals", methods=["GET"])
@login_required
def list_deals():
    stage = request.args.get("stage", "").strip()
    query = Deal.query

    if stage:
        query = query.filter(Deal.stage == stage)

    deals = query.order_by(Deal.created_at.desc()).all()
    return jsonify([d.to_dict() for d in deals])


@api_bp.route("/deals", methods=["POST"])
@login_required
def create_deal():
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    from datetime import date as date_type
    close_date = data.get("expected_close_date")
    if close_date and isinstance(close_date, str):
        close_date = date_type.fromisoformat(close_date)

    deal = Deal(
        title=data["title"],
        contact_id=data.get("contact_id"),
        value=data.get("value", 0),
        stage=data.get("stage", "New Lead"),
        expected_close_date=close_date,
    )
    db.session.add(deal)
    db.session.commit()

    contact_name = deal.contact.name if deal.contact else "No contact"
    log_activity("deal_created", f"Created deal: {deal.title} ({contact_name})", contact_id=deal.contact_id, deal_id=deal.id)

    return jsonify(deal.to_dict()), 201


@api_bp.route("/deals/<int:deal_id>", methods=["PUT"])
@login_required
def update_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    data = request.get_json()

    if "title" in data:
        deal.title = data["title"]
    if "contact_id" in data:
        deal.contact_id = data["contact_id"]
    if "value" in data:
        deal.value = data["value"]
    if "stage" in data:
        old_stage = deal.stage
        deal.stage = data["stage"]
        if old_stage != deal.stage:
            log_activity("deal_moved", f"Moved '{deal.title}' from {old_stage} to {deal.stage}", contact_id=deal.contact_id, deal_id=deal.id)
    if "expected_close_date" in data:
        from datetime import date as date_type
        close_date = data["expected_close_date"]
        if close_date and isinstance(close_date, str):
            close_date = date_type.fromisoformat(close_date)
        deal.expected_close_date = close_date
    if "won_lost_reason" in data:
        deal.won_lost_reason = data["won_lost_reason"]

    db.session.commit()

    return jsonify(deal.to_dict())


@api_bp.route("/deals/<int:deal_id>", methods=["DELETE"])
@login_required
def delete_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    title = deal.title
    db.session.delete(deal)
    db.session.commit()

    log_activity("deal_deleted", f"Deleted deal: {title}")

    return jsonify({"message": f"Deal '{title}' deleted"})


@api_bp.route("/deals/<int:deal_id>/stage", methods=["PATCH"])
@login_required
def move_deal_stage(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    data = request.get_json()
    new_stage = data.get("stage")

    valid_stages = ["New Lead", "Contacted", "Proposal", "Negotiation", "Won", "Lost"]
    if new_stage not in valid_stages:
        return jsonify({"error": f"Invalid stage. Must be one of: {valid_stages}"}), 400

    old_stage = deal.stage
    deal.stage = new_stage
    db.session.commit()

    log_activity("deal_moved", f"Moved '{deal.title}' from {old_stage} to {new_stage}", contact_id=deal.contact_id, deal_id=deal.id)

    return jsonify(deal.to_dict())


# --- DASHBOARD STATS ---

@api_bp.route("/dashboard-stats", methods=["GET"])
@login_required
def dashboard_stats():
    from sqlalchemy import func
    from datetime import datetime

    total_contacts = Contact.query.count()
    total_leads = Contact.query.filter(Contact.status == "Lead").count()

    pipeline_value = db.session.query(func.coalesce(func.sum(Deal.value), 0)).filter(
        Deal.stage.notin_(["Won", "Lost"])
    ).scalar()

    total_revenue = db.session.query(func.coalesce(func.sum(Deal.value), 0)).filter(
        Deal.stage == "Won"
    ).scalar()

    # Deals by stage
    stages = ["New Lead", "Contacted", "Proposal", "Negotiation", "Won", "Lost"]
    deals_by_stage = {}
    for stage in stages:
        deals_by_stage[stage] = Deal.query.filter(Deal.stage == stage).count()

    # Recent activity
    recent = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()

    return jsonify({
        "total_contacts": total_contacts,
        "total_leads": total_leads,
        "pipeline_value": float(pipeline_value),
        "total_revenue": float(total_revenue),
        "deals_by_stage": deals_by_stage,
        "recent_activity": [a.to_dict() for a in recent],
    })
```

- [ ] **Step 2: Test API with curl**

```bash
# Create a contact
curl -X POST http://localhost:5000/api/contacts \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}' \
  --cookie "session=..."
```

Note: For local testing, you'll need to login first to get a session cookie.

- [ ] **Step 3: Commit**

```bash
git add blueprints/api.py
git commit -m "feat: full CRUD API for contacts, deals, notes with dashboard stats"
```

---

### Task 9: Dashboard Page

**Files:**
- Create: `templates/admin/dashboard.html`
- Modify: `blueprints/admin.py` (add data loading)

- [ ] **Step 1: Update admin.py dashboard route to load data**

```python
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    from models import Contact, Deal, ActivityLog
    from sqlalchemy import func

    stats = {
        "total_contacts": Contact.query.count(),
        "total_leads": Contact.query.filter(Contact.status == "Lead").count(),
        "pipeline_value": float(db.session.query(func.coalesce(func.sum(Deal.value), 0)).filter(
            Deal.stage.notin_(["Won", "Lost"])
        ).scalar()),
        "total_revenue": float(db.session.query(func.coalesce(func.sum(Deal.value), 0)).filter(
            Deal.stage == "Won"
        ).scalar()),
    }
    recent_activity = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()

    return render_template("admin/dashboard.html", stats=stats, recent_activity=recent_activity)
```

Add `from app import db` at top of admin.py.

- [ ] **Step 2: Create dashboard.html**

- Extends `base_admin.html`
- 4 KPI stat cards in a grid row:
  1. Total Contacts (icon: users) — `stats.total_contacts`
  2. Active Leads (icon: target) — `stats.total_leads`
  3. Pipeline Value (icon: trending-up) — `${{ stats.pipeline_value | format_currency }}`
  4. Revenue (Won Deals) (icon: dollar) — `${{ stats.total_revenue | format_currency }}`
- Each card: `.stat-card` with icon (gold circle bg), value (28px bold), label (14px muted)
- Below: "Recent Activity" card with timeline list of `recent_activity` entries
- Each activity: icon by type + description + relative timestamp
- Empty state: "No activity yet. Start by adding your first contact!" with CTA button

- [ ] **Step 3: Test dashboard**

Login and visit `/admin/dashboard`. Should show 4 KPI cards (all zeros with no data) and empty activity.

- [ ] **Step 4: Commit**

```bash
git add templates/admin/dashboard.html blueprints/admin.py
git commit -m "feat: dashboard page with KPI cards and activity feed"
```

---

### Task 10: Contacts List Page

**Files:**
- Create: `templates/admin/contacts.html`
- Modify: `blueprints/admin.py` (add query params)

- [ ] **Step 1: Update contacts route in admin.py**

```python
@admin_bp.route("/contacts")
@login_required
def contacts():
    from models import Contact

    q = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()

    query = Contact.query
    if q:
        search = f"%{q}%"
        query = query.filter(
            db.or_(
                Contact.name.ilike(search),
                Contact.email.ilike(search),
                Contact.company.ilike(search),
            )
        )
    if status_filter:
        query = query.filter(Contact.status == status_filter)

    contacts = query.order_by(Contact.created_at.desc()).all()
    return render_template("admin/contacts.html", contacts=contacts, q=q, status_filter=status_filter)
```

- [ ] **Step 2: Create contacts.html**

- Extends `base_admin.html`
- Page header: "Contacts" + "Add Contact" button (`.btn-primary`)
- Search bar (full width, gold border on focus) + status filter dropdown
- Use Alpine.js `x-data` for the "Add Contact" modal toggle
- Contact table with columns: Name, Email, Company, Status (badge), Lead Source, Created
- Each row clickable → links to `/admin/contacts/<id>`
- Status badges: Lead (gold outline), Customer (green), VIP (gold filled), Inactive (gray)
- Empty state: "No contacts yet. Add your first contact to get started!"
- Add Contact modal (Alpine.js `x-show`): form with name, email, phone, company, status dropdown, lead source dropdown
- Modal form POSTs to `/api/contacts` via `fetch()`, then reloads page on success
- Mobile: table becomes card layout on small screens

- [ ] **Step 3: Test contacts page**

Login → navigate to Contacts → see empty state → click "Add Contact" → fill form → submit → see new contact in list → click on contact → navigate to detail.

- [ ] **Step 4: Commit**

```bash
git add templates/admin/contacts.html blueprints/admin.py
git commit -m "feat: contacts list page with search, filter, and add contact modal"
```

---

### Task 11: Contact Detail Page

**Files:**
- Create: `templates/admin/contact_detail.html`
- Modify: `blueprints/admin.py` (load full contact data)

- [ ] **Step 1: Update contact_detail route in admin.py**

```python
@admin_bp.route("/contacts/<int:contact_id>")
@login_required
def contact_detail(contact_id):
    from models import Contact, ActivityLog

    contact = Contact.query.get_or_404(contact_id)
    activities = ActivityLog.query.filter_by(contact_id=contact_id).order_by(ActivityLog.created_at.desc()).limit(20).all()

    return render_template("admin/contact_detail.html", contact=contact, activities=activities)
```

- [ ] **Step 2: Create contact_detail.html**

- Extends `base_admin.html`
- Back button ("← Contacts")
- Two-column layout (stacks on mobile):
  - **Left column (60%)**: Contact info card
    - Editable fields (Alpine.js inline edit): name, email, phone, company
    - Status dropdown (updates via API on change)
    - Lead source dropdown
    - Created/Updated timestamps
    - Edit/Delete buttons (delete with confirmation modal)
  - **Right column (40%)**:
    - **Notes card**: List of notes (newest first) + "Add Note" textarea + submit button
    - **Deals card**: List of associated deals with stage badges and values
    - **Activity Timeline**: Chronological list of all activity for this contact

- [ ] **Step 3: Test contact detail**

Create a contact → visit their detail page → edit a field → add a note → see activity timeline update.

- [ ] **Step 4: Commit**

```bash
git add templates/admin/contact_detail.html blueprints/admin.py
git commit -m "feat: contact detail page with inline edit, notes, deals, and activity timeline"
```

---

### Task 12: Deals Page (List View)

**Files:**
- Create: `templates/admin/deals.html`
- Modify: `blueprints/admin.py`

- [ ] **Step 1: Update deals route in admin.py**

```python
@admin_bp.route("/deals")
@login_required
def deals():
    from models import Deal

    stages = ["New Lead", "Contacted", "Proposal", "Negotiation", "Won", "Lost"]
    deals_by_stage = {}
    for stage in stages:
        deals_by_stage[stage] = Deal.query.filter_by(stage=stage).order_by(Deal.created_at.desc()).all()

    return render_template("admin/deals.html", stages=stages, deals_by_stage=deals_by_stage)
```

- [ ] **Step 2: Create deals.html**

- Extends `base_admin.html`
- Page header: "Sales Pipeline" + "New Deal" button
- Pipeline layout: 6 columns (one per stage), each with header showing stage name + deal count + total value
- Each deal displayed as a card (`.deal-card`):
  - Title (bold)
  - Contact name (muted, linked)
  - Value in gold ($X,XXX)
  - Expected close date
  - Stage move dropdown (select → PATCH API → update card position)
- "New Deal" modal (Alpine.js): title, contact (dropdown of existing contacts), value, stage, expected close date
- For Phase 1, this is a **columnar list view** (not drag-and-drop yet — that's Phase 4)
- Mobile: columns stack vertically, each stage is an accordion section
- Stage column colors: subtle gold tint on header, each card has left-border color by stage

- [ ] **Step 3: Test deals page**

Add a deal via modal → see it appear in the correct stage column → change stage via dropdown → see it move.

- [ ] **Step 4: Commit**

```bash
git add templates/admin/deals.html blueprints/admin.py
git commit -m "feat: deals pipeline page with columnar stage view and deal cards"
```

---

### Task 13: Seed Data

**Files:**
- Create: `seed.py`

- [ ] **Step 1: Create seed.py with realistic mortgage broker demo data**

```python
"""Seed the database with demo data for the workshop.

Run: python seed.py
"""
from app import create_app, db
from models import Contact, Deal, Note, ActivityLog
from datetime import datetime, timedelta
import random

app = create_app()


def seed():
    with app.app_context():
        # Clear existing data
        ActivityLog.query.delete()
        Note.query.delete()
        Deal.query.delete()
        Contact.query.delete()
        db.session.commit()

        # --- CONTACTS ---
        contacts_data = [
            {"name": "Maria Garcia", "email": "maria.garcia@email.com", "phone": "(555) 234-5678", "company": "Garcia Properties", "status": "Customer", "lead_source": "Referral"},
            {"name": "James Wilson", "email": "james.w@outlook.com", "phone": "(555) 345-6789", "company": "Wilson Financial", "status": "Lead", "lead_source": "Website Form"},
            {"name": "Sarah Chen", "email": "sarah.chen@gmail.com", "phone": "(555) 456-7890", "company": "Chen & Associates", "status": "VIP", "lead_source": "Workshop"},
            {"name": "Michael Brown", "email": "mbrown@brownrealty.com", "phone": "(555) 567-8901", "company": "Brown Realty Group", "status": "Customer", "lead_source": "Referral"},
            {"name": "Jessica Taylor", "email": "jtaylor@email.com", "phone": "(555) 678-9012", "company": "", "status": "Lead", "lead_source": "TikTok"},
            {"name": "Robert Martinez", "email": "rmartinez@gmail.com", "phone": "(555) 789-0123", "company": "Martinez Ventures", "status": "Lead", "lead_source": "Cold Outreach"},
            {"name": "Amanda Johnson", "email": "amanda.j@hotmail.com", "phone": "(555) 890-1234", "company": "Johnson Consulting", "status": "Customer", "lead_source": "Cold Outreach"},
            {"name": "David Kim", "email": "dkim@kimgroup.com", "phone": "(555) 901-2345", "company": "Kim Investment Group", "status": "VIP", "lead_source": "Referral"},
            {"name": "Lisa Patel", "email": "lpatel@email.com", "phone": "(555) 012-3456", "company": "Patel & Partners", "status": "Lead", "lead_source": "Website Form"},
            {"name": "Chris Anderson", "email": "chris.a@gmail.com", "phone": "(555) 123-4567", "company": "", "status": "Lead", "lead_source": "TikTok"},
            {"name": "Nicole Thompson", "email": "nthompson@thompsonlaw.com", "phone": "(555) 234-5679", "company": "Thompson Law Firm", "status": "Customer", "lead_source": "Workshop"},
            {"name": "Daniel Lee", "email": "dlee@email.com", "phone": "(555) 345-6780", "company": "Lee Capital", "status": "Inactive", "lead_source": "Cold Outreach"},
            {"name": "Rachel White", "email": "rwhite@gmail.com", "phone": "(555) 456-7891", "company": "", "status": "Lead", "lead_source": "Website Form"},
            {"name": "Kevin Harris", "email": "kharris@harrisgroup.com", "phone": "(555) 567-8902", "company": "Harris Group LLC", "status": "Lead", "lead_source": "Cold Outreach"},
            {"name": "Sophia Rivera", "email": "srivera@email.com", "phone": "(555) 678-9013", "company": "Rivera Homes", "status": "Customer", "lead_source": "Referral"},
        ]

        contacts = []
        for i, c in enumerate(contacts_data):
            contact = Contact(
                **c,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
            )
            db.session.add(contact)
            contacts.append(contact)

        db.session.flush()  # Get IDs

        # --- DEALS ---
        deals_data = [
            {"title": "Garcia Properties - Home Purchase", "contact": 0, "value": 450000, "stage": "Won"},
            {"title": "Wilson Financial - Refinance", "contact": 1, "value": 325000, "stage": "New Lead"},
            {"title": "Chen & Associates - Commercial Loan", "contact": 2, "value": 1200000, "stage": "Negotiation"},
            {"title": "Brown Realty - Investment Property", "contact": 3, "value": 675000, "stage": "Proposal"},
            {"title": "Taylor - First-Time Buyer", "contact": 4, "value": 285000, "stage": "Contacted"},
            {"title": "Martinez Ventures - Portfolio Loan", "contact": 5, "value": 2500000, "stage": "New Lead"},
            {"title": "Kim Investment - Multi-Unit Purchase", "contact": 7, "value": 3400000, "stage": "Won"},
            {"title": "Patel & Partners - Office Mortgage", "contact": 8, "value": 890000, "stage": "Lost"},
        ]

        deals = []
        for d in deals_data:
            deal = Deal(
                title=d["title"],
                contact_id=contacts[d["contact"]].id,
                value=d["value"],
                stage=d["stage"],
                expected_close_date=datetime.utcnow().date() + timedelta(days=random.randint(7, 90)),
                won_lost_reason="Client found better rate elsewhere" if d["stage"] == "Lost" else None,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            )
            db.session.add(deal)
            deals.append(deal)

        db.session.flush()

        # --- NOTES ---
        notes_data = [
            (0, "Initial consultation went well. Maria is looking to purchase a 3-bedroom home in the suburbs. Budget around $450K."),
            (0, "Pre-approval completed. Maria qualified for $475K. Sending property listings tomorrow."),
            (0, "Closed! Maria purchased the property at 123 Oak Street. Great referral potential."),
            (1, "James called about refinancing his current home. Currently at 6.5% - could save him $400/month."),
            (2, "Sarah needs a commercial loan for her new office space. Looking at $1.2M. She's been a great client — treating this as VIP."),
            (2, "Sent term sheet. Sarah is reviewing with her business partner. Follow up Friday."),
            (3, "Michael referred by Maria Garcia. Looking for an investment property — rental income focused."),
            (3, "Showed Michael 3 properties. He's interested in the duplex on Elm Street."),
            (4, "Jessica found us on TikTok. First-time buyer, needs education on the process. Scheduled intro call."),
            (5, "Cold outreach via LinkedIn. Robert has a portfolio of 5 properties, looking to add more."),
            (7, "David is a high-net-worth client. Looking at multi-unit investment. Needs specialized lending."),
            (7, "Met with David's financial advisor. They want to structure this as an LLC purchase."),
            (8, "Lisa needs office space mortgage for her accounting firm. Straightforward deal."),
            (10, "Nicole referred by Sarah Chen. Looking at buying her first commercial property for her law firm."),
            (11, "Daniel went cold after initial call. Sent 2 follow-ups, no response. Moving to inactive."),
            (14, "Sophia closed on her new home! She's already referring friends."),
        ]

        for contact_idx, content in notes_data:
            note = Note(
                contact_id=contacts[contact_idx].id,
                content=content,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 45)),
            )
            db.session.add(note)

        # --- ACTIVITY LOG ---
        activities = [
            ("contact_created", "Created contact: Maria Garcia", 0, None),
            ("deal_created", "Created deal: Garcia Properties - Home Purchase", 0, 0),
            ("deal_moved", "Moved 'Garcia Properties' from Proposal to Won", 0, 0),
            ("contact_created", "Created contact: James Wilson", 1, None),
            ("deal_created", "Created deal: Wilson Financial - Refinance", 1, 1),
            ("note_added", "Added note to Sarah Chen", 2, None),
            ("deal_created", "Created deal: Chen & Associates - Commercial Loan", 2, 2),
            ("deal_moved", "Moved 'Chen & Associates' from Proposal to Negotiation", 2, 2),
            ("contact_created", "Created contact: Jessica Taylor", 4, None),
            ("contact_created", "Created contact: Robert Martinez", 5, None),
            ("deal_created", "Created deal: Kim Investment - Multi-Unit Purchase", 7, 6),
            ("deal_moved", "Moved 'Kim Investment' from Negotiation to Won", 7, 6),
            ("contact_updated", "Updated Daniel Lee status to Inactive", 11, None),
            ("deal_moved", "Moved 'Patel & Partners' from Proposal to Lost", 8, 7),
            ("note_added", "Added note to Sophia Rivera", 14, None),
        ]

        for action_type, desc, contact_idx, deal_idx in activities:
            activity = ActivityLog(
                action_type=action_type,
                description=desc,
                contact_id=contacts[contact_idx].id,
                deal_id=deals[deal_idx].id if deal_idx is not None else None,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23)),
            )
            db.session.add(activity)

        db.session.commit()
        print(f"✅ Seeded {len(contacts)} contacts, {len(deals)} deals, {len(notes_data)} notes, {len(activities)} activities")


if __name__ == "__main__":
    seed()
```

- [ ] **Step 2: Run seed script**

```bash
python seed.py
```

Expected: `✅ Seeded 15 contacts, 8 deals, 16 notes, 15 activities`

- [ ] **Step 3: Verify data on dashboard**

Login → Dashboard should now show:
- Total Contacts: 15
- Active Leads: 6
- Pipeline Value: ~$5,000,000 (deals not Won/Lost)
- Revenue: ~$3,850,000 (Won deals)
- Recent activity populated

- [ ] **Step 4: Commit**

```bash
git add seed.py
git commit -m "feat: seed script with 15 demo contacts, 8 deals, notes, and activity log"
```

---

### Task 14: Integration Testing + Polish

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: Create test fixtures in conftest.py**

```python
import pytest
from app import create_app, db as _db
import os


@pytest.fixture
def app():
    os.environ["DATABASE_URL"] = "sqlite://"  # In-memory database
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["ADMIN_USER"] = "testadmin"
    os.environ["ADMIN_PASS"] = "testpass"

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
    client.post("/admin/login", data={"username": "testadmin", "password": "testpass"})
    return client
```

- [ ] **Step 2: Create API tests in test_api.py**

```python
def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json["status"] == "ok"


def test_login_required(client):
    r = client.get("/api/contacts")
    assert r.status_code == 302  # Redirect to login


def test_create_contact(auth_client):
    r = auth_client.post("/api/contacts", json={"name": "Test User", "email": "test@example.com"})
    assert r.status_code == 201
    assert r.json["name"] == "Test User"


def test_list_contacts(auth_client):
    r = auth_client.get("/api/contacts")
    assert r.status_code == 200
    assert isinstance(r.json, list)


def test_create_deal(auth_client):
    r = auth_client.post("/api/deals", json={"title": "Test Deal", "value": 5000})
    assert r.status_code == 201
    assert r.json["title"] == "Test Deal"


def test_dashboard_stats(auth_client):
    r = auth_client.get("/api/dashboard-stats")
    assert r.status_code == 200
    assert "total_contacts" in r.json
    assert "pipeline_value" in r.json
```

- [ ] **Step 3: Run tests**

```bash
pip install pytest
pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "test: API tests for contacts, deals, auth, and dashboard stats"
```

---

### Task 15: Final Polish + README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README with deployment instructions**

Include:
- Project description and screenshot placeholder
- Quick start (local dev): clone, create .env, pip install, python seed.py, python app.py
- Railway deployment: step-by-step with screenshots
- Environment variables table
- Default credentials
- Project structure overview
- Phase roadmap (what's built, what's next)
- Restaurant analogy overview

- [ ] **Step 2: Final smoke test**

```bash
# Start fresh
rm -f crm.db
python app.py &
python seed.py
# Visit http://localhost:5000/admin/login
# Login with admin/admin
# Verify: dashboard shows KPIs, contacts list has 15 entries, deals pipeline shows 8 deals
# Click a contact → see detail with notes
# Add a new contact via modal
# Add a new deal
# Kill server
kill %1
```

- [ ] **Step 3: Commit everything**

```bash
git add README.md
git commit -m "docs: README with setup, deployment, and workshop guide"
```

---

## PHASE 2: THE MENU & FRONT DOOR

**Goal:** Public-facing lead magnet page + sales page + form submissions creating CRM contacts.
**Restaurant analogy:** "Your menu and front door — how customers find you and what you offer."

### Task 16: Lead Magnet Landing Page
- Create `templates/public/landing.html` extending `base.html`
- Hero section: headline, subheadline, email capture form
- Benefits list (3-4 items with icons)
- Social proof section (testimonial placeholders)
- Form POSTs to `/lp/submit` → creates Contact (status: Lead, source: Website Form) → redirects to thank-you
- Fully responsive, premium dark gold design

### Task 17: Sales Page
- Create `templates/public/sales.html`
- Hero with value proposition
- Features/benefits section
- Pricing section with Stripe checkout link button (from env var)
- FAQ accordion (Alpine.js)
- CTA button at bottom

### Task 18: Thank You Page
- Create `templates/public/thank_you.html`
- Confirmation message
- Lead magnet download link (from env var)
- Redirect CTA to sales page

### Task 19: Form Submission Route
- Update `blueprints/public.py` with POST `/lp/submit`
- Create contact from form data
- Log activity
- Flash success message
- Redirect to thank-you

### Task 20: Toast Notifications
- Add Alpine.js toast component to `base.html`
- Success/error/warning variants
- Auto-dismiss after 4 seconds
- SlideIn animation from right

---

## PHASE 3: THE WAITER (AI Chatbot)

**Goal:** AI sidebar on all admin pages, CRUD via natural language.
**Restaurant analogy:** "Your waiter — takes orders and manages the floor for you."

### Task 21: Chat Panel Frontend (Alpine.js)
### Task 22: Chat API Endpoint (/api/chat)
### Task 23: Intent Classification (Gemini 2.5 Flash)
### Task 24: CRUD Action Execution
### Task 25: Chat History Persistence

---

## PHASE 4: THE ORDER BOARD (Kanban)

**Goal:** Drag-and-drop pipeline + activity timeline.
**Restaurant analogy:** "Your order board — see every ticket at a glance."

### Task 26: SortableJS Kanban Integration
### Task 27: Drag-and-Drop Stage API
### Task 28: Activity Timeline Component

---

## PHASE 5: THE CASH REGISTER (Analytics)

**Goal:** Charts + metrics + PWA manifest.
**Restaurant analogy:** "Your cash register — know exactly how the business is doing."

### Task 29: Chart.js Dashboard Charts
### Task 30: Conversion Metrics
### Task 31: PWA Manifest + Icons

---

## PHASE 6: THE MANAGER (Customization)

**Goal:** Settings page + branding + Sonnet 4 + CSV import/export.
**Restaurant analogy:** "Your manager — handles the hard stuff so you can focus."

### Task 32: Settings Page + Config Table
### Task 33: Branding Injection
### Task 34: Sonnet 4 Complex Queries
### Task 35: CSV Import/Export
