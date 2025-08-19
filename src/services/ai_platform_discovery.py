# src/services/ai_platform_discovery.py

"""
🔍 AI Platform Discovery & Management System

Two-Table Architecture:
1. active_ai_providers - Only providers with environment API keys (Top 3 per category)
2. discovered_ai_providers - Research discoveries and suggestions

Process:
1. Scan environment variables → Table 1
2. Web research new platforms → Table 2
3. Admin reviews suggestions in Table 2
4. Admin adds API keys → Auto-move Table 2 → Table 1
"""

import os
import re
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, DECIMAL, Enum
from sqlalchemy.ext.declarative import declarative_base
import json

Base = declarative_base()

# ✅ TABLE 1: Active AI Providers (with API keys)
class ActiveAIProvider(Base):
    """Providers with API keys in environment variables - Ready to use"""
    __tablename__ = "active_ai_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(255), nullable=False, index=True)
    env_var_name = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)  # text_generation, image_generation, video_generation
    use_type = Column(String(100), nullable=False)  # content_creation, analysis, conversation, etc.
    
    # Performance & Cost Data
    cost_per_1k_tokens = Column(DECIMAL(10, 6), nullable=True)
    cost_per_image = Column(DECIMAL(8, 4), nullable=True)
    cost_per_minute_video = Column(DECIMAL(8, 4), nullable=True)
    quality_score = Column(DECIMAL(3, 2), default=4.0)
    speed_score = Column(DECIMAL(3, 2), default=3.0)  # 1-5 scale
    
    # Technical Details
    primary_model = Column(String(255), nullable=True)
    api_endpoint = Column(String(255), nullable=True)
    capabilities = Column(Text, nullable=True)  # JSON array
    rate_limits = Column(Text, nullable=True)   # JSON object
    
    # Status & Ranking
    category_rank = Column(Integer, default=999)  # 1-3 for top performers
    is_top_3 = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_performance_check = Column(DateTime, nullable=True)
    
    # Metadata
    discovered_date = Column(DateTime, default=datetime.utcnow)
    promoted_date = Column(DateTime, default=datetime.utcnow)  # When moved from Table 2
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

# ✅ TABLE 2: Discovered AI Providers (research suggestions)
class DiscoveredAIProvider(Base):
    """New AI platforms discovered via web research - Suggestions for future use"""
    __tablename__ = "discovered_ai_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(255), nullable=False, index=True)
    suggested_env_var_name = Column(String(255), nullable=True)  # What env var should be
    category = Column(String(100), nullable=False, index=True)
    use_type = Column(String(100), nullable=False)
    
    # Analysis Data (from web research)
    estimated_cost_per_1k_tokens = Column(DECIMAL(10, 6), nullable=True)
    estimated_cost_per_image = Column(DECIMAL(8, 4), nullable=True)
    estimated_cost_per_minute_video = Column(DECIMAL(8, 4), nullable=True)
    estimated_quality_score = Column(DECIMAL(3, 2), default=3.0)
    estimated_speed_score = Column(DECIMAL(3, 2), default=3.0)
    
    # Research Source Data
    website_url = Column(String(500), nullable=True)
    pricing_url = Column(String(500), nullable=True)
    documentation_url = Column(String(500), nullable=True)
    api_endpoint = Column(String(255), nullable=True)
    
    # Discovery Details
    discovery_source = Column(String(100), nullable=True)  # web_search, api_directory, manual
    discovery_keywords = Column(Text, nullable=True)  # What search found it
    research_notes = Column(Text, nullable=True)  # AI analysis notes
    
    # Recommendation Status
    recommendation_priority = Column(String(20), default='medium')  # high, medium, low
    cost_effectiveness_score = Column(DECIMAL(5, 2), nullable=True)
    unique_features = Column(Text, nullable=True)  # JSON array
    
    # Status Tracking
    is_reviewed = Column(Boolean, default=False)
    admin_notes = Column(Text, nullable=True)
    promotion_status = Column(String(20), default='pending')  # pending, approved, rejected, promoted
    
    # Metadata
    discovered_date = Column(DateTime, default=datetime.utcnow)
    last_research_update = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class AIPlatformDiscoveryService:
    """Main service for AI platform discovery and management"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.categories = {
            'text_generation': ['content_creation', 'conversation', 'analysis', 'code_generation'],
            'image_generation': ['art_creation', 'photo_editing', 'design', 'avatar_generation'],
            'video_generation': ['video_creation', 'animation', 'video_editing', 'presentation'],
            'audio_generation': ['voice_synthesis', 'music_generation', 'sound_effects'],
            'multimodal': ['vision_chat', 'document_analysis', 'general_ai']
        }
    
    async def full_discovery_cycle(self) -> Dict[str, Any]:
        """
        🔄 Complete discovery cycle:
        1. Scan environment → Update Table 1
        2. Web research → Update Table 2  
        3. Rank and prioritize
        4. Return summary
        """
        results = {
            'environment_scan': await self.scan_environment_providers(),
            'web_research': await self.research_new_platforms(),
            'ranking_update': await self.update_rankings(),
            'promotion_check': await self.check_for_promotions(),
            'summary': await self.generate_summary()
        }
        
        return results
    
    async def scan_environment_providers(self) -> Dict[str, Any]:
        """
        1️⃣ Scan environment variables for AI provider API keys
        Update Table 1 with current active providers
        """
        env_vars = dict(os.environ)
        discovered_providers = []
        
        # AI provider patterns
        ai_patterns = [
            r'^([A-Z_]+)_API_KEY$',
            r'^([A-Z_]+)_KEY$',
            r'^([A-Z_]+)_TOKEN$',
            r'^([A-Z_]+)_API_TOKEN$'
        ]
        
        skip_patterns = ['DATABASE', 'JWT', 'SECRET', 'CLOUDFLARE', 'RAILWAY', 'SUPABASE', 'STRIPE']
        
        for env_var, value in env_vars.items():
            for pattern in ai_patterns:
                match = re.match(pattern, env_var)
                if match:
                    provider_key = match.group(1)
                    
                    # Skip non-AI variables
                    if any(skip in provider_key for skip in skip_patterns):
                        continue
                    
                    # Check if this provider exists in Table 1
                    existing = self.db.query(ActiveAIProvider).filter(
                        ActiveAIProvider.env_var_name == env_var
                    ).first()
                    
                    if not existing and value and value.strip():
                        # New provider found - analyze and add
                        provider_data = await self.analyze_new_active_provider(env_var, provider_key, value)
                        if provider_data:
                            discovered_providers.append(provider_data)
                    break
        
        # Add new providers to Table 1
        for provider_data in discovered_providers:
            new_provider = ActiveAIProvider(**provider_data)
            self.db.add(new_provider)
        
        self.db.commit()
        
        return {
            'new_active_providers': len(discovered_providers),
            'total_active_providers': self.db.query(ActiveAIProvider).count(),
            'providers_added': [p['provider_name'] for p in discovered_providers]
        }
    
    async def research_new_platforms(self) -> Dict[str, Any]:
        """
        2️⃣ Research web for new AI platforms
        Add discoveries to Table 2 for review
        """
        research_queries = [
            "new AI API platforms 2024",
            "cheap AI text generation API",
            "best AI image generation API",
            "AI video generation platforms",
            "latest AI model APIs",
            "AI API pricing comparison"
        ]
        
        discovered_platforms = []
        
        for query in research_queries:
            try:
                # Simulate web research (in real implementation, use web scraping)
                platforms = await self.web_research_simulation(query)
                discovered_platforms.extend(platforms)
                
                # Rate limit to be respectful
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"Research query failed: {query} - {e}")
        
        # Add to Table 2 if not already exists
        new_discoveries = 0
        for platform in discovered_platforms:
            existing = self.db.query(DiscoveredAIProvider).filter(
                DiscoveredAIProvider.provider_name == platform['provider_name']
            ).first()
            
            if not existing:
                new_discovery = DiscoveredAIProvider(**platform)
                self.db.add(new_discovery)
                new_discoveries += 1
        
        self.db.commit()
        
        return {
            'research_queries': len(research_queries),
            'platforms_found': len(discovered_platforms),
            'new_discoveries': new_discoveries,
            'total_discovered': self.db.query(DiscoveredAIProvider).count()
        }
    
    async def web_research_simulation(self, query: str) -> List[Dict[str, Any]]:
        """
        🌐 Simulate web research (replace with real web scraping)
        In production, this would use:
        - Web scraping with BeautifulSoup/Scrapy
        - API directories like RapidAPI, APIs.guru
        - AI model hubs like Hugging Face
        - Tech news sites and blogs
        """
        # Simulated discoveries based on real platforms
        simulated_discoveries = {
            "new AI API platforms 2024": [
                {
                    'provider_name': 'Mistral AI',
                    'suggested_env_var_name': 'MISTRAL_API_KEY',
                    'category': 'text_generation',
                    'use_type': 'conversation',
                    'estimated_cost_per_1k_tokens': 0.0002,
                    'estimated_quality_score': 4.2,
                    'website_url': 'https://mistral.ai',
                    'discovery_source': 'web_search',
                    'discovery_keywords': query,
                    'recommendation_priority': 'high',
                    'unique_features': '["european_ai", "privacy_focused", "open_source"]'
                }
            ],
            "cheap AI text generation API": [
                {
                    'provider_name': 'Anyscale',
                    'suggested_env_var_name': 'ANYSCALE_API_KEY',
                    'category': 'text_generation',
                    'use_type': 'content_creation',
                    'estimated_cost_per_1k_tokens': 0.00015,
                    'estimated_quality_score': 3.8,
                    'website_url': 'https://anyscale.com',
                    'discovery_source': 'web_search',
                    'discovery_keywords': query,
                    'recommendation_priority': 'high',
                    'unique_features': '["ultra_cheap", "open_source_models"]'
                }
            ],
            "best AI image generation API": [
                {
                    'provider_name': 'Leonardo AI',
                    'suggested_env_var_name': 'LEONARDO_API_KEY',
                    'category': 'image_generation',
                    'use_type': 'art_creation',
                    'estimated_cost_per_image': 0.015,
                    'estimated_quality_score': 4.4,
                    'website_url': 'https://leonardo.ai',
                    'discovery_source': 'web_search',
                    'discovery_keywords': query,
                    'recommendation_priority': 'medium',
                    'unique_features': '["game_assets", "consistent_characters"]'
                }
            ]
        }
        
        return simulated_discoveries.get(query, [])
    
    async def update_rankings(self) -> Dict[str, Any]:
        """
        3️⃣ Update rankings to show top 3 per category
        Calculate cost-effectiveness and rank providers
        """
        ranking_results = {}
        
        for category in self.categories.keys():
            # Get all active providers in this category
            providers = self.db.query(ActiveAIProvider).filter(
                ActiveAIProvider.category == category,
                ActiveAIProvider.is_active == True
            ).all()
            
            # Calculate cost-effectiveness scores
            for provider in providers:
                cost_score = self.calculate_cost_score(provider)
                quality_score = float(provider.quality_score or 3.0)
                speed_score = float(provider.speed_score or 3.0)
                
                # Combined effectiveness score
                effectiveness = (quality_score * 0.4) + (speed_score * 0.3) + (cost_score * 0.3)
                provider.cost_effectiveness_score = effectiveness
            
            # Sort by effectiveness and rank top 3
            providers.sort(key=lambda p: p.cost_effectiveness_score or 0, reverse=True)
            
            # Update rankings
            for i, provider in enumerate(providers[:3]):
                provider.category_rank = i + 1
                provider.is_top_3 = True
                
            # Mark others as not top 3
            for provider in providers[3:]:
                provider.is_top_3 = False
                provider.category_rank = 999
            
            ranking_results[category] = {
                'total_providers': len(providers),
                'top_3': [p.provider_name for p in providers[:3]]
            }
        
        self.db.commit()
        return ranking_results
    
    async def check_for_promotions(self) -> Dict[str, Any]:
        """
        4️⃣ Check if any Table 2 providers should be promoted to Table 1
        (When API keys are added to environment)
        """
        env_vars = dict(os.environ)
        promotions = []
        
        # Check discovered providers for new API keys
        discovered_providers = self.db.query(DiscoveredAIProvider).filter(
            DiscoveredAIProvider.promotion_status == 'pending'
        ).all()
        
        for provider in discovered_providers:
            suggested_env_var = provider.suggested_env_var_name
            if suggested_env_var and suggested_env_var in env_vars:
                api_key = env_vars[suggested_env_var]
                if api_key and api_key.strip():
                    # Promote to Table 1
                    await self.promote_provider(provider, suggested_env_var, api_key)
                    promotions.append(provider.provider_name)
        
        return {
            'promotions_processed': len(promotions),
            'promoted_providers': promotions
        }
    
    async def promote_provider(self, discovered_provider: DiscoveredAIProvider, env_var: str, api_key: str):
        """Move provider from Table 2 to Table 1"""
        # Create active provider from discovered provider
        active_provider = ActiveAIProvider(
            provider_name=discovered_provider.provider_name,
            env_var_name=env_var,
            category=discovered_provider.category,
            use_type=discovered_provider.use_type,
            cost_per_1k_tokens=discovered_provider.estimated_cost_per_1k_tokens,
            cost_per_image=discovered_provider.estimated_cost_per_image,
            cost_per_minute_video=discovered_provider.estimated_cost_per_minute_video,
            quality_score=discovered_provider.estimated_quality_score,
            speed_score=discovered_provider.estimated_speed_score,
            api_endpoint=discovered_provider.api_endpoint,
            capabilities=discovered_provider.unique_features,
            promoted_date=datetime.utcnow()
        )
        
        # Add to Table 1
        self.db.add(active_provider)
        
        # Update Table 2 status
        discovered_provider.promotion_status = 'promoted'
        discovered_provider.updated_at = datetime.utcnow()
        
        self.db.commit()
    
    def calculate_cost_score(self, provider: ActiveAIProvider) -> float:
        """Calculate cost effectiveness score (higher = better value)"""
        if provider.cost_per_1k_tokens:
            # Invert cost so lower cost = higher score
            if provider.cost_per_1k_tokens <= 0.0002:
                return 5.0  # Ultra cheap
            elif provider.cost_per_1k_tokens <= 0.001:
                return 4.0  # Cheap
            elif provider.cost_per_1k_tokens <= 0.01:
                return 3.0  # Moderate
            else:
                return 2.0  # Expensive
        return 3.0  # Default
    
    async def generate_summary(self) -> Dict[str, Any]:
        """Generate summary of current state"""
        active_by_category = {}
        discovered_by_category = {}
        
        for category in self.categories.keys():
            active_count = self.db.query(ActiveAIProvider).filter(
                ActiveAIProvider.category == category,
                ActiveAIProvider.is_active == True
            ).count()
            
            discovered_count = self.db.query(DiscoveredAIProvider).filter(
                DiscoveredAIProvider.category == category,
                DiscoveredAIProvider.promotion_status == 'pending'
            ).count()
            
            active_by_category[category] = active_count
            discovered_by_category[category] = discovered_count
        
        return {
            'active_providers_by_category': active_by_category,
            'discovered_providers_by_category': discovered_by_category,
            'total_active_providers': sum(active_by_category.values()),
            'total_discovered_providers': sum(discovered_by_category.values()),
            'last_update': datetime.utcnow().isoformat()
        }

# Factory function
def get_discovery_service(db_session):
    """Get AI Platform Discovery Service instance"""
    return AIPlatformDiscoveryService(db_session)