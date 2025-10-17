# app/api/routes/mockups.py
from fastapi import APIRouter, UploadFile, Form, HTTPException
from uuid import UUID
from src.mockups.services.mockup_service import generate_mockup
from src.mockups.schemas.mockup_schema import MockupGenerateResponse

router = APIRouter(prefix="/mockups", tags=["mockups"])

@router.post("/", response_model=MockupGenerateResponse)
async def create_mockup(
    user_id: UUID = Form(...),
    template_name: str = Form(...),
    product_image: UploadFile = Form(...),
):
    try:
        result = await generate_mockup(user_id, template_name, product_image)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
