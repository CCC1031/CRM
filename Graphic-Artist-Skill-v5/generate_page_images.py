"""
Generate professional images for Workshop + Academy pages.
JPG format, dark-gold theme, web-optimized.
"""

import os
from dotenv import load_dotenv
from image_generator import ImageGenerator

load_dotenv()

api_key = os.getenv("KIE_API_KEY")
if not api_key:
    raise ValueError("KIE_API_KEY not found in .env")

gen = ImageGenerator(
    api_key=api_key,
    theme="dark-gold",
    output_format="jpg",
)

# Override style for more professional, polished look
gen.style_suffix = (
    "Professional flat vector illustration, modern and polished, tech-forward. "
    "Dark charcoal (#0A0A0A) background. Gold (#D4AF37) and warm amber (#E8C85A) accent colors. "
    "Clean lines, minimal text (labels only). Sleek and premium feel. "
    "No photographs, no realistic people. Stylized professional icons and shapes. "
    "Maximum 3-4 subjects. High contrast for dark backgrounds. Web-ready composition."
)

prompts = [
    # ── Workshop Page ──────────────────────────────────────────────────
    {
        "id": "ws_student_projects",
        "prompt": (
            "Four glowing laptop screens arranged in a 2x2 grid, each showing a different "
            "AI app interface: a CRM dashboard, a social media content tool, a chat assistant, "
            "and an analytics panel. Gold UI elements on dark screens. Premium tech showcase."
        ),
    },
    {
        "id": "ws_problem",
        "prompt": (
            "Split comparison: Left side shows a frustrated person with a giant invoice "
            "showing $10,000 in red. Right side shows a confident person at a laptop with "
            "golden AI sparkles building an app effortlessly. Dark background, dramatic contrast."
        ),
    },
    {
        "id": "ws_vibe_coding",
        "prompt": (
            "A person speaking into the air, golden speech bubbles transforming into lines of "
            "code that flow into a laptop screen. The concept: plain English becomes real software. "
            "Magical, futuristic, empowering. Voice to code transformation."
        ),
    },
    {
        "id": "ws_two_apps",
        "prompt": (
            "Two polished app interfaces side by side: an AI CRM with contact cards and pipeline view, "
            "and a Social Media Content Generator with image/text output. Both on sleek dark screens "
            "with gold accent buttons and headers. Professional software mockup style."
        ),
    },
    {
        "id": "ws_hour_1",
        "prompt": (
            "A laptop powering on with VS Code editor opening, a terminal window glowing gold, "
            "and setup icons (gear, wrench, checkmark) floating around it. 'Getting started' energy. "
            "Clean, simple, welcoming."
        ),
        "aspect_ratio": "4:3",
    },
    {
        "id": "ws_hour_3",
        "prompt": (
            "A golden rocket launching upward from a laptop screen, trailing sparkles. Below the rocket, "
            "a web browser shows a live deployed app with a URL bar. The concept: your app going live "
            "on the internet. Exciting, milestone moment."
        ),
        "aspect_ratio": "4:3",
    },
    {
        "id": "ws_hour_5",
        "prompt": (
            "A marketing funnel diagram with golden leads flowing in from the top (social media icons), "
            "through the middle (content, engagement), to the bottom (dollar signs, customers). "
            "Clean funnel visualization showing monetization and growth strategy."
        ),
        "aspect_ratio": "4:3",
    },
    {
        "id": "ws_audience",
        "prompt": (
            "Five professional silhouette icons in a row: a real estate agent with a house, "
            "a coach with a clipboard, a consultant with a chart, an entrepreneur with a lightbulb, "
            "and a freelancer with a laptop. Each glowing gold. Diverse professionals concept."
        ),
    },
    {
        "id": "ws_value_stack",
        "prompt": (
            "A premium gift box opening with golden light radiating outward. Inside, stacked items "
            "are floating: a video player icon, a workbook, a template document, a strategy blueprint, "
            "and a certificate. Value and abundance concept. Premium and exciting."
        ),
    },

    # ── Academy Page ───────────────────────────────────────────────────
    {
        "id": "ac_gap",
        "prompt": (
            "Two diverging paths: the left path is gray, cracked, and leads to a person stuck "
            "at an old computer. The right path is golden, glowing, and leads to a person thriving "
            "with AI tools and multiple screens. Fork in the road concept. Dramatic contrast."
        ),
    },
    {
        "id": "ac_offer",
        "prompt": (
            "A sleek platform dashboard mockup with four panels: a video course library, "
            "a live class calendar, a community chat feed, and an AI tools section. "
            "Gold-themed interface on a dark background. Premium learning platform feel."
        ),
    },
    {
        "id": "ac_build",
        "prompt": (
            "A collection of AI project icons connected by golden lines in a network: "
            "a chatbot bubble, an automation gear, a content generator, a data dashboard, "
            "and an AI assistant. Central hub showing what you can create. Connected ecosystem."
        ),
    },
    {
        "id": "ac_tools",
        "prompt": (
            "Three AI tool icons (a brain for ChatGPT, a star for Claude, a diamond for Gemini) "
            "arranged in a triangle around a central golden learning hub. Arrows showing mastery flow. "
            "Clean, iconic representation of AI tool ecosystem."
        ),
    },
    {
        "id": "ac_challenge",
        "prompt": (
            "Seven golden stepping stones forming a path from left to right, numbered 1 through 7. "
            "Each stone glows brighter as you progress. A flag/trophy at the end of day 7. "
            "Journey and progress concept. 7-day challenge visualization."
        ),
    },
    {
        "id": "ac_community",
        "prompt": (
            "A network of connected professional avatar circles, each with a specialty icon "
            "(laptop, chart, camera, microphone, lightbulb). Golden connection lines between them "
            "forming a community web. Collaboration and support concept."
        ),
    },
    {
        "id": "ac_pricing",
        "prompt": (
            "A golden ticket or VIP pass with 'FREE 7 DAYS' prominently displayed, "
            "radiating light on a dark background. A welcoming open door behind it. "
            "Low-risk, high-reward, inviting concept. Premium but accessible."
        ),
        "aspect_ratio": "4:3",
    },
]

output_dir = "simpletechskills-site/images/page-images"

print(f"Generating {len(prompts)} professional images for Workshop + Academy pages...")
results = gen.batch_generate_from_prompts(prompts, max_parallel=3, output_dir=output_dir)
print(f"\nDone! Images saved to {output_dir}/")
