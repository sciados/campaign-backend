# --- backend/src/mockups/services/mockup_service.py ---
from PIL import Image
import requests
from io import BytesIO
import os
import boto3
from botocore.client import Config


# Cloudflare R2 Configuration (example env vars)
R2_ENDPOINT = os.getenv('CLOUDFLARE_R2_ENDPOINT')
R2_KEY_ID = os.getenv('CLOUDFLARE_R2_KEY_ID')
R2_SECRET = os.getenv('CLOUDFLARE_R2_SECRET')
R2_BUCKET = os.getenv('CLOUDFLARE_R2_BUCKET')


s3_client = boto3.client('s3', endpoint_url=R2_ENDPOINT,
aws_access_key_id=R2_KEY_ID,
aws_secret_access_key=R2_SECRET,
config=Config(signature_version='s3v4'))


TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')


def generate_mockup(template_name: str, product_image_url: str) -> str:
    template_path = os.path.join(TEMPLATES_DIR, f"{template_name}.png")
    template_img = Image.open(template_path).convert("RGBA")


    response = requests.get(product_image_url)
    product_img = Image.open(BytesIO(response.content)).convert("RGBA")


    # Example size and position (customize per template)
    product_img = product_img.resize((400, 600))
    position = (50, 50)
    template_img.paste(product_img, position, product_img)


    output_filename = f"{template_name}_mockup.png"
    output_path = os.path.join('/tmp', output_filename)
    template_img.save(output_path)


    # Upload to Cloudflare R2
    s3_client.upload_file(output_path, R2_BUCKET, f"mockup-generated/{output_filename}")
    url = f"{R2_ENDPOINT}/{R2_BUCKET}/mockup-generated/{output_filename}"
    return url