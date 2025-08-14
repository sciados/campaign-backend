"""
File: src/intelligence/routers/content_routes.py
✅ CRUD MIGRATION COMPLETE: Content Routes with CRUD-enabled handlers
✅ FIXED: All database operations now use CRUD patterns
✅ FIXED: Direct SQLAlchemy imports removed and replaced with CRUD
✅ FIXED: ChunkedIteratorResult elimination via CRUD integration
✅ FIXED: Frontend compatibility - matching expected endpoints
✅ PATTERN: Route CRUD Verification (following analysis_routes.py pattern)
"""
from fastapi import APIRouter, Depends, HTTPException, status as http_status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timezone
import asyncio
import json
import uuid
from uuid import UUID

# ✅ CRUD MIGRATION: Use get_async_db for proper async session management
from src.core.database import get_async_db
from src.auth.dependencies import get_current_user
from src.models.user import User

# ✅ CRUD MIGRATION: Import CRUD-enabled systems
from src.core.crud import campaign_crud, intelligence_crud

router = APIRouter()
logger = logging.getLogger(__name__)

# ============================================================================
# ✅ FRONTEND COMPATIBLE ENDPOINTS - MATCHING EXPECTED URLs
# ============================================================================

@router.post("/generate")
async def generate_content(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    🎯 FRONTEND COMPATIBLE: Generate content endpoint
    POST /api/intelligence/content/generate
    """
    try:
        logger.info("🎯 Content generation request received")
        
        # Extract request data
        content_type = request_data.get("content_type", "email_sequence")
        campaign_id = request_data.get("campaign_id")
        preferences = request_data.get("preferences", {})
        prompt = request_data.get("prompt", f"Generate {content_type}")
        
        if not campaign_id:
            raise HTTPException(
                status_code=400,
                detail="campaign_id is required"
            )
        
        # ✅ CRUD MIGRATION: Verify campaign access using CRUD
        campaign = await campaign_crud.get(db=db, id=campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=404,
                detail="Campaign not found"
            )
        
        if campaign.company_id != current_user.company_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied to this campaign"
            )
        
        # ✅ CRUD MIGRATION: Get intelligence using CRUD
        intelligence_entries = await intelligence_crud.get_campaign_intelligence(
            db=db, 
            campaign_id=campaign_id
        )
        
        if not intelligence_entries:
            raise HTTPException(
                status_code=400,
                detail="No intelligence available for content generation. Please analyze some sources first."
            )
        
        # Use first intelligence source for generation
        primary_intel = intelligence_entries[0]
        
        # Generate content using intelligence data
        generated_content = await generate_content_from_intelligence(
            content_type=content_type,
            intelligence=primary_intel,
            preferences=preferences,
            prompt=prompt
        )
        
        # Save generated content via CRUD
        content_id = await save_generated_content_crud(
            db=db,
            user=current_user,
            campaign_id=campaign_id,
            content_type=content_type,
            content=generated_content,
            intelligence_id=str(primary_intel.id)
        )
        
        # Return frontend-compatible response
        response = {
            "content_id": content_id,
            "content_type": content_type,
            "campaign_id": campaign_id,
            "generated_content": {
                "title": generated_content.get("title", f"Generated {content_type.replace('_', ' ').title()}"),
                "content": generated_content.get("content", {}),
                "metadata": generated_content.get("metadata", {})
            },
            "intelligence_used": [str(primary_intel.id)],
            "generation_metadata": {
                "timestamp": datetime.now().isoformat(),
                "content_type": content_type,
                "preferences_used": preferences,
                "intelligence_confidence": primary_intel.confidence_score
            },
            "performance_predictions": generated_content.get("performance_predictions", {}),
            "smart_url": generated_content.get("smart_url"),
            "success": True
        }
        
        logger.info(f"✅ Content generated successfully: {content_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Content generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Content generation failed: {str(e)}"
        )

@router.get("/{campaign_id}")
async def get_generated_content(
    campaign_id: str,
    include_body: bool = True,
    content_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 FRONTEND COMPATIBLE: Get generated content for campaign
    GET /api/intelligence/content/{campaign_id}
    """
    try:
        logger.info(f"🔍 Getting content for campaign {campaign_id}")
        
        # ✅ CRUD MIGRATION: Verify campaign access
        campaign = await campaign_crud.get(db=db, id=campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        if campaign.company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # ✅ CRUD MIGRATION: Get generated content using CRUD
        content_entries = await intelligence_crud.get_generated_content(
            db=db,
            campaign_id=campaign_id,
            content_type=content_type,
            limit=limit,
            offset=offset
        )
        
        # Transform to frontend-compatible format
        content_items = []
        for content in content_entries:
            content_item = {
                "content_id": str(content.id),
                "campaign_id": campaign_id,
                "content_type": content.content_type,
                "content_title": content.content_title,
                "is_published": getattr(content, 'is_published', False),
                "user_rating": getattr(content, 'user_rating', None),
                "created_at": content.created_at.isoformat() if content.created_at else datetime.now().isoformat(),
                "updated_at": content.updated_at.isoformat() if content.updated_at else None,
            }
            
            if include_body:
                content_item["content_body"] = content.content_body
                content_item["parsed_content"] = content.content_metadata or {}
            
            content_items.append(content_item)
        
        logger.info(f"✅ Retrieved {len(content_items)} content items")
        return content_items
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting content: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get content: {str(e)}")

@router.get("/{campaign_id}/content/{content_id}")
async def get_content_detail(
    campaign_id: str,
    content_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed content by ID"""
    try:
        # ✅ CRUD MIGRATION: Verify campaign access
        campaign = await campaign_crud.get(db=db, id=campaign_id)
        if not campaign or campaign.company_id != current_user.company_id:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # ✅ CRUD MIGRATION: Get content using CRUD
        content = await intelligence_crud.get_generated_content_by_id(
            db=db,
            content_id=content_id
        )
        
        if not content or str(content.campaign_id) != campaign_id:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return {
            "id": str(content.id),
            "campaign_id": campaign_id,
            "content_type": content.content_type,
            "content_title": content.content_title,
            "content_body": content.content_body,
            "parsed_content": content.content_metadata or {},
            "created_at": content.created_at.isoformat(),
            "updated_at": content.updated_at.isoformat() if content.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{campaign_id}/content/{content_id}")
async def update_content(
    campaign_id: str,
    content_id: str,
    update_data: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Update content"""
    try:
        # ✅ CRUD MIGRATION: Verify access and update using CRUD
        content = await intelligence_crud.get_generated_content_by_id(
            db=db,
            content_id=content_id
        )
        
        if not content or str(content.campaign_id) != campaign_id:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Update content using CRUD
        updated_content = await intelligence_crud.update_generated_content(
            db=db,
            content_id=content_id,
            update_data=update_data
        )
        
        return {
            "id": content_id,
            "message": "Content updated successfully",
            "updated_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{campaign_id}/content/{content_id}")
async def delete_content(
    campaign_id: str,
    content_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Delete content"""
    try:
        # ✅ CRUD MIGRATION: Verify access and delete using CRUD
        content = await intelligence_crud.get_generated_content_by_id(
            db=db,
            content_id=content_id
        )
        
        if not content or str(content.campaign_id) != campaign_id:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Delete content using CRUD
        await intelligence_crud.delete_generated_content(
            db=db,
            content_id=content_id
        )
        
        return {"message": "Content deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ✅ HELPER FUNCTIONS FOR CONTENT GENERATION
# ============================================================================

async def generate_content_from_intelligence(
    content_type: str,
    intelligence,
    preferences: Dict[str, Any],
    prompt: str
) -> Dict[str, Any]:
    """Generate content using intelligence data"""
    
    # Extract intelligence data
    offer_intel = intelligence.offer_intelligence or {}
    psych_intel = intelligence.psychology_intelligence or {}
    source_title = intelligence.source_title or "Unknown Source"
    
    # Generate content based on type
    if content_type == "email_sequence":
        content = generate_email_sequence(offer_intel, psych_intel, source_title, preferences)
    elif content_type == "social_post":
        content = generate_social_posts(offer_intel, psych_intel, source_title)
    elif content_type == "ad_copy":
        content = generate_ad_copy(offer_intel, psych_intel, source_title)
    elif content_type == "blog_post":
        content = generate_blog_post(offer_intel, psych_intel, source_title)
    else:
        content = generate_generic_content(content_type, offer_intel, psych_intel, source_title)
    
    return {
        "title": content.get("title", f"Generated {content_type.replace('_', ' ').title()}"),
        "content": content,
        "metadata": {
            "content_type": content_type,
            "generated_at": datetime.now().isoformat(),
            "intelligence_source": str(intelligence.id),
            "source_confidence": intelligence.confidence_score,
            "generation_method": "intelligence_based"
        },
        "performance_predictions": {
            "estimated_engagement": "Medium" if intelligence.confidence_score > 70 else "Low",
            "confidence_score": intelligence.confidence_score
        }
    }

def generate_email_sequence(offer_intel, psych_intel, source_title, preferences):
    """Generate email sequence from intelligence"""
    sequence_length = int(preferences.get('length', 3))
    
    main_benefits = offer_intel.get('main_benefits', 'key benefits')
    emotional_triggers = psych_intel.get('emotional_triggers', 'success and achievement')
    
    emails = []
    
    # Email 1
    emails.append({
        "day": 1,
        "subject": f"Discover the Secret Behind {main_benefits}",
        "preview": f"What we learned from analyzing {source_title}...",
        "body": f"""Hi there!

I just finished analyzing {source_title}, and I discovered something fascinating about {main_benefits}.

The insights we gathered show that {emotional_triggers} plays a crucial role in success.

Want to know more? I'll share the complete breakdown tomorrow.

Best regards,
Your Marketing Team"""
    })
    
    # Email 2 (if sequence > 1)
    if sequence_length > 1:
        emails.append({
            "day": 3,
            "subject": f"The Psychology Behind {emotional_triggers}",
            "preview": f"Why this approach works so well...",
            "body": f"""Yesterday I shared our analysis of {source_title}.

Today, let's dive deeper into the psychology behind why this works.

Our research shows that people are motivated by {emotional_triggers}.

This is powerful because it addresses their core needs while delivering {main_benefits}.

[Continue reading the full analysis]

Best,
Your Marketing Team"""
        })
    
    # Email 3 (if sequence > 2)
    if sequence_length > 2:
        emails.append({
            "day": 7,
            "subject": f"Last Chance: Apply These {source_title} Insights",
            "preview": "Don't let this opportunity slip away...",
            "body": f"""This is your final reminder.

Over the past week, I've shared exclusive insights from our analysis of {source_title}.

You've learned about the power of {main_benefits} and how {emotional_triggers} drives decisions.

The window to apply these insights is closing soon.

[Take Action Now]

Your Marketing Team"""
        })
    
    return {
        "title": f"Email Sequence Based on {source_title} Analysis",
        "emails": emails[:sequence_length],
        "sequence_info": {
            "total_emails": len(emails[:sequence_length]),
            "schedule_days": [email["day"] for email in emails[:sequence_length]],
            "based_on": source_title
        }
    }

def generate_social_posts(offer_intel, psych_intel, source_title):
    """Generate social media posts"""
    main_benefits = offer_intel.get('main_benefits', 'amazing results')
    emotional_triggers = psych_intel.get('emotional_triggers', 'success')
    
    posts = [
        {
            "platform": "facebook",
            "content": f"🎯 Just analyzed {source_title} and discovered the secret to {main_benefits}!\n\nThe key? Understanding {emotional_triggers}.\n\n#MarketingInsights #Success #Strategy"
        },
        {
            "platform": "twitter", 
            "content": f"🔥 {source_title} analysis reveals: {main_benefits} comes from understanding {emotional_triggers}\n\n#marketing #insights"
        },
        {
            "platform": "linkedin",
            "content": f"After analyzing {source_title}, I've identified key patterns that drive {main_benefits}:\n\n• Understanding {emotional_triggers}\n• Applying proven strategies\n• Targeting the right psychology\n\nWhat's your experience with these strategies?"
        }
    ]
    
    return {
        "title": f"Social Media Posts Based on {source_title}",
        "posts": posts
    }

def generate_ad_copy(offer_intel, psych_intel, source_title):
    """Generate advertising copy"""
    main_benefits = offer_intel.get('main_benefits', 'transformative results')
    emotional_triggers = psych_intel.get('emotional_triggers', 'achievement')
    
    return {
        "title": f"Ad Copy Based on {source_title} Analysis",
        "headline": f"Finally, The {main_benefits} You've Been Searching For",
        "subheadline": f"Discover what {source_title} teaches about {emotional_triggers}",
        "description": f"Based on our analysis of {source_title}, we've identified the exact strategies you need to achieve {main_benefits}.",
        "call_to_action": f"Get These {source_title} Insights Now"
    }

def generate_blog_post(offer_intel, psych_intel, source_title):
    """Generate blog post content"""
    main_benefits = offer_intel.get('main_benefits', 'success')
    emotional_triggers = psych_intel.get('emotional_triggers', 'motivation')
    
    return {
        "title": f"What {source_title} Teaches About {main_benefits}",
        "introduction": f"After analyzing {source_title}, we've uncovered valuable insights about achieving {main_benefits}.",
        "sections": [
            {
                "heading": f"The Psychology Behind {emotional_triggers}",
                "content": f"Our analysis reveals that {emotional_triggers} is crucial for understanding success patterns."
            },
            {
                "heading": f"Key Strategies from {source_title}",
                "content": f"The strategies identified show a clear pattern designed to achieve {main_benefits}."
            }
        ],
        "conclusion": f"The success of {source_title} isn't accidental. By understanding {emotional_triggers}, you can achieve similar {main_benefits}."
    }

def generate_generic_content(content_type, offer_intel, psych_intel, source_title):
    """Generate generic content for unsupported types"""
    return {
        "title": f"{content_type.replace('_', ' ').title()} Based on {source_title}",
        "content": f"Content generated from analysis of {source_title}",
        "intelligence_summary": {
            "offer_intelligence": offer_intel,
            "psychology_intelligence": psych_intel,
            "source": source_title
        }
    }

async def save_generated_content_crud(
    db: AsyncSession,
    user: User,
    campaign_id: str,
    content_type: str,
    content: Dict[str, Any],
    intelligence_id: str
) -> str:
    """Save generated content using CRUD patterns"""
    try:
        content_id = str(uuid.uuid4())
        
        content_data = {
            "id": content_id,
            "user_id": user.id,
            "company_id": user.company_id,
            "campaign_id": UUID(campaign_id),
            "content_type": content_type,
            "content_title": content.get("title", f"Generated {content_type}"),
            "content_body": json.dumps(content),
            "content_metadata": content.get("metadata", {}),
            "intelligence_used": {"intelligence_id": intelligence_id},
            "performance_data": content.get("performance_predictions", {}),
            "is_published": False
        }
        
        # ✅ CRUD MIGRATION: Use CRUD to save content
        created_content = await intelligence_crud.create_generated_content(
            db=db,
            content_data=content_data
        )
        
        return str(created_content.id)
        
    except Exception as e:
        logger.error(f"❌ Failed to save content via CRUD: {e}")
        raise

# ============================================================================
# ✅ TEST AND DEBUG ENDPOINTS
# ============================================================================

@router.get("/test-route")
async def test_route():
    """Test endpoint to verify route mounting"""
    return {
        "message": "Content routes are working!",
        "mounted_at": "/api/intelligence/content",
        "endpoints": {
            "generate": "POST /api/intelligence/content/generate",
            "get_content": "GET /api/intelligence/content/{campaign_id}",
            "get_detail": "GET /api/intelligence/content/{campaign_id}/content/{content_id}",
            "update": "PUT /api/intelligence/content/{campaign_id}/content/{content_id}",
            "delete": "DELETE /api/intelligence/content/{campaign_id}/content/{content_id}"
        },
        "timestamp": datetime.now().isoformat()
    }