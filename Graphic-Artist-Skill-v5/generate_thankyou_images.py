"""
Generate images for the Workshop Thank You page sections.
Uses kie.ai Nano Banana Pro via the book-image-toolkit.
"""

import os
from dotenv import load_dotenv
from image_generator import ImageGenerator

load_dotenv()

api_key = os.getenv("KIE_API_KEY")
if not api_key:
    raise ValueError("KIE_API_KEY not found in .env")

gen = ImageGenerator(api_key=api_key)

prompts = [
    {
        "id": "thankyou_survey",
        "prompt": (
            "A friendly cartoon person filling out a short checklist survey on a clipboard. "
            "Gold checkmarks appear next to completed items. A speech bubble says 'Almost done!' "
            "Simple, warm, encouraging feeling."
        ),
    },
    {
        "id": "thankyou_wispr",
        "prompt": (
            "A cartoon person speaking into a microphone icon, with golden sound waves flowing "
            "from their mouth into a glowing computer screen where text appears magically. "
            "The concept is: voice to text, no keyboard needed. Futuristic but simple."
        ),
    },
    {
        "id": "thankyou_vscode",
        "prompt": (
            "A cartoon laptop computer showing the VS Code editor icon (blue square with code brackets). "
            "A large friendly download arrow points down into the laptop. "
            "Simple setup concept — one click install. Encouraging and easy."
        ),
    },
    {
        "id": "thankyou_ready",
        "prompt": (
            "A cartoon person at a desk with a laptop, headphones on, coffee cup, ready to learn. "
            "A golden rocket ship launching from the screen symbolizing being ready to go. "
            "Excitement and preparation for a workshop."
        ),
    },
]

output_dir = "simpletechskills-site/workshop/thank-you-7x9k2m/images"

print("Generating thank you page images...")
results = gen.batch_generate_from_prompts(prompts, max_parallel=3, output_dir=output_dir)
print(f"\nDone! Images saved to {output_dir}/")
