# src/content/services/smart_provider_router.py
"""
Smart AI Provider Router
Intelligently routes content generation to optimal AI provider based on:
- User tier (free, starter, professional, agency)
- Task complexity (simple, standard, complex, premium)
- Budget constraints
- Quality requirements
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime, timezone
from uuid import UUID

logger = logging.getLogger(__name__)


class UserTier(Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    AGENCY = "agency"


class TaskComplexity(Enum):
    SIMPLE = "simple"           # Social posts, simple emails, short content
    STANDARD = "standard"       # Blog posts, ad copy, email sequences
    COMPLEX = "complex"         # Long-form articles, white papers
    PREMIUM = "premium"         # Press releases, strategic content


class ContentQuality(Enum):
    BUDGET = "budget"           # Testing quality
    STANDARD = "standard"       # Professional quality
    HIGH = "high"              # Marketing-ready
    PREMIUM = "premium"        # Brand-critical


class SmartProviderRouter:
    """
    Intelligently route content generation to optimal AI provider
    Balances quality, cost, and user tier constraints
    """

    # Text Generation Provider Matrix
    TEXT_PROVIDER_MATRIX = {
        UserTier.FREE: {
            TaskComplexity.SIMPLE: "gemini-flash",
            TaskComplexity.STANDARD: "deepseek-v3",
            TaskComplexity.COMPLEX: "deepseek-v3",
            TaskComplexity.PREMIUM: "deepseek-v3"
        },
        UserTier.STARTER: {
            TaskComplexity.SIMPLE: "gemini-flash",
            TaskComplexity.STANDARD: "gpt-4o-mini",
            TaskComplexity.COMPLEX: "gpt-4o-mini",
            TaskComplexity.PREMIUM: "gpt-4o-mini"
        },
        UserTier.PROFESSIONAL: {
            TaskComplexity.SIMPLE: "gpt-4o-mini",
            TaskComplexity.STANDARD: "claude-haiku",
            TaskComplexity.COMPLEX: "gpt-4o",
            TaskComplexity.PREMIUM: "gpt-4o"
        },
        UserTier.AGENCY: {
            TaskComplexity.SIMPLE: "gpt-4o-mini",
            TaskComplexity.STANDARD: "gpt-4o",
            TaskComplexity.COMPLEX: "claude-sonnet-3.5",
            TaskComplexity.PREMIUM: "claude-sonnet-3.5"
        }
    }

    # Image Generation Provider Matrix
    IMAGE_PROVIDER_MATRIX = {
        UserTier.FREE: {
            "all": "flux-schnell"  # $0.003 per image
        },
        UserTier.STARTER: {
            "social_media": "flux-schnell",
            "marketing": "sdxl",
            "hero": "dall-e-3-standard"
        },
        UserTier.PROFESSIONAL: {
            "social_media": "flux-schnell",
            "marketing": "dall-e-3-standard",
            "hero": "dall-e-3-hd"
        },
        UserTier.AGENCY: {
            "social_media": "flux-schnell",
            "marketing": "dall-e-3-hd",
            "hero": "dall-e-3-hd"
        }
    }

    # Provider Costs (per 1M tokens for text, per image for images)
    PROVIDER_COSTS = {
        # Text providers (input cost, output cost per 1M tokens)
        "claude-sonnet-3.5": {"input": 3.00, "output": 15.00, "quality": 5},
        "gpt-4o": {"input": 2.50, "output": 10.00, "quality": 5},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60, "quality": 4},
        "claude-haiku": {"input": 0.25, "output": 1.25, "quality": 4},
        "deepseek-v3": {"input": 0.14, "output": 0.28, "quality": 4},
        "gemini-flash": {"input": 0.075, "output": 0.30, "quality": 3},

        # Image providers (per image)
        "dall-e-3-hd": {"cost": 0.080, "quality": 5},
        "dall-e-3-standard": {"cost": 0.040, "quality": 4},
        "flux-pro": {"cost": 0.055, "quality": 5},
        "flux-schnell": {"cost": 0.003, "quality": 4},
        "sdxl": {"cost": 0.0055, "quality": 3}
    }

    # Tier monthly budgets (in dollars)
    TIER_BUDGETS = {
        UserTier.FREE: 0.50,
        UserTier.STARTER: 15.00,
        UserTier.PROFESSIONAL: 80.00,
        UserTier.AGENCY: 400.00
    }

    # Tier credit allocations
    TIER_CREDITS = {
        UserTier.FREE: 50,
        UserTier.STARTER: 500,
        UserTier.PROFESSIONAL: 2000,
        UserTier.AGENCY: 10000
    }

    def __init__(self):
        self.name = "smart_provider_router"
        self.version = "1.0.0"
        logger.info(f"✅ SmartProviderRouter v{self.version} initialized")

    def select_text_provider(
        self,
        user_tier: str,
        task_complexity: str,
        content_type: str,
        credits_remaining: int,
        user_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Select optimal text AI provider

        Args:
            user_tier: User's subscription tier
            task_complexity: Complexity of the task
            content_type: Type of content being generated
            credits_remaining: User's remaining credits
            user_preference: User's provider preference (agency tier only)

        Returns:
            Dict with provider name, estimated cost, quality level
        """

        try:
            tier_enum = UserTier(user_tier.lower())
            complexity_enum = TaskComplexity(task_complexity.lower())
        except ValueError as e:
            logger.warning(f"Invalid tier or complexity: {e}, using defaults")
            tier_enum = UserTier.FREE
            complexity_enum = TaskComplexity.STANDARD

        # Agency users can override provider selection
        if tier_enum == UserTier.AGENCY and user_preference:
            if user_preference in self.PROVIDER_COSTS:
                provider = user_preference
            else:
                provider = self.TEXT_PROVIDER_MATRIX[tier_enum][complexity_enum]
        else:
            provider = self.TEXT_PROVIDER_MATRIX[tier_enum][complexity_enum]

        # Check if credits running low, downgrade provider if needed
        if credits_remaining < 50 and tier_enum != UserTier.FREE:
            provider = self._get_fallback_text_provider(provider)
            logger.warning(f"⚠️ Low credits ({credits_remaining}), downgrading to {provider}")

        provider_info = self.PROVIDER_COSTS[provider]

        return {
            "provider": provider,
            "quality": provider_info["quality"],
            "input_cost_per_1m": provider_info["input"],
            "output_cost_per_1m": provider_info["output"],
            "tier": user_tier,
            "complexity": task_complexity
        }

    def select_image_provider(
        self,
        user_tier: str,
        image_type: str,
        credits_remaining: int,
        user_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Select optimal image AI provider

        Args:
            user_tier: User's subscription tier
            image_type: Type of image (social_media, marketing, hero)
            credits_remaining: User's remaining credits
            user_preference: User's provider preference (agency tier only)

        Returns:
            Dict with provider name, cost, quality level
        """

        try:
            tier_enum = UserTier(user_tier.lower())
        except ValueError:
            tier_enum = UserTier.FREE

        # Agency users can override
        if tier_enum == UserTier.AGENCY and user_preference:
            if user_preference in self.PROVIDER_COSTS:
                provider = user_preference
            else:
                tier_providers = self.IMAGE_PROVIDER_MATRIX[tier_enum]
                provider = tier_providers.get(image_type, tier_providers.get("all", "flux-schnell"))
        else:
            tier_providers = self.IMAGE_PROVIDER_MATRIX[tier_enum]
            provider = tier_providers.get(image_type, tier_providers.get("all", "flux-schnell"))

        # Low credits fallback
        if credits_remaining < 10:
            provider = "flux-schnell"
            logger.warning(f"⚠️ Low credits ({credits_remaining}), downgrading to {provider}")

        provider_info = self.PROVIDER_COSTS[provider]

        return {
            "provider": provider,
            "quality": provider_info["quality"],
            "cost_per_image": provider_info["cost"],
            "tier": user_tier,
            "image_type": image_type
        }

    def estimate_text_cost(
        self,
        provider: str,
        estimated_input_tokens: int,
        estimated_output_tokens: int
    ) -> float:
        """
        Estimate cost for text generation

        Args:
            provider: AI provider name
            estimated_input_tokens: Estimated input tokens
            estimated_output_tokens: Estimated output tokens

        Returns:
            Estimated cost in dollars
        """

        if provider not in self.PROVIDER_COSTS:
            logger.warning(f"Unknown provider {provider}, using default")
            provider = "gemini-flash"

        costs = self.PROVIDER_COSTS[provider]
        input_cost = (estimated_input_tokens / 1_000_000) * costs["input"]
        output_cost = (estimated_output_tokens / 1_000_000) * costs["output"]

        return input_cost + output_cost

    def estimate_credits_needed(
        self,
        content_type: str,
        user_tier: str,
        quantity: int = 1
    ) -> int:
        """
        Estimate credits needed for content generation

        Args:
            content_type: Type of content
            user_tier: User's tier
            quantity: Number of items to generate

        Returns:
            Estimated credits needed
        """

        # Base credit costs per content type (for standard complexity)
        BASE_CREDITS = {
            UserTier.FREE: {
                "email": 4,
                "social_post": 1,
                "blog_post": 1,
                "ad_copy": 1,
                "image": 1,
                "video_script": 1
            },
            UserTier.STARTER: {
                "email": 5,
                "social_post": 1,
                "blog_post": 1,
                "ad_copy": 1,
                "image": 1,
                "video_script": 1
            },
            UserTier.PROFESSIONAL: {
                "email": 5,
                "social_post": 1,
                "blog_post": 3,
                "ad_copy": 1,
                "image": 2,
                "video_script": 2
            },
            UserTier.AGENCY: {
                "email": 10,
                "social_post": 2,
                "blog_post": 5,
                "ad_copy": 2,
                "image": 2,
                "video_script": 3
            }
        }

        try:
            tier_enum = UserTier(user_tier.lower())
        except ValueError:
            tier_enum = UserTier.FREE

        base = BASE_CREDITS[tier_enum].get(content_type, 1)
        return base * quantity

    def _get_fallback_text_provider(self, current_provider: str) -> str:
        """Get cheaper fallback provider"""

        FALLBACK_CHAIN = {
            "claude-sonnet-3.5": "gpt-4o",
            "gpt-4o": "claude-haiku",
            "claude-haiku": "gpt-4o-mini",
            "gpt-4o-mini": "deepseek-v3",
            "deepseek-v3": "gemini-flash",
            "gemini-flash": "gemini-flash"  # Cheapest, no fallback
        }

        return FALLBACK_CHAIN.get(current_provider, "gemini-flash")

    def get_tier_info(self, user_tier: str) -> Dict[str, Any]:
        """Get tier information"""

        try:
            tier_enum = UserTier(user_tier.lower())
        except ValueError:
            tier_enum = UserTier.FREE

        return {
            "tier": tier_enum.value,
            "monthly_budget": self.TIER_BUDGETS[tier_enum],
            "monthly_credits": self.TIER_CREDITS[tier_enum],
            "text_providers": {
                complexity.value: provider
                for complexity, provider in self.TEXT_PROVIDER_MATRIX[tier_enum].items()
            },
            "image_providers": self.IMAGE_PROVIDER_MATRIX[tier_enum]
        }

    def recommend_upgrade(
        self,
        current_tier: str,
        usage_pattern: Dict[str, int]
    ) -> Optional[Dict[str, Any]]:
        """
        Recommend tier upgrade based on usage patterns

        Args:
            current_tier: User's current tier
            usage_pattern: Dict of content_type: monthly_count

        Returns:
            Recommendation dict or None
        """

        try:
            tier_enum = UserTier(current_tier.lower())
        except ValueError:
            tier_enum = UserTier.FREE

        # Calculate credits needed for usage pattern
        total_credits_needed = sum(
            self.estimate_credits_needed(content_type, current_tier, count)
            for content_type, count in usage_pattern.items()
        )

        current_allocation = self.TIER_CREDITS[tier_enum]

        # If usage exceeds current tier by 20%+, recommend upgrade
        if total_credits_needed > current_allocation * 1.2:
            next_tier = self._get_next_tier(tier_enum)
            if next_tier:
                return {
                    "should_upgrade": True,
                    "current_tier": tier_enum.value,
                    "recommended_tier": next_tier.value,
                    "current_allocation": current_allocation,
                    "needed_credits": total_credits_needed,
                    "savings": self._calculate_savings(tier_enum, next_tier, usage_pattern)
                }

        return None

    def _get_next_tier(self, current_tier: UserTier) -> Optional[UserTier]:
        """Get next tier up"""

        TIER_PROGRESSION = {
            UserTier.FREE: UserTier.STARTER,
            UserTier.STARTER: UserTier.PROFESSIONAL,
            UserTier.PROFESSIONAL: UserTier.AGENCY,
            UserTier.AGENCY: None
        }

        return TIER_PROGRESSION.get(current_tier)

    def _calculate_savings(
        self,
        current_tier: UserTier,
        next_tier: UserTier,
        usage_pattern: Dict[str, int]
    ) -> str:
        """Calculate potential savings/benefits from upgrade"""

        current_cost_per_credit = self.TIER_BUDGETS[current_tier] / self.TIER_CREDITS[current_tier]
        next_cost_per_credit = self.TIER_BUDGETS[next_tier] / self.TIER_CREDITS[next_tier]

        if next_cost_per_credit < current_cost_per_credit:
            savings_pct = ((current_cost_per_credit - next_cost_per_credit) / current_cost_per_credit) * 100
            return f"{savings_pct:.0f}% cost per credit savings"
        else:
            return "Access to higher quality providers and more features"
