# src/core/crud/subject_template_crud.py
"""
CRUD operations for email subject templates
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from src.core.crud.base_crud import BaseCRUD
from src.models.email_subject_templates import EmailSubjectTemplate, EmailSubjectPerformance, SubjectLineCategory, PerformanceLevel

class SubjectTemplateCRUD(BaseCRUD[EmailSubjectTemplate]):
    """CRUD operations for email subject templates"""
    
    def __init__(self):
        super().__init__(EmailSubjectTemplate)
    
    async def get_templates_by_category(
        self, 
        db: AsyncSession, 
        category: SubjectLineCategory,
        performance_level: Optional[PerformanceLevel] = None,
        limit: int = 20
    ) -> List[EmailSubjectTemplate]:
        """Get templates by category and performance level"""
        
        query = select(self.model).where(
            self.model.category == category,
            self.model.is_active == True
        )
        
        if performance_level:
            query = query.where(self.model.performance_level == performance_level)
        
        # Order by performance (open rate desc, then total uses desc)
        query = query.order_by(
            self.model.avg_open_rate.desc(),
            self.model.total_uses.desc()
        ).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_top_performing_templates(
        self,
        db: AsyncSession,
        limit: int = 10,
        min_uses: int = 5
    ) -> List[EmailSubjectTemplate]:
        """Get top performing templates across all categories"""
        
        query = select(self.model).where(
            self.model.is_active == True,
            self.model.total_uses >= min_uses,
            self.model.avg_open_rate > 0
        ).order_by(
            self.model.avg_open_rate.desc()
        ).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_template_performance(
        self,
        db: AsyncSession,
        template_id: str,
        new_opens: int,
        new_sends: int
    ) -> Optional[EmailSubjectTemplate]:
        """Update template performance metrics"""
        
        template = await self.get(db=db, id=template_id)
        if not template:
            return None
        
        # Update counters
        template.total_opens += new_opens
        template.total_uses += new_sends
        
        # Recalculate average open rate
        if template.total_uses > 0:
            template.avg_open_rate = (template.total_opens / template.total_uses) * 100
        
        # Update performance level based on metrics
        if template.avg_open_rate >= 30 and template.total_uses >= 20:
            template.performance_level = PerformanceLevel.TOP_TIER
        elif template.avg_open_rate >= 25 and template.total_uses >= 10:
            template.performance_level = PerformanceLevel.HIGH_PERFORMING
        elif template.avg_open_rate >= 20 and template.total_uses >= 5:
            template.performance_level = PerformanceLevel.GOOD
        
        await db.commit()
        await db.refresh(template)
        return template
    
    async def add_template_batch(
        self,
        db: AsyncSession,
        templates_data: List[Dict[str, Any]]
    ) -> List[EmailSubjectTemplate]:
        """Add multiple templates at once"""
        
        templates = []
        for data in templates_data:
            template = EmailSubjectTemplate(
                template_text=data["template_text"],
                category=data["category"],
                performance_level=data.get("performance_level", PerformanceLevel.EXPERIMENTAL),
                psychology_triggers=data.get("psychology_triggers", []),
                keywords=data.get("keywords", []),
                character_count=len(data["template_text"]),
                source=data.get("source", "initial_load"),
                is_verified=data.get("is_verified", False)
            )
            templates.append(template)
        
        db.add_all(templates)
        await db.commit()
        
        for template in templates:
            await db.refresh(template)
        
        return templates

class SubjectPerformanceCRUD(BaseCRUD[EmailSubjectPerformance]):
    """CRUD operations for subject line performance tracking"""
    
    def __init__(self):
        super().__init__(EmailSubjectPerformance)
    
    async def record_subject_usage(
        self,
        db: AsyncSession,
        subject_line: str,
        product_name: str,
        category: SubjectLineCategory,
        campaign_id: str,
        email_number: int,
        strategic_angle: str,
        template_id: Optional[str] = None,
        ai_provider: Optional[str] = None,
        generation_method: str = "ai_with_template_reference"
    ) -> EmailSubjectPerformance:
        """Record when a subject line is used"""
        
        performance_record = EmailSubjectPerformance(
            template_id=template_id,
            subject_line=subject_line,
            product_name=product_name,
            category_used=category,
            campaign_id=campaign_id,
            email_number_in_sequence=email_number,
            strategic_angle=strategic_angle,
            ai_provider_used=ai_provider,
            generation_method=generation_method
        )
        
        return await self.create(db=db, obj_in=performance_record)
    
    async def update_performance_metrics(
        self,
        db: AsyncSession,
        performance_id: str,
        emails_sent: int,
        emails_opened: int,
        click_rate: Optional[float] = None
    ) -> Optional[EmailSubjectPerformance]:
        """Update performance metrics for a subject line"""
        
        performance = await self.get(db=db, id=performance_id)
        if not performance:
            return None
        
        performance.emails_sent = emails_sent
        performance.emails_opened = emails_opened
        performance.calculate_open_rate()
        
        if click_rate is not None:
            performance.click_rate = click_rate
        
        performance.performance_updated_at = func.now()
        
        await db.commit()
        await db.refresh(performance)
        return performance