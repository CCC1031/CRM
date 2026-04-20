"""
Core image generation via kie.ai API.
Handles single image creation, polling, batch generation with parallel workers,
caching, multiple formats (PNG/JPG/WebP), aspect ratios, and CLI usage.
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

from style_config import (
    DEFAULT_ASPECT_RATIO,
    DEFAULT_FORMAT,
    DEFAULT_RESOLUTION,
    SUPPORTED_ASPECT_RATIOS,
    SUPPORTED_FORMATS,
    SUPPORTED_RESOLUTIONS,
    STYLE_SUFFIX,
    THEMES,
)


class ImageGenerator:
    """Generate images via kie.ai Nano Banana Pro model."""

    API_BASE = "https://api.kie.ai/api/v1"
    MODEL = "nano-banana-pro"
    POLL_INTERVAL = 2  # seconds
    MAX_POLLS = 120  # 240 seconds max wait

    def __init__(
        self,
        api_key: str,
        style_suffix: str | None = None,
        theme: str | None = None,
        aspect_ratio: str | None = None,
        resolution: str | None = None,
        output_format: str | None = None,
    ):
        """Initialize the generator.

        Args:
            api_key: kie.ai Bearer token (include "Bearer " prefix)
            style_suffix: Custom style string appended to every prompt.
                          Overrides theme if both are provided.
            theme: Name of a preset theme from THEMES dict.
                   Ignored if style_suffix is provided.
            aspect_ratio: Default aspect ratio (16:9, 1:1, 4:3, etc.)
            resolution: Default resolution (1K, 2K, 4K)
            output_format: Default output format (png, jpg, webp)
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }

        # Resolve style: explicit suffix > theme > default
        if style_suffix:
            self.style_suffix = style_suffix
        elif theme and theme in THEMES:
            self.style_suffix = THEMES[theme]
        else:
            self.style_suffix = STYLE_SUFFIX

        # Defaults (can be overridden per-prompt)
        self.default_aspect_ratio = aspect_ratio or DEFAULT_ASPECT_RATIO
        self.default_resolution = resolution or DEFAULT_RESOLUTION
        self.default_format = output_format or DEFAULT_FORMAT

        # Validate defaults
        if self.default_aspect_ratio not in SUPPORTED_ASPECT_RATIOS:
            raise ValueError(
                f"Unsupported aspect ratio: {self.default_aspect_ratio}. "
                f"Choose from: {', '.join(SUPPORTED_ASPECT_RATIOS)}"
            )
        if self.default_resolution not in SUPPORTED_RESOLUTIONS:
            raise ValueError(
                f"Unsupported resolution: {self.default_resolution}. "
                f"Choose from: {', '.join(SUPPORTED_RESOLUTIONS)}"
            )
        if self.default_format not in SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {self.default_format}. "
                f"Choose from: {', '.join(SUPPORTED_FORMATS)}"
            )

    def generate_single(
        self,
        prompt: str,
        aspect_ratio: str | None = None,
        resolution: str | None = None,
    ) -> bytes | None:
        """Generate one image. Returns image bytes or None on failure.

        Args:
            prompt: Image description (style suffix is appended automatically)
            aspect_ratio: Override default aspect ratio for this image
            resolution: Override default resolution for this image
        """
        full_prompt = f"{prompt} {self.style_suffix}"
        ar = aspect_ratio or self.default_aspect_ratio
        res = resolution or self.default_resolution

        create_resp = requests.post(
            f"{self.API_BASE}/jobs/createTask",
            headers=self.headers,
            json={
                "model": self.MODEL,
                "input": {
                    "prompt": full_prompt,
                    "aspect_ratio": ar,
                    "resolution": res,
                },
            },
            timeout=30,
        )
        create_resp.raise_for_status()
        resp_data = create_resp.json()
        task_id = resp_data.get("taskId") or resp_data.get("data", {}).get("taskId")

        if not task_id:
            return None

        for _ in range(self.MAX_POLLS):
            time.sleep(self.POLL_INTERVAL)
            poll_resp = requests.get(
                f"{self.API_BASE}/jobs/recordInfo",
                params={"taskId": task_id},
                headers=self.headers,
                timeout=15,
            )
            poll_resp.raise_for_status()
            poll_data = poll_resp.json()

            state = poll_data.get("state") or poll_data.get("data", {}).get("state", "")
            if state == "failed":
                return None
            if state == "success":
                result_json = poll_data.get("resultJson") or poll_data.get("data", {}).get("resultJson", "")
                if isinstance(result_json, str):
                    result_json = json.loads(result_json)
                urls = result_json.get("resultUrls", [])
                if not urls:
                    return None
                img_resp = requests.get(urls[0], timeout=60)
                img_resp.raise_for_status()
                return img_resp.content

        return None

    def _get_file_extension(self, fmt: str | None) -> str:
        """Get file extension for format. Normalizes jpeg -> jpg."""
        fmt = fmt or self.default_format
        return "jpg" if fmt == "jpeg" else fmt

    def _convert_format(self, img_bytes: bytes, fmt: str) -> bytes:
        """Convert image bytes to target format if needed."""
        if fmt in ("png",):
            return img_bytes  # kie.ai returns PNG by default
        try:
            from PIL import Image
            from io import BytesIO
            img = Image.open(BytesIO(img_bytes))
            output = BytesIO()
            if fmt in ("jpg", "jpeg"):
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                img.save(output, format="JPEG", quality=90)
            elif fmt == "webp":
                img.save(output, format="WEBP", quality=90)
            else:
                return img_bytes
            return output.getvalue()
        except ImportError:
            print("  WARNING: Pillow not installed, saving as PNG instead")
            return img_bytes

    def _generate_with_id(
        self,
        prompt: str,
        img_id: str,
        aspect_ratio: str | None = None,
        resolution: str | None = None,
    ) -> tuple[str, bytes | None, str]:
        """Generate with ID tracking. Returns (id, bytes|None, status)."""
        try:
            result = self.generate_single(prompt, aspect_ratio, resolution)
            return (img_id, result, "success" if result else "generation failed")
        except Exception as e:
            return (img_id, None, str(e))

    def batch_generate(
        self,
        markers: list[dict],
        max_parallel: int = 3,
        output_dir: str | Path = "infographics",
        output_format: str | None = None,
    ) -> dict[int, bytes]:
        """Batch-generate images from extracted markers.

        Args:
            markers: List of dicts with keys: index, prompt, chapter, description
                     Optional keys: aspect_ratio, resolution
            max_parallel: Max concurrent API calls
            output_dir: Directory to save image files
            output_format: Override default format for this batch

        Returns:
            Dict mapping index -> image bytes
        """
        fmt = output_format or self.default_format
        ext = self._get_file_extension(fmt)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        total = len(markers)
        results = {}
        failed = []

        print(f"\nGenerating {total} infographics ({max_parallel} parallel workers)...")
        print(f"Format: {fmt.upper()} | Aspect: {self.default_aspect_ratio} | Resolution: {self.default_resolution}")
        print(f"Estimated cost: ~${total * 0.09:.2f}")
        print(f"Estimated time: ~{max(1, total * 20 // max_parallel // 60)} minutes\n")

        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            futures = {}
            for info in markers:
                idx = info["index"]
                img_file = output_path / f"infographic_{idx:03d}.{ext}"

                if img_file.exists():
                    print(f"  [{idx+1}/{total}] CACHED: {info.get('chapter', '')} -- {info.get('description', '')[:60]}...")
                    results[idx] = img_file.read_bytes()
                    continue

                ar = info.get("aspect_ratio")
                res = info.get("resolution")
                future = executor.submit(self._generate_with_id, info["prompt"], str(idx), ar, res)
                futures[future] = info

            for future in as_completed(futures):
                info = futures[future]
                idx = info["index"]
                _, img_bytes, status = future.result()

                if img_bytes:
                    if fmt != "png":
                        img_bytes = self._convert_format(img_bytes, fmt)
                    img_file = output_path / f"infographic_{idx:03d}.{ext}"
                    img_file.write_bytes(img_bytes)
                    results[idx] = img_bytes
                    print(f"  [{idx+1}/{total}] OK: {info.get('chapter', '')} -- {info.get('description', '')[:60]}...")
                else:
                    failed.append((idx, info, status))
                    print(f"  [{idx+1}/{total}] FAILED: {info.get('chapter', '')} -- {status}")

        print(f"\nResults: {len(results)} generated, {len(failed)} failed")
        if failed:
            print("Failed infographics:")
            for idx, info, status in failed:
                print(f"  #{idx}: {info.get('description', '')[:80]} -- {status}")

        return results

    def batch_generate_from_prompts(
        self,
        prompts: list[dict],
        max_parallel: int = 3,
        output_dir: str | Path = "infographics",
        output_format: str | None = None,
    ) -> dict[str, bytes]:
        """Batch-generate from pre-written prompt dicts.

        Args:
            prompts: List of dicts with keys: id, prompt
                     Optional keys: aspect_ratio, resolution, format
            max_parallel: Max concurrent API calls
            output_dir: Directory to save image files
            output_format: Override default format for this batch

        Returns:
            Dict mapping id -> image bytes
        """
        batch_fmt = output_format or self.default_format
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        total = len(prompts)
        results = {}
        failed = []

        print(f"\nGenerating {total} images ({max_parallel} parallel workers)...")
        print(f"Format: {batch_fmt.upper()} | Aspect: {self.default_aspect_ratio} | Resolution: {self.default_resolution}")
        print(f"Estimated cost: ~${total * 0.09:.2f}\n")

        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            futures = {}
            for item in prompts:
                img_id = item["id"]
                # Per-prompt format override
                item_fmt = item.get("format", batch_fmt)
                item_ext = self._get_file_extension(item_fmt)
                img_file = output_path / f"{img_id}.{item_ext}"

                if img_file.exists():
                    print(f"  CACHED: {img_id} -- {item['prompt'][:60]}...")
                    results[img_id] = img_file.read_bytes()
                    continue

                ar = item.get("aspect_ratio")
                res = item.get("resolution")
                future = executor.submit(self._generate_with_id, item["prompt"], img_id, ar, res)
                futures[future] = item

            done = 0
            for future in as_completed(futures):
                item = futures[future]
                img_id, img_bytes, status = future.result()
                done += 1

                if img_bytes:
                    item_fmt = item.get("format", batch_fmt)
                    item_ext = self._get_file_extension(item_fmt)
                    if item_fmt != "png":
                        img_bytes = self._convert_format(img_bytes, item_fmt)
                    img_file = output_path / f"{img_id}.{item_ext}"
                    img_file.write_bytes(img_bytes)
                    results[img_id] = img_bytes
                    print(f"  [{done}/{len(futures)}] OK: {img_id} -- {item['prompt'][:60]}...")
                else:
                    failed.append((img_id, status))
                    print(f"  [{done}/{len(futures)}] FAILED: {img_id} -- {status}")

        print(f"\nDone! Generated: {len(results)}, Failed: {len(failed)}")
        if failed:
            for fid, reason in failed:
                print(f"  FAILED: {fid} -- {reason}")

        return results


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    """CLI entry point for image generation."""
    parser = argparse.ArgumentParser(
        description="Generate AI images via kie.ai Nano Banana Pro",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from a JSON prompts file using the dark-gold website theme
  python image_generator.py --prompts prompts.json --theme dark-gold

  # Generate square JPGs for social media
  python image_generator.py --prompts prompts.json --aspect 1:1 --format jpg

  # Use a custom style suffix
  python image_generator.py --prompts prompts.json --style "Watercolor style, pastel colors"

  # High-res 4K images for print
  python image_generator.py --prompts prompts.json --resolution 4K --format png

  # List available themes
  python image_generator.py --list-themes

Prompts JSON format:
  [
    {"id": "hero_image", "prompt": "A friendly robot waving hello"},
    {"id": "step_1", "prompt": "Person downloading an app", "aspect_ratio": "1:1"},
    {"id": "banner", "prompt": "Workshop banner", "format": "jpg"}
  ]

  Each prompt can override: aspect_ratio, resolution, format
        """,
    )

    parser.add_argument("--prompts", type=str, help="Path to JSON file with prompts array")
    parser.add_argument("--output", type=str, default="generated-images", help="Output directory (default: generated-images)")
    parser.add_argument("--theme", type=str, choices=list(THEMES.keys()), help=f"Preset theme: {', '.join(THEMES.keys())}")
    parser.add_argument("--style", type=str, help="Custom style suffix (overrides --theme)")
    parser.add_argument("--aspect", type=str, choices=SUPPORTED_ASPECT_RATIOS, default=DEFAULT_ASPECT_RATIO, help=f"Aspect ratio (default: {DEFAULT_ASPECT_RATIO})")
    parser.add_argument("--format", type=str, choices=SUPPORTED_FORMATS, default=DEFAULT_FORMAT, help=f"Output format (default: {DEFAULT_FORMAT})")
    parser.add_argument("--resolution", type=str, choices=SUPPORTED_RESOLUTIONS, default=DEFAULT_RESOLUTION, help=f"Resolution (default: {DEFAULT_RESOLUTION})")
    parser.add_argument("--parallel", type=int, default=3, help="Max parallel workers (default: 3)")
    parser.add_argument("--list-themes", action="store_true", help="List all available themes and exit")

    args = parser.parse_args()

    # List themes
    if args.list_themes:
        print("\nAvailable themes:\n")
        for name, suffix in THEMES.items():
            print(f"  {name}:")
            print(f"    {suffix}\n")
        return

    # Validate
    if not args.prompts:
        parser.error("--prompts is required (use --list-themes to see themes)")

    # Load API key
    api_key = os.environ.get("KIE_API_KEY") or os.environ.get("KIE_AI_API_KEY")
    if not api_key:
        # Try .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.environ.get("KIE_API_KEY") or os.environ.get("KIE_AI_API_KEY")
        except ImportError:
            pass

    if not api_key:
        print("ERROR: Set KIE_API_KEY environment variable or add it to .env")
        print("  export KIE_API_KEY='Bearer your-key-here'")
        sys.exit(1)

    # Load prompts
    prompts_path = Path(args.prompts)
    if not prompts_path.exists():
        print(f"ERROR: Prompts file not found: {args.prompts}")
        sys.exit(1)

    with open(prompts_path) as f:
        prompts = json.load(f)

    if not isinstance(prompts, list):
        print("ERROR: Prompts file must contain a JSON array")
        sys.exit(1)

    print(f"\nLoaded {len(prompts)} prompts from {args.prompts}")
    print(f"Theme: {args.theme or 'default (book)'}")
    print(f"Output: {args.output}/")

    # Generate
    gen = ImageGenerator(
        api_key=api_key,
        theme=args.theme,
        style_suffix=args.style,
        aspect_ratio=args.aspect,
        resolution=args.resolution,
        output_format=args.format,
    )

    gen.batch_generate_from_prompts(
        prompts,
        max_parallel=args.parallel,
        output_dir=args.output,
        output_format=args.format,
    )


if __name__ == "__main__":
    main()
