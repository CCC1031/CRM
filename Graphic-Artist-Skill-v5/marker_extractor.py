"""
Extract [INFOGRAPHIC: ...] markers from markdown chapter files.
"""

import re
from pathlib import Path


def extract_markers_from_chapters(
    chapters_dir: str | Path,
    chapter_order: list[str],
) -> list[dict]:
    """Scan markdown files for [INFOGRAPHIC: description] markers.

    Args:
        chapters_dir: Path to directory containing chapter .md files
        chapter_order: Ordered list of chapter filenames

    Returns:
        List of dicts: {chapter, description, prompt, index}
    """
    chapters_path = Path(chapters_dir)
    markers = []

    for chapter_file in chapter_order:
        filepath = chapters_path / chapter_file
        if not filepath.exists():
            continue
        text = filepath.read_text(encoding="utf-8")
        for match in re.finditer(r'\[INFOGRAPHIC:\s*(.+?)(?:\]|$)', text, re.MULTILINE):
            desc = match.group(1).rstrip("]").strip()
            markers.append({
                "chapter": chapter_file,
                "description": desc,
                "prompt": desc[:500],  # kie.ai prompt length limit
                "index": len(markers),
            })

    return markers


def extract_markers_from_single_file(filepath: str | Path) -> list[dict]:
    """Extract markers from a single markdown file.

    Returns:
        List of dicts: {description, prompt, index}
    """
    text = Path(filepath).read_text(encoding="utf-8")
    markers = []
    for match in re.finditer(r'\[INFOGRAPHIC:\s*(.+?)(?:\]|$)', text, re.MULTILINE):
        desc = match.group(1).rstrip("]").strip()
        markers.append({
            "description": desc,
            "prompt": desc[:500],
            "index": len(markers),
        })
    return markers
