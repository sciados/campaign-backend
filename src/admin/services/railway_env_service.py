import os
import asyncio
from typing import List, Dict, Any
from src.core.database import get_database
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

class RailwayEnvironmentService:
    """Service to manage Railway environment variables for AI providers"""
    
    def __init__(self):
        self.db = get_database()
    
    async def check_railway_env_vars(self) -> Dict[str, Any]:
        """Check which environment variables are actually configured in Railway"""
        try:
            # Get all providers from database
            providers = await self.db.fetch_all(
                "SELECT id, provider_name, env_var_name, env_var_configured FROM ai_providers_config"
            )
            
            results = {
                "total_providers": len(providers),
                "configured_count": 0,
                "missing_count": 0,
                "updated_providers": [],
                "missing_providers": []
            }
            
            for provider in providers:
                env_var_exists = os.getenv(provider['env_var_name']) is not None
                
                # Update database with current status
                await self.db.execute(
                    """UPDATE ai_providers_config 
                       SET env_var_configured = $1, env_var_last_checked = NOW() 
                       WHERE id = $2""",
                    env_var_exists, provider['id']
                )
                
                # Track results
                if env_var_exists:
                    results["configured_count"] += 1
                    results["updated_providers"].append(provider['provider_name'])
                else:
                    results["missing_count"] += 1
                    results["missing_providers"].append({
                        "name": provider['provider_name'],
                        "env_var": provider['env_var_name']
                    })
                
                logger.info(f"Provider {provider['provider_name']}: {provider['env_var_name']} = {'✅' if env_var_exists else '❌'}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error checking Railway environment variables: {e}")
            raise
    
    async def get_missing_env_vars(self) -> List[Dict[str, str]]:
        """Get list of providers with missing environment variables"""
        try:
            missing = await self.db.fetch_all(
                """SELECT provider_name, env_var_name, railway_instructions, priority_tier
                   FROM ai_providers_config 
                   WHERE env_var_configured = FALSE 
                   ORDER BY 
                     CASE priority_tier 
                       WHEN 'discovered' THEN 1
                       WHEN 'primary' THEN 2  
                       WHEN 'secondary' THEN 3
                       ELSE 4
                     END"""
            )
            return [dict(row) for row in missing]
        except Exception as e:
            logger.error(f"Error getting missing env vars: {e}")
            raise
    
    async def mark_provider_as_configured(self, provider_id: str) -> bool:
        """Manually mark a provider as configured (for admin override)"""
        try:
            await self.db.execute(
                """UPDATE ai_providers_config 
                   SET env_var_configured = TRUE, 
                       integration_status = 'active',
                       env_var_last_checked = NOW()
                   WHERE id = $1""",
                provider_id
            )
            return True
        except Exception as e:
            logger.error(f"Error marking provider as configured: {e}")
            return False
    
    async def generate_railway_setup_instructions(self, provider_id: str) -> Dict[str, Any]:
        """Generate step-by-step Railway setup instructions for a provider"""
        try:
            provider = await self.db.fetch_one(
                "SELECT * FROM ai_providers_config WHERE id = $1",
                provider_id
            )
            
            if not provider:
                raise ValueError("Provider not found")
            
            instructions = {
                "provider_name": provider['provider_name'],
                "env_var_name": provider['env_var_name'],
                "railway_steps": [
                    "1. Go to Railway Dashboard (railway.app)",
                    "2. Select your CampaignForge project",
                    "3. Click on 'Variables' tab",
                    f"4. Click 'Add Variable'",
                    f"5. Name: {provider['env_var_name']}",
                    f"6. Value: Your API key from {provider['provider_name']}",
                    "7. Click 'Add' to save",
                    "8. Redeploy your service"
                ],
                "api_endpoint": provider.get('api_endpoint'),
                "estimated_time": "3-5 minutes",
                "verification": f"System will auto-detect when {provider['env_var_name']} is available"
            }
            
            return instructions
            
        except Exception as e:
            logger.error(f"Error generating setup instructions: {e}")
            raise

# Create service instance
railway_env_service = RailwayEnvironmentService()