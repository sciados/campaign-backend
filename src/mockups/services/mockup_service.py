# src/mockups/services/mockup_service.py
import os
from pathlib import Path
from uuid import UUID
from PIL import Image

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

TEMPLATE_MAP = {
    "book_cover": TEMPLATES_DIR / "book_cover.png",
    "supplement_bottle": TEMPLATES_DIR / "supplement_bottle.png",
    "product_box": TEMPLATES_DIR / "product_box.png",
}

MOCKUP_OUTPUT_DIR = Path(__file__).parent.parent / "generated"
MOCKUP_OUTPUT_DIR.mkdir(exist_ok=True)


class MockupsService:
    """Handles all mockup-related operations"""

    async def list_templates(self):
        """Return available mockup templates"""
        templates = []
        for name, path in TEMPLATE_MAP.items():
            templates.append({
                "name": name,
                "url": f"/static/mockups/{path.name}"
            })
        return templates

    async def create_mockup(self, user_id: str, template_name: str, product_image_url: str):
        """Simulate creating a mockup from a product image URL"""
        template_path = TEMPLATE_MAP.get(template_name.lower())
        if not template_path or not template_path.exists():
            raise FileNotFoundError(f"Template '{template_name}' not found")

        try:
            # Load template
            template = Image.open(template_path).convert("RGBA")

            # In production, you’d download product_image_url, here we just reuse the template
            product = template.copy()

            # Overlay (placeholder logic)
            template.paste(product, (template.width // 4, template.height // 4), product)

            output_path = MOCKUP_OUTPUT_DIR / f"{user_id}_{template_name}_mockup.png"
            template.save(output_path)

            return {
                "id": str(UUID(user_id)),
                "user_id": user_id,
                "template_name": template_name,
                "product_image_url": product_image_url,
                "final_image_url": f"/static/mockups/{output_path.name}",
            }

        except Exception as e:
            raise Exception(f"Mockup generation failed: {e}")

    async def get_user_mockups(self, user_id: str):
        """List all generated mockups for a user"""
        mockups = []
        for file in MOCKUP_OUTPUT_DIR.glob(f"{user_id}_*_mockup.png"):
            template_name = file.stem.replace(f"{user_id}_", "").replace("_mockup", "")
            mockups.append({
                "id": str(UUID(user_id)),
                "user_id": user_id,
                "template_name": template_name,
                "product_image_url": "",
                "final_image_url": f"/static/mockups/{file.name}",
                "created_at": file.stat().st_mtime,
            })
        return mockups
