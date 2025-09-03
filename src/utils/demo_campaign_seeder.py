# src/utils/demo_campaign_seeder.py
"""
Demo Campaign Seeder - Creates educational demo campaigns for new users
🎯 FIXED: Campaign + Intelligence Only - Users test content generation manually
"""
from datetime import datetime, timezone
import uuid
import json
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.campaign import Campaign, AutoAnalysisStatus, CampaignStatus, CampaignWorkflowState
from src.core.crud.intelligence_crud import intelligence_crud, GeneratedContent, IntelligenceSourceType, AnalysisStatus

import logging

from src.utils.json_utils import safe_json_dumps

logger = logging.getLogger(__name__)

class DemoCampaignSeeder:
    """Creates comprehensive demo campaigns for user onboarding"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_demo_campaign(self, company_id: uuid.UUID, user_id: uuid.UUID) -> Campaign:
        """
        Create demo campaign with intelligence analysis - STOPS BEFORE CONTENT GENERATION
        🎯 Perfect onboarding: Users see analysis results, then manually test content tools
        """
        try:
            logger.info(f"🎭 Creating demo campaign with intelligence for company {company_id}")
            
            # ✅ STEP 1: Create demo campaign
            demo_campaign = Campaign(
                id=uuid.uuid4(),
                title="🎯 Demo: Social Media Scheduler Analysis",
                description="This is a demo campaign showing how CampaignForge analyzes competitors. Try the content generation tools when you're ready!",
                keywords=["social media", "scheduling", "automation", "marketing"],
                target_audience="Small business owners and marketing teams who need to manage multiple social media accounts efficiently",
                company_id=company_id,
                user_id=user_id,
                
                # Demo competitor URL - analyzed
                salespage_url="https://buffer.com",
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
                content_generated=0,  # ✅ ZERO - User will generate manually
                generated_content_count=0,
                
                # Step states: Step 1 complete, Step 2 ready
                step_states={
                    "step_1": {
                        "status": "completed",
                        "progress": 100,
                        "can_skip": False,
                        "description": "Campaign Setup & Analysis - COMPLETE ✅"
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
                generate_content_after_analysis=False,  # ✅ MANUAL ONLY
                
                # Demo settings
                settings={
                    "demo_campaign": True,
                    "demo_created_at": datetime.now(timezone.utc).isoformat(),
                    "demo_version": "1.0",
                    "demo_description": "Analysis complete - ready for content generation testing",
                    "user_instructions": "This demo shows completed analysis. Use content generation tools to create marketing materials."
                }
            )

            # Set analysis timestamps
            demo_campaign.auto_analysis_started_at = datetime.now(timezone.utc)
            demo_campaign.auto_analysis_completed_at = datetime.now(timezone.utc)
            
            logger.info("✅ STEP 1: Demo campaign created, saving to database...")
            
            # Save the campaign
            self.db.add(demo_campaign)
            await self.db.commit()
            await self.db.refresh(demo_campaign)
            
            logger.info(f"✅ STEP 1 COMPLETE: Demo campaign saved: {demo_campaign.id}")
            
            # ✅ STEP 2: Create demo intelligence (realistic Buffer analysis)
            logger.info("🧠 STEP 2: Creating demo intelligence analysis...")
            try:
                demo_intelligence = await self._create_demo_intelligence(demo_campaign.id, user_id, company_id)
                logger.info(f"✅ STEP 2 COMPLETE: Demo intelligence created: {demo_intelligence.id}")
            except Exception as intel_error:
                logger.error(f"❌ Demo intelligence creation failed: {intel_error}")
                # Campaign still works without intelligence, but log the error
                
            # ✅ STEP 3: DELIBERATELY SKIP CONTENT GENERATION
            logger.info("📝 STEP 3: SKIPPING content generation - users will test manually")
            logger.info("🎯 Demo Philosophy: Show analysis results, let users discover content tools themselves")
            
            logger.info(f"🎉 DEMO READY FOR USER TESTING: {demo_campaign.id}")
            logger.info("📋 Users can now:")
            logger.info("   • View comprehensive analysis results")
            logger.info("   • Explore intelligence insights")
            logger.info("   • Test content generation tools manually")
            logger.info("   • Learn the workflow at their own pace")
            
            return demo_campaign
            
        except Exception as e:
            logger.error(f"❌ Demo creation failed: {str(e)}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            await self.db.rollback()
            raise e
    
    async def _create_demo_intelligence(self, campaign_id: uuid.UUID, user_id: uuid.UUID, company_id: uuid.UUID) -> CampaignIntelligence:
        """Create demo intelligence analysis results"""
        
        demo_intelligence = CampaignIntelligence(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            user_id=user_id,
            company_id=company_id,
            
            source_url="https://buffer.com",
            source_title="Buffer - Social Media Management Platform",
            source_type=IntelligenceSourceType.SALES_PAGE,
            analysis_status=AnalysisStatus.COMPLETED,
            confidence_score=0.92,
            
            # Realistic analysis results
            offer_intelligence=safe_json_dumps({
                "products": [
                    {
                        "name": "Buffer Publish",
                        "description": "Schedule and publish content across social platforms",
                        "price": "$6/month",
                        "value_proposition": "Save time with batch scheduling and content planning"
                    },
                    {
                        "name": "Buffer Analyze", 
                        "description": "Social media analytics and reporting",
                        "price": "$35/month",
                        "value_proposition": "Data-driven insights to improve social performance"
                    }
                ],
                "pricing": [
                    {"tier": "Free", "price": "$0", "features": "3 social accounts, 10 scheduled posts"},
                    {"tier": "Essentials", "price": "$6/month", "features": "Unlimited posts, 1 user"},
                    {"tier": "Team", "price": "$12/month", "features": "Unlimited posts, 2 users"}
                ],
                "value_propositions": [
                    "Save hours every week with smart scheduling",
                    "Grow your audience with consistent posting",
                    "Analyze what works with detailed insights",
                    "Collaborate seamlessly with team members"
                ],
                "guarantees": [
                    "14-day free trial",
                    "Cancel anytime",
                    "No setup fees"
                ]
            }),
            
            psychology_intelligence=safe_json_dumps({
                "target_audience": "Small business owners, marketing teams, social media managers",
                "pain_points": [
                    "Spending too much time on social media management",
                    "Inconsistent posting schedule hurting engagement", 
                    "Difficulty measuring social media ROI",
                    "Team coordination challenges",
                    "Content planning overwhelm"
                ],
                "emotional_triggers": [
                    "Time scarcity and efficiency",
                    "Professional growth and success",
                    "Simplicity and ease of use",
                    "Social proof and popularity",
                    "Control and organization"
                ],
                "persuasion_techniques": [
                    "Social proof (customer testimonials)",
                    "Free trial reduces risk",
                    "Simple pricing structure",
                    "Feature comparison tables",
                    "Success stories and case studies"
                ]
            }),
            
            competitive_intelligence=safe_json_dumps({
                "strengths": [
                    "Clean, intuitive interface",
                    "Strong brand recognition",
                    "Comprehensive feature set",
                    "Good customer support",
                    "Reliable scheduling"
                ],
                "weaknesses": [
                    "Limited advanced analytics in lower tiers",
                    "No direct Instagram publishing on free plan",
                    "Fewer automation features compared to competitors",
                    "Limited video editing capabilities"
                ],
                "opportunities": [
                    "Emphasize superior analytics capabilities",
                    "Highlight more affordable pricing",
                    "Focus on better automation features",
                    "Promote stronger customer support",
                    "Showcase advanced team collaboration tools"
                ]
            }),
            
            content_intelligence=safe_json_dumps({
                "content_themes": [
                    "Time-saving automation",
                    "Professional social presence", 
                    "Data-driven growth",
                    "Team collaboration",
                    "Content consistency"
                ],
                "messaging_angles": [
                    "Stop wasting time on manual posting",
                    "Grow your social media like a pro",
                    "Your social media, simplified",
                    "Better results with less effort",
                    "Professional social media made easy"
                ],
                "content_gaps": [
                    "More video content needed",
                    "Industry-specific case studies",
                    "Advanced strategy guides",
                    "Integration tutorials"
                ]
            }),
            
            brand_intelligence=safe_json_dumps({
                "brand_personality": "Professional, friendly, helpful, innovative",
                "brand_values": ["Simplicity", "Efficiency", "Growth", "Collaboration"],
                "visual_style": "Clean, modern, blue and white color scheme",
                "tone_of_voice": "Professional yet approachable, helpful, solution-focused"
            }),
            
            # Demo scientific intelligence (showing amplification)
            scientific_intelligence=safe_json_dumps({
                "research_backing": [
                    {
                        "finding": "Consistent social media posting increases engagement by 67%",
                        "source": "Social Media Marketing Research 2024",
                        "relevance": "Supports scheduling value proposition"
                    },
                    {
                        "finding": "Businesses using analytics see 23% better ROI on social media",
                        "source": "Digital Marketing Institute Study",
                        "relevance": "Validates analytics feature importance"
                    }
                ],
                "psychological_principles": [
                    {
                        "principle": "Consistency Bias",
                        "application": "Regular posting builds trust and credibility"
                    },
                    {
                        "principle": "Social Proof",
                        "application": "Customer testimonials and user counts build confidence"
                    }
                ]
            }),
            
            # Demo credibility intelligence
            credibility_intelligence=safe_json_dumps({
                "trust_signals": [
                    "Over 140,000 customers worldwide",
                    "Trusted by major brands like Microsoft, Shopify",
                    "14-day free trial with no credit card required",
                    "99.9% uptime guarantee",
                    "Award-winning customer support"
                ],
                "authority_indicators": [
                    "Founded in 2010 - established player",
                    "Featured in TechCrunch, Forbes, Entrepreneur",
                    "Active thought leadership in social media space",
                    "Regular industry reports and insights"
                ]
            }),
            
            processing_metadata=safe_json_dumps({
                "demo_intelligence": True,
                "amplification_applied": True,
                "amplification_method": "demo_enhanced_analysis",
                "confidence_boost": 0.15,
                "analysis_type": "comprehensive_demo",
                "created_for_onboarding": True
            })
        )
        
        self.db.add(demo_intelligence)
        await self.db.commit()
        await self.db.refresh(demo_intelligence)
        
        return demo_intelligence
    
    async def check_and_create_demo_campaign(self, company_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Campaign]:
        """
        Check if a demo campaign exists for this company, create one if not
        🎯 Call this when users access the campaigns page
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
            
            # Create demo campaign
            demo_campaign = await self.create_demo_campaign(company_id, user_id)
            logger.info(f"✅ Demo campaign created for new company {company_id}")
            return demo_campaign
            
        except Exception as e:
            logger.error(f"❌ Error checking/creating demo campaign: {str(e)}")
            return None


# ============================================================================
# 🎯 INTEGRATION FUNCTIONS
# ============================================================================

async def ensure_demo_campaign_exists(db: AsyncSession, company_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """
    Ensure a demo campaign exists for the company
    🎯 Call this from your campaigns list endpoint
    """
    try:
        seeder = DemoCampaignSeeder(db)
        demo_campaign = await seeder.check_and_create_demo_campaign(company_id, user_id)
        return demo_campaign is not None
    except Exception as e:
        logger.error(f"❌ Failed to ensure demo campaign exists: {str(e)}")
        return False

async def create_demo_for_new_company(db: AsyncSession, company_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """
    Create demo campaign for a newly registered company
    🎯 Call this from your company/user registration process
    """
    try:
        seeder = DemoCampaignSeeder(db)
        demo_campaign = await seeder.create_demo_campaign(company_id, user_id)
        logger.info(f"🎭 Demo campaign created for new company: {demo_campaign.id}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create demo for new company: {str(e)}")
        return False

def is_demo_campaign(campaign: Campaign) -> bool:
    """Check if a campaign is a demo campaign"""
    return campaign.settings.get('demo_campaign', False) if campaign.settings else False