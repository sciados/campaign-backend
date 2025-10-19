# src/mockups/services/mockup_service.py

import io
from uuid import UUID
from PIL import Image
from pathlib import Path
import logging

from src.core.config.storage_config import r2_client, BUCKET_NAME, R2_PUBLIC_URL

logger = logging.getLogger(__name__)

# Local templates folder inside repository
LOCAL_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Cloudflare R2 structure:
# campaignforge-storage/templates/
# campaignforge-storage/mockups/{user_id}/

TEMPLATE_MAP = {
    "book_cover": LOCAL_TEMPLATES_DIR / "book_cover.png",
    "supplement_bottle": LOCAL_TEMPLATES_DIR / "supplement_bottle.png",
    "product_box": LOCAL_TEMPLATES_DIR / "product_box.png",
}


class MockupsService:
    """
    Handles generation and storage of product mockup images.
    Templates live in Cloudflare R2 under /templates/
    Generated mockups are stored per user under /mockups/{user_id}/
    """

    async def list_templates(self):
        """List available templates from Cloudflare R2."""
        templates = []
        try:
            for key, path in TEMPLATE_MAP.items():
                templates.append({
                    "name": key,
                    "url": f"{R2_PUBLIC_URL}/templates/{path.name}"
                })
        except Exception as e:
            logger.error(f"⚠️ Failed to list templates: {e}")
        return templates

    async def create_mockup(self, user_id: str, template_name: str, product_image_url: str):
        """Generate a mockup image and store it in Cloudflare R2."""

        if template_name not in TEMPLATE_MAP:
            raise ValueError(f"Unknown template: {template_name}")

        template_path = TEMPLATE_MAP[template_name]

        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found locally: {template_path}")

        # Open template and overlay product image (download product image)
        from io import BytesIO
        import requests

        response = requests.get(product_image_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch product image from {product_image_url}")

        product_image = Image.open(BytesIO(response.content)).convert("RGBA")
        template = Image.open(template_path).convert("RGBA")

        # Resize product and composite onto template
        product_image = product_image.resize((template.width // 2, template.height // 2))
        template.paste(product_image, (template.width // 4, template.height // 4), product_image)

        # Save composite image to memory
        output_buffer = io.BytesIO()
        template.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        # Upload to Cloudflare R2
        output_filename = f"{user_id}_{template_name}_mockup.png"
        mockup_key = f"mockups/{user_id}/{output_filename}"

        try:
            r2_client.put_object(
                Bucket=BUCKET_NAME,
                Key=mockup_key,
                Body=output_buffer,
                ContentType="image/png"
            )
            logger.info(f"✅ Uploaded mockup to Cloudflare R2: {mockup_key}")
        except Exception as e:
            logger.error(f"❌ Failed to upload mockup: {e}")
            raise

        return {
            "user_id": user_id,
            "template_name": template_name,
            "final_image_url": f"{R2_PUBLIC_URL}/{mockup_key}"
        }

    async def get_user_mockups(self, user_id: str):
        """List all mockups for a user from Cloudflare R2."""
        try:
            response = r2_client.list_objects_v2(
                Bucket=BUCKET_NAME,
                Prefix=f"mockups/{user_id}/"
            )
            contents = response.get("Contents", [])
            return [
                {
                    "key": obj["Key"],
                    "url": f"{R2_PUBLIC_URL}/{obj['Key']}",
                    "size": obj.get("Size"),
                }
                for obj in contents
            ]
        except Exception as e:
            logger.error(f"❌ Failed to fetch user mockups: {e}")
            return []
