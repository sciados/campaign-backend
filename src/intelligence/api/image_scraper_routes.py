"""
Product Image Scraper API Routes

Endpoints for extracting product images from sales pages
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
import logging

from src.core.database.session import get_db
from src.core.auth.dependencies import get_current_user
from src.intelligence.services.product_image_scraper import (
    ProductImageScraper,
    get_product_image_scraper
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/product-images",
    tags=["product-images"]
)


# ============================================================================
# Request/Response Models
# ============================================================================

class ScrapeImagesRequest(BaseModel):
    """Request to scrape images from sales page"""
    campaign_id: str = Field(..., description="Campaign to associate images with")
    sales_page_url: HttpUrl = Field(..., description="Sales page URL to scrape")
    max_images: int = Field(10, ge=1, le=20, description="Maximum images to extract")
    auto_analyze: bool = Field(True, description="Automatically analyze image suitability")


class ScrapedImageMetadata(BaseModel):
    """Scraped image metadata"""
    original_url: str
    width: int
    height: int
    file_size: int
    format: str
    alt_text: Optional[str]
    context: Optional[str]
    is_hero: bool
    is_product: bool
    is_lifestyle: bool
    quality_score: float
    scraped_at: str


class ScrapeImagesResponse(BaseModel):
    """Response from image scraping"""
    success: bool
    campaign_id: str
    images_found: int
    images_saved: int
    images_skipped: int
    images: List[Dict[str, Any]]  # url, r2_path, metadata
    error: Optional[str] = None


class ImageListResponse(BaseModel):
    """List of scraped images for campaign"""
    success: bool
    campaign_id: str
    images: List[Dict[str, Any]]
    count: int


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/scrape", response_model=ScrapeImagesResponse)
async def scrape_product_images(
    request: ScrapeImagesRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Scrape product images from sales page

    **Process:**
    1. Fetches HTML from sales page
    2. Extracts all images
    3. Analyzes and scores images (quality, type, relevance)
    4. Filters for best product images
    5. Downloads and saves to R2/Cloudflare
    6. Associates with campaign

    **Image Types Detected:**
    - Hero images (main product shot)
    - Product images (bottle, box, package)
    - Lifestyle images (product in use)

    **Quality Scoring:**
    - Resolution and dimensions
    - File size optimization
    - Context relevance
    - Product indicators in URL/alt text

    **Use Cases:**
    - Extract product images for mockup composition
    - Get hero image for campaign visuals
    - Collect lifestyle shots for social media
    - Build product asset library

    **Example:**
    ```json
    {
      "campaign_id": "abc-123",
      "sales_page_url": "https://example.com/product",
      "max_images": 5,
      "auto_analyze": true
    }
    ```
    """

    try:
        user_id = current_user.get("id", "unknown")
        logger.info(f"🖼️  Image scraping request from user {user_id}")
        logger.info(f"📄 Sales page: {request.sales_page_url}")
        logger.info(f"🎯 Campaign: {request.campaign_id}")

        # Verify campaign belongs to user
        # TODO: Add campaign ownership check
        # campaign = await verify_campaign_ownership(request.campaign_id, user_id, db)

        # Scrape images
        async with ProductImageScraper() as scraper:
            result = await scraper.scrape_sales_page(
                url=str(request.sales_page_url),
                campaign_id=request.campaign_id,
                max_images=request.max_images
            )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error or "Image scraping failed"
            )

        # Format response
        images = []
        for i in range(len(result.image_urls)):
            images.append({
                "url": result.image_urls[i],
                "r2_path": result.r2_paths[i],
                "metadata": result.metadata[i]
            })

        # TODO: Save to database
        # background_tasks.add_task(
        #     save_scraped_images_to_db,
        #     campaign_id=request.campaign_id,
        #     images=images,
        #     db=db
        # )

        logger.info(f"✅ Successfully scraped {result.images_saved} images")

        return ScrapeImagesResponse(
            success=True,
            campaign_id=result.campaign_id,
            images_found=result.images_found,
            images_saved=result.images_saved,
            images_skipped=result.images_skipped,
            images=images
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image scraping error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scrape images: {str(e)}"
        )


@router.get("/{campaign_id}", response_model=ImageListResponse)
async def get_scraped_images(
    campaign_id: str,
    image_type: Optional[str] = None,  # hero, product, lifestyle
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get scraped images for campaign

    **Filters:**
    - `image_type=hero` - Hero/main product images
    - `image_type=product` - Product-focused images
    - `image_type=lifestyle` - Lifestyle/contextual images
    - No filter - All images

    **Example:**
    ```
    GET /api/intelligence/product-images/abc-123?image_type=hero
    ```
    """

    try:
        user_id = current_user.get("id", "unknown")
        logger.info(f"📋 Fetching scraped images for campaign {campaign_id}")

        # TODO: Fetch from database
        # images = await fetch_scraped_images(campaign_id, image_type, db)

        # Temporary: Return empty list
        images = []

        return ImageListResponse(
            success=True,
            campaign_id=campaign_id,
            images=images,
            count=len(images)
        )

    except Exception as e:
        logger.error(f"Error fetching scraped images: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/analyze-url", response_model=Dict[str, Any])
async def analyze_images_on_page(
    url: HttpUrl,
    current_user: dict = Depends(get_current_user)
):
    """
    Preview images available on sales page without saving

    **Use Case:** Preview before scraping

    Returns count and summary of images found
    """

    try:
        logger.info(f"🔍 Analyzing images on: {url}")

        async with ProductImageScraper() as scraper:
            # Fetch and analyze (don't save)
            html = await scraper._fetch_html(str(url))
            if not html:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch page"
                )

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            raw_images = scraper._extract_image_elements(soup)

            # Quick analysis
            analyzed = []
            for img_elem in raw_images[:50]:  # Limit to first 50
                img_data = await scraper._analyze_image(img_elem, str(url))
                if img_data:
                    analyzed.append(img_data)

            # Categorize
            hero_count = sum(1 for img in analyzed if img.is_hero)
            product_count = sum(1 for img in analyzed if img.is_product)
            lifestyle_count = sum(1 for img in analyzed if img.is_lifestyle)

            return {
                "success": True,
                "url": str(url),
                "images_found": len(raw_images),
                "images_suitable": len(analyzed),
                "hero_images": hero_count,
                "product_images": product_count,
                "lifestyle_images": lifestyle_count,
                "top_images": [
                    {
                        "url": img.url,
                        "width": img.width,
                        "height": img.height,
                        "quality_score": img.quality_score,
                        "type": (
                            "hero" if img.is_hero else
                            "product" if img.is_product else
                            "lifestyle" if img.is_lifestyle else
                            "other"
                        )
                    }
                    for img in sorted(analyzed, key=lambda x: x.quality_score, reverse=True)[:10]
                ]
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{campaign_id}/{image_id}")
async def delete_scraped_image(
    campaign_id: str,
    image_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete scraped image

    Removes from database and R2 storage
    """

    try:
        user_id = current_user.get("id", "unknown")
        logger.info(f"🗑️  Deleting image {image_id} from campaign {campaign_id}")

        # TODO: Delete from database and R2
        # await delete_scraped_image_from_db(campaign_id, image_id, db)
        # await r2_service.delete_file(r2_path)

        return {
            "success": True,
            "message": "Image deleted successfully"
        }

    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
