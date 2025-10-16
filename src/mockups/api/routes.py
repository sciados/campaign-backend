# --- backend/src/mockups/api/routes.py ---
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_db
from services.mockup_service import generate_mockup
from models.mockup_image import MockupImage
from schemas.mockup_schema import MockupCreate, MockupResponse
from typing import List
from uuid import UUID
import os

# Cloudflare R2 config
R2_ENDPOINT = os.getenv('CLOUDFLARE_R2_ENDPOINT')
R2_BUCKET = os.getenv('CLOUDFLARE_R2_BUCKET')

router = APIRouter()

# --- Create Mockup ---
@router.post("/mockups/", response_model=MockupResponse)
def create_mockup(mockup: MockupCreate, db: Session = get_db):
    try:
        final_image_url = generate_mockup(mockup.template_name, mockup.product_image_url)
        record = MockupImage(
            user_id=mockup.user_id,
            template_name=mockup.template_name,
            product_image_url=mockup.product_image_url,
            final_image_url=final_image_url
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- List Templates ---
@router.get("/mockups/templates")
def list_templates():
    templates = ["blank_book", "blank_bottle", "blank_box"]
    result = [
        {
            "name": t,
            "url": f"{R2_ENDPOINT}/{R2_BUCKET}/mockup-templates/{t}.png"
        }
        for t in templates
    ]
    return result

# --- List User's Mockups ---
@router.get("/mockups/user/{user_id}", response_model=List[MockupResponse])
def get_user_mockups(user_id: UUID, db: Session = get_db):
    records = db.query(MockupImage).filter(MockupImage.user_id == user_id).all()
    return records
