"""
Parse PDF/DOCX documents and use OpenRouter AI to recommend where infographics should go.
"""

import json
import os

import fitz  # PyMuPDF
import requests
from docx import Document

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "anthropic/claude-haiku-3.5-20241022"

ANALYSIS_PROMPT = """You are a document enhancement assistant. I will give you the section titles and first paragraph of each section from a document.

For each section, decide if an infographic would help the reader understand the concept better. Only recommend images for sections that explain a PROCESS, COMPARISON, CONCEPT, or RELATIONSHIP.

Do NOT recommend images for: introductions, conclusions, simple lists, or sections that are already clear without visuals.

For each recommended section, write a Nano Banana Pro image generation prompt that:
- Has maximum 3 subjects/elements in the image
- Uses minimal text — just labels
- Is notebook-style, flat vector, clean white background
- Uses soft teal, blue, and orange accents
- Is educational and easy to understand at a glance

Return ONLY a JSON array (no markdown fences):
[
  {
    "section_title": "...",
    "recommend_image": true,
    "prompt": "Clean minimal infographic on white background showing..."
  }
]

Include ALL sections in the response, with recommend_image set to true or false."""


def extract_sections_pdf(filepath: str) -> list[dict]:
    """Extract sections from a PDF by detecting headings (font size >= 14 or bold >= 12)."""
    doc = fitz.open(filepath)
    sections = []
    current_heading = None
    current_body_lines = []

    for page in doc:
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                line_text = "".join(span["text"] for span in line["spans"]).strip()
                if not line_text:
                    continue
                max_size = max(span["size"] for span in line["spans"])
                is_bold = any("bold" in (span.get("font", "").lower()) for span in line["spans"])
                is_heading = max_size >= 14 or (max_size >= 12 and is_bold)

                if is_heading:
                    if current_heading:
                        sections.append({
                            "title": current_heading,
                            "body": "\n".join(current_body_lines).strip(),
                        })
                    current_heading = line_text
                    current_body_lines = []
                else:
                    current_body_lines.append(line_text)

    if current_heading:
        sections.append({
            "title": current_heading,
            "body": "\n".join(current_body_lines).strip(),
        })

    doc.close()

    if not sections and current_body_lines:
        sections.append({
            "title": "Document Content",
            "body": "\n".join(current_body_lines).strip(),
        })

    return sections


def extract_sections_docx(filepath: str) -> list[dict]:
    """Extract sections from a DOCX by detecting Heading styles."""
    doc = Document(filepath)
    sections = []
    current_heading = None
    current_body_lines = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        is_heading = para.style.name.startswith("Heading")

        if is_heading:
            if current_heading:
                sections.append({
                    "title": current_heading,
                    "body": "\n".join(current_body_lines).strip(),
                })
            current_heading = text
            current_body_lines = []
        else:
            current_body_lines.append(text)

    if current_heading:
        sections.append({
            "title": current_heading,
            "body": "\n".join(current_body_lines).strip(),
        })

    if not sections and current_body_lines:
        sections.append({
            "title": "Document Content",
            "body": "\n".join(current_body_lines).strip(),
        })

    return sections


def analyze_sections(
    sections: list[dict],
    api_key: str | None = None,
) -> list[dict]:
    """Send sections to OpenRouter AI for image recommendations.

    Returns list of dicts: {section_title, recommend_image, prompt}
    """
    api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY required")

    section_summaries = []
    for s in sections:
        preview = s["body"][:300] if s["body"] else ""
        section_summaries.append(f"## {s['title']}\n{preview}")

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": ANALYSIS_PROMPT},
            {"role": "user", "content": "\n\n".join(section_summaries)},
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }

    resp = requests.post(
        OPENROUTER_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()

    content = resp.json()["choices"][0]["message"]["content"]
    parsed = json.loads(content)

    # Handle various response shapes from the AI
    if isinstance(parsed, dict) and "sections" in parsed:
        return parsed["sections"]
    if isinstance(parsed, dict) and "recommendations" in parsed:
        return parsed["recommendations"]
    if isinstance(parsed, list):
        return parsed
    for value in parsed.values():
        if isinstance(value, list):
            return value
    return []


def analyze_document(
    filepath: str,
    api_key: str | None = None,
) -> list[dict]:
    """Full pipeline: parse document + AI analysis.

    Returns list of dicts with recommended sections and prompts.
    """
    ext = filepath.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        sections = extract_sections_pdf(filepath)
    elif ext == "docx":
        sections = extract_sections_docx(filepath)
    else:
        raise ValueError(f"Unsupported format: {ext}. Use PDF or DOCX.")

    if not sections:
        return []

    recommendations = analyze_sections(sections, api_key)

    # Merge recommendations with original section data
    sections_by_title = {s["title"].lower().strip(): s for s in sections}
    result = []
    for rec in recommendations:
        if not rec.get("recommend_image", True):
            continue
        title = rec.get("section_title") or rec.get("title", "")
        orig = sections_by_title.get(title.lower().strip(), {})
        result.append({
            "title": title,
            "body": orig.get("body", ""),
            "prompt": rec.get("prompt", ""),
        })

    return result
