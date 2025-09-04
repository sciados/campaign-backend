# src/utils/demo_campaign_seeder.py - COMPLETE FOR NEW SCHEMA
"""
Demo Campaign Seeder - Creates educational demo campaigns for new users
FIXED: Updated to use new optimized intelligence schema (IntelligenceCore + normalized tables)
COMPLETE: Full implementation with all methods and integration functions
"""
from datetime import datetime, timezone
import uuid
import json
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.campaign import Campaign, AutoAnalysisStatus, CampaignStatus, CampaignWorkflowState
from src.core.crud.intelligence_crud import intelligence_crud  # FIXED: Use new CRUD
from src.models.intelligence import IntelligenceSourceType, AnalysisStatus  # FIXED: IntelligenceSourceType is now enum
import logging

logger = logging.getLogger(__name__)

class DemoCampaignSeeder:
    """Creates comprehensive demo campaigns for user onboarding - FIXED FOR NEW SCHEMA"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_demo_campaign(self, company_id: uuid.UUID, user_id: uuid.UUID) -> Campaign:
        """
        Create demo campaign with intelligence analysis - FIXED FOR NEW SCHEMA
        Perfect onboarding: Users see analysis results, then manually test content tools
        """
        try:
            logger.info(f"Creating demo campaign with NEW SCHEMA intelligence for company {company_id}")
            
            # STEP 1: Create demo campaign
            demo_campaign = Campaign(
                id=uuid.uuid4(),
                title="Demo: Social Media Scheduler Analysis",
                description="This is a demo campaign showing how CampaignForge analyzes competitors. Try the content generation tools when you're ready!",
                keywords=["social media", "scheduling", "automation", "marketing"],
                target_audience="Small business owners and marketing teams who need to manage multiple social media accounts efficiently",
                company_id=company_id,
                user_id=user_id,
                
                # Demo competitor URL - analyzed
                salespage_url="https://buffer.com",
                product_name="Advanced Social Media Manager Pro",
                auto_analysis_enabled=True,
                auto_analysis_status=AutoAnalysisStatus.COMPLETED,
                
                # Analysis completed with high confidence
                analysis_confidence_score=0.92,
                analysis_summary={
                    "competitor_analyzed": "Buffer - Social Media Management Platform",
                    "analysis_type": "Comprehensive competitor analysis",
                    "key_findings": [
                        "Freemium model with 3-account limit",
                        "Premium analytics at $35/month",
                        "Strong brand recognition but limited automation"
                    ],
                    "content_opportunities": [
                        "Email sequences highlighting unlimited accounts",
                        "Ad copy emphasizing cost savings",
                        "Social posts showcasing advanced features"
                    ],
                    "competitive_advantages": [
                        "No account limits vs Buffer's 3-account restriction",
                        "Included analytics vs $35/month add-on",
                        "Advanced automation features"
                    ],
                    "confidence_level": "High - Ready for content generation",
                    "next_step": "Use content generation tools to create marketing materials"
                },
                
                # Campaign ready for content generation
                status=CampaignStatus.ANALYSIS_COMPLETE,
                workflow_state=CampaignWorkflowState.ANALYSIS_COMPLETE,
                
                # Analysis complete, content ready to be generated
                sources_count=1,
                sources_processed=1,
                intelligence_extracted=1,
                intelligence_count=1,
                content_generated=0,  # ZERO - User will generate manually
                generated_content_count=0,
                
                # Step states: Step 1 complete, Step 2 ready
                step_states={
                    "step_1": {
                        "status": "completed",
                        "progress": 100,
                        "can_skip": False,
                        "description": "Campaign Setup & Analysis - COMPLETE"
                    },
                    "step_2": {
                        "status": "available", 
                        "progress": 0,
                        "can_skip": False,
                        "description": "Content Generation - Ready when you are!"
                    }
                },
                completed_steps=[1],
                available_steps=[1, 2],
                active_steps=[2],  # Ready for Step 2
                last_active_step=2,
                
                # Content preferences ready for generation
                content_types=["email_sequence", "ad_copy", "social_post"],
                content_tone="professional",
                content_style="modern",
                generate_content_after_analysis=False,  # MANUAL ONLY
                
                # Demo settings
                settings={
                    "demo_campaign": True,
                    "demo_created_at": datetime.now(timezone.utc).isoformat(),
                    "demo_version": "2.0_new_schema",
                    "demo_description": "Analysis complete - ready for content generation testing",
                    "user_instructions": "This demo shows completed analysis. Use content generation tools to create marketing materials.",
                    "schema_version": "optimized_normalized"
                }
            )

            # Set analysis timestamps
            demo_campaign.auto_analysis_started_at = datetime.now(timezone.utc)
            demo_campaign.auto_analysis_completed_at = datetime.now(timezone.utc)
            
            logger.info("STEP 1: Demo campaign created, saving to database...")
            
            # Save the campaign
            self.db.add(demo_campaign)
            await self.db.commit()
            await self.db.refresh(demo_campaign)
            
            logger.info(f"STEP 1 COMPLETE: Demo campaign saved: {demo_campaign.id}")
            
            # STEP 2: Create demo intelligence using NEW SCHEMA
            logger.info("STEP 2: Creating demo intelligence analysis using NEW SCHEMA...")
            try:
                demo_intelligence_id = await self._create_demo_intelligence_new_schema(demo_campaign.id, user_id, company_id)
                logger.info(f"STEP 2 COMPLETE: Demo intelligence created: {demo_intelligence_id}")
                
                # Update campaign with intelligence reference
                demo_campaign.analysis_intelligence_id = demo_intelligence_id
                await self.db.commit()
                
            except Exception as intel_error:
                logger.error(f"Demo intelligence creation failed: {intel_error}")
                # Campaign still works without intelligence, but log the error
                
            # STEP 3: DELIBERATELY SKIP CONTENT GENERATION
            logger.info("STEP 3: SKIPPING content generation - users will test manually")
            logger.info("Demo Philosophy: Show analysis results, let users discover content tools themselves")
            
            logger.info(f"DEMO READY FOR USER TESTING: {demo_campaign.id}")
            logger.info("Users can now:")
            logger.info("   • View comprehensive analysis results")
            logger.info("   • Explore intelligence insights")
            logger.info("   • Test content generation tools manually")
            logger.info("   • Learn the workflow at their own pace")
            
            return demo_campaign
            
        except Exception as e:
            logger.error(f"Demo creation failed: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            await self.db.rollback()
            raise e
    
    async def _create_demo_intelligence_new_schema(self, campaign_id: uuid.UUID, user_id: uuid.UUID, company_id: uuid.UUID) -> str:
        """
        Create demo intelligence analysis using NEW OPTIMIZED SCHEMA
        FIXED: Uses intelligence_crud.create_intelligence instead of direct model creation
        """
        try:
            logger.info("Creating demo intelligence using NEW SCHEMA (IntelligenceCore + normalized tables)")
            
            # FIXED: Use NEW SCHEMA structure via intelligence_crud
            demo_analysis_data = {
                "product_name": "Advanced Social Media Manager Pro",
                "source_url": "https://buffer.com",
                "confidence_score": 0.92,
                "analysis_method": "demo_comprehensive_analysis",
                
                # Offer intelligence data (will be stored in product_data table)
                "offer_intelligence": {
                    "key_features": [
                        "Unlimited social media accounts",
                        "Advanced scheduling with best-time optimization", 
                        "Comprehensive analytics dashboard",
                        "Team collaboration tools",
                        "Content calendar with drag-drop",
                        "Auto-posting with smart queues",
                        "Hashtag research and suggestions",
                        "Multi-platform publishing"
                    ],
                    "primary_benefits": [
                        "Save 10+ hours per week with automated scheduling",
                        "Increase engagement by 300% with optimal timing", 
                        "Scale your social presence across unlimited accounts",
                        "Make data-driven decisions with advanced analytics",
                        "Collaborate seamlessly with team members",
                        "Never miss a post with reliable automation",
                        "Grow your audience with consistent, quality content",
                        "Professional social media management made simple"
                    ],
                    "ingredients_list": [
                        "AI-powered scheduling engine",
                        "Advanced analytics and reporting system",
                        "Multi-platform integration APIs",
                        "Team collaboration framework",
                        "Content optimization algorithms",
                        "Automated hashtag research tools",
                        "Smart queue management system",
                        "Real-time engagement tracking"
                    ],
                    "target_conditions": [
                        "Inconsistent social media posting",
                        "Time management challenges with content",
                        "Poor social media engagement rates",
                        "Team coordination difficulties",
                        "Lack of analytics insights",
                        "Manual posting inefficiencies",
                        "Content planning overwhelm",
                        "Multi-platform management complexity"
                    ],
                    "usage_instructions": [
                        "Connect all your social media accounts in one dashboard",
                        "Schedule posts weeks in advance with the content calendar",
                        "Use AI-powered optimal timing for maximum engagement",
                        "Monitor performance with comprehensive analytics",
                        "Collaborate with team members using shared workspaces",
                        "Automate hashtag research for better discoverability",
                        "Set up smart queues for consistent posting",
                        "Track ROI and adjust strategy based on data insights"
                    ]
                },
                
                # Competitive intelligence (will be stored in market_data table)
                "competitive_intelligence": {
                    "market_category": "Social Media Management Software",
                    "market_positioning": "Premium all-in-one social media management solution",
                    "competitive_advantages": [
                        "Unlimited accounts vs Buffer's 3-account limit on free plan",
                        "Included advanced analytics vs Buffer's $35/month addon",
                        "AI-powered optimal timing vs manual scheduling",
                        "Advanced team collaboration features",
                        "Comprehensive hashtag research tools",
                        "Smart automation vs basic scheduling",
                        "Better value pricing structure",
                        "More robust API integrations"
                    ]
                },
                
                # Psychology intelligence (will be stored in market_data table)
                "psychology_intelligence": {
                    "target_audience": "Small business owners, marketing teams, social media managers, entrepreneurs, agencies"
                },
                
                # Additional demonstration data for content generation
                "content_intelligence": {
                    "content_themes": [
                        "Time-saving automation",
                        "Professional social presence", 
                        "Data-driven growth",
                        "Team collaboration efficiency",
                        "Content consistency",
                        "ROI optimization"
                    ],
                    "messaging_angles": [
                        "Stop wasting hours on manual social media posting",
                        "Grow your social media presence like a professional",
                        "Your social media success, automated and optimized",
                        "Better results with intelligent automation",
                        "Professional social media management for everyone",
                        "Scale your social presence without the complexity"
                    ],
                    "competitive_positioning": [
                        "Why pay extra for basic features that should be included?",
                        "Unlimited accounts vs artificial limitations",
                        "AI-powered optimization vs guesswork scheduling",
                        "All-in-one solution vs expensive add-ons"
                    ]
                },
                
                # Brand intelligence for content generation
                "brand_intelligence": {
                    "brand_personality": "Innovative, reliable, professional, user-focused",
                    "brand_values": ["Efficiency", "Innovation", "Reliability", "Growth", "Simplicity"],
                    "visual_style": "Modern, clean, professional with vibrant accents",
                    "tone_of_voice": "Professional yet friendly, confident, solution-focused, empowering"
                }
            }
            
            # FIXED: Use intelligence_crud.create_intelligence for NEW SCHEMA
            intelligence_id = await intelligence_crud.create_intelligence(
                db=self.db,
                analysis_data=demo_analysis_data
            )
            
            logger.info(f"Demo intelligence created using NEW SCHEMA: {intelligence_id}")
            return intelligence_id
            
        except Exception as e:
            logger.error(f"Error creating demo intelligence with NEW SCHEMA: {str(e)}")
            raise
    
    async def check_and_create_demo_campaign(self, company_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Campaign]:
        """
        Check if a demo campaign exists for this company, create one if not
        Call this when users access the campaigns page
        """
        try:
            # Check if demo campaign already exists
            existing_demo = await self.db.execute(
                select(Campaign).where(
                    Campaign.company_id == company_id,
                    Campaign.settings.op('->>')('demo_campaign') == 'true'
                )
            )
            
            if existing_demo.scalar_one_or_none():
                logger.info(f"Demo campaign already exists for company {company_id}")
                return None
            
            # Create demo campaign using NEW SCHEMA
            demo_campaign = await self.create_demo_campaign(company_id, user_id)
            logger.info(f"Demo campaign created for new company {company_id} using NEW SCHEMA")
            return demo_campaign
            
        except Exception as e:
            logger.error(f"Error checking/creating demo campaign: {str(e)}")
            return None
    
    async def create_content_generation_demo(self, company_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Campaign]:
        """
        Create a separate demo focused on content generation capabilities
        This shows users what they can create after analysis is complete
        """
        try:
            logger.info(f"Creating content generation demo for company {company_id}")
            
            # Create content-focused demo campaign
            content_demo = Campaign(
                id=uuid.uuid4(),
                title="Demo: Content Generation Showcase",
                description="See what CampaignForge can create! This demo shows completed content generation examples.",
                keywords=["content generation", "email marketing", "ad copy", "social media"],
                target_audience="Marketers who want to see content generation capabilities",
                company_id=company_id,
                user_id=user_id,
                
                # Already analyzed competitor
                salespage_url="https://mailchimp.com",
                product_name="Email Marketing Automation Suite",
                auto_analysis_enabled=True,
                auto_analysis_status=AutoAnalysisStatus.COMPLETED,
                
                # High confidence analysis
                analysis_confidence_score=0.95,
                
                # Ready for content generation
                status=CampaignStatus.CONTENT_GENERATION,
                workflow_state=CampaignWorkflowState.CONTENT_GENERATION,
                
                # Analysis complete, some content already generated as examples
                sources_count=1,
                sources_processed=1,
                intelligence_extracted=1,
                intelligence_count=1,
                content_generated=3,  # Some example content
                generated_content_count=3,
                
                # Both steps available
                step_states={
                    "step_1": {
                        "status": "completed",
                        "progress": 100,
                        "can_skip": False,
                        "description": "Analysis Complete - See Results"
                    },
                    "step_2": {
                        "status": "active",
                        "progress": 60,
                        "can_skip": False,
                        "description": "Content Generation - Examples Available!"
                    }
                },
                completed_steps=[1, 2],
                available_steps=[1, 2],
                active_steps=[2],
                last_active_step=2,
                
                # Content preferences
                content_types=["email_sequence", "ad_copy", "social_post", "blog_outline"],
                content_tone="professional",
                content_style="persuasive",
                generate_content_after_analysis=True,
                
                # Demo settings
                settings={
                    "demo_campaign": True,
                    "demo_type": "content_generation",
                    "demo_created_at": datetime.now(timezone.utc).isoformat(),
                    "demo_version": "2.0_content_showcase",
                    "demo_description": "Content generation examples and capabilities showcase",
                    "user_instructions": "Explore the content generation examples and try creating your own!",
                    "schema_version": "optimized_normalized",
                    "show_content_examples": True
                }
            )
            
            # Set timestamps
            demo_time = datetime.now(timezone.utc)
            content_demo.auto_analysis_started_at = demo_time
            content_demo.auto_analysis_completed_at = demo_time
            content_demo.content_generation_started_at = demo_time
            
            # Save the campaign
            self.db.add(content_demo)
            await self.db.commit()
            await self.db.refresh(content_demo)
            
            # Create intelligence for content demo
            content_intelligence_id = await self._create_content_demo_intelligence(content_demo.id, user_id, company_id)
            content_demo.analysis_intelligence_id = content_intelligence_id
            await self.db.commit()
            
            logger.info(f"Content generation demo created: {content_demo.id}")
            return content_demo
            
        except Exception as e:
            logger.error(f"Content demo creation failed: {str(e)}")
            return None
    
    async def _create_content_demo_intelligence(self, campaign_id: uuid.UUID, user_id: uuid.UUID, company_id: uuid.UUID) -> str:
        """Create intelligence for content generation demo"""
        try:
            content_demo_data = {
                "product_name": "Email Marketing Automation Suite",
                "source_url": "https://mailchimp.com",
                "confidence_score": 0.95,
                "analysis_method": "demo_content_focused_analysis",
                
                "offer_intelligence": {
                    "key_features": [
                        "Advanced email automation workflows",
                        "Drag-and-drop email builder",
                        "A/B testing capabilities", 
                        "Detailed analytics and reporting",
                        "CRM integration",
                        "Landing page builder",
                        "Social media advertising",
                        "E-commerce integration"
                    ],
                    "primary_benefits": [
                        "Increase email open rates by up to 67%",
                        "Automate follow-up sequences to save time",
                        "Create professional emails without coding",
                        "Track performance with detailed insights",
                        "Grow your subscriber list faster",
                        "Boost sales with targeted campaigns",
                        "Integrate with your existing tools",
                        "Scale your email marketing effortlessly"
                    ],
                    "target_conditions": [
                        "Low email engagement rates",
                        "Manual email sending inefficiencies",
                        "Lack of email marketing automation",
                        "Poor email design and formatting",
                        "Missing analytics and insights"
                    ],
                    "usage_instructions": [
                        "Set up automated welcome sequences for new subscribers",
                        "Create targeted campaigns based on user behavior",
                        "Design professional emails with drag-and-drop builder",
                        "A/B test subject lines and content for optimization",
                        "Monitor campaign performance and adjust strategy"
                    ]
                },
                
                "competitive_intelligence": {
                    "market_category": "Email Marketing Automation",
                    "market_positioning": "Comprehensive email marketing solution with advanced automation",
                    "competitive_advantages": [
                        "More advanced automation than basic email services",
                        "Better deliverability rates than competitors",
                        "More comprehensive analytics dashboard",
                        "Superior template design options",
                        "Better integration ecosystem"
                    ]
                },
                
                "psychology_intelligence": {
                    "target_audience": "Small business owners, e-commerce stores, marketing professionals, content creators"
                }
            }
            
            intelligence_id = await intelligence_crud.create_intelligence(
                db=self.db,
                analysis_data=content_demo_data
            )
            
            return intelligence_id
            
        except Exception as e:
            logger.error(f"Error creating content demo intelligence: {str(e)}")
            raise


# ============================================================================
# INTEGRATION FUNCTIONS - UPDATED FOR NEW SCHEMA
# ============================================================================

async def ensure_demo_campaign_exists(db: AsyncSession, company_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """
    Ensure a demo campaign exists for the company
    FIXED: Uses new schema intelligence creation
    """
    try:
        seeder = DemoCampaignSeeder(db)
        demo_campaign = await seeder.check_and_create_demo_campaign(company_id, user_id)
        return demo_campaign is not None
    except Exception as e:
        logger.error(f"Failed to ensure demo campaign exists: {str(e)}")
        return False

async def create_demo_for_new_company(db: AsyncSession, company_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """
    Create demo campaign for a newly registered company
    FIXED: Uses new schema intelligence creation
    """
    try:
        seeder = DemoCampaignSeeder(db)
        demo_campaign = await seeder.create_demo_campaign(company_id, user_id)
        logger.info(f"Demo campaign created for new company using NEW SCHEMA: {demo_campaign.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to create demo for new company: {str(e)}")
        return False

async def create_content_demo_for_company(db: AsyncSession, company_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """
    Create content generation demo for a company
    Shows users what they can accomplish with the content generation tools
    """
    try:
        seeder = DemoCampaignSeeder(db)
        content_demo = await seeder.create_content_generation_demo(company_id, user_id)
        if content_demo:
            logger.info(f"Content generation demo created: {content_demo.id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to create content demo: {str(e)}")
        return False

async def ensure_both_demos_exist(db: AsyncSession, company_id: uuid.UUID, user_id: uuid.UUID) -> Dict[str, bool]:
    """
    Ensure both analysis demo and content demo exist for comprehensive onboarding
    """
    try:
        seeder = DemoCampaignSeeder(db)
        
        # Check/create analysis demo
        analysis_demo = await seeder.check_and_create_demo_campaign(company_id, user_id)
        analysis_created = analysis_demo is not None
        
        # Check/create content demo
        content_demo = await seeder.create_content_generation_demo(company_id, user_id)
        content_created = content_demo is not None
        
        return {
            "analysis_demo_created": analysis_created,
            "content_demo_created": content_created,
            "total_demos": 1 + (1 if content_created else 0)
        }
    except Exception as e:
        logger.error(f"Failed to ensure both demos exist: {str(e)}")
        return {
            "analysis_demo_created": False,
            "content_demo_created": False,
            "total_demos": 0
        }

def is_demo_campaign(campaign: Campaign) -> bool:
    """Check if a campaign is a demo campaign"""
    return campaign.settings.get('demo_campaign', False) if campaign.settings else False

def get_demo_type(campaign: Campaign) -> str:
    """Get the type of demo campaign"""
    if not is_demo_campaign(campaign):
        return "none"
    return campaign.settings.get('demo_type', 'analysis')

def get_demo_instructions(campaign: Campaign) -> str:
    """Get user instructions for the demo campaign"""
    if not is_demo_campaign(campaign):
        return ""
    return campaign.settings.get('user_instructions', 'This is a demo campaign to help you learn the system.')

# ============================================================================
# DEMO CAMPAIGN MANAGEMENT
# ============================================================================

async def cleanup_old_demo_campaigns(db: AsyncSession, company_id: uuid.UUID, keep_recent: int = 2) -> int:
    """
    Clean up old demo campaigns, keeping only the most recent ones
    Useful for companies that might have accumulated multiple demos during testing
    """
    try:
        # Get all demo campaigns for the company
        demo_campaigns = await db.execute(
            select(Campaign).where(
                Campaign.company_id == company_id,
                Campaign.settings.op('->>')('demo_campaign') == 'true'
            ).order_by(Campaign.created_at.desc())
        )
        
        demo_list = demo_campaigns.scalars().all()
        
        if len(demo_list) <= keep_recent:
            return 0  # Nothing to clean up
        
        # Delete older demos
        campaigns_to_delete = demo_list[keep_recent:]
        deleted_count = 0
        
        for campaign in campaigns_to_delete:
            # Note: Intelligence records will be cascade deleted due to foreign key relationships
            await db.delete(campaign)
            deleted_count += 1
        
        await db.commit()
        logger.info(f"Cleaned up {deleted_count} old demo campaigns for company {company_id}")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up demo campaigns: {str(e)}")
        await db.rollback()
        return 0

async def get_company_demo_status(db: AsyncSession, company_id: uuid.UUID) -> Dict[str, Any]:
    """
    Get comprehensive demo status for a company
    Useful for admin dashboards and user onboarding tracking
    """
    try:
        # Get all demo campaigns
        demo_campaigns = await db.execute(
            select(Campaign).where(
                Campaign.company_id == company_id,
                Campaign.settings.op('->>')('demo_campaign') == 'true'
            ).order_by(Campaign.created_at.desc())
        )
        
        demo_list = demo_campaigns.scalars().all()
        
        demo_types = {}
        for campaign in demo_list:
            demo_type = get_demo_type(campaign)
            if demo_type not in demo_types:
                demo_types[demo_type] = []
            demo_types[demo_type].append({
                "id": str(campaign.id),
                "title": campaign.title,
                "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
                "status": campaign.status.value if campaign.status else "unknown",
                "workflow_state": campaign.workflow_state.value if campaign.workflow_state else "unknown"
            })
        
        return {
            "company_id": str(company_id),
            "total_demos": len(demo_list),
            "demo_types": demo_types,
            "has_analysis_demo": "analysis" in demo_types,
            "has_content_demo": "content_generation" in demo_types,
            "onboarding_complete": len(demo_types) >= 1,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting demo status: {str(e)}")
        return {
            "company_id": str(company_id),
            "total_demos": 0,
            "demo_types": {},
            "has_analysis_demo": False,
            "has_content_demo": False,
            "onboarding_complete": False,
            "error": str(e),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }