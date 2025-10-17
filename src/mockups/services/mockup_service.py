# src/mockups/services/mockup_service.py
import os
from pathlib import Path
from uuid import UUID
from fastapi import UploadFile
from PIL import Image

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

TEMPLATE_MAP = {
    "book_cover": TEMPLATES_DIR / "book_cover.png",
    "supplement_bottle": TEMPLATES_DIR / "supplement_bottle.png",
    "product_box": TEMPLATES_DIR / "product_box.png",
}

async def generate_mockup(user_id: UUID, template_name: str, product_image: UploadFile):
    template_path = TEMPLATE_MAP.get(template_name.lower())
    if not template_path or not template_path.exists():
        raise FileNotFoundError(f"Template '{template_name}' not found")

    # Load template
    template = Image.open(template_path).convert("RGBA")
    product = Image.open(product_image.file).convert("RGBA")

    # Resize product to fit template (example: fit inside template)
    product = product.resize((template.width // 2, template.height // 2))

    # Composite product onto template
    template.paste(product, (template.width // 4, template.height // 4), product)

    # Save result to a temporary file
    output_path = TEMPLATES_DIR / f"{user_id}_{template_name}_mockup.png"
    template.save(output_path)

    return {"mockup_url": f"/static/mockups/{output_path.name}"}
