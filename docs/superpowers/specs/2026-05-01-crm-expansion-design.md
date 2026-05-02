# CRM Expansion Design — GoHighLevel Alternative for Coaches/Consultants

**Date:** 2026-05-01
**Status:** Approved

## Overview

Expand the existing CRM Demo into a universal template for coaches, consultants, and service providers selling digital products. Each feature is a togglable Flask blueprint. All features work out-of-the-box with mock/demo mode (no external API keys required), and activate real integrations when API keys are provided.

## Target User

Coaches, consultants, and service providers who primarily sell digital products (PDFs, courses, workshops, templates). They need a simple CRM to capture leads, manage clients, sell products, and track internal tasks.

## Architecture

### Core Principle
Each feature is a self-contained Flask blueprint with its own models, routes, templates, and seed data. Feature toggles in `.env` control which modules are active. Sidebar dynamically reflects enabled features.

### Feature Toggle System
```env
FEATURE_PRODUCTS=true
FEATURE_CLIENTS=true
FEATURE_TASKS=true
FEATURE_EMAIL=true
FEATURE_ANALYTICS=true
```

Disabled features: routes not registered, sidebar links hidden, seed data skipped.

## Bug Fixes

### Chatbot Alpine.js Scope Bug
- **Problem:** Chat panel uses `x-show="chatOpen"` but `chatOpen` is in parent `x-data` scope. Nested `x-data` directives on Contacts, Deals, Contact Detail pages create scope isolation that prevents chat toggle from working.
- **Fix:** Restructure Alpine.js scopes in `base_admin.html` so chat state is accessible across all admin pages.

## Feature Modules

### 1. Products & eCommerce (`blueprints/products.py`)

**Models:**
- `Product`: name, description, price (Decimal), product_type (free/paid), delivery_url, stripe_price_id (nullable), image_url, active (bool), created_at, updated_at
- `Purchase`: contact_id (FK), product_id (FK), stripe_session_id (nullable), amount, status (completed/pending/refunded), purchased_at

**Routes:**
- `GET /admin/products` — Product list with active/inactive filter
- `GET /admin/products/<id>` — Product detail
- `POST /api/products` — Create product
- `PUT /api/products/<id>` — Update product
- `DELETE /api/products/<id>` — Delete product
- `GET /store` — Public store page (optional, for buyers)
- `POST /api/checkout/<product_id>` — Create Stripe Checkout Session (or mock)
- `GET /checkout/success` — Handle successful purchase
- `GET /checkout/cancel` — Handle cancelled checkout

**Mock Mode (no STRIPE_SECRET_KEY):**
- Checkout button shows "Connect Stripe to enable payments"
- Demo purchases can be created manually via admin
- All UI renders with seed data

**Seed Data:** 3-4 products (e.g., "Business Blueprint PDF" $47, "Video Workshop" $197, "Free Checklist" $0, "VIP Coaching Toolkit" $497)

### 2. Clients (`blueprints/clients.py`)

**Approach:** Extends the existing Contact model — adds "Client" to the status enum. No new model for the client itself.

**Models:**
- `ClientNote`: id, contact_id (FK), title, content (Text, markdown), created_at, updated_at

**Status Progression:**
- Lead → Customer (auto when deal Won) → Client (manual promotion) → Archived

**Routes:**
- `GET /admin/clients` — Filtered view of contacts with status Client/Customer, active/archived toggle
- `GET /admin/clients/<id>` — Client detail with markdown notes, purchase history, deals
- `POST /api/clients/<id>/notes` — Add markdown note
- `PUT /api/clients/<id>/notes/<note_id>` — Edit note
- `DELETE /api/clients/<id>/notes/<note_id>` — Delete note
- `PATCH /api/clients/<id>/archive` — Toggle archived status

**Auto-promotion:** When a deal is moved to "Won" stage, the associated contact's status auto-updates to "Customer."

**Seed Data:** 4-5 clients with markdown notes (meeting summaries, project briefs, onboarding checklists)

### 3. Tasks (`blueprints/tasks.py`)

**Models:**
- `Task`: id, title, description (Text), status (todo/in_progress/done), priority (low/medium/high), due_date, created_at, updated_at

**Routes:**
- `GET /admin/tasks` — Kanban board (3 columns: To Do, In Progress, Done)
- `POST /api/tasks` — Create task
- `PUT /api/tasks/<id>` — Update task
- `DELETE /api/tasks/<id>` — Delete task
- `PATCH /api/tasks/<id>/status` — Move task (drag-drop)

**UI:** Reuse the deals pipeline Kanban pattern. Cards show title, priority badge, due date.

**Seed Data:** 6-8 tasks across statuses and priorities

### 4. Email Triggers (`blueprints/email.py`)

**Models:**
- `EmailTemplate`: id, name, subject, body_html (Text), trigger_type (lead_magnet/purchase_confirmation), active (bool), created_at, updated_at
- `EmailLog`: id, template_id (FK), contact_id (FK), sent_at, status (sent/failed/mock)

**Routes:**
- `GET /admin/email-templates` — List templates
- `PUT /api/email-templates/<id>` — Edit template
- `GET /admin/email-log` — View sent email log

**Triggers:**
- Landing page opt-in → sends lead magnet email with `lead_magnet_url`
- Purchase completed → sends purchase confirmation with `product.delivery_url`

**Mock Mode (no RESEND_API_KEY):**
- Emails logged to `EmailLog` with status "mock" instead of actually sending
- Admin can see what would have been sent
- UI shows "Connect Resend to enable live emails"

**Seed Data:** 2 default templates (lead magnet delivery, purchase confirmation), 5-6 mock email log entries

### 5. Analytics (added to existing dashboard)

**Models:**
- `PageView`: id, page (string), visitor_id (string, anonymous cookie), referrer (nullable), contact_id (FK, nullable), created_at

**Implementation:**
- `@app.before_request` middleware logs views on public pages (landing, sales, store)
- Dashboard widget shows simple funnel: Views → Signups → Purchases with conversion percentages
- Last 30 days by default

**Seed Data:** 200+ randomized page views over last 30 days to show realistic funnel data

## Chatbot Enhancements

Extend chatbot actions to support new modules:
- `create_task`, `list_tasks` — manage tasks via chat
- `list_products` — query product catalog
- `check_analytics` — get funnel stats

## File Structure

```
blueprints/
  public.py          # existing
  admin.py           # existing
  api.py             # existing
  products.py        # NEW
  clients.py         # NEW
  tasks.py           # NEW
  email.py           # NEW
templates/admin/
  dashboard.html     # existing (add analytics widget)
  products.html      # NEW
  product_detail.html # NEW
  clients.html       # NEW
  client_detail.html # NEW
  tasks.html         # NEW
  email_templates.html # NEW
  email_log.html     # NEW
models.py            # extended with new models
seed.py              # extended with new seed data
.env.example         # updated with new feature flags and API keys
```

## Environment Variables (New)

```env
# Feature Toggles
FEATURE_PRODUCTS=true
FEATURE_CLIENTS=true
FEATURE_TASKS=true
FEATURE_EMAIL=true
FEATURE_ANALYTICS=true

# Stripe (optional — mock mode if unset)
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=

# Resend (optional — mock mode if unset)
RESEND_API_KEY=
RESEND_FROM_EMAIL=hello@yourdomain.com
```

## Design Constraints

- All features work without external API keys (mock/demo mode)
- Seed data populates all modules for immediate demo experience
- Dark gold design system maintained across all new pages
- Mobile responsive
- No client-facing portal — all admin/internal
- Simple, not bloated — YAGNI strictly enforced
