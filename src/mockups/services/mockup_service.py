import os
import requests
from io import BytesIO
from uuid import UUID
from PIL import Image
import boto3


class MockupsService:
    """Generates mockups and stores them in Cloudflare R2."""

    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=os.getenv("R2_ENDPOINT_URL"),
            aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
        )
        self.bucket_name = os.getenv("R2_BUCKET_NAME", "mockups")
        self.cdn_base_url = os.getenv("R2_CDN_BASE_URL", "https://cdn.rodgersdigital.com/mockups")

        # Templates hosted in R2
        self.template_map = {
            "book_cover": f"{self.cdn_base_url}/templates/book_cover.png",
            "supplement_bottle": f"{self.cdn_base_url}/templates/supplement_bottle.png",
            "product_box": f"{self.cdn_base_url}/templates/product_box.png",
        }

    async def list_templates(self):
        """Return the available mockup templates"""
        return [{"name": name, "url": url} for name, url in self.template_map.items()]

    async def create_mockup(self, user_id: str, template_name: str, product_image_url: str):
        """Create a composite mockup and upload to Cloudflare R2"""
        template_url = self.template_map.get(template_name.lower())
        if not template_url:
            raise ValueError(f"Template '{template_name}' not found")

        try:
            # Download both images from their URLs
            template_img = Image.open(BytesIO(requests.get(template_url).content)).convert("RGBA")
            product_img = Image.open(BytesIO(requests.get(product_image_url).content)).convert("RGBA")

            # Resize and overlay the product onto the template
            product_img = product_img.resize((template_img.width // 2, template_img.height // 2))
            template_img.paste(product_img, (template_img.width // 4, template_img.height // 4), product_img)

            # Save composite to memory
            buffer = BytesIO()
            template_img.save(buffer, format="PNG")
            buffer.seek(0)

            filename = f"generated/{user_id}_{template_name}_mockup.png"

            # Upload to Cloudflare R2
            self.s3.upload_fileobj(
                buffer,
                self.bucket_name,
                filename,
                ExtraArgs={"ContentType": "image/png", "ACL": "public-read"},
            )

            # Return final public URL
            final_url = f"{self.cdn_base_url}/{filename}"

            return {
                "user_id": user_id,
                "template_name": template_name,
                "product_image_url": product_image_url,
                "final_image_url": final_url,
            }

        except Exception as e:
            raise Exception(f"❌ Mockup generation failed: {e}")
