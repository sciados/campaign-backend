"""
Composite Image Service - Modular Image Composition System

Combines multiple image layers (backgrounds, mockups, logos) with text overlays
into a single composite image without modifying existing generation systems.

Architecture: Consumes URLs from other modules, produces composite images
Isolation: No dependencies on image_generator, mockup_service, or variations
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import aiohttp
import asyncio
import io
import logging
from datetime import datetime
import uuid
from enum import Enum

logger = logging.getLogger(__name__)


class BlendMode(str, Enum):
    """Image blending modes"""
    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"


class Anchor(str, Enum):
    """Position anchors for smart positioning"""
    CENTER = "center"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    TOP_CENTER = "top_center"
    BOTTOM_CENTER = "bottom_center"
    CENTER_LEFT = "center_left"
    CENTER_RIGHT = "center_right"


@dataclass
class Position:
    """Position specification - can be absolute or relative"""
    x: Optional[int] = None
    y: Optional[int] = None
    anchor: Optional[Anchor] = None
    offset_x: int = 0
    offset_y: int = 0


@dataclass
class Stroke:
    """Text stroke/outline"""
    color: str = "#000000"
    width: int = 2


@dataclass
class Shadow:
    """Text shadow effect"""
    color: str = "#000000"
    offset_x: int = 2
    offset_y: int = 2
    blur: int = 4


@dataclass
class ImageLayer:
    """Foreground image layer (mockup, logo, badge, etc.)"""
    image_url: str
    position: Position = field(default_factory=lambda: Position(anchor=Anchor.CENTER))
    scale: float = 1.0
    opacity: float = 1.0
    blend_mode: BlendMode = BlendMode.NORMAL
    z_index: int = 1
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    maintain_aspect: bool = True


@dataclass
class TextLayer:
    """Text overlay layer"""
    text: str
    position: Position = field(default_factory=lambda: Position(anchor=Anchor.TOP_CENTER, offset_y=50))
    font_family: str = "Arial"
    font_size: int = 48
    color: str = "#FFFFFF"
    alignment: str = "center"  # left, center, right
    stroke: Optional[Stroke] = None
    shadow: Optional[Shadow] = None
    max_width: Optional[int] = None
    z_index: int = 100
    bold: bool = False
    italic: bool = False


@dataclass
class CompositeImageRequest:
    """Request to create composite image"""
    background_image_url: str
    foreground_layers: List[ImageLayer] = field(default_factory=list)
    text_layers: List[TextLayer] = field(default_factory=list)
    output_width: Optional[int] = None
    output_height: Optional[int] = None
    output_format: str = "PNG"
    quality: int = 95
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompositeImageResponse:
    """Response from composite creation"""
    success: bool
    composite_id: str
    image_data: Optional[bytes] = None
    width: int = 0
    height: int = 0
    file_size: int = 0
    layers_count: int = 0
    generation_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CompositeImageService:
    """
    Modular image composition service

    Responsibilities:
    - Fetch images from URLs (from any source)
    - Compose layers with positioning and effects
    - Render text overlays
    - Export final composite

    Does NOT:
    - Generate new AI images (use image_generator)
    - Create mockups (use dynamic_mockups_service)
    - Modify existing services
    """

    def __init__(self):
        self.default_font = "Arial"
        self.font_cache: Dict[str, ImageFont.FreeTypeFont] = {}

    async def create_composite(
        self,
        request: CompositeImageRequest
    ) -> CompositeImageResponse:
        """
        Create composite image from multiple layers

        Process:
        1. Download background image
        2. Download and position foreground layers
        3. Render text layers
        4. Compose all layers by z-index
        5. Export final image
        """

        start_time = datetime.now()
        composite_id = str(uuid.uuid4())

        try:
            logger.info(f"🎨 Creating composite image {composite_id}")
            logger.info(f"  Background: {request.background_image_url}")
            logger.info(f"  Foreground layers: {len(request.foreground_layers)}")
            logger.info(f"  Text layers: {len(request.text_layers)}")

            # Step 1: Download and prepare background
            background = await self._download_image(request.background_image_url)
            if not background:
                return CompositeImageResponse(
                    success=False,
                    composite_id=composite_id,
                    error="Failed to download background image"
                )

            # Resize background if dimensions specified
            if request.output_width or request.output_height:
                background = self._resize_image(
                    background,
                    request.output_width,
                    request.output_height
                )

            canvas_width, canvas_height = background.size
            logger.info(f"  Canvas size: {canvas_width}x{canvas_height}")

            # Step 2: Collect all layers (foreground + text) and sort by z-index
            all_layers = []

            # Add foreground image layers
            for fg_layer in request.foreground_layers:
                all_layers.append(("image", fg_layer))

            # Add text layers
            for text_layer in request.text_layers:
                all_layers.append(("text", text_layer))

            # Sort by z-index
            all_layers.sort(key=lambda x: x[1].z_index)

            # Step 3: Compose layers onto background
            canvas = background.convert("RGBA")

            for layer_type, layer in all_layers:
                if layer_type == "image":
                    canvas = await self._apply_image_layer(
                        canvas,
                        layer,
                        canvas_width,
                        canvas_height
                    )
                elif layer_type == "text":
                    canvas = self._apply_text_layer(
                        canvas,
                        layer,
                        canvas_width,
                        canvas_height
                    )

            # Step 4: Convert to output format and export
            output_buffer = io.BytesIO()

            if request.output_format.upper() == "PNG":
                canvas.save(output_buffer, format="PNG", optimize=True)
            elif request.output_format.upper() in ["JPG", "JPEG"]:
                # Convert RGBA to RGB for JPEG
                rgb_canvas = Image.new("RGB", canvas.size, (255, 255, 255))
                rgb_canvas.paste(canvas, mask=canvas.split()[3])  # Use alpha as mask
                rgb_canvas.save(
                    output_buffer,
                    format="JPEG",
                    quality=request.quality,
                    optimize=True
                )
            else:
                canvas.save(output_buffer, format=request.output_format)

            image_data = output_buffer.getvalue()
            generation_time = (datetime.now() - start_time).total_seconds()

            logger.info(f"✅ Composite {composite_id} created in {generation_time:.2f}s")
            logger.info(f"  Output size: {len(image_data)} bytes")

            return CompositeImageResponse(
                success=True,
                composite_id=composite_id,
                image_data=image_data,
                width=canvas.width,
                height=canvas.height,
                file_size=len(image_data),
                layers_count=len(all_layers),
                generation_time=generation_time,
                metadata={
                    **request.metadata,
                    "background_source": request.background_image_url,
                    "foreground_count": len(request.foreground_layers),
                    "text_count": len(request.text_layers)
                }
            )

        except Exception as e:
            logger.error(f"❌ Composite creation failed: {e}")
            return CompositeImageResponse(
                success=False,
                composite_id=composite_id,
                error=str(e)
            )

    async def _download_image(self, url: str) -> Optional[Image.Image]:
        """Download image from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to download image: {response.status}")
                        return None

                    image_data = await response.read()
                    return Image.open(io.BytesIO(image_data))
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {e}")
            return None

    def _resize_image(
        self,
        image: Image.Image,
        target_width: Optional[int],
        target_height: Optional[int],
        maintain_aspect: bool = True
    ) -> Image.Image:
        """Resize image to target dimensions"""
        if not target_width and not target_height:
            return image

        current_width, current_height = image.size

        if maintain_aspect:
            # Calculate aspect ratio
            aspect = current_width / current_height

            if target_width and target_height:
                # Fit within box
                if current_width / target_width > current_height / target_height:
                    new_width = target_width
                    new_height = int(target_width / aspect)
                else:
                    new_height = target_height
                    new_width = int(target_height * aspect)
            elif target_width:
                new_width = target_width
                new_height = int(target_width / aspect)
            else:
                new_height = target_height
                new_width = int(target_height * aspect)
        else:
            new_width = target_width or current_width
            new_height = target_height or current_height

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def _calculate_position(
        self,
        position: Position,
        layer_width: int,
        layer_height: int,
        canvas_width: int,
        canvas_height: int
    ) -> Tuple[int, int]:
        """Calculate absolute x,y from position specification"""

        # If absolute position provided
        if position.x is not None and position.y is not None:
            return (position.x + position.offset_x, position.y + position.offset_y)

        # Use anchor-based positioning
        anchor = position.anchor or Anchor.CENTER

        anchor_positions = {
            Anchor.CENTER: (
                (canvas_width - layer_width) // 2,
                (canvas_height - layer_height) // 2
            ),
            Anchor.TOP_LEFT: (0, 0),
            Anchor.TOP_RIGHT: (canvas_width - layer_width, 0),
            Anchor.BOTTOM_LEFT: (0, canvas_height - layer_height),
            Anchor.BOTTOM_RIGHT: (
                canvas_width - layer_width,
                canvas_height - layer_height
            ),
            Anchor.TOP_CENTER: ((canvas_width - layer_width) // 2, 0),
            Anchor.BOTTOM_CENTER: (
                (canvas_width - layer_width) // 2,
                canvas_height - layer_height
            ),
            Anchor.CENTER_LEFT: (0, (canvas_height - layer_height) // 2),
            Anchor.CENTER_RIGHT: (
                canvas_width - layer_width,
                (canvas_height - layer_height) // 2
            ),
        }

        x, y = anchor_positions.get(anchor, ((canvas_width - layer_width) // 2, (canvas_height - layer_height) // 2))

        return (x + position.offset_x, y + position.offset_y)

    async def _apply_image_layer(
        self,
        canvas: Image.Image,
        layer: ImageLayer,
        canvas_width: int,
        canvas_height: int
    ) -> Image.Image:
        """Apply foreground image layer to canvas"""

        # Download layer image
        layer_image = await self._download_image(layer.image_url)
        if not layer_image:
            logger.warning(f"Failed to download layer image: {layer.image_url}")
            return canvas

        # Convert to RGBA
        layer_image = layer_image.convert("RGBA")

        # Scale if needed
        if layer.scale != 1.0:
            new_size = (
                int(layer_image.width * layer.scale),
                int(layer_image.height * layer.scale)
            )
            layer_image = layer_image.resize(new_size, Image.Resampling.LANCZOS)

        # Resize if max dimensions specified
        if layer.max_width or layer.max_height:
            layer_image = self._resize_image(
                layer_image,
                layer.max_width,
                layer.max_height,
                layer.maintain_aspect
            )

        # Apply opacity
        if layer.opacity < 1.0:
            alpha = layer_image.split()[3]
            alpha = alpha.point(lambda p: int(p * layer.opacity))
            layer_image.putalpha(alpha)

        # Calculate position
        x, y = self._calculate_position(
            layer.position,
            layer_image.width,
            layer_image.height,
            canvas_width,
            canvas_height
        )

        # Paste onto canvas
        canvas.paste(layer_image, (x, y), layer_image)

        return canvas

    def _apply_text_layer(
        self,
        canvas: Image.Image,
        layer: TextLayer,
        canvas_width: int,
        canvas_height: int
    ) -> Image.Image:
        """Apply text layer to canvas"""

        # Create drawing context
        draw = ImageDraw.Draw(canvas)

        # Load font
        try:
            font = self._get_font(layer.font_family, layer.font_size, layer.bold, layer.italic)
        except Exception as e:
            logger.warning(f"Font loading failed, using default: {e}")
            font = ImageFont.load_default()

        # Measure text
        bbox = draw.textbbox((0, 0), layer.text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate position
        x, y = self._calculate_position(
            layer.position,
            text_width,
            text_height,
            canvas_width,
            canvas_height
        )

        # Apply shadow if specified
        if layer.shadow:
            shadow_x = x + layer.shadow.offset_x
            shadow_y = y + layer.shadow.offset_y
            # TODO: Implement blur (requires PIL extensions)
            draw.text(
                (shadow_x, shadow_y),
                layer.text,
                font=font,
                fill=layer.shadow.color
            )

        # Apply stroke if specified
        if layer.stroke:
            draw.text(
                (x, y),
                layer.text,
                font=font,
                fill=layer.color,
                stroke_width=layer.stroke.width,
                stroke_fill=layer.stroke.color
            )
        else:
            draw.text(
                (x, y),
                layer.text,
                font=font,
                fill=layer.color
            )

        return canvas

    def _get_font(
        self,
        font_family: str,
        font_size: int,
        bold: bool = False,
        italic: bool = False
    ) -> ImageFont.FreeTypeFont:
        """Get font from cache or load"""

        cache_key = f"{font_family}_{font_size}_{bold}_{italic}"

        if cache_key in self.font_cache:
            return self.font_cache[cache_key]

        # Try to load system font
        # This is a simplified version - production should use proper font discovery
        try:
            font = ImageFont.truetype(font_family, font_size)
            self.font_cache[cache_key] = font
            return font
        except:
            # Fall back to default
            return ImageFont.load_default()


# Factory function for dependency injection
def get_composite_service() -> CompositeImageService:
    """Get singleton composite service instance"""
    return CompositeImageService()
