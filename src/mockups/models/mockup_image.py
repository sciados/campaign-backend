# --- backend/src/mockups/models/mockup_image.py ---
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base


class MockupImage(Base):
    __tablename__ = "mockup_images"


id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
template_name = Column(String, nullable=False)
product_image_url = Column(String, nullable=False)
final_image_url = Column(String, nullable=True)
created_at = Column(DateTime(timezone=True), server_default=func.now())


# --- backend/src/mockups/schemas/mockup_schema.py ---
from pydantic import BaseModel, UUID4


class MockupCreate(BaseModel):
    user_id: UUID4
    template_name: str
    product_image_url: str


class MockupResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    template_name: str
    product_image_url: str
    final_image_url: str