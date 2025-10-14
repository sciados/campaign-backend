"""
Composite Image API Routes

Endpoints for creating composite images by combining:
- Background scenes (from AI generation or stock)
- Product mockups (from Dynamic Mockups)
- Text overlays (product names, CTAs)

Modular design: Consumes URLs from other services, doesn't modify them
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
from fastapi.responses import Response

from src.core.database.session import get_db
from src.core.auth.dependencies import get_current_user
from src.content.services.composite_image_service import (
    CompositeImageService,
    get_composite_service,
    ImageLayer,
    TextLayer,
    Position,
    Anchor,
    Stroke,
    Shadow,
    BlendMode,
    CompositeImageRequest,
)
from src.storage.services.r2_storage_service import get_r2_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/composite",
    tags=["composite-images"]
)


# ============================================================================
# Request/Response Models
# ============================================================================

class PositionRequest(BaseModel):
    """Position specification"""
    x: Optional[int] = None
    y: Optional[int] = None
    anchor: Optional[str] = Field(None, description="center, top_left, bottom_right, etc.")
    offset_x: int = 0
    offset_y: int = 0


class StrokeRequest(BaseModel):
    """Text stroke"""
    color: str = "#000000"
    width: int = 2


class ShadowRequest(BaseModel):
    """Text shadow"""
    color: str = "#000000"
    offset_x: int = 2
    offset_y: int = 2
    blur: int = 4


class ImageLayerRequest(BaseModel):
    """Foreground image layer"""
    image_url: str = Field(..., description="URL of image to layer (mockup, logo, etc.)")
    position: Optional[PositionRequest] = None
    scale: float = Field(1.0, ge=0.1, le=5.0)
    opacity: float = Field(1.0, ge=0.0, le=1.0)
    blend_mode: str = "normal"
    z_index: int = 1
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    maintain_aspect: bool = True


class TextLayerRequest(BaseModel):
    """Text overlay layer"""
    text: str = Field(..., description="Text to render")
    position: Optional[PositionRequest] = None
    font_family: str = "Arial"
    font_size: int = Field(48, ge=8, le=300)
    color: str = "#FFFFFF"
    alignment: str = "center"
    stroke: Optional[StrokeRequest] = None
    shadow: Optional[ShadowRequest] = None
    max_width: Optional[int] = None
    z_index: int = 100
    bold: bool = False
    italic: bool = False


class CreateCompositeRequest(BaseModel):
    """Request to create composite image"""
    campaign_id: str = Field(..., description="Campaign ID for organization")
    background_image_url: str = Field(..., description="Background scene URL")
    foreground_layers: List[ImageLayerRequest] = Field(default_factory=list, description="Product mockups, logos")
    text_layers: List[TextLayerRequest] = Field(default_factory=list, description="Product names, CTAs")
    output_width: Optional[int] = None
    output_height: Optional[int] = None
    output_format: str = "PNG"
    quality: int = Field(95, ge=1, le=100)
    save_to_r2: bool = Field(True, description="Upload result to R2 storage")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QuickCompositeRequest(BaseModel):
    """Quick composite: mockup + background + text"""
    campaign_id: str
    background_url: str = Field(..., description="AI-generated scene background")
    mockup_url: str = Field(..., description="Product mockup from Dynamic Mockups")
    product_name: Optional[str] = Field(None, description="Product name overlay")
    cta_text: Optional[str] = Field(None, description="Call-to-action text")
    mockup_position: str = Field("center", description="center, bottom_center, etc.")
    mockup_scale: float = Field(0.8, ge=0.1, le=2.0, description="Mockup size relative to canvas")


class CompositeResponse(BaseModel):
    """Response from composite creation"""
    success: bool
    composite_id: str
    image_url: Optional[str] = None
    r2_path: Optional[str] = None
    width: int = 0
    height: int = 0
    file_size: int = 0
    layers_count: int = 0
    generation_time: float = 0.0
    cost: float = Field(0.0, description="Processing cost")
    error: Optional[str] = None


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/create", response_model=CompositeResponse)
async def create_composite(
    request: CreateCompositeRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create composite image from multiple layers

    **Use Cases:**
    - Combine AI background + product mockup + text
    - Add logos and badges to generated images
    - Create social media posts with multiple elements

    **Workflow:**
    1. Generate background scene using AI image generator
    2. Generate product mockup using Dynamic Mockups
    3. Call this endpoint to combine them with text

    **Example:**
    ```json
    {
      "campaign_id": "abc-123",
      "background_image_url": "https://r2.com/gym-scene.jpg",
      "foreground_layers": [
        {
          "image_url": "https://r2.com/bottle-mockup.png",
          "position": {"anchor": "center"},
          "scale": 0.7
        }
      ],
      "text_layers": [
        {
          "text": "NEW PRODUCT",
          "position": {"anchor": "top_center", "offset_y": 50},
          "font_size": 72,
          "color": "#FFFFFF",
          "stroke": {"color": "#000000", "width": 3}
        }
      ]
    }
    ```
    """

    try:
        user_id = current_user.get("id", "unknown")
        logger.info(f"🎨 Composite request from user {user_id} for campaign {request.campaign_id}")

        # Convert request models to service models
        foreground_layers = []
        for layer_req in request.foreground_layers:
            position = None
            if layer_req.position:
                position = Position(
                    x=layer_req.position.x,
                    y=layer_req.position.y,
                    anchor=Anchor(layer_req.position.anchor) if layer_req.position.anchor else None,
                    offset_x=layer_req.position.offset_x,
                    offset_y=layer_req.position.offset_y
                )

            foreground_layers.append(ImageLayer(
                image_url=layer_req.image_url,
                position=position or Position(anchor=Anchor.CENTER),
                scale=layer_req.scale,
                opacity=layer_req.opacity,
                blend_mode=BlendMode(layer_req.blend_mode),
                z_index=layer_req.z_index,
                max_width=layer_req.max_width,
                max_height=layer_req.max_height,
                maintain_aspect=layer_req.maintain_aspect
            ))

        text_layers = []
        for text_req in request.text_layers:
            position = None
            if text_req.position:
                position = Position(
                    x=text_req.position.x,
                    y=text_req.position.y,
                    anchor=Anchor(text_req.position.anchor) if text_req.position.anchor else None,
                    offset_x=text_req.position.offset_x,
                    offset_y=text_req.position.offset_y
                )

            stroke = None
            if text_req.stroke:
                stroke = Stroke(
                    color=text_req.stroke.color,
                    width=text_req.stroke.width
                )

            shadow = None
            if text_req.shadow:
                shadow = Shadow(
                    color=text_req.shadow.color,
                    offset_x=text_req.shadow.offset_x,
                    offset_y=text_req.shadow.offset_y,
                    blur=text_req.shadow.blur
                )

            text_layers.append(TextLayer(
                text=text_req.text,
                position=position or Position(anchor=Anchor.TOP_CENTER, offset_y=50),
                font_family=text_req.font_family,
                font_size=text_req.font_size,
                color=text_req.color,
                alignment=text_req.alignment,
                stroke=stroke,
                shadow=shadow,
                max_width=text_req.max_width,
                z_index=text_req.z_index,
                bold=text_req.bold,
                italic=text_req.italic
            ))

        # Create composite request
        composite_request = CompositeImageRequest(
            background_image_url=request.background_image_url,
            foreground_layers=foreground_layers,
            text_layers=text_layers,
            output_width=request.output_width,
            output_height=request.output_height,
            output_format=request.output_format,
            quality=request.quality,
            metadata={
                **request.metadata,
                "campaign_id": request.campaign_id,
                "user_id": user_id
            }
        )

        # Generate composite
        compositor = get_composite_service()
        result = await compositor.create_composite(composite_request)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error or "Composite creation failed"
            )

        # Upload to R2 if requested
        image_url = None
        r2_path = None

        if request.save_to_r2 and result.image_data:
            r2_service = get_r2_service()
            r2_key = f"composites/{request.campaign_id}/{result.composite_id}.{request.output_format.lower()}"

            upload_result = await r2_service.upload_file(
                file_data=result.image_data,
                key=r2_key,
                content_type=f"image/{request.output_format.lower()}"
            )

            if upload_result.get("success"):
                image_url = upload_result.get("url")
                r2_path = r2_key
                logger.info(f"✅ Composite uploaded to R2: {r2_path}")

        # Calculate cost (composite processing fee)
        cost = 0.02  # $0.02 per composite

        return CompositeResponse(
            success=True,
            composite_id=result.composite_id,
            image_url=image_url,
            r2_path=r2_path,
            width=result.width,
            height=result.height,
            file_size=result.file_size,
            layers_count=result.layers_count,
            generation_time=result.generation_time,
            cost=cost
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Composite creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Composite creation failed: {str(e)}"
        )


@router.post("/quick", response_model=CompositeResponse)
async def create_quick_composite(
    request: QuickCompositeRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Quick composite: Background + Mockup + Text

    Simplified endpoint for common use case:
    - AI-generated background scene
    - Product mockup from Dynamic Mockups
    - Optional product name and CTA

    **Example:**
    ```json
    {
      "campaign_id": "abc-123",
      "background_url": "https://r2.com/gym-scene.jpg",
      "mockup_url": "https://r2.com/bottle-mockup.png",
      "product_name": "PRO FUEL",
      "cta_text": "Buy Now",
      "mockup_position": "center",
      "mockup_scale": 0.8
    }
    ```
    """

    # Build full request from quick parameters
    foreground_layers = [
        ImageLayerRequest(
            image_url=request.mockup_url,
            position=PositionRequest(anchor=request.mockup_position),
            scale=request.mockup_scale,
            z_index=1
        )
    ]

    text_layers = []

    if request.product_name:
        text_layers.append(TextLayerRequest(
            text=request.product_name,
            position=PositionRequest(anchor="top_center", offset_y=50),
            font_size=72,
            color="#FFFFFF",
            bold=True,
            stroke=StrokeRequest(color="#000000", width=4),
            z_index=100
        ))

    if request.cta_text:
        text_layers.append(TextLayerRequest(
            text=request.cta_text,
            position=PositionRequest(anchor="bottom_center", offset_y=-80),
            font_size=48,
            color="#FFD700",
            bold=True,
            stroke=StrokeRequest(color="#000000", width=3),
            z_index=101
        ))

    full_request = CreateCompositeRequest(
        campaign_id=request.campaign_id,
        background_image_url=request.background_url,
        foreground_layers=foreground_layers,
        text_layers=text_layers,
        save_to_r2=True,
        metadata={
            "quick_composite": True,
            "mockup_url": request.mockup_url,
            "product_name": request.product_name,
            "cta_text": request.cta_text
        }
    )

    return await create_composite(full_request, current_user, db)


@router.get("/preview")
async def preview_composite(
    background_url: str,
    mockup_url: str,
    product_name: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Preview composite without saving

    Returns image directly as response for quick preview
    """

    try:
        # Build quick composite request
        foreground_layers = [
            ImageLayer(
                image_url=mockup_url,
                position=Position(anchor=Anchor.CENTER),
                scale=0.8,
                z_index=1
            )
        ]

        text_layers = []
        if product_name:
            text_layers.append(TextLayer(
                text=product_name,
                position=Position(anchor=Anchor.TOP_CENTER, offset_y=50),
                font_size=72,
                color="#FFFFFF",
                bold=True,
                stroke=Stroke(color="#000000", width=4),
                z_index=100
            ))

        composite_request = CompositeImageRequest(
            background_image_url=background_url,
            foreground_layers=foreground_layers,
            text_layers=text_layers,
            output_format="PNG"
        )

        # Generate composite
        compositor = get_composite_service()
        result = await compositor.create_composite(composite_request)

        if not result.success or not result.image_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Preview generation failed"
            )

        return Response(
            content=result.image_data,
            media_type="image/png"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Preview generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
