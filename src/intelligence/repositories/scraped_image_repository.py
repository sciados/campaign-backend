"""
ScrapedImage Repository

Database operations for scraped product images.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func
from datetime import datetime
import logging

from src.intelligence.models.scraped_image import ScrapedImage

logger = logging.getLogger(__name__)


class ScrapedImageRepository:
    """Repository for scraped image database operations"""

    @staticmethod
    async def create(
        db: AsyncSession,
        campaign_id: str,
        user_id: str,
        r2_path: str,
        cdn_url: str,
        width: int,
        height: int,
        file_size: int,
        format: str,
        quality_score: float,
        is_hero: bool = False,
        is_product: bool = False,
        is_lifestyle: bool = False,
        original_url: Optional[str] = None,
        alt_text: Optional[str] = None,
        context: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ScrapedImage:
        """Create a new scraped image record"""

        image = ScrapedImage(
            campaign_id=campaign_id,
            user_id=user_id,
            r2_path=r2_path,
            cdn_url=cdn_url,
            original_url=original_url,
            width=width,
            height=height,
            file_size=file_size,
            format=format,
            alt_text=alt_text,
            context=context,
            quality_score=quality_score,
            is_hero=is_hero,
            is_product=is_product,
            is_lifestyle=is_lifestyle,
            extra_metadata=metadata,
            scraped_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(image)
        await db.commit()
        await db.refresh(image)

        logger.info(f"✅ Created scraped image record: {image.id}")
        return image

    @staticmethod
    async def get_by_campaign(
        db: AsyncSession,
        campaign_id: str,
        image_type: Optional[str] = None
    ) -> List[ScrapedImage]:
        """Get all scraped images for a campaign, optionally filtered by type"""

        query = select(ScrapedImage).where(ScrapedImage.campaign_id == campaign_id)

        # Apply type filter
        if image_type == "hero":
            query = query.where(ScrapedImage.is_hero == True)
        elif image_type == "product":
            query = query.where(ScrapedImage.is_product == True)
        elif image_type == "lifestyle":
            query = query.where(ScrapedImage.is_lifestyle == True)

        # Order by quality score descending
        query = query.order_by(ScrapedImage.quality_score.desc())

        result = await db.execute(query)
        images = list(result.scalars().all())

        logger.info(f"Found {len(images)} scraped images for campaign {campaign_id}")
        return images

    @staticmethod
    async def get_by_id(db: AsyncSession, image_id: str) -> Optional[ScrapedImage]:
        """Get scraped image by ID"""

        query = select(ScrapedImage).where(ScrapedImage.id == image_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_by_id(db: AsyncSession, image_id: str) -> bool:
        """Delete scraped image by ID"""

        query = delete(ScrapedImage).where(ScrapedImage.id == image_id)
        result = await db.execute(query)
        await db.commit()

        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"✅ Deleted scraped image: {image_id}")
        else:
            logger.warning(f"No scraped image found with id: {image_id}")

        return deleted

    @staticmethod
    async def delete_by_campaign(db: AsyncSession, campaign_id: str) -> int:
        """Delete all scraped images for a campaign"""

        query = delete(ScrapedImage).where(ScrapedImage.campaign_id == campaign_id)
        result = await db.execute(query)
        await db.commit()

        count = result.rowcount
        logger.info(f"✅ Deleted {count} scraped images for campaign {campaign_id}")
        return count

    @staticmethod
    async def increment_usage(db: AsyncSession, image_id: str) -> bool:
        """Increment usage count and update last_used_at"""

        query = (
            update(ScrapedImage)
            .where(ScrapedImage.id == image_id)
            .values(
                times_used=ScrapedImage.times_used + 1,
                last_used_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )

        result = await db.execute(query)
        await db.commit()

        updated = result.rowcount > 0
        if updated:
            logger.info(f"✅ Incremented usage for image: {image_id}")

        return updated

    @staticmethod
    async def get_stats(db: AsyncSession, campaign_id: str) -> Dict[str, Any]:
        """Get statistics for scraped images in a campaign"""

        query = select(
            func.count(ScrapedImage.id).label("total_count"),
            func.count(ScrapedImage.id).filter(ScrapedImage.is_hero == True).label("hero_count"),
            func.count(ScrapedImage.id).filter(ScrapedImage.is_product == True).label("product_count"),
            func.count(ScrapedImage.id).filter(ScrapedImage.is_lifestyle == True).label("lifestyle_count"),
            func.avg(ScrapedImage.quality_score).label("avg_quality"),
            func.max(ScrapedImage.quality_score).label("max_quality"),
            func.sum(ScrapedImage.file_size).label("total_size"),
        ).where(ScrapedImage.campaign_id == campaign_id)

        result = await db.execute(query)
        row = result.one()

        return {
            "total_count": row.total_count or 0,
            "hero_count": row.hero_count or 0,
            "product_count": row.product_count or 0,
            "lifestyle_count": row.lifestyle_count or 0,
            "avg_quality": float(row.avg_quality) if row.avg_quality else 0.0,
            "max_quality": float(row.max_quality) if row.max_quality else 0.0,
            "total_size_bytes": row.total_size or 0,
            "total_size_mb": round((row.total_size or 0) / (1024 * 1024), 2),
        }

    @staticmethod
    async def get_most_used(
        db: AsyncSession,
        campaign_id: str,
        limit: int = 10
    ) -> List[ScrapedImage]:
        """Get most frequently used images for a campaign"""

        query = (
            select(ScrapedImage)
            .where(ScrapedImage.campaign_id == campaign_id)
            .where(ScrapedImage.times_used > 0)
            .order_by(ScrapedImage.times_used.desc())
            .limit(limit)
        )

        result = await db.execute(query)
        return result.scalars().all()
