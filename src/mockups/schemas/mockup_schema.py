from pydantic import BaseModel

class PresignUploadResponse(BaseModel):
    uploadUrl: str
    publicUrl: str

class MockupGenerateResponse(BaseModel):
    success: bool
    image_url: str
