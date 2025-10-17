# src/mockups/api/routes.py

from fastapi import APIRouter, HTTPException
from src.mockups.services.mockup_service import MockupsService

router = APIRouter(prefix="/mockups", tags=["mockups"])
service = MockupsService()


@router.get("/templates")
async def get_mockup_templates():
    return await service.list_templates()


@router.post("/")
async def create_mockup(data: dict):
    user_id = data.get("user_id")
    template_name = data.get("template_name")
    product_image_url = data.get("product_image_url")

    if not all([user_id, template_name, product_image_url]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    return await service.create_mockup(user_id, template_name, product_image_url)


@router.get("/user/{user_id}")
async def get_user_mockups(user_id: str):
    return await service.get_user_mockups(user_id)
