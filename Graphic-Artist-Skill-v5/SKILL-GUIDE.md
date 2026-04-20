# Image Generation Toolkit

A portable, reusable system for generating AI images via kie.ai and optionally embedding them into DOCX manuscripts. Works for **books** and **websites**.

## What This Does

1. **Generates images** via kie.ai API (Nano Banana Pro model) with preset themes or custom styles
2. **Supports multiple formats** -- PNG, JPG, WebP
3. **Supports multiple aspect ratios** -- 16:9, 1:1, 4:3, 3:4, 9:16, 3:2, 2:3
4. **Supports multiple resolutions** -- 1K, 2K, 4K
5. **Batch processes** with parallel workers, caching, and progress tracking
6. **CLI mode** -- run directly from terminal with a JSON prompts file, no scripting needed
7. **Analyzes documents** via OpenRouter (Claude Haiku) to recommend where images should go
8. **Embeds images** into DOCX manuscripts with full markdown-to-DOCX conversion

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in your project root:

```
KIE_API_KEY=Bearer your-key-here
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

- **kie.ai**: Sign up at kie.ai, get API key. ~$0.09/image.
- **OpenRouter**: Sign up at openrouter.ai, get API key. ~$0.01/analysis call. (Only needed for document analysis.)

### 3. Choose Your Workflow

#### Option A: CLI (Fastest -- No Coding)

Create a `prompts.json` file:

```json
[
  {"id": "hero_image", "prompt": "A friendly robot waving hello"},
  {"id": "step_1", "prompt": "Person downloading an app on their laptop"},
  {"id": "banner", "prompt": "Workshop celebration banner", "aspect_ratio": "16:9", "format": "jpg"}
]
```

Then run:

```bash
# Use the dark-gold theme for websites
python image_generator.py --prompts prompts.json --theme dark-gold --output my-images/

# Square JPGs for social media posts
python image_generator.py --prompts prompts.json --aspect 1:1 --format jpg

# High-res PNGs for a book
python image_generator.py --prompts prompts.json --theme book --resolution 2K

# List all available themes
python image_generator.py --list-themes
```

Each prompt in the JSON can override the defaults:
- `aspect_ratio` -- override for this image only (e.g., "1:1")
- `resolution` -- override for this image only (e.g., "4K")
- `format` -- override for this image only (e.g., "jpg")

#### Option B: Python Script

```python
from image_generator import ImageGenerator

gen = ImageGenerator(
    api_key="Bearer your-key",
    theme="dark-gold",           # or "book", "book-humorous", "minimal-light"
    aspect_ratio="1:1",          # default for all images
    output_format="jpg",         # default for all images
    resolution="1K",             # default for all images
)

prompts = [
    {"id": "img_001", "prompt": "A cartoon showing..."},
    {"id": "img_002", "prompt": "An infographic of...", "aspect_ratio": "16:9"},  # override
]

gen.batch_generate_from_prompts(prompts, output_dir="my-images/")
```

#### Option C: Book workflow (markers in markdown)

Place `[INFOGRAPHIC: description]` markers in your chapter markdown files, then run:

```python
from image_generator import ImageGenerator
from marker_extractor import extract_markers_from_chapters
from docx_builder import BookBuilder

gen = ImageGenerator(api_key="Bearer your-key", theme="book")
markers = extract_markers_from_chapters("chapters/", chapter_order=["01-intro.md", "02-topic.md"])
images = gen.batch_generate(markers, max_parallel=3, output_dir="infographics/")
builder = BookBuilder()
builder.build("chapters/", chapter_order, images, "output/My-Book.docx")
```

#### Option D: Document analysis (upload a PDF/DOCX, get recommendations)

```python
from doc_analyzer import analyze_document

sections = analyze_document("my-document.pdf")  # or .docx
# Returns sections with AI-recommended image prompts
```

## Architecture

```
book-image-toolkit/
 SKILL-GUIDE.md          # This file
 requirements.txt        # Python dependencies
 image_generator.py      # Core: kie.ai API client + batch generation + CLI
 style_config.py         # Themes, formats, aspect ratios, DOCX constants
 marker_extractor.py     # Extract [INFOGRAPHIC: ...] from markdown files
 doc_analyzer.py         # Parse PDF/DOCX + OpenRouter AI analysis
 docx_builder.py         # Markdown-to-DOCX converter with image embedding
```

## Themes

Built-in themes (style suffixes appended to every prompt):

| Theme | Best For | Look |
|-------|----------|------|
| `book` | Books, print | White bg, teal/blue/orange, flat vector |
| `book-humorous` | Fun books | Same colors, cartoon, slightly humorous |
| `dark-gold` | Websites (dark mode) | Dark bg, gold/amber accents, modern |
| `minimal-light` | Clean websites | White bg, gray/blue, thin line art |

Add your own themes in `style_config.py` by adding entries to the `THEMES` dict.

You can also pass a fully custom style string:

```python
gen = ImageGenerator(api_key="...", style_suffix="Watercolor, pastel, dreamy feel")
```

## Formats, Aspect Ratios, and Resolutions

**Formats:** png, jpg, webp
**Aspect Ratios:** 16:9, 1:1, 4:3, 3:4, 9:16, 3:2, 2:3
**Resolutions:** 1K (1024px), 2K, 4K

Set defaults at the generator level, override per-prompt:

```python
gen = ImageGenerator(api_key="...", aspect_ratio="16:9", output_format="png")

prompts = [
    {"id": "hero", "prompt": "...", "aspect_ratio": "16:9"},       # uses default
    {"id": "icon", "prompt": "...", "aspect_ratio": "1:1"},        # square override
    {"id": "social", "prompt": "...", "format": "jpg"},            # jpg override
    {"id": "print", "prompt": "...", "resolution": "4K"},          # high-res override
]
```

## CLI Reference

```
python image_generator.py [OPTIONS]

Required:
  --prompts FILE        Path to JSON prompts file

Options:
  --output DIR          Output directory (default: generated-images)
  --theme NAME          Preset theme: book, book-humorous, dark-gold, minimal-light
  --style TEXT          Custom style suffix (overrides --theme)
  --aspect RATIO        Aspect ratio: 16:9, 1:1, 4:3, etc. (default: 16:9)
  --format FMT          Output format: png, jpg, webp (default: png)
  --resolution RES      Resolution: 1K, 2K, 4K (default: 1K)
  --parallel N          Max parallel workers (default: 3)
  --list-themes         List all themes and exit
```

## API Details

### kie.ai Image Generation

- **Model**: `nano-banana-pro`
- **Endpoint**: `https://api.kie.ai/api/v1/jobs/createTask`
- **Poll**: `https://api.kie.ai/api/v1/jobs/recordInfo` (every 2s, max 240s)
- **Cost**: ~$0.09/image
- **Auth**: Bearer token in Authorization header

### OpenRouter Document Analysis

- **Model**: `anthropic/claude-haiku-3.5-20241022`
- **Endpoint**: `https://openrouter.ai/api/v1/chat/completions`
- **Cost**: ~$0.01/call
- **Auth**: Bearer token in Authorization header

## Decoupled Architecture

The toolkit is split so you only need what you use:

- **Image generation only** (websites, social media): Needs `requests`, optionally `Pillow` for JPG/WebP. No `python-docx` required.
- **Full book pipeline** (DOCX output): Needs `python-docx`, `Pillow`, and `PyMuPDF` (for PDF analysis).

`style_config.py` keeps DOCX colors behind a `get_docx_colors()` function so importing it for image generation never triggers a `python-docx` import.

## Cost Estimates

| Items | Cost | Time (3 workers) |
|-------|------|-------------------|
| 10 images | ~$0.90 | ~1 min |
| 50 images | ~$4.50 | ~6 min |
| 100 images | ~$9.00 | ~12 min |

## Caching

All scripts check if an image file already exists before regenerating. Re-runs skip cached images, saving time and money.
