# Dr. AI CRM — Command Center

A full-featured CRM template built for coaches, consultants, and service providers selling digital products. Built with Flask, Alpine.js, and Tailwind CSS. Designed as a plug-and-play alternative to GoHighLevel.

**Every feature works out-of-the-box with demo data — no external accounts required.**

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/jjacuna/ai-crm.git
cd ai-crm

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env with your values (defaults work for demo)

# 5. Seed the database with demo data
python3 seed.py

# 6. Run the app
python3 app.py
# Open http://localhost:8000
```

**Default login:** `admin` / `admin` (change in `.env` before deploying)

---

## Features

### Core CRM
| Feature | Description |
|---------|------------|
| **Dashboard** | KPI cards (contacts, leads, pipeline, revenue), conversion funnel, activity timeline |
| **Contacts** | Full CRUD, search, status filtering (Lead/Customer/VIP/Client/Inactive), lead source tracking |
| **Deals Pipeline** | Kanban board with 6 stages, drag-and-drop, deal values, expected close dates |
| **AI Chatbot** | Natural language CRM management — create contacts, move deals, add notes via chat. Powered by OpenRouter (Gemini 2.5 Flash / Claude Sonnet 4) |

### Expansion Modules (Togglable)
| Module | Description | Toggle |
|--------|------------|--------|
| **Products & eCommerce** | Digital product catalog, Stripe checkout (mock or live), purchase tracking | `FEATURE_PRODUCTS=true` |
| **Clients** | Graduated contacts (Lead → Customer → Client), markdown notes, active/archived management | `FEATURE_CLIENTS=true` |
| **Tasks** | Internal kanban board (To Do / In Progress / Done), priority levels, due dates, drag-and-drop | `FEATURE_TASKS=true` |
| **Email Triggers** | Automated emails on lead capture and purchase, editable HTML templates, email log | `FEATURE_EMAIL=true` |
| **Analytics** | Page view tracking, conversion funnel (Views → Signups → Purchases) on dashboard | `FEATURE_ANALYTICS=true` |

### Public Pages
| Page | URL | Purpose |
|------|-----|---------|
| Landing Page | `/lp` | Lead capture form — creates contact as "Lead" |
| Thank You | `/lp/thank-you` | Post-signup with lead magnet download link |
| Sales Page | `/sales` | Product/service showcase with Stripe CTA |
| Store | `/store` | Digital product storefront with checkout |

---

## Feature Toggles

Disable any module by setting its flag to `false` in `.env`:

```env
FEATURE_PRODUCTS=true    # Digital product catalog + Stripe checkout
FEATURE_CLIENTS=true     # Client management with markdown notes
FEATURE_TASKS=true       # Internal task kanban board
FEATURE_EMAIL=true       # Email automation with Resend
FEATURE_ANALYTICS=true   # Page view tracking + funnel
```

When disabled, the module's routes won't register and its sidebar link won't appear.

---

## Mock Mode vs Live Mode

All integrations work in **mock/demo mode** by default (no API keys needed):

| Integration | Mock Mode (no key) | Live Mode (key set) |
|-------------|-------------------|---------------------|
| **Stripe** | Checkout creates mock purchase records | Real Stripe Checkout Sessions |
| **Resend** | Emails logged with status "mock" | Emails actually sent |
| **AI Chatbot** | Returns error message | Full AI-powered CRM assistant |

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Required
DATABASE_URL=sqlite:///crm.db     # PostgreSQL in production
ADMIN_USER=admin                   # Change before deploying!
ADMIN_PASS=changeme                # Change before deploying!
SECRET_KEY=change-this             # python3 -c "import secrets; print(secrets.token_hex(32))"

# Business Branding
BUSINESS_NAME=My Business CRM

# Feature Toggles (all default to true)
FEATURE_PRODUCTS=true
FEATURE_CLIENTS=true
FEATURE_TASKS=true
FEATURE_EMAIL=true
FEATURE_ANALYTICS=true

# Optional Integrations
OPENROUTER_API_KEY=               # AI chatbot (https://openrouter.ai)
STRIPE_SECRET_KEY=                # Stripe payments (https://dashboard.stripe.com/apikeys)
STRIPE_PUBLISHABLE_KEY=           # Stripe frontend key
RESEND_API_KEY=                   # Email sending (https://resend.com)
RESEND_FROM_EMAIL=hello@you.com   # Sender email address
STRIPE_CHECKOUT_URL=              # Legacy checkout link for sales page
LEAD_MAGNET_URL=                  # Free download URL for landing page
KIE_AI_API_KEY=                   # Image generation (https://kie.ai)
```

---

## Project Structure

```
ai-crm/
├── app.py                    # Flask app factory, feature toggles, analytics middleware
├── models.py                 # SQLAlchemy models (Contact, Deal, Note, Product, Task, etc.)
├── extensions.py             # Flask-SQLAlchemy instance
├── auth.py                   # Login decorator + credential check
├── chatbot.py                # AI chatbot engine (OpenRouter API)
├── seed.py                   # Demo data seeder (run: python3 seed.py)
├── requirements.txt          # Python dependencies
├── Procfile                  # Gunicorn config for production
├── railway.toml              # Railway deployment config
├── .env.example              # Environment variable template
│
├── blueprints/
│   ├── public.py             # Landing page, sales page, lead capture
│   ├── admin.py              # Dashboard, contacts, deals (core admin routes)
│   ├── api.py                # JSON API for contacts, deals, notes, chat
│   ├── products.py           # Products CRUD, store, Stripe checkout
│   ├── clients.py            # Client management, markdown notes, archive
│   ├── tasks.py              # Task kanban board, CRUD, status moves
│   └── email.py              # Email templates, log, Resend trigger
│
├── templates/
│   ├── base.html             # Root template (Tailwind, Alpine.js, toasts)
│   ├── base_admin.html       # Admin layout (sidebar, chat panel)
│   ├── admin/
│   │   ├── login.html
│   │   ├── dashboard.html    # KPI stats + conversion funnel
│   │   ├── contacts.html     # Contact list + search/filter
│   │   ├── contact_detail.html
│   │   ├── deals.html        # Kanban pipeline
│   │   ├── clients.html      # Client list (active/archived)
│   │   ├── client_detail.html
│   │   ├── products.html     # Product card grid
│   │   ├── product_detail.html
│   │   ├── tasks.html        # Task kanban board
│   │   ├── email_templates.html
│   │   └── email_log.html
│   └── public/
│       ├── landing.html      # Lead capture page
│       ├── thank_you.html
│       ├── sales.html        # Pricing/sales page
│       ├── store.html        # Product storefront
│       ├── checkout_success.html
│       └── checkout_cancel.html
│
├── static/
│   ├── css/custom.css        # Dark gold design system (3250+ lines)
│   └── js/chat.js            # AI chatbot Alpine.js component
│
├── tests/
│   ├── conftest.py           # pytest fixtures (app, client, auth_client)
│   ├── test_api.py           # Core API tests (contacts, deals, notes)
│   ├── test_auth.py          # Login/logout/redirect tests
│   ├── test_products.py      # Products CRUD, checkout, store tests
│   ├── test_clients.py       # Client notes, archive tests
│   ├── test_tasks.py         # Task CRUD, status moves tests
│   ├── test_email.py         # Email template, trigger tests
│   ├── test_analytics.py     # Page view tracking, funnel tests
│   └── test_e2e.py           # Playwright browser tests (24 tests)
│
└── docs/
    └── superpowers/specs/    # Design specifications
```

---

## Database Models

| Model | Table | Purpose |
|-------|-------|---------|
| `Contact` | contacts | People in the CRM (leads, customers, clients) |
| `Deal` | deals | Sales pipeline opportunities |
| `Note` | notes | Quick notes on contacts |
| `ActivityLog` | activity_log | Audit trail of all CRM actions |
| `Product` | products | Digital products for sale |
| `Purchase` | purchases | Purchase records (Stripe or mock) |
| `ClientNote` | client_notes | Detailed markdown notes for clients |
| `Task` | tasks | Internal to-do items |
| `EmailTemplate` | email_templates | HTML email templates with triggers |
| `EmailLog` | email_log | Sent/mock email history |
| `PageView` | page_views | Analytics page view tracking |

---

## Testing

### Run All Tests (94 total)
```bash
python3 -m pytest tests/ -v
```

### Unit Tests Only (70 tests, ~2 seconds)
```bash
python3 -m pytest tests/ --ignore=tests/test_e2e.py -v
```

### Playwright Browser Tests (24 tests, ~23 seconds)
```bash
# Install Playwright browsers first (one-time)
pip install pytest-playwright
playwright install chromium

# Run headless
python3 -m pytest tests/test_e2e.py -v

# Run with visible browser (great for demos)
python3 -m pytest tests/test_e2e.py -v --headed
```

### Test Coverage by Module

| Test File | Tests | What's Covered |
|-----------|-------|----------------|
| `test_api.py` | 20 | Contacts CRUD, deals CRUD, notes, dashboard stats, pages |
| `test_auth.py` | 6 | Login, logout, auth redirect, invalid credentials |
| `test_products.py` | 15 | Product CRUD, mock checkout, purchase creation, store |
| `test_clients.py` | 9 | Client pages, notes CRUD, archive/unarchive |
| `test_tasks.py` | 9 | Task CRUD, status moves, invalid status |
| `test_email.py` | 6 | Template update, mock email trigger, missing template |
| `test_analytics.py` | 5 | Dashboard funnel, page view tracking, all pages load |
| `test_e2e.py` | 24 | Full browser tests: all pages, chatbot on every screen, sidebar, forms |

---

## API Endpoints

### Contacts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/contacts` | List contacts (query: `?q=search&status=Lead`) |
| POST | `/api/contacts` | Create contact |
| GET | `/api/contacts/<id>` | Get contact with notes and deals |
| PUT | `/api/contacts/<id>` | Update contact |
| DELETE | `/api/contacts/<id>` | Delete contact |
| GET | `/api/contacts/<id>/notes` | List notes for contact |
| POST | `/api/contacts/<id>/notes` | Add note to contact |

### Deals
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/deals` | List deals (query: `?stage=Won`) |
| POST | `/api/deals` | Create deal |
| PUT | `/api/deals/<id>` | Update deal |
| DELETE | `/api/deals/<id>` | Delete deal |
| PATCH | `/api/deals/<id>/stage` | Move deal to new stage |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/products` | Create product |
| PUT | `/api/products/<id>` | Update product |
| DELETE | `/api/products/<id>` | Delete product |
| POST | `/api/checkout/<id>` | Create Stripe checkout (or mock) |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tasks` | Create task |
| PUT | `/api/tasks/<id>` | Update task |
| DELETE | `/api/tasks/<id>` | Delete task |
| PATCH | `/api/tasks/<id>/status` | Move task status |

### Clients
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/clients/<id>/notes` | Add client note |
| PUT | `/api/clients/<id>/notes/<nid>` | Edit client note |
| DELETE | `/api/clients/<id>/notes/<nid>` | Delete client note |
| PATCH | `/api/clients/<id>/archive` | Toggle archive status |

### Email
| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | `/api/email-templates/<id>` | Update email template |

### Other
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/dashboard-stats` | Dashboard statistics JSON |
| POST | `/api/chat` | AI chatbot endpoint |

---

## Deployment (Railway)

### One-Click Deploy

1. Push to GitHub
2. Connect repo to [Railway](https://railway.app)
3. Add a PostgreSQL database
4. Set environment variables in Railway dashboard
5. Deploy

Railway auto-detects the `Procfile` and `requirements.txt`.

### Required Railway Environment Variables

```
DATABASE_URL          → Provided automatically by Railway PostgreSQL
SECRET_KEY            → Generate a random string
ADMIN_USER            → Your admin username
ADMIN_PASS            → Your admin password
BUSINESS_NAME         → Your brand name
```

### Optional Railway Environment Variables

```
OPENROUTER_API_KEY    → For AI chatbot
STRIPE_SECRET_KEY     → For live payments
STRIPE_PUBLISHABLE_KEY
RESEND_API_KEY        → For live email sending
RESEND_FROM_EMAIL
LEAD_MAGNET_URL       → Your free download link
STRIPE_CHECKOUT_URL   → Your Stripe checkout link
```

### Seed Production Database

```bash
railway run python3 seed.py
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Flask 3.1+, SQLAlchemy 2.0+, Gunicorn |
| **Database** | SQLite (dev), PostgreSQL (production) |
| **Frontend** | Tailwind CSS 3.x (CDN), Alpine.js 3.x (CDN) |
| **AI** | OpenRouter API (Gemini 2.5 Flash + Claude Sonnet 4) |
| **Payments** | Stripe Checkout Sessions |
| **Email** | Resend API |
| **Testing** | pytest + Playwright |
| **Hosting** | Railway (Nixpacks build) |

---

## Customization Guide

### Change Branding
- Set `BUSINESS_NAME` in `.env`
- Edit sidebar brand in `templates/base_admin.html` (lines 19-25)
- Modify CSS variables in `static/css/custom.css` (`:root` section)

### Add a New Contact Status
1. Update status options in `templates/admin/contacts.html` (filter buttons + select)
2. Add badge CSS class in `static/css/custom.css`
3. Update chatbot system prompt in `chatbot.py`

### Add a New Feature Module
1. Create `blueprints/yourfeature.py` with a Blueprint
2. Create template in `templates/admin/`
3. Add models to `models.py`
4. Register blueprint in `app.py` (guarded by `FEATURE_YOURFEATURE`)
5. Add sidebar link in `templates/base_admin.html`
6. Add seed data to `seed.py`
7. Write tests in `tests/test_yourfeature.py`

### Connect Stripe (Live Payments)
1. Get API keys from [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Set `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY` in `.env`
3. Optionally set `stripe_price_id` on products for pre-configured prices
4. Checkout will automatically switch from mock to live mode

### Connect Resend (Live Email)
1. Sign up at [Resend](https://resend.com)
2. Verify your sending domain
3. Set `RESEND_API_KEY` and `RESEND_FROM_EMAIL` in `.env`
4. Edit email templates at `/admin/email-templates`
5. Emails will automatically switch from mock to live

---

## Seed Data

Run `python3 seed.py` to populate the database with realistic demo data:

| Data | Count |
|------|-------|
| Contacts | 17 (leads, customers, clients, VIP, archived) |
| Deals | 8 (across all pipeline stages) |
| Notes | 22 |
| Activity Log | 32 entries |
| Products | 4 (1 free, 3 paid: $47-$497) |
| Purchases | 10 |
| Client Notes | 6 (with markdown formatting) |
| Tasks | 8 (across all kanban columns) |
| Email Templates | 2 (lead magnet + purchase confirmation) |
| Email Log | 6 mock entries |
| Page Views | 250 (last 30 days, for analytics funnel) |

---

## License

MIT
