"""
Shared style constants for image generation and DOCX building.

Image styles and DOCX styles are fully decoupled — you can use image
generation without installing python-docx.
"""

# ── Image Generation Themes ────────────────────────────────────────────────
# Each theme is a style suffix appended to every image prompt.
# Use THEMES["name"] or pass a custom string to ImageGenerator.

THEMES = {
    "book": (
        "Flat vector illustration, notebook-style, educational. "
        "Clean white background. Minimal text, just labels. "
        "Soft teal (#0d9488), deep blue (#1a365d), and orange (#f97316) color palette. "
        "No photographs, no realistic people. Maximum 3 subjects in the image."
    ),
    "book-humorous": (
        "Flat vector illustration, notebook-style, educational, slightly humorous. "
        "Clean white background. Minimal text, just labels. "
        "Soft teal (#0d9488), deep blue (#1a365d), and orange (#f97316) color palette. "
        "No photographs, no realistic people. Cartoon style, fun and memorable. "
        "Maximum 3-4 subjects in the image."
    ),
    "dark-gold": (
        "Flat vector illustration, modern and clean, educational. "
        "Dark charcoal (#0A0A0A) background. Gold (#D4AF37) and warm amber (#E8C85A) accent colors. "
        "Minimal text, just labels. Simple icons and shapes. "
        "No photographs, no realistic people. Friendly cartoon style. "
        "Maximum 3 subjects in the image. High contrast for dark backgrounds."
    ),
    "minimal-light": (
        "Flat vector illustration, minimalist, clean. "
        "White (#FFFFFF) background. Soft gray (#6B7280) and blue (#3B82F6) accents. "
        "Minimal text, just labels. Thin line art style. "
        "No photographs, no realistic people. Maximum 3 subjects in the image."
    ),
}

# Default theme for backward compatibility
STYLE_SUFFIX = THEMES["book"]
STYLE_SUFFIX_HUMOROUS = THEMES["book-humorous"]

# ── Supported Formats ──────────────────────────────────────────────────────

SUPPORTED_FORMATS = ["png", "jpg", "jpeg", "webp"]
DEFAULT_FORMAT = "png"

# ── Supported Aspect Ratios ────────────────────────────────────────────────

SUPPORTED_ASPECT_RATIOS = ["16:9", "1:1", "4:3", "3:4", "9:16", "3:2", "2:3"]
DEFAULT_ASPECT_RATIO = "16:9"

# ── Supported Resolutions ─────────────────────────────────────────────────

SUPPORTED_RESOLUTIONS = ["1K", "2K", "4K"]
DEFAULT_RESOLUTION = "1K"


# ── DOCX Colors (only imported by docx_builder.py) ────────────────────────
# Wrapped in a function to avoid requiring python-docx at import time.

def get_docx_colors():
    """Return DOCX color constants. Requires python-docx installed."""
    from docx.shared import RGBColor
    return {
        "DEEP_BLUE": RGBColor(0x1A, 0x36, 0x5D),
        "TEAL": RGBColor(0x0D, 0x94, 0x88),
        "ORANGE": RGBColor(0xF9, 0x73, 0x16),
        "DARK_GRAY": RGBColor(0x37, 0x41, 0x51),
        "LIGHT_GRAY": RGBColor(0x9C, 0xA3, 0xAF),
    }


# ── DOCX Formatting ───────────────────────────────────────────────────────

FONT_FAMILY = "Calibri"
CODE_FONT = "Courier New"
BODY_SIZE_PT = 11
CODE_SIZE_PT = 10
H1_SIZE_PT = 24
H2_SIZE_PT = 18
H3_SIZE_PT = 14
FOOTER_SIZE_PT = 8
IMAGE_WIDTH_INCHES = 4.5

# Heading styles: (size_pt, color_key) for levels 1-3
# Use get_docx_colors() to resolve color_key to RGBColor at runtime
HEADING_STYLE_DEFS = [
    (H1_SIZE_PT, "DEEP_BLUE"),
    (H2_SIZE_PT, "TEAL"),
    (H3_SIZE_PT, "DEEP_BLUE"),
]

# ── Page Setup (6x9 trade paperback) ──────────────────────────────────────

PAGE_WIDTH_INCHES = 6
PAGE_HEIGHT_INCHES = 9
MARGIN_TOP_INCHES = 0.8
MARGIN_BOTTOM_INCHES = 0.8
MARGIN_LEFT_INCHES = 0.75
MARGIN_RIGHT_INCHES = 0.75

# ── Callout Markers ───────────────────────────────────────────────────────

CALLOUT_MARKER_DEFS = {
    "[PROMPT]": "TEAL",
    "[CHECKPOINT]": "TEAL",
    "[WATCH OUT]": "ORANGE",
    "[TRY IT]": "TEAL",
    "[SAVE $$$]": "ORANGE",
    "[WORKBOOK]": "TEAL",
    "[PRO TIP]": "TEAL",
}
