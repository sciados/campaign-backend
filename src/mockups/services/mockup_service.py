# src/mockups/services/mockup_service.py
"""
Cloudflare R2-integrated Mockup Service
---------------------------------------
Handles:
- Uploading static mockup templates (shared across all campaigns)
- Generating new mockup images and saving to R2
- Returning public URLs for templates and generated mockups
"""

import io
import logging
from pathlib import Path
from uuid import UUID
from datetime import datetime
from PIL import Image

from src.core.config.storage_config import r2_client, BUCKET_NAME, R2_PUBLIC_URL

logger = logging.getLogger(__name__)

# Local path to template assets (checked on startup)
LOCAL_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Folder names in Cloudflare R2
R2_TEMPLATES_PREFIX = "templates/"
R2_MOCKUPS_PREFIX = "campaigns/{campaign_id}/mockups/"


class MockupsService:
    """Handles uploading templates and generating new mockups"""

    def __init__(self):
        self.templates = {
            "book_cover": LOCAL_TEMPLATES_DIR / "book_cover.png",
            "supplement_bottle": LOCAL_TEMPLATES_DIR / "supplement_bottle.png",
            "product_box": LOCAL_TEMPLATES_DIR / "product_box.png",
        }

    async def list_templates(self):
        """Return URLs of available templates in R2"""
        available_templates = []
        for name in self.templates.keys():
            key = f"{R2_TEMPLATES_PREFIX}{name}.png"
            url = f"{R2_PUBLIC_URL}/{key}"
            available_templates.append({"name": name, "url": url})
        return available_templates

    async def ensure_templates_uploaded(self):
        """Ensure that local templates exist in R2"""
        for name, path in self.templates.items():
            key = f"{R2_TEMPLATES_PREFIX}{name}.png"
            try:
                # Check if the template already exists
                r2_client.head_object(Bucket=BUCKET_NAME, Key=key)
                logger.info(f"✅ Template already exists in R2: {key}")
            except Exception:
                # Upload if not found
                if path.exists():
                    with open(path, "rb") as f:
                        r2_client.put_object(
                            Bucket=BUCKET_NAME,
                            Key=key,
                            Body=f,
                            ContentType="image/png",
                        )
                    logger.info(f"⬆️ Uploaded template to R2: {key}")
                else:
                    logger.warning(f"⚠️ Template not found locally: {path}")

    async def create_mockup(self, user_id: str, template_name: str, product_image_url: str):
        """Generate a mockup and save to R2"""
        try:
            campaign_id = user_id  # Using user_id as campaign owner for simplicity

            # 1️⃣ Load template from local or R2
            template_path = self.templates.get(template_name.lower())
            if not template_path or not template_path.exists():
                raise FileNotFoundError(f"Template '{template_name}' not found locally")

            template = Image.open(template_path).convert("RGBA")

            # 2️⃣ Load product image from URL (download to memory)
            import requests
            resp = requests.get(product_image_url)
            resp.raise_for_status()
            product = Image.open(io.BytesIO(resp.content)).convert("RGBA")

            # 3️⃣ Resize & composite
            product = product.resize((template.width // 2, template.height // 2))
            template.paste(product, (template.width // 4, template.height // 4), product)

            # 4️⃣ Save mockup to memory
            output_buffer = io.BytesIO()
            template.save(output_buffer, format="PNG")
            output_buffer.seek(0)

            # 5️⃣ Upload to Cloudflare R2
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            key = f"{R2_MOCKUPS_PREFIX.format(campaign_id=campaign_id)}{timestamp}_{template_name}_mockup.png"

            r2_client.put_object(
                Bucket=BUCKET_NAME,
                Key=key,
                Body=output_buffer,
                ContentType="image/png",
            )

            final_url = f"{R2_PUBLIC_URL}/{key}"
            logger.info(f"✅ Uploaded generated mockup: {final_url}")

            return {
                "success": True,
                "user_id": user_id,
                "template_name": template_name,
                "product_image_url": product_image_url,
                "final_image_url": final_url,
            }

        except Exception as e:
            logger.error(f"❌ Failed to generate mockup: {e}")
            return {"success": False, "error": str(e)}

    async def get_user_mockups(self, user_id: str):
        """List mockups created by a specific user"""
        prefix = R2_MOCKUPS_PREFIX.format(campaign_id=user_id)
        try:
            response = r2_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
            items = response.get("Contents", [])
            return [
                {
                    "key": obj["Key"],
                    "url": f"{R2_PUBLIC_URL}/{obj['Key']}",
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"].isoformat(),
                }
                for obj in items
            ]
        except Exception as e:
            logger.error(f"⚠️ Failed to list user mockups: {e}")
            return []
