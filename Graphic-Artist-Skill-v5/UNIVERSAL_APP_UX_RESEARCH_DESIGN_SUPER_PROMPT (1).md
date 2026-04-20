---
name: ui-ux-audit
description: UI/UX audit and mockup generation skill for websites and mobile apps. Runs competitive research, user mapping, UX best practices analysis, design synthesis, and generates high-fidelity mockups via Nano Banana Pro (kie.ai). Menu-driven -- pick individual phases or run the full pipeline.
type: skill
triggers:
  - UI audit
  - UX audit
  - UX research
  - mockup generation
  - design audit
  - app design
  - mobile app design
  - website design review
---

# UI/UX Audit and Mockup Generation Skill

A menu-driven skill for running UI/UX audits on websites and mobile apps, with integrated mockup generation via Nano Banana Pro (kie.ai).

## WHEN TO USE

- Auditing an existing app or website's UI/UX
- Designing the frontend for a new mobile app or web app
- Generating high-fidelity mockups for screens
- Running competitive analysis on a product category
- Building a design system for a project

## PHASE MENU

When this skill is invoked, present the user with this menu:

```
Which phases do you want to run?

1. Competitive Landscape Deep Dive
2. User and Use Case Mapping
3. UI/UX Best Practices Analysis
4. Design Synthesis (colors, typography, components, IA)
5. Mockup Generation (Nano Banana Pro)
6. Full Deliverable (compile everything into a markdown report)

Options:
  A. Full Pipeline (all 6 phases)
  B. Quick Audit (phases 1-4, no mockups)
  C. Mockups Only (phase 5)
  D. Pick specific phases (comma-separated, e.g. "1,3,5")
```

Wait for the user's selection before proceeding.

## INPUT VARIABLES

Collect these before running any phase. If the user has a PRD or existing screenshots, ask for them. Mark optional fields -- skip what is not needed for the selected phases.

| Variable | Required For | Description |
|----------|-------------|-------------|
| APP_NAME | All phases | Name of the app or website |
| APP_CATEGORY | Phases 1,3 | e.g., CRM, LMS, marketplace, booking, EHR |
| ONE_SENTENCE_DESCRIPTION | All phases | What the product does in one line |
| PRD | Phases 2,4 | Product requirements document (paste or file path) |
| CURRENT_SCREENSHOTS | Phase 3,5 | Existing UI screenshots if auditing a live product |
| TARGET_USERS | Phase 2 | ICP with demographics, tech comfort, primary device |
| PRIMARY_GOALS | Phases 2,3 | What the interface must help users accomplish, priority order |
| BRAND_PALETTE | Phases 4,5 | Hex codes, or "design fresh and recommend" |
| CONSTRAINTS | Phases 3,4 | Mobile required, accessibility level, tech stack, integrations |
| INSPIRATIONS | Phases 4,5 | 2-3 products whose UX to borrow from |

Only collect variables relevant to the selected phases. Do not ask for everything if the user only wants mockups.

---

## PHASE 1: COMPETITIVE LANDSCAPE DEEP DIVE

Research the live market using web search. Do not rely on training data alone.

### 1A. Direct Competitors (find 5-7)

For each competitor produce:

- Product name and URL
- Price tiers and market positioning
- Dashboard, core workspace, detail view, and settings screen descriptions
- Information architecture: what is in the nav, what is hidden, what is prominent
- Visual language: color palette hex codes, typography, spacing scale
- 3 things they do brilliantly
- 3 things they do poorly
- 1 unique UX innovation worth studying

### 1B. Adjacent Products with World-Class UX (find 3-5)

Products in different categories that solve similar design problems or have transferable patterns. Consider: Linear (speed, keyboard-first), Notion (flexibility), Stripe (data density), Superhuman (power-user workflows), Figma (collaboration), Airtable (flexible data views).

### 1C. Competitive Scorecard

Output a comparison table scoring each competitor 1-5 on:

| Dimension | What to evaluate |
|-----------|-----------------|
| Clarity | Can users understand what to do immediately? |
| Data Density | How much useful info per screen? |
| Speed | Perceived performance and interaction speed |
| Learnability | How fast can a new user be productive? |
| Mobile Experience | Responsive quality, touch targets, mobile flows |
| Customization | Can users adapt the UI to their workflow? |
| Onboarding | First-run experience quality |
| Overall Polish | Animations, consistency, attention to detail |

Highlight the top performer in each dimension.

### 1D. Market Gaps

Based on research, identify 3-5 specific UX gaps a new entrant could exploit.

**Output:** `[APP_NAME]_competitive_analysis.md`

---

## PHASE 2: USER AND USE CASE MAPPING

### 2A. Personas (build 3-5)

For each persona:

- Name, role, age range
- Primary goal with the product
- Top 3 pain points today
- Tech comfort level (1-5)
- Primary device (desktop, mobile, split)
- Usage frequency (daily, weekly, monthly)
- The single metric they care about
- One quote that captures their mindset

### 2B. Jobs-to-be-Done

List the top 15 jobs across all personas. For each: frequency (daily/weekly/rare) and strategic importance (core/supporting/nice-to-have).

### 2C. Critical User Journeys

Map happy path and key error states for the 5 most important flows:
- Trigger
- Steps
- Decision points
- Possible exit points
- Success criteria

### 2D. Display Pattern Recommendations

For every significant data type in the PRD, recommend a primary display pattern and a secondary option.

**Do not default to Kanban.** Actively consider: tables, cards, lists, timelines, calendars, pipelines, maps, charts, grids, split views, master-detail, inbox layouts, spreadsheet views.

Explain in one sentence why each pattern fits the data and user task.

**Output:** `[APP_NAME]_user_mapping.md`

---

## PHASE 3: UI/UX BEST PRACTICES ANALYSIS

Research category-specific patterns. Cite real products by name for every recommendation.

Cover each of these areas:

| Area | What to research |
|------|-----------------|
| Navigation | Sidebar vs top nav vs command palette vs hybrid. What wins for this category? |
| Data Display | When to use table vs card vs timeline vs pipeline vs kanban vs calendar |
| Forms and Input | Inline edit, modals, side panels, slide-over drawers, full-page flows |
| Search and Filter | Global search, faceted filters, saved views, smart filters |
| Empty/Loading/Error States | States that actually help users, not just spinners |
| Onboarding | Checklists, tours, empty-state coaching, sample data |
| Progressive Disclosure | How to handle complex features without overwhelming |
| Keyboard Shortcuts | Power user affordances |
| Mobile Adaptation | Responsive vs native-feel, what to cut, what to prioritize on small screens |
| Dark Mode | When to support it, implementation considerations |
| Accessibility | WCAG AA contrast, focus states, screen reader support, keyboard nav |
| Micro-interactions | Which are worth the budget vs vanity animations |

### Mobile-Specific Checklist (for mobile apps)

- Touch targets minimum 44x44pt
- Bottom navigation for primary actions (thumb zone)
- Swipe gestures for common actions
- Pull-to-refresh where appropriate
- Offline state handling
- Safe area insets (notch, home indicator)
- Haptic feedback for confirmations
- Sheet/bottom-sheet patterns over modals

### Website-Specific Checklist

- Above-the-fold hierarchy and CTA placement
- Responsive breakpoints (mobile, tablet, desktop)
- Page load performance considerations
- SEO-friendly structure
- Cookie consent and privacy patterns
- Footer navigation and sitemap

**Output:** `[APP_NAME]_ux_best_practices.md`

---

## PHASE 4: DESIGN SYNTHESIS

Produce a concrete, implementable design brief.

### 4A. Design Principles
3-5 guiding principles for this specific app (not generic platitudes).

### 4B. Information Architecture
Text tree or ASCII diagram showing the full screen hierarchy and navigation structure.

### 4C. Screen Inventory
Every screen with a one-line purpose statement.

### 4D. Visual System

| Element | Deliverable |
|---------|------------|
| Color Palette | Hex codes with usage rules: primary, secondary, accent, neutral scale, semantic (success/warning/error) |
| Typography | Font family, size scale, weights, line heights |
| Component Checklist | Buttons, inputs, cards, modals, tables, nav, toasts, badges, avatars, etc. |
| Grid and Spacing | Base unit and scale (e.g., 4px base, 4/8/12/16/24/32/48) |
| Icon Style | Direction and recommended library (Lucide, Heroicons, Phosphor, etc.) |
| Border Radius | Scale for cards, buttons, inputs |

### 4E. UI Copy Guidelines
3 tone rules plus 5 do/don't examples for microcopy.

**Output:** `[APP_NAME]_design_system.md`

---

## PHASE 5: MOCKUP GENERATION VIA NANO BANANA PRO

Generate high-fidelity mockup images using the project's `image_generator.py` and kie.ai API.

### Toolkit Integration

This skill uses the image generation toolkit in this same folder:

```
image_generator.py   -- Core kie.ai API client + batch generation + CLI
style_config.py      -- Themes, formats, aspect ratios
```

**Environment required:** `KIE_API_KEY` must be set in `.env` or environment.

### Screen Set Selection

Choose the appropriate set based on what is being designed:

#### Mobile App Mockups (generate 8)

| # | Screen | Aspect Ratio |
|---|--------|-------------|
| 1 | Mobile home/dashboard | 9:16 |
| 2 | Mobile primary workspace (the core screen users live in) | 9:16 |
| 3 | Mobile detail view | 9:16 |
| 4 | Mobile creation/edit flow | 9:16 |
| 5 | Mobile navigation (expanded nav or tab bar in context) | 9:16 |
| 6 | Mobile empty state for a key screen | 9:16 |
| 7 | Mobile settings/profile | 9:16 |
| 8 | Mobile onboarding/first-run screen | 9:16 |

#### Website Mockups (generate 8)

| # | Screen | Aspect Ratio |
|---|--------|-------------|
| 1 | Desktop hero/landing above the fold | 16:9 |
| 2 | Desktop dashboard or primary workspace | 16:9 |
| 3 | Desktop detail view with side panel or drawer | 16:9 |
| 4 | Desktop creation/edit flow | 16:9 |
| 5 | Mobile responsive version of the hero | 9:16 |
| 6 | Mobile responsive version of the primary workspace | 9:16 |
| 7 | Desktop empty state for a key screen | 16:9 |
| 8 | Desktop settings or admin view | 16:9 |

#### Full App (both desktop + mobile, generate 10)

| # | Screen | Aspect Ratio |
|---|--------|-------------|
| 1 | Desktop dashboard/home | 16:9 |
| 2 | Desktop primary workspace | 16:9 |
| 3 | Desktop detail view with side panel | 16:9 |
| 4 | Desktop creation/edit flow | 16:9 |
| 5 | Mobile dashboard | 9:16 |
| 6 | Mobile primary workspace | 9:16 |
| 7 | Mobile detail view | 9:16 |
| 8 | Empty state (desktop) | 16:9 |
| 9 | Empty state (mobile) | 9:16 |
| 10 | Settings/admin (desktop) | 16:9 |

### Prompt Structure for Each Mockup

Every mockup prompt sent to Nano Banana Pro must follow this structure:

```
Design a high fidelity [screen type] mockup for [APP_NAME], a [APP_CATEGORY].

USER CONTEXT: [who is viewing this screen, what they are trying to do]

LAYOUT (top to bottom, left to right):
  - [element 1 with position and content]
  - [element 2 with position and content]
  - [continue for every visible element]

SAMPLE DATA: [realistic data -- real-sounding names, numbers, dates, statuses. Never lorem ipsum.]

COLORS: Primary [#hex], secondary [#hex], accent [#hex], neutral scale [#hex through #hex], semantic colors for success, warning, error.

TYPOGRAPHY: [font family], [size hierarchy].

STYLE REFERENCE: [Reference 2-3 real products, e.g. "Clean like Linear, data density like Stripe, warm typography like Notion"]

QUALITY: High fidelity, production ready, realistic shadows, pixel-perfect alignment. No generic gradients, no stock imagery, no placeholder text.

ASPECT RATIO: [16:9 for desktop, 9:16 for mobile]
```

### Generating Mockups

**Option A: CLI (recommended)**

Create a `mockups.json` file with all prompts, then run:

```bash
python image_generator.py \
  --prompts mockups.json \
  --theme minimal-light \
  --output [APP_NAME]-mockups/ \
  --parallel 3
```

**Option B: Python script**

```python
from image_generator import ImageGenerator

gen = ImageGenerator(
    api_key=os.environ["KIE_API_KEY"],
    theme="minimal-light",  # or "dark-gold" for dark UI
)

prompts = [
    {"id": "01_desktop_dashboard", "prompt": "...", "aspect_ratio": "16:9"},
    {"id": "02_mobile_home", "prompt": "...", "aspect_ratio": "9:16"},
    # ... all screens
]

gen.batch_generate_from_prompts(prompts, output_dir=f"{APP_NAME}-mockups/")
```

### Theme Selection Guide

| Use Case | Theme | Why |
|----------|-------|-----|
| Light website or SaaS | `minimal-light` | Clean, professional, white backgrounds |
| Dark-mode app or premium product | `dark-gold` | Modern, high contrast, dark backgrounds |
| Custom brand | Pass `--style "..."` | Full control over the visual language |

**Output:** `[APP_NAME]-mockups/` directory with all generated images + `mockups.json` prompt file

---

## PHASE 6: FINAL DELIVERABLE

Compile all completed phases into a single markdown report.

**Filename:** `[APP_NAME]_UX_Research_and_Design_[YYYY-MM-DD].md`

### Report Structure

```markdown
# [APP_NAME] UX Research and Design Report

## 1. Executive Summary
- Top 5 recommendations with expected impact
- One paragraph on the biggest UX opportunity

## 2. Competitive Analysis
- Competitor profiles
- Scorecard table
- Gap analysis

## 3. Personas and Journeys
- Persona cards
- Jobs-to-be-done table
- Critical user journey maps
- Display pattern recommendations

## 4. UI/UX Best Practices
- Category-specific patterns with product citations
- Mobile/website checklists

## 5. Design System
- Design principles
- Information architecture
- Color palette, typography, components, grid
- UI copy guidelines

## 6. Screen Specifications
- Screen-by-screen breakdown with mockup references
- Element inventory per screen

## 7. Mockup Gallery
- All generated mockups with captions
- Key design decisions each mockup demonstrates

## 8. Implementation Priorities
- P0: Must-have for launch
- P1: Should-have for v1.1
- P2: Nice-to-have for future

## 9. Open Questions and Assumptions

## 10. References
- Every product cited
- Every pattern source with links
```

**Output:** `[APP_NAME]_UX_Research_and_Design_[YYYY-MM-DD].md`

---

## QUALITY STANDARDS

These apply to ALL phases:

- Every recommendation ties to a user goal from the PRD
- Every pattern cites a real product that uses it well
- No generic AI aesthetic. No default purple gradients. No floating glass cards unless justified. No stock photos.
- Mockups look like production screenshots, not wireframes or concept art
- Short sentences. One idea each.
- Explanations at an 8th-grade reading level
- Use web search aggressively for competitive research -- do not rely on training data alone

## FAIL-FAST RULES

Stop and ask for clarification if:

- PRD is missing critical information (user roles, data models, key flows)
- Contradictions exist between PRD sections
- Stated constraints make stated goals impossible
- Direct competitive landscape has no real matches (pivot to adjacent patterns and flag this)
- Brand palette conflicts with accessibility minimums

## PHASE COMPLETION

After each phase, output:

```
PHASE [N] COMPLETE. Output saved to [filename].
```

If running multiple phases, continue to the next. If running a single phase, present the deliverable and ask if the user wants to continue to another phase.
