# src/intelligence/routers/enhanced_email_routes.py
"""
Enhanced Email Generation Routes with Database Learning System
✅ Database-referenced AI subject line generation
✅ Self-learning system integration  
✅ Performance tracking endpoints
✅ Learning analytics
✅ Railway deployment compatible
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

# Core imports
from src.core.database import get_async_session
from src.auth.dependencies import get_current_user
from src.models.user import User

# Enhanced email generator with database learning
from src.intelligence.generators.email_generator import EmailSequenceGenerator
from src.intelligence.generators.self_learning_subject_service import SelfLearningSubjectService
from src.intelligence.generators.database_seeder import seed_subject_line_templates

# Schemas for API requests/responses
from pydantic import BaseModel, Field
from uuid import UUID

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/enhanced-emails", tags=["Enhanced Email Generation"])

# =====================================
# PYDANTIC SCHEMAS
# =====================================

class EmailGenerationRequest(BaseModel):
    """Request schema for email generation"""
    campaign_id: str
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    use_database_templates: bool = Field(default=True, description="Use database templates for AI reference")
    enable_learning: bool = Field(default=True, description="Enable self-learning from performance")

class PerformanceTrackingRequest(BaseModel):
    """Request schema for tracking email performance"""
    performance_data: List[Dict[str, Any]] = Field(
        description="List of performance records",
        example=[{
            "performance_record_id": "123e4567-e89b-12d3-a456-426614174000",
            "emails_sent": 100,
            "emails_opened": 32,
            "click_rate": 4.5
        }]
    )

class EmailGenerationResponse(BaseModel):
    """Response schema for email generation"""
    success: bool
    emails: List[Dict[str, Any]]
    learning_metadata: Optional[List[Dict[str, Any]]] = None
    generation_info: Dict[str, Any]
    message: str

class PerformanceTrackingResponse(BaseModel):
    """Response schema for performance tracking"""
    success: bool
    performance_updates: List[Dict[str, Any]]
    learning_results: Dict[str, Any]
    message: str

class LearningAnalyticsResponse(BaseModel):
    """Response schema for learning analytics"""
    template_stats: List[Dict[str, Any]]
    ai_performance: Dict[str, Any]
    top_templates: List[Dict[str, Any]]
    learning_active: bool
    system_status: str

# =====================================
# HELPER FUNCTIONS
# =====================================

async def get_campaign_intelligence(campaign_id: str, db: AsyncSession, user: User) -> Dict[str, Any]:
    """
    Get campaign intelligence data - adapt this to your existing implementation
    This is a placeholder that should be replaced with your actual intelligence gathering
    """
    try:
        # TODO: Replace with your actual campaign intelligence retrieval
        # This might involve querying your campaigns table, intelligence sources, etc.
        
        # For now, return a sample structure that works with the email generator
        return {
            "source_title": f"Product-{campaign_id}",  # This becomes the product name
            "target_audience": "individuals seeking solutions",
            "offer_intelligence": {
                "main_benefits": "comprehensive benefits",
                "key_features": "proven approach"
            },
            "campaign_id": campaign_id
        }
    
    except Exception as e:
        logger.error(f"Failed to get campaign intelligence: {str(e)}")
        # Fallback for testing
        return {
            "source_title": f"TestProduct-{campaign_id}",
            "target_audience": "individuals seeking solutions",
            "offer_intelligence": {
                "main_benefits": "improved results",
                "key_features": "proven methodology"
            },
            "campaign_id": campaign_id
        }

# =====================================
# ENHANCED EMAIL GENERATION ENDPOINTS
# =====================================

@router.post("/generate", response_model=EmailGenerationResponse)
async def generate_enhanced_email_sequence(
    request: EmailGenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Generate email sequence with database-enhanced AI subject lines
    
    This endpoint:
    - Uses database templates as AI reference patterns
    - Enables self-learning from performance data
    - Tracks generation metadata for learning
    - Provides high-quality, unique subject lines
    """
    
    try:
        # Get campaign intelligence data
        intelligence_data = await get_campaign_intelligence(
            request.campaign_id, db, current_user
        )
        
        # Initialize the enhanced generator
        generator = EmailSequenceGenerator()
        
        # Check if templates are seeded, seed if needed
        background_tasks.add_task(ensure_templates_seeded, db)
        
        # Generate emails with appropriate method
        if request.use_database_templates:
            # Use database-enhanced generation
            result = await generator.generate_email_sequence_with_db(
                intelligence_data=intelligence_data,
                db=db,
                campaign_id=request.campaign_id,
                preferences=request.preferences
            )
        else:
            # Use standard generation
            result = await generator.generate_email_sequence(
                intelligence_data=intelligence_data,
                preferences=request.preferences
            )
        
        # Extract emails and metadata
        emails = result.get("content", {}).get("emails", [])
        generation_metadata = result.get("content", {}).get("generation_metadata", {})
        
        # Prepare learning metadata for tracking
        learning_metadata = []
        for email in emails:
            if email.get("subject_metadata", {}).get("performance_record_id"):
                learning_metadata.append({
                    "email_number": email.get("email_number"),
                    "performance_record_id": email["subject_metadata"]["performance_record_id"],
                    "can_learn_from": email["subject_metadata"].get("method") == "ai_with_db_reference"
                })
        
        # Prepare response
        generation_info = {
            "database_enhanced": result.get("content", {}).get("database_enhanced", False),
            "unique_subjects": len(set(email.get("subject") for email in emails)),
            "total_emails": len(emails),
            "learning_enabled": request.enable_learning,
            "generation_method": "database_enhanced" if request.use_database_templates else "standard"
        }
        
        logger.info(f"✅ Generated {len(emails)} emails for campaign {request.campaign_id}")
        
        return EmailGenerationResponse(
            success=True,
            emails=emails,
            learning_metadata=learning_metadata if request.enable_learning else None,
            generation_info=generation_info,
            message=f"Generated {len(emails)} emails with AI subject lines using database templates"
        )
        
    except Exception as e:
        logger.error(f"❌ Enhanced email generation failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Email generation failed: {str(e)}"
        )

@router.post("/track-performance", response_model=PerformanceTrackingResponse)
async def track_email_performance(
    request: PerformanceTrackingRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Track email performance and trigger learning from successful subjects
    
    Call this endpoint after sending emails to update performance metrics
    and enable the self-learning system to improve future generations.
    """
    
    try:
        generator = EmailSequenceGenerator()
        results = []
        
        # Update performance for each email
        for data in request.performance_data:
            try:
                success = await generator.track_subject_performance(
                    db=db,
                    performance_record_id=data["performance_record_id"],
                    emails_sent=data["emails_sent"],
                    emails_opened=data["emails_opened"],
                    click_rate=data.get("click_rate")
                )
                
                open_rate = (data["emails_opened"] / data["emails_sent"] * 100) if data["emails_sent"] > 0 else 0
                
                results.append({
                    "performance_record_id": data["performance_record_id"],
                    "open_rate": open_rate,
                    "updated": success,
                    "high_performer": open_rate >= 25.0
                })
                
            except Exception as e:
                logger.error(f"Failed to track performance for {data.get('performance_record_id')}: {str(e)}")
                results.append({
                    "performance_record_id": data.get("performance_record_id"),
                    "open_rate": 0,
                    "updated": False,
                    "error": str(e)
                })
        
        # Trigger learning evaluation in background
        background_tasks.add_task(trigger_learning_evaluation, db)
        
        # Get immediate learning results
        learning_service = SelfLearningSubjectService()
        learning_results = await learning_service.evaluate_and_store_successful_subjects(
            db=db,
            auto_evaluate_recent=True
        )
        
        logger.info(f"✅ Updated {len(results)} performance records")
        
        return PerformanceTrackingResponse(
            success=True,
            performance_updates=results,
            learning_results=learning_results,
            message=f"Updated {len(results)} performance records, stored {learning_results.get('stored_as_templates', 0)} new templates"
        )
        
    except Exception as e:
        logger.error(f"❌ Performance tracking failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Performance tracking failed: {str(e)}"
        )

@router.get("/learning-analytics", response_model=LearningAnalyticsResponse)
async def get_learning_analytics(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get analytics on the learning system performance
    
    Shows how the AI is improving over time with metrics on:
    - Template performance by source
    - AI-generated subject performance  
    - Top performing templates
    - Learning system status
    """
    
    try:
        from sqlalchemy import select, func
        from src.models.email_subject_templates import EmailSubjectTemplate, EmailSubjectPerformance
        
        # Get template stats by source
        template_stats_query = select(
            EmailSubjectTemplate.source,
            EmailSubjectTemplate.performance_level,
            func.count(EmailSubjectTemplate.id).label('count'),
            func.avg(EmailSubjectTemplate.avg_open_rate).label('avg_open_rate')
        ).group_by(
            EmailSubjectTemplate.source,
            EmailSubjectTemplate.performance_level
        )
        
        template_stats_result = await db.execute(template_stats_query)
        template_stats = [dict(row._mapping) for row in template_stats_result]
        
        # Get recent AI performance
        ai_performance_query = select(
            func.count(EmailSubjectPerformance.id).label('total_ai_subjects'),
            func.avg(EmailSubjectPerformance.open_rate).label('avg_ai_open_rate'),
            func.count().filter(EmailSubjectPerformance.open_rate >= 25.0).label('high_performing_count'),
            func.count().filter(EmailSubjectPerformance.open_rate >= 35.0).label('top_tier_count')
        ).where(
            EmailSubjectPerformance.was_ai_generated == True,
            EmailSubjectPerformance.emails_sent >= 10
        )
        
        ai_performance_result = await db.execute(ai_performance_query)
        ai_performance = dict(ai_performance_result.first()._mapping) if ai_performance_result.first() else {}
        
        # Get top performing templates
        top_templates_query = select(
            EmailSubjectTemplate.template_text,
            EmailSubjectTemplate.avg_open_rate,
            EmailSubjectTemplate.performance_level,
            EmailSubjectTemplate.source
        ).where(
            EmailSubjectTemplate.is_active == True
        ).order_by(
            EmailSubjectTemplate.avg_open_rate.desc()
        ).limit(5)
        
        top_templates_result = await db.execute(top_templates_query)
        top_templates = [dict(row._mapping) for row in top_templates_result]
        
        logger.info("✅ Retrieved learning analytics")
        
        return LearningAnalyticsResponse(
            template_stats=template_stats,
            ai_performance=ai_performance,
            top_templates=top_templates,
            learning_active=True,
            system_status="Database-enhanced AI learning system active"
        )
        
    except Exception as e:
        logger.error(f"❌ Analytics retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analytics retrieval failed: {str(e)}"
        )

@router.post("/trigger-learning")
async def trigger_learning_evaluation_endpoint(
    days_back: int = 7,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger learning evaluation from recent performance
    
    Use this endpoint to force the system to learn from recent email
    performance data and store successful patterns as new templates.
    """
    
    try:
        learning_service = SelfLearningSubjectService()
        results = await learning_service.evaluate_and_store_successful_subjects(
            db=db,
            auto_evaluate_recent=True
        )
        
        logger.info(f"✅ Manual learning evaluation completed")
        
        return {
            "success": True,
            "learning_results": results,
            "message": f"Evaluated {results.get('evaluated_count', 0)} subjects, stored {results.get('stored_as_templates', 0)} as new templates"
        }
        
    except Exception as e:
        logger.error(f"❌ Learning trigger failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Learning trigger failed: {str(e)}"
        )

@router.post("/seed-templates")
async def seed_templates_endpoint(
    force_reseed: bool = False,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Seed database with proven subject line templates
    
    This endpoint initializes the database with high-converting
    email subject line templates for AI reference.
    """
    
    try:
        if force_reseed:
            # Clear existing templates if force reseed
            from sqlalchemy import delete
            from src.models.email_subject_templates import EmailSubjectTemplate
            
            await db.execute(delete(EmailSubjectTemplate))
            await db.commit()
            logger.info("🔄 Cleared existing templates for reseed")
        
        # Check if templates already exist
        from sqlalchemy import select, func
        from src.models.email_subject_templates import EmailSubjectTemplate
        
        template_count_result = await db.execute(select(func.count(EmailSubjectTemplate.id)))
        template_count = template_count_result.scalar()
        
        if template_count > 0 and not force_reseed:
            return {
                "success": True,
                "message": f"Templates already seeded ({template_count} templates exist)",
                "templates_seeded": 0,
                "existing_count": template_count
            }
        
        # Seed the templates
        success = await seed_subject_line_templates()
        
        # Get new count
        new_count_result = await db.execute(select(func.count(EmailSubjectTemplate.id)))
        new_count = new_count_result.scalar()
        
        logger.info(f"✅ Templates seeded successfully")
        
        return {
            "success": success,
            "message": "Templates seeded successfully" if success else "Template seeding failed",
            "templates_seeded": new_count - template_count if not force_reseed else new_count,
            "total_templates": new_count
        }
        
    except Exception as e:
        logger.error(f"❌ Template seeding failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Template seeding failed: {str(e)}"
        )

# =====================================
# BACKGROUND TASKS
# =====================================

async def ensure_templates_seeded(db: AsyncSession):
    """Background task to ensure templates are seeded"""
    try:
        from sqlalchemy import select, func
        from src.models.email_subject_templates import EmailSubjectTemplate
        
        # Check if templates exist
        template_count_result = await db.execute(select(func.count(EmailSubjectTemplate.id)))
        template_count = template_count_result.scalar()
        
        if template_count == 0:
            logger.info("🔄 Seeding templates in background...")
            await seed_subject_line_templates()
            logger.info("✅ Background template seeding completed")
    
    except Exception as e:
        logger.error(f"❌ Background template seeding failed: {str(e)}")

async def trigger_learning_evaluation(db: AsyncSession):
    """Background task to trigger learning evaluation"""
    try:
        learning_service = SelfLearningSubjectService()
        results = await learning_service.evaluate_and_store_successful_subjects(
            db=db,
            auto_evaluate_recent=True
        )
        logger.info(f"🧠 Background learning evaluation: {results}")
    
    except Exception as e:
        logger.error(f"❌ Background learning evaluation failed: {str(e)}")

# =====================================
# SYSTEM STATUS ENDPOINTS
# =====================================

@router.get("/system-status")
async def get_system_status(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get enhanced email generation system status
    
    Returns information about:
    - Template database status
    - Learning system status  
    - Recent generation statistics
    """
    
    try:
        from sqlalchemy import select, func
        from src.models.email_subject_templates import EmailSubjectTemplate, EmailSubjectPerformance
        
        # Check template database
        template_count_result = await db.execute(select(func.count(EmailSubjectTemplate.id)))
        template_count = template_count_result.scalar()
        
        active_templates_result = await db.execute(
            select(func.count(EmailSubjectTemplate.id)).where(EmailSubjectTemplate.is_active == True)
        )
        active_templates = active_templates_result.scalar()
        
        # Check recent performance records
        recent_performance_result = await db.execute(
            select(func.count(EmailSubjectPerformance.id)).where(
                EmailSubjectPerformance.created_at >= func.now() - func.interval('7 days')
            )
        )
        recent_performance = recent_performance_result.scalar()
        
        # System status
        system_ready = template_count > 0
        learning_active = recent_performance > 0
        
        return {
            "system_ready": system_ready,
            "learning_active": learning_active,
            "template_database": {
                "total_templates": template_count,
                "active_templates": active_templates,
                "templates_seeded": template_count > 0
            },
            "performance_tracking": {
                "recent_records": recent_performance,
                "tracking_active": recent_performance > 0
            },
            "status_message": "Enhanced email generation system ready" if system_ready else "Templates need to be seeded"
        }
        
    except Exception as e:
        logger.error(f"❌ System status check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"System status check failed: {str(e)}"
        )

# =====================================
# TESTING ENDPOINTS (Development only)
# =====================================

@router.post("/test-generation")
async def test_email_generation(
    product_name: str = "TestProduct",
    sequence_length: int = 3,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Test endpoint for email generation (development/testing only)
    
    Generates a test email sequence to verify system functionality
    """
    
    try:
        # Create test intelligence data
        test_intelligence = {
            "source_title": product_name,
            "target_audience": "individuals seeking solutions",
            "offer_intelligence": {
                "main_benefits": "improved results and satisfaction",
                "key_features": "proven methodology and support"
            },
            "campaign_id": "test-campaign-123"
        }
        
        # Generate emails
        generator = EmailSequenceGenerator()
        result = await generator.generate_email_sequence_with_db(
            intelligence_data=test_intelligence,
            db=db,
            campaign_id="test-campaign-123",
            preferences={"length": str(sequence_length)}
        )
        
        emails = result.get("content", {}).get("emails", [])
        
        return {
            "success": True,
            "test_result": "Generation successful",
            "emails_generated": len(emails),
            "sample_subjects": [email.get("subject", "") for email in emails[:3]],
            "generation_method": "database_enhanced_test",
            "product_name_used": product_name
        }
        
    except Exception as e:
        logger.error(f"❌ Test generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Test generation failed: {str(e)}"
        )