# src/utils/demo_campaign_seeder.py
"""
Demo Campaign Seeder - Creates educational demo campaigns for new users
🎯 Solves empty state issues while providing excellent onboarding
"""
from datetime import datetime, timezone
import uuid
import json
from sqlalchemy import DateTime, func
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.campaign import Campaign, AutoAnalysisStatus, CampaignStatus, CampaignWorkflowState
from src.models.intelligence import CampaignIntelligence, GeneratedContent, IntelligenceSourceType, AnalysisStatus

import logging
logger = logging.getLogger(__name__)

class DemoCampaignSeeder:
    """Creates comprehensive demo campaigns for user onboarding"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_demo_campaign(self, company_id: uuid.UUID, user_id: uuid.UUID) -> Campaign:
        """
        Create a complete demo campaign with analysis and generated content
        🎯 Shows users the full workflow and capabilities
        """
        try:
            logger.info(f"🎭 Creating demo campaign for company {company_id}")
            
            # Create the demo campaign
            demo_campaign = Campaign(
                id=uuid.uuid4(),
                title="🎯 Demo: Social Media Scheduler Analysis",
                description="This is a demo campaign showing how CampaignForge analyzes competitors and generates marketing content. Explore the analysis results and generated content to see what's possible!",
                keywords=["social media", "scheduling", "automation", "marketing"],
                target_audience="Small business owners and marketing teams who need to manage multiple social media accounts efficiently",
                company_id=company_id,
                user_id=user_id,
                
                # Demo competitor URL
                salespage_url="https://buffer.com",
                auto_analysis_enabled=True,
                auto_analysis_status=AutoAnalysisStatus.COMPLETED,
                auto_analysis_started_at = datetime.now(timezone.utc),
                auto_analysis_completed_at = datetime.now(timezone.utc),
                
                # Analysis results
                analysis_confidence_score=0.92,
                analysis_summary=self._get_demo_analysis_summary(),
                
                # Campaign status
                status=CampaignStatus.ANALYSIS_COMPLETE,
                workflow_state=CampaignWorkflowState.ANALYSIS_COMPLETE,
                
                # Progress tracking
                sources_count=1,
                sources_processed=1,
                intelligence_extracted=1,
                intelligence_count=1,
                content_generated=3,  # We'll create 3 demo content pieces
                generated_content_count=3,
                
                # Step states for 2-step workflow
                step_states={
                    "step_1": {
                        "status": "completed",
                        "progress": 100,
                        "can_skip": False,
                        "description": "Campaign Setup & Analysis"
                    },
                    "step_2": {
                        "status": "available", 
                        "progress": 75,
                        "can_skip": False,
                        "description": "Content Generation"
                    }
                },
                completed_steps=[1],
                available_steps=[1, 2],
                active_steps=[2],
                last_active_step=2,
                
                # Content preferences
                content_types=["email_sequence", "ad_copy", "social_post"],
                content_tone="professional",
                content_style="modern",
                
                # Settings
                settings={
                    "demo_campaign": True,
                    "demo_created_at": datetime.now(timezone.utc),
                    "demo_version": "1.0"
                }
            )
            
            # Save the campaign
            self.db.add(demo_campaign)
            await self.db.commit()
            await self.db.refresh(demo_campaign)
            
            # Create demo intelligence record
            demo_intelligence = await self._create_demo_intelligence(demo_campaign.id, user_id, company_id)
            
            # Create demo generated content
            await self._create_demo_content(demo_campaign.id, demo_intelligence.id, user_id, company_id)
            
            logger.info(f"✅ Demo campaign created successfully: {demo_campaign.id}")
            return demo_campaign
            
        except Exception as e:
            logger.error(f"❌ Failed to create demo campaign: {str(e)}")
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
            offer_intelligence=json.dumps({
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
            
            psychology_intelligence=json.dumps({
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
            
            competitive_intelligence=json.dumps({
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
            
            content_intelligence=json.dumps({
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
            
            brand_intelligence=json.dumps({
                "brand_personality": "Professional, friendly, helpful, innovative",
                "brand_values": ["Simplicity", "Efficiency", "Growth", "Collaboration"],
                "visual_style": "Clean, modern, blue and white color scheme",
                "tone_of_voice": "Professional yet approachable, helpful, solution-focused"
            }),
            
            # Demo scientific intelligence (showing amplification)
            scientific_intelligence=json.dumps({
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
            credibility_intelligence=json.dumps({
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
            
            processing_metadata=json.dumps({
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
    
    async def _create_demo_content(self, campaign_id: uuid.UUID, intelligence_id: uuid.UUID, user_id: uuid.UUID, company_id: uuid.UUID):
        """Create demo generated content pieces"""
        
        demo_content_pieces = [
            {
                "content_type": "email_sequence",
                "content_title": "5-Email Welcome Series for Social Media Tool",
                "content_body": json.dumps({
                    "emails": [
                        {
                            "subject": "Welcome! Your social media success starts now 🚀",
                            "body": "Hi there!\n\nWelcome to [Your Tool Name]! You've just joined thousands of businesses who've discovered the secret to effortless social media management.\n\nUnlike tools like Buffer that limit your free plan to just 3 accounts, we believe in giving you the freedom to grow from day one.\n\nHere's what makes us different:\n✅ Unlimited social accounts (even on free plan)\n✅ Advanced analytics that actually help you grow\n✅ Smart automation that saves you 10+ hours per week\n\nReady to see the difference? Let's get your first post scheduled!\n\n[Get Started Button]\n\nBest,\nThe [Your Tool] Team",
                            "day": 0
                        },
                        {
                            "subject": "The #1 mistake 87% of businesses make with social media",
                            "body": "Hi [Name],\n\nI just analyzed 10,000+ social media accounts, and I discovered something shocking...\n\n87% of businesses post inconsistently, killing their engagement rates.\n\nHere's what happens when you post irregularly:\n❌ Algorithm stops showing your content\n❌ Followers forget about your brand\n❌ Competitors steal your audience\n\nBut here's the good news...\n\nWith [Your Tool], you can schedule a month's worth of content in just 30 minutes. Our AI even suggests the best times to post for maximum engagement.\n\nWant to see how? Watch this 2-minute demo:\n\n[Watch Demo Button]\n\nTo your success,\n[Your Name]",
                            "day": 2
                        },
                        {
                            "subject": "Why [Competitor] customers are switching to us",
                            "body": "Hi [Name],\n\nJust last week, Sarah from Denver told me:\n\n\"I was paying Buffer $12/month for basic features. With [Your Tool], I get 10x more functionality for half the price. I should have switched months ago!\"\n\nShe's not alone. Here's why businesses are making the switch:\n\n🎯 Buffer charges $35/month for analytics. Ours are included FREE\n🎯 Buffer limits team collaboration. We offer unlimited team members\n🎯 Buffer lacks advanced automation. Our AI does the heavy lifting\n\nPlus, our customers see an average of 67% increase in engagement within 30 days.\n\nReady to join them?\n\n[Start Free Trial - No Credit Card Required]\n\nBest regards,\n[Your Name]",
                            "day": 5
                        }
                    ],
                    "metadata": {
                        "sequence_type": "welcome_onboarding",
                        "target_audience": "social_media_managers",
                        "tone": "professional_friendly",
                        "competitor_analysis": "buffer_comparison"
                    }
                }),
                "generation_settings": {
                    "style": "professional",
                    "tone": "helpful",
                    "competitor_focus": "buffer"
                }
            },
            {
                "content_type": "ad_copy",
                "content_title": "Facebook/Google Ads - Social Media Tool",
                "content_body": json.dumps({
                    "ads": [
                        {
                            "platform": "facebook",
                            "type": "conversion",
                            "headline": "Stop Wasting 10+ Hours/Week on Social Media",
                            "primary_text": "While you're manually posting one by one, your competitors are using smart automation to dominate social media.\n\nOur social media tool does what Buffer can't:\n✅ Unlimited accounts (Buffer limits you to 3)\n✅ Advanced analytics included (Buffer charges $35/month extra)\n✅ AI-powered posting optimization\n✅ True team collaboration\n\nJoin 50,000+ businesses saving 10+ hours weekly.\n\n👆 Start your free trial - no credit card required",
                            "cta": "Start Free Trial",
                            "audience": "business_owners_social_media"
                        },
                        {
                            "platform": "google",
                            "type": "search",
                            "headline_1": "Better Than Buffer",
                            "headline_2": "50% Less Cost, 10x Features",
                            "headline_3": "Free Trial - No Credit Card",
                            "description_1": "Get unlimited social accounts, advanced analytics, and AI automation. See why 50,000+ businesses switched from Buffer.",
                            "description_2": "Stop paying $35/month for basic analytics. Our advanced insights are included FREE. Start your trial today.",
                            "keywords": ["buffer alternative", "social media scheduler", "better than buffer"]
                        },
                        {
                            "platform": "linkedin",
                            "type": "sponsored_content",
                            "headline": "Why Smart Marketers Are Ditching Buffer",
                            "primary_text": "Buffer was great... in 2015.\n\nBut today's marketers need more than basic scheduling:\n\n🎯 Advanced AI optimization (not just basic scheduling)\n🎯 Comprehensive analytics (not $35/month add-ons)\n🎯 True collaboration tools (not limited team features)\n🎯 Unlimited growth potential (not artificial account limits)\n\nDiscover why 50,000+ professionals have upgraded to the next generation of social media management.\n\nSee the difference with a free trial →",
                            "cta": "Start Free Trial",
                            "audience": "marketing_professionals"
                        }
                    ]
                }),
                "generation_settings": {
                    "competitive_angle": "buffer_comparison",
                    "focus": "feature_superiority",
                    "tone": "confident_professional"
                }
            },
            {
                "content_type": "social_post",
                "content_title": "Social Media Content - Launch Sequence",
                "content_body": json.dumps({
                    "posts": [
                        {
                            "platform": "linkedin",
                            "content": "🚀 Just discovered something that's going to change how businesses think about social media management...\n\nAfter analyzing 10,000+ social accounts, we found that 87% of businesses are making the same critical mistake:\n\nThey're stuck with tools that worked 5 years ago.\n\nWhile Buffer charges $35/month for basic analytics, smart businesses are moving to platforms that include advanced AI optimization, unlimited accounts, and comprehensive analytics as standard features.\n\nThe result? 67% increase in engagement within 30 days.\n\nWhat old tool are you ready to upgrade? 👇\n\n#SocialMediaMarketing #MarketingAutomation #DigitalTransformation",
                            "image_suggestion": "Chart showing engagement improvement statistics",
                            "best_time": "Tuesday 9:00 AM"
                        },
                        {
                            "platform": "twitter",
                            "content": "Hot take: If you're still manually posting to social media in 2024, you're doing it wrong 🔥\n\nSmart businesses automate their social media and focus on:\n• Strategy (not busy work)\n• Engagement (not posting)\n• Results (not vanity metrics)\n\nTime to upgrade your approach 📈\n\n#SocialMediaTip #MarketingAutomation",
                            "image_suggestion": "Comparison graphic: Manual vs Automated workflow",
                            "best_time": "Wednesday 2:00 PM"
                        },
                        {
                            "platform": "facebook", 
                            "content": "📊 CASE STUDY: How one business increased their social media engagement by 67% in just 30 days\n\nThe secret? They stopped using outdated tools and upgraded to a platform with:\n\n✅ AI-powered posting optimization\n✅ Advanced analytics included (not $35/month extra)\n✅ Unlimited social accounts\n✅ True team collaboration\n\nWant to see similar results? Comment 'GROWTH' and I'll share the exact strategy they used.\n\n#SocialMediaGrowth #MarketingStrategy #BusinessGrowth",
                            "image_suggestion": "Before/after engagement statistics",
                            "best_time": "Thursday 7:00 PM"
                        }
                    ]
                }),
                "generation_settings": {
                    "content_mix": "educational_promotional",
                    "competitive_positioning": "innovation_focus",
                    "engagement_style": "high_value_content"
                }
            }
        ]
        
        for content_data in demo_content_pieces:
            demo_content = GeneratedContent(
                id=uuid.uuid4(),
                campaign_id=campaign_id,
                intelligence_source_id=intelligence_id,
                user_id=user_id,
                company_id=company_id,
                
                content_type=content_data["content_type"],
                content_title=content_data["content_title"],
                content_body=content_data["content_body"],
                
                generation_settings=json.dumps(content_data["generation_settings"]),
                content_metadata=json.dumps({
                    "demo_content": True,
                    "created_for_onboarding": True,
                    "content_quality": "high",
                    "competitive_analysis_applied": True
                }),
                
                intelligence_used=json.dumps({
                    "amplified": True,
                    "confidence_score": 0.92,
                    "competitive_insights": True,
                    "psychological_triggers": True,
                    "scientific_backing": True
                }),
                
                user_rating=5,  # Perfect demo content
                is_published=False,
                published_at=None,
                
                performance_data=json.dumps({
                    "demo_metrics": {
                        "estimated_engagement": "67% above average",
                        "conversion_potential": "high",
                        "competitive_advantage": "strong"
                    }
                })
            )
            
            self.db.add(demo_content)
        
        await self.db.commit()
        logger.info(f"✅ Created {len(demo_content_pieces)} demo content pieces")
    
    def _get_demo_analysis_summary(self) -> Dict[str, Any]:
        """Get comprehensive demo analysis summary for content generation"""
        return {
            "product_analysis": {
                "products": [
                    "Buffer Publish - Social media scheduling platform",
                    "Buffer Analyze - Social media analytics tool"
                ],
                "key_value_props": [
                    "Save time with batch scheduling",
                    "Grow with consistent posting", 
                    "Analyze performance with detailed insights",
                    "Collaborate seamlessly with teams",
                    "Professional social media presence"
                ],
                "pricing_strategy": [
                    "Freemium model with 3 account limit",
                    "Tiered pricing from $6-12/month",
                    "Analytics as premium add-on ($35/month)"
                ],
                "guarantees": [
                    "14-day free trial",
                    "Cancel anytime policy"
                ]
            },
            "audience_insights": {
                "target_audience": "Small business owners, marketing teams, social media managers",
                "pain_points": [
                    "Time-consuming manual posting",
                    "Inconsistent posting hurting engagement",
                    "Difficulty measuring social ROI",
                    "Team coordination challenges",
                    "Content planning overwhelm"
                ],
                "emotional_triggers": [
                    "Time scarcity and efficiency needs",
                    "Professional growth aspirations",
                    "Simplicity and ease of use desires",
                    "Social proof and validation",
                    "Control and organization needs"
                ],
                "persuasion_techniques": [
                    "Social proof through testimonials",
                    "Risk reduction with free trials",
                    "Simplicity in pricing structure",
                    "Feature comparison advantages"
                ]
            },
            "competitive_advantages": [
                "Emphasize unlimited accounts vs Buffer's 3-account limit",
                "Highlight included analytics vs Buffer's $35/month add-on",
                "Focus on advanced automation features",
                "Promote stronger team collaboration tools",
                "Showcase better pricing value"
            ],
            "content_opportunities": [
                "Create email sequences highlighting feature advantages",
                "Develop comparison-focused ad copy",
                "Generate social proof content with switching stories",
                "Build educational content around social media best practices",
                "Design case studies showing superior results",
                "Craft landing pages with competitive comparisons",
                "Produce video content demonstrating ease of use",
                "Write blog posts about social media automation trends"
            ],
            "amplification_data": {
                "scientific_backing_available": True,
                "credibility_enhancements": 0.87,
                "total_enhancements": 24,
                "confidence_boost": 0.15,
                "enhancement_quality": "excellent"
            }
        }
    
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