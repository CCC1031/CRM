# CRM Command Center — Design Spec

## Overview
A lightweight, premium CRM web app for workshop students replacing Go High Level. Built with Flask + PostgreSQL, deployed to Railway, with an AI chatbot sidebar as the primary interface. Students learn to build and customize it through 6 phases using restaurant analogies.

**Target users**: Non-technical business owners (mortgage brokers, service businesses)
**Teaching time**: ~2 hours for core deployment
**Priority split**: 60% UI/UX polish, 40% functionality

---

## Architecture

### Tech Stack
| Layer | Choice | Why |
|-------|--------|-----|
| Backend | Flask 3.x | Battle-tested, zero build step, teachable in 2 hours |
| ORM | SQLAlchemy 2.x | Gold standard Python ORM, PostgreSQL native |
| Database | PostgreSQL | Enterprise-grade, Railway-hosted |
| Templates | Jinja2 | Server-rendered, no JavaScript framework needed |
| CSS | Tailwind CSS (CDN) | No build step, utility-first, responsive |
| Interactivity | Alpine.js (CDN) | Lightweight (~15KB), handles chat sidebar + modals |
| Drag-and-drop | SortableJS (CDN) | 12KB, touch-friendly, zero deps |
| Charts | Chart.js (CDN) | Simple, responsive charts |
| AI | OpenRouter API | Routes to Gemini 2.5 Flash + Sonnet 4 |
| Server | gunicorn | Production WSGI server |
| Deployment | Railway | One-click PostgreSQL, env vars, custom domains |

### No Build Step Required
Everything loads via CDN or pip. Students need only Python installed.

---

## Brand System (CAM 2.0)

### Colors
```css
:root {
  /* Backgrounds */
  --bg-primary: #0B0B0D;
  --bg-card: #17181C;
  --bg-card-hover: #1E2025;
  --bg-tertiary: #111215;

  /* Gold System */
  --gold: #C7A35A;
  --gold-hover: #B88933;
  --gold-champagne: #E4D3A2;
  --gold-bronze: #87652C;
  --gold-tint: rgba(199, 163, 90, 0.10);

  /* Text */
  --text-primary: #F5F0E8;
  --text-muted: #C8C0B4;
  --text-subtle: #9E978C;

  /* Borders */
  --border: #31343C;

  /* Status */
  --success: #22c55e;
  --warning: #f59e0b;
  --danger: #ef4444;
}
```

### Typography
- **Font**: Inter (Google Fonts CDN)
- **Headings**: 600-700 weight
- **Body**: 500 weight, 14px base
- **Monospace**: SF Mono, Consolas

### Components
- **Cards**: 12px radius, 20px padding, `#17181C` bg, `#31343C` border
- **Buttons**: 8px radius, 8px 16px padding, 14px text
- **Inputs**: 8px radius, 8px 12px padding, `#0B0B0D` bg
- **Sidebar**: 200px fixed, collapsible to 60px, `#17181C` bg
- **Toasts**: Fixed bottom-right, slideIn animation, colored left border

---

## Database Schema

### contacts
| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL PK | |
| name | VARCHAR(200) | NOT NULL |
| email | VARCHAR(200) | |
| phone | VARCHAR(50) | |
| company | VARCHAR(200) | |
| status | VARCHAR(20) | Lead, Customer, VIP, Inactive |
| lead_source | VARCHAR(30) | Website Form, TikTok, Referral, Workshop, Cold Outreach, Other |
| created_at | TIMESTAMP | DEFAULT NOW() |
| updated_at | TIMESTAMP | DEFAULT NOW() |

### deals
| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL PK | |
| title | VARCHAR(300) | NOT NULL |
| contact_id | INTEGER FK | REFERENCES contacts(id) |
| value | NUMERIC(12,2) | DEFAULT 0 |
| stage | VARCHAR(30) | New Lead, Contacted, Proposal, Negotiation, Won, Lost |
| expected_close_date | DATE | |
| won_lost_reason | TEXT | |
| created_at | TIMESTAMP | DEFAULT NOW() |
| updated_at | TIMESTAMP | DEFAULT NOW() |

### notes
| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL PK | |
| contact_id | INTEGER FK | CASCADE delete |
| content | TEXT | NOT NULL |
| created_at | TIMESTAMP | DEFAULT NOW() |

### activity_log
| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL PK | |
| action_type | VARCHAR(50) | contact_created, deal_moved, note_added, etc. |
| description | TEXT | |
| contact_id | INTEGER FK | SET NULL on delete |
| deal_id | INTEGER FK | SET NULL on delete |
| created_at | TIMESTAMP | DEFAULT NOW() |

---

## Routes

### Public
| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/` | Redirect to `/lp` |
| GET | `/lp` | Lead magnet landing page |
| POST | `/lp/submit` | Form → create contact → thank you |
| GET | `/lp/thank-you` | Thank you page |
| GET | `/sales` | Sales page + Stripe checkout link |

### Admin (auth required)
| Method | Route | Purpose |
|--------|-------|---------|
| GET/POST | `/admin/login` | Login form |
| GET | `/admin/logout` | Clear session |
| GET | `/admin/dashboard` | KPI cards + activity |
| GET | `/admin/contacts` | Contact list + search |
| GET | `/admin/contacts/<id>` | Contact detail |
| GET | `/admin/deals` | Kanban pipeline |

### API (auth required)
| Method | Route | Purpose |
|--------|-------|---------|
| GET/POST | `/api/contacts` | List/Create contacts |
| PUT/DELETE | `/api/contacts/<id>` | Update/Delete contact |
| GET/POST | `/api/contacts/<id>/notes` | List/Add notes |
| GET/POST | `/api/deals` | List/Create deals |
| PUT/DELETE | `/api/deals/<id>` | Update/Delete deal |
| PATCH | `/api/deals/<id>/stage` | Move deal stage |
| GET | `/api/dashboard-stats` | KPI data |
| POST | `/api/chat` | AI chatbot |

---

## AI Chatbot

### Flow
1. User message → POST `/api/chat`
2. Gemini 2.5 Flash classifies intent (JSON: intent, confidence, params)
3. If simple CRUD (confidence > 0.8) → execute directly
4. If complex/ambiguous → forward to Sonnet 4 with CRM context
5. Return: `{ response, actions_taken }`

### Supported Intents
- `create_contact`, `update_contact`, `query_contacts`
- `create_deal`, `update_deal`, `move_deal`, `query_deals`
- `dashboard_stats`, `general_question`

### Frontend
- Alpine.js component in `base_admin.html`
- Collapsible right panel (320px wide)
- Message history in localStorage
- Floating toggle button on mobile

---

## Phased Roadmap

### Phase 1: The Kitchen (MVP)
Flask app + login + contacts + deals + dashboard + seed data + dark gold theme + Railway deploy

### Phase 2: The Menu & Front Door
Lead magnet page + sales page + form submissions + toast notifications

### Phase 3: The Waiter
AI chatbot sidebar + OpenRouter integration + CRUD via natural language

### Phase 4: The Order Board
SortableJS Kanban pipeline + activity timeline + mobile polish

### Phase 5: The Cash Register
Chart.js analytics + conversion metrics + PWA manifest

### Phase 6: The Manager
Settings page + branding customization + Sonnet 4 complex queries + CSV import/export

---

## Environment Variables
```
DATABASE_URL=postgresql://...
ADMIN_USER=admin
ADMIN_PASS=changeme
SECRET_KEY=random-string
OPENROUTER_API_KEY=sk-or-...
BUSINESS_NAME=My Business
STRIPE_CHECKOUT_URL=https://buy.stripe.com/...
LEAD_MAGNET_URL=https://...
```

---

## Pre-loaded Demo Data
- 15 contacts: mix of Lead, Customer, VIP statuses across industries
- 8 deals: spread across all 6 pipeline stages with realistic values
- 20+ notes: conversation summaries, follow-up reminders
- 30+ activity log entries: creates, updates, stage moves
- Scenario: Mortgage broker CRM with realistic names and companies
