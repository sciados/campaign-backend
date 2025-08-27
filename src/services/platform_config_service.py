# src/services/platform_config_service.py
from typing import Dict, List, Any
from enum import Enum

class PlatformType(str, Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    PINTEREST = "pinterest"
    TWITCH = "twitch"

class PlatformConfigService:
    
    PLATFORM_CONFIGS = {
        "affiliate_marketer": {
            "recommended_platforms": [
                PlatformType.YOUTUBE,
                PlatformType.INSTAGRAM,
                PlatformType.TIKTOK,
                PlatformType.PINTEREST
            ],
            "required_metrics": ["followers", "click_through_rate", "avg_views"],
            "optional_metrics": ["conversion_rate", "commission_per_click"],
            "dashboard_focus": ["commission_tracking", "traffic_sources", "conversion_optimization"]
        },
        "content_creator": {
            "recommended_platforms": [
                PlatformType.INSTAGRAM,
                PlatformType.TIKTOK,
                PlatformType.YOUTUBE,
                PlatformType.TWITTER
            ],
            "required_metrics": ["followers", "engagement_rate", "avg_views"],
            "optional_metrics": ["viral_score", "brand_deal_rate", "subscriber_growth"],
            "dashboard_focus": ["viral_opportunities", "engagement_analysis", "growth_tracking"]
        },
        "business_owner": {
            "recommended_platforms": [
                PlatformType.LINKEDIN,
                PlatformType.FACEBOOK,
                PlatformType.INSTAGRAM,
                PlatformType.YOUTUBE
            ],
            "required_metrics": ["followers", "leads_generated", "website_clicks"],
            "optional_metrics": ["conversion_rate", "cost_per_lead", "customer_acquisition"],
            "dashboard_focus": ["lead_generation", "customer_insights", "roi_tracking"]
        }
    }
    
    @classmethod
    def get_config_for_user_type(cls, user_type: str) -> Dict[str, Any]:
        return cls.PLATFORM_CONFIGS.get(user_type, {})
    
    @classmethod
    def get_recommended_platforms(cls, user_type: str) -> List[str]:
        config = cls.get_config_for_user_type(user_type)
        return [p.value for p in config.get("recommended_platforms", [])]