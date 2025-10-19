# src/mockups/services/mockup_service.py

import io
import boto3
import logging
import requests
from uuid import UUID
from pathlib import Path
from PIL import Image
from botocore.exceptions import ClientError

from src.core.config.storage_config import storage_config

logger = logging.getLogger(__name__)

# Local templates directory
LOCAL_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


class MockupService:
    """
    Handles generation and storage of product mockup images.

    Templates live in Cloudflare R2 under /templates/
    Generated mockups are stored under /mockups/{user_id}/
    """

    def __init__(self):
        self.bucket_name = storage_config.cloudflare_r2.bucket_name
        self.r2 = boto3.client("s3", **storage_config.cloudflare_r2.boto3_config)
        self.public_url = storage_config.cloudflare_r2.public_url
        self.templates_dir = LOCAL_TEMPLATES_DIR

    # -------------------------------------------------------------------------
    # Ensure templates are uploaded to Cloudflare R2
    # -------------------------------------------------------------------------
    async def ensure_templates_uploaded(self):
        """
        Ensure that the three default templates exist in the R2 bucket.
        Upload them from /src/mockups/templates if missing.
        """
        template_files = {
            "book_cover": "book_cover.png",
            "supplement_bottle": "supplement_bottle.png",
            "product_box": "product_box.png",
        }

        for key, filename in template_files.items():
            local_path = self.templates_dir / filename
            remote_key = f"templates/{filename}"

            if not local_path.exists():
                logger.warning(f"⚠️ Local template not found: {local_path}")
                continue

            try:
                self.r2.head_object(Bucket=self.bucket_name, Key=remote_key)
                logger.info(f"✅ Template already exists in R2: {remote_key}")
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    logger.info(f"📤 Uploading missing template: {remote_key}")
                    with open(local_path, "rb") as f:
                        self.r2.upload_fileobj(f, self.bucket_name, remote_key)
                else:
                    logger.error(f"❌ Error checking/uploading {remote_key}: {e}")

        logger.info("📦 Template sync to R2 complete.")

    # -------------------------------------------------------------------------
    # List available templates
    # -------------------------------------------------------------------------
    async def list_templates(self):
        """List available templates from Cloudflare R2."""
        templates = []
        try:
            response = self.r2.list_objects_v2(
                Bucket=self.bucket_name, Prefix="templates/"
            )
            for obj in response.get("Contents", []):
                if obj["Key"].endswith(".png"):
                    templates.append({
                        "name": Path(obj["Key"]).stem,
                        "url": f"{self.public_url}/{obj['Key']}"
                    })
        except Exception as e:
            logger.error(f"⚠️ Failed to list templates: {e}")
        return templates

    # -------------------------------------------------------------------------
    # Generate and upload a new mockup
    # -------------------------------------------------------------------------
    async def create_mockup(self, user_id: str, template_name: str, product_image_url: str):
        """Generate a mockup image and store it in Cloudflare R2."""
        try:
            template_key = f"templates/{template_name}.png"
            local_template_path = self.templates_dir / f"{template_name}.png"

            # Ensure local template exists (for compositing)
            if not local_template_path.exists():
                logger.info(f"⬇️ Downloading template from R2: {template_key}")
                with open(local_template_path, "wb") as f:
                    obj = self.r2.get_object(Bucket=self.bucket_name, Key=template_key)
                    f.write(obj["Body"].read())

            # Load template
            template = Image.open(local_template_path).convert("RGBA")

            # Fetch product image
            response = requests.get(product_image_url)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch product image: {product_image_url}")
            product = Image.open(io.BytesIO(response.content)).convert("RGBA")

            # Composite product onto template
            product = product.resize((template.width // 2, template.height // 2))
            template.paste(product, (template.width // 4, template.height // 4), product)

            # Save to buffer
            buffer = io.BytesIO()
            template.save(buffer, format="PNG")
            buffer.seek(0)

            # Upload to R2
            output_key = f"mockups/{user_id}/{template_name}_mockup.png"
            self.r2.upload_fileobj(buffer, self.bucket_name, output_key, ExtraArgs={"ContentType": "image/png"})

            logger.info(f"✅ Uploaded mockup to R2: {output_key}")

            return {
                "user_id": user_id,
                "template_name": template_name,
                "final_image_url": f"{self.public_url}/{output_key}"
            }

        except Exception as e:
            logger.error(f"❌ Mockup generation failed: {e}")
            raise

    # -------------------------------------------------------------------------
    # List all mockups for a user
    # -------------------------------------------------------------------------
    async def get_user_mockups(self, user_id: str):
        """List all mockups for a user from Cloudflare R2."""
        try:
            response = self.r2.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"mockups/{user_id}/"
            )
            contents = response.get("Contents", [])
            return [
                {
                    "key": obj["Key"],
                    "url": f"{self.public_url}/{obj['Key']}",
                    "size": obj.get("Size"),
                }
                for obj in contents
            ]
        except Exception as e:
            logger.error(f"❌ Failed to fetch user mockups: {e}")
            return []
