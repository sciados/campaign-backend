# src/content/services/content_orchestrator.py
"""
Content Generation Orchestrator
Routes intelligence analysis results to appropriate content generators based on user type and tier
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass

from src.core.database.session import AsyncSessionManager
from src.campaigns.models.campaign import Campaign
from src.users.models.user import User

logger = logging.getLogger(__name__)

class UserType(Enum):
    AFFILIATE = "affiliate"
    BUSINESS = "business"
    CREATOR = "creator"
    AGENCY = "agency"

class SubscriptionTier(Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class ContentType(Enum):
    # Email Marketing
    EMAIL_SEQUENCE = "email_sequence"
    EMAIL_NEWSLETTER = "email_newsletter"
    
    # Social Media
    SOCIAL_POSTS = "social_posts"
    INSTAGRAM_CAPTIONS = "instagram_captions"
    LINKEDIN_POSTS = "linkedin_posts"
    TWITTER_THREADS = "twitter_threads"
    
    # Advertising
    AD_COPY = "ad_copy"
    GOOGLE_ADS = "google_ads"
    FACEBOOK_ADS = "facebook_ads"
    
    # Long-form Content
    BLOG_ARTICLES = "blog_articles"
    SALES_PAGES = "sales_pages"
    PRODUCT_DESCRIPTIONS = "product_descriptions"
    
    # Video Content
    VIDEO_SCRIPTS = "video_scripts"
    YOUTUBE_SCRIPTS = "youtube_scripts"
    TIKTOK_SCRIPTS = "tiktok_scripts"
    
    # Visual Content
    IMAGE_CONCEPTS = "image_concepts"
    THUMBNAIL_IDEAS = "thumbnail_ideas"
    INFOGRAPHIC_CONCEPTS = "infographic_concepts"
    
    # Premium/Enterprise Only
    MARKET_ANALYSIS_REPORT = "market_analysis_report"
    COMPETITOR_INTELLIGENCE = "competitor_intelligence"
    STRATEGY_DOCUMENT = "strategy_document"
    BRAND_GUIDELINES = "brand_guidelines"
    CONVERSION_OPTIMIZATION = "conversion_optimization"

@dataclass
class ContentGenerationTask:
    content_type: ContentType
    priority: int  # 1 = highest, 10 = lowest
    estimated_tokens: int
    requires_premium: bool
    generator_class: str
    config: Dict[str, Any]

class ContentOrchestrator:
    """
    Main orchestrator that determines what content to generate based on:
    - User type (affiliate, business, creator, agency)
    - Subscription tier (free, basic, pro, enterprise)
    - Intelligence analysis results
    - User preferences/settings
    """
    
    def __init__(self):
        self.content_mappings = self._initialize_content_mappings()
        self.tier_limits = self._initialize_tier_limits()
    
    def _initialize_content_mappings(self) -> Dict[UserType, Dict[SubscriptionTier, List[ContentGenerationTask]]]:
        """Define what content each user type gets at each tier"""
        
        mappings = {
            UserType.AFFILIATE: {
                SubscriptionTier.FREE: [
                    ContentGenerationTask(
                        content_type=ContentType.EMAIL_SEQUENCE,
                        priority=1,
                        estimated_tokens=2000,
                        requires_premium=False,
                        generator_class="EmailSequenceGenerator",
                        config={"sequence_length": 3, "tone": "persuasive"}
                    ),
                    ContentGenerationTask(
                        content_type=ContentType.SOCIAL_POSTS,
                        priority=2,
                        estimated_tokens=500,
                        requires_premium=False,
                        generator_class="SocialPostGenerator",
                        config={"platforms": ["facebook", "instagram"], "count": 5}
                    )
                ],
                SubscriptionTier.BASIC: [
                    # All FREE content plus:
                    ContentGenerationTask(
                        content_type=ContentType.EMAIL_SEQUENCE,
                        priority=1,
                        estimated_tokens=4000,
                        requires_premium=False,
                        generator_class="EmailSequenceGenerator",
                        config={"sequence_length": 7, "tone": "persuasive", "personalization": True}
                    ),
                    ContentGenerationTask(
                        content_type=ContentType.AD_COPY,
                        priority=2,
                        estimated_tokens=1000,
                        requires_premium=False,
                        generator_class="AdCopyGenerator",
                        config={"platforms": ["facebook", "google"], "variations": 5}
                    ),
                    ContentGenerationTask(
                        content_type=ContentType.BLOG_ARTICLES,
                        priority=3,
                        estimated_tokens=3000,
                        requires_premium=False,
                        generator_class="BlogGenerator",
                        config={"count": 2, "seo_optimized": True}
                    )
                ],
                SubscriptionTier.PRO: [
                    # All BASIC content plus:
                    ContentGenerationTask(
                        content_type=ContentType.VIDEO_SCRIPTS,
                        priority=3,
                        estimated_tokens=2000,
                        requires_premium=True,
                        generator_class="VideoScriptGenerator",
                        config={"types": ["review", "tutorial", "promotional"], "count": 3}
                    ),
                    ContentGenerationTask(
                        content_type=ContentType.COMPETITOR_INTELLIGENCE,
                        priority=4,
                        estimated_tokens=5000,
                        requires_premium=True,
                        generator_class="CompetitorAnalysisGenerator",
                        config={"detailed": True, "actionable_insights": True}
                    )
                ]
            },
            
            UserType.BUSINESS: {
                SubscriptionTier.FREE: [
                    ContentGenerationTask(
                        content_type=ContentType.PRODUCT_DESCRIPTIONS,
                        priority=1,
                        estimated_tokens=1000,
                        requires_premium=False,
                        generator_class="ProductDescriptionGenerator",
                        config={"variations": 3, "seo_focused": True}
                    ),
                    ContentGenerationTask(
                        content_type=ContentType.EMAIL_NEWSLETTER,
                        priority=2,
                        estimated_tokens=1500,
                        requires_premium=False,
                        generator_class="NewsletterGenerator",
                        config={"template": "business", "sections": 4}
                    )
                ],
                SubscriptionTier.PRO: [
                    # Comprehensive business content
                    ContentGenerationTask(
                        content_type=ContentType.SALES_PAGES,
                        priority=1,
                        estimated_tokens=6000,
                        requires_premium=True,
                        generator_class="SalesPageGenerator",
                        config={"sections": ["hero", "benefits", "social_proof", "cta"], "conversion_optimized": True}
                    ),
                    ContentGenerationTask(
                        content_type=ContentType.MARKET_ANALYSIS_REPORT,
                        priority=2,
                        estimated_tokens=15000,
                        requires_premium=True,
                        generator_class="MarketAnalysisGenerator",
                        config={"comprehensive": True, "charts": True, "recommendations": True}
                    )
                ],
                SubscriptionTier.ENTERPRISE: [
                    # Full enterprise suite
                    ContentGenerationTask(
                        content_type=ContentType.STRATEGY_DOCUMENT,
                        priority=1,
                        estimated_tokens=25000,
                        requires_premium=True,
                        generator_class="StrategyDocumentGenerator",
                        config={"comprehensive": True, "quarterly_plan": True, "budget_allocation": True}
                    ),
                    ContentGenerationTask(
                        content_type=ContentType.BRAND_GUIDELINES,
                        priority=2,
                        estimated_tokens=10000,
                        requires_premium=True,
                        generator_class="BrandGuidelinesGenerator",
                        config={"voice_tone": True, "visual_guidelines": True, "usage_examples": True}
                    )
                ]
            },
            
            UserType.CREATOR: {
                SubscriptionTier.FREE: [
                    ContentGenerationTask(
                        content_type=ContentType.INSTAGRAM_CAPTIONS,
                        priority=1,
                        estimated_tokens=800,
                        requires_premium=False,
                        generator_class="InstagramCaptionGenerator",
                        config={"count": 10, "hashtag_research": True}
                    ),
                    ContentGenerationTask(
                        content_type=ContentType.YOUTUBE_SCRIPTS,
                        priority=2,
                        estimated_tokens=2000,
                        requires_premium=False,
                        generator_class="YouTubeScriptGenerator",
                        config={"length": "5-10min", "engagement_hooks": True}
                    )
                ],
                SubscriptionTier.PRO: [
                    ContentGenerationTask(
                        content_type=ContentType.TIKTOK_SCRIPTS,
                        priority=1,
                        estimated_tokens=1000,
                        requires_premium=True,
                        generator_class="TikTokScriptGenerator",
                        config={"viral_elements": True, "trend_integration": True, "count": 10}
                    ),
                    ContentGenerationTask(
                        content_type=ContentType.THUMBNAIL_IDEAS,
                        priority=2,
                        estimated_tokens=1500,
                        requires_premium=True,
                        generator_class="ThumbnailConceptGenerator",
                        config={"eye_catching": True, "a_b_variations": True, "count": 5}
                    )
                ]
            },
            
            UserType.AGENCY: {
                SubscriptionTier.PRO: [
                    # Agency gets comprehensive suite
                    ContentGenerationTask(
                        content_type=ContentType.STRATEGY_DOCUMENT,
                        priority=1,
                        estimated_tokens=20000,
                        requires_premium=True,
                        generator_class="AgencyStrategyGenerator",
                        config={"client_focused": True, "presentation_ready": True}
                    ),
                    ContentGenerationTask(
                        content_type=ContentType.COMPETITOR_INTELLIGENCE,
                        priority=2,
                        estimated_tokens=10000,
                        requires_premium=True,
                        generator_class="CompetitorAnalysisGenerator",
                        config={"detailed": True, "swot_analysis": True, "opportunities": True}
                    )
                ],
                SubscriptionTier.ENTERPRISE: [
                    # Full agency enterprise suite
                    ContentGenerationTask(
                        content_type=ContentType.MARKET_ANALYSIS_REPORT,
                        priority=1,
                        estimated_tokens=30000,
                        requires_premium=True,
                        generator_class="EnterpriseMarketAnalysis",
                        config={"white_label": True, "executive_summary": True, "roi_projections": True}
                    )
                ]
            }
        }
        
        return mappings
    
    def _initialize_tier_limits(self) -> Dict[SubscriptionTier, Dict[str, Any]]:
        """Define limits for each subscription tier"""
        return {
            SubscriptionTier.FREE: {
                "max_monthly_tokens": 10000,
                "max_concurrent_generations": 1,
                "premium_content": False,
                "priority_queue": False
            },
            SubscriptionTier.BASIC: {
                "max_monthly_tokens": 50000,
                "max_concurrent_generations": 2,
                "premium_content": False,
                "priority_queue": False
            },
            SubscriptionTier.PRO: {
                "max_monthly_tokens": 200000,
                "max_concurrent_generations": 5,
                "premium_content": True,
                "priority_queue": True
            },
            SubscriptionTier.ENTERPRISE: {
                "max_monthly_tokens": 1000000,
                "max_concurrent_generations": 10,
                "premium_content": True,
                "priority_queue": True,
                "white_label": True
            }
        }
    
    async def orchestrate_content_generation(
        self, 
        campaign_id: str, 
        user_id: str, 
        intelligence_data: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main orchestration method that:
        1. Determines user type and tier
        2. Gets appropriate content tasks
        3. Queues content generation jobs
        4. Returns generation status
        """
        
        try:
            # Get user and campaign info
            user = await self._get_user_info(user_id)
            campaign = await self._get_campaign_info(campaign_id)
            
            user_type = UserType(user.user_type)
            subscription_tier = SubscriptionTier(user.subscription_tier)
            
            # Get content tasks for this user type/tier
            content_tasks = self._get_content_tasks(user_type, subscription_tier)
            
            # Filter tasks based on user preferences and usage limits
            filtered_tasks = await self._filter_tasks(
                content_tasks, 
                user, 
                user_preferences or {}
            )
            
            # Queue generation jobs
            generation_jobs = []
            for task in filtered_tasks:
                job_id = await self._queue_content_generation_job(
                    campaign_id=campaign_id,
                    user_id=user_id,
                    task=task,
                    intelligence_data=intelligence_data,
                    priority=task.priority
                )
                generation_jobs.append({
                    "job_id": job_id,
                    "content_type": task.content_type.value,
                    "estimated_completion": self._estimate_completion_time(task),
                    "status": "queued"
                })
            
            logger.info(f"Orchestrated {len(generation_jobs)} content generation jobs for campaign {campaign_id}")
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "user_type": user_type.value,
                "subscription_tier": subscription_tier.value,
                "jobs": generation_jobs,
                "total_estimated_tokens": sum(task.estimated_tokens for task in filtered_tasks),
                "estimated_completion_time": max(
                    self._estimate_completion_time(task) for task in filtered_tasks
                ) if filtered_tasks else 0
            }
            
        except Exception as e:
            logger.error(f"Content orchestration failed for campaign {campaign_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "campaign_id": campaign_id
            }
    
    def _get_content_tasks(
        self, 
        user_type: UserType, 
        subscription_tier: SubscriptionTier
    ) -> List[ContentGenerationTask]:
        """Get content tasks for user type and tier, including inherited tasks from lower tiers"""
        
        tasks = []
        
        # Get tasks for current tier
        current_tasks = self.content_mappings.get(user_type, {}).get(subscription_tier, [])
        tasks.extend(current_tasks)
        
        # For higher tiers, also include tasks from lower tiers (but upgrade them)
        if subscription_tier == SubscriptionTier.BASIC:
            free_tasks = self.content_mappings.get(user_type, {}).get(SubscriptionTier.FREE, [])
            tasks.extend(free_tasks)
        elif subscription_tier == SubscriptionTier.PRO:
            basic_tasks = self.content_mappings.get(user_type, {}).get(SubscriptionTier.BASIC, [])
            free_tasks = self.content_mappings.get(user_type, {}).get(SubscriptionTier.FREE, [])
            tasks.extend(basic_tasks + free_tasks)
        elif subscription_tier == SubscriptionTier.ENTERPRISE:
            # Enterprise gets everything
            for tier in [SubscriptionTier.PRO, SubscriptionTier.BASIC, SubscriptionTier.FREE]:
                tier_tasks = self.content_mappings.get(user_type, {}).get(tier, [])
                tasks.extend(tier_tasks)
        
        # Remove duplicates by content_type, keeping highest priority
        seen = {}
        unique_tasks = []
        for task in sorted(tasks, key=lambda t: t.priority):
            if task.content_type not in seen:
                seen[task.content_type] = task
                unique_tasks.append(task)
        
        return unique_tasks
    
    async def _filter_tasks(
        self, 
        tasks: List[ContentGenerationTask], 
        user: Any, 
        preferences: Dict[str, Any]
    ) -> List[ContentGenerationTask]:
        """Filter tasks based on user limits, preferences, and usage"""
        
        tier_limits = self.tier_limits[SubscriptionTier(user.subscription_tier)]
        
        # Check monthly token usage
        monthly_usage = await self._get_monthly_token_usage(user.id)
        available_tokens = tier_limits["max_monthly_tokens"] - monthly_usage
        
        # Filter out premium content for non-premium users
        if not tier_limits["premium_content"]:
            tasks = [task for task in tasks if not task.requires_premium]
        
        # Filter by available tokens
        filtered_tasks = []
        total_tokens = 0
        
        for task in sorted(tasks, key=lambda t: t.priority):
            if total_tokens + task.estimated_tokens <= available_tokens:
                filtered_tasks.append(task)
                total_tokens += task.estimated_tokens
            else:
                logger.info(f"Skipping {task.content_type} - insufficient tokens")
        
        # Apply user preferences
        if preferences.get("excluded_content_types"):
            excluded = set(preferences["excluded_content_types"])
            filtered_tasks = [
                task for task in filtered_tasks 
                if task.content_type.value not in excluded
            ]
        
        return filtered_tasks
    
    async def _queue_content_generation_job(
        self,
        campaign_id: str,
        user_id: str,
        task: ContentGenerationTask,
        intelligence_data: Dict[str, Any],
        priority: int
    ) -> str:
        """Queue a content generation job and return job ID"""
        
        # TODO: Implement actual job queueing system (Redis, Celery, etc.)
        job_id = f"job_{campaign_id}_{task.content_type.value}_{int(asyncio.get_event_loop().time())}"
        
        job_data = {
            "job_id": job_id,
            "campaign_id": campaign_id,
            "user_id": user_id,
            "content_type": task.content_type.value,
            "generator_class": task.generator_class,
            "config": task.config,
            "intelligence_data": intelligence_data,
            "priority": priority,
            "status": "queued",
            "created_at": asyncio.get_event_loop().time()
        }
        
        # Store job in database
        await self._store_generation_job(job_data)
        
        logger.info(f"Queued content generation job: {job_id}")
        return job_id
    
    def _estimate_completion_time(self, task: ContentGenerationTask) -> int:
        """Estimate completion time in seconds based on task complexity"""
        base_time = 30  # 30 seconds base
        token_factor = task.estimated_tokens / 1000 * 10  # 10 seconds per 1000 tokens
        
        if task.requires_premium:
            token_factor *= 1.5  # Premium content takes longer
        
        return int(base_time + token_factor)
    
    async def _get_user_info(self, user_id: str):
        """Get user information from database"""
        # TODO: Implement actual database query
        pass
    
    async def _get_campaign_info(self, campaign_id: str):
        """Get campaign information from database"""
        # TODO: Implement actual database query
        pass
    
    async def _get_monthly_token_usage(self, user_id: str) -> int:
        """Get user's token usage for current month"""
        # TODO: Implement actual usage tracking query
        return 0
    
    async def _store_generation_job(self, job_data: Dict[str, Any]):
        """Store generation job in database"""
        # TODO: Implement actual database storage
        pass

# Factory function for easy import
def create_content_orchestrator() -> ContentOrchestrator:
    return ContentOrchestrator()