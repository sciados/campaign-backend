# src/content/services/prompt_storage_service.py
"""
Prompt Storage Service
Handles saving, retrieving, and managing AI-generated prompts
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class PromptStorageService:
    """
    Service for storing and retrieving AI-generated prompts
    Enables prompt reuse, analytics, and continuous improvement
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_prompt(
        self,
        campaign_id: str,
        user_id: str,
        content_type: str,
        user_prompt: str,
        system_message: str,
        intelligence_variables: Dict[str, Any],
        prompt_result: Dict[str, Any],
        ai_result: Dict[str, Any],
        content_id: Optional[str] = None
    ) -> str:
        """
        Save a generated prompt to the database for future reuse

        Args:
            campaign_id: Campaign identifier
            user_id: User identifier
            content_type: Type of content (email, email_sequence, etc.)
            user_prompt: The actual prompt sent to AI
            system_message: System context message
            intelligence_variables: Variables extracted from intelligence
            prompt_result: Result from PromptGenerationService
            ai_result: Result from AIProviderService
            content_id: Optional link to generated content

        Returns:
            prompt_id: UUID of saved prompt
        """

        try:
            prompt_id = str(uuid4())

            # Extract metadata from results
            quality_score = prompt_result.get("quality_score", 0)
            psychology_stage = prompt_result.get("psychology_stage", "")
            prompt_template_id = prompt_result.get("metadata", {}).get("template_used", "")

            ai_provider = ai_result.get("provider", "")
            ai_model = ai_result.get("provider_name", "")
            tokens_used = ai_result.get("estimated_tokens", 0)
            generation_cost = str(ai_result.get("cost", 0.0))
            generation_time = str(ai_result.get("generation_time", 0.0))

            # Calculate metrics
            variable_count = len(intelligence_variables)
            prompt_length = len(user_prompt)

            query = text("""
                INSERT INTO generated_prompts (
                    prompt_id, campaign_id, user_id, content_id,
                    content_type, psychology_stage,
                    user_prompt, system_message,
                    intelligence_variables, prompt_template_id,
                    quality_score, variable_count, prompt_length,
                    ai_provider, ai_model, tokens_used, generation_cost, generation_time,
                    created_at
                ) VALUES (
                    :prompt_id, :campaign_id, :user_id, :content_id,
                    :content_type, :psychology_stage,
                    :user_prompt, :system_message,
                    :intelligence_variables::jsonb, :prompt_template_id,
                    :quality_score, :variable_count, :prompt_length,
                    :ai_provider, :ai_model, :tokens_used, :generation_cost, :generation_time,
                    :created_at
                )
            """)

            await self.db.execute(query, {
                "prompt_id": prompt_id,
                "campaign_id": campaign_id,
                "user_id": user_id,
                "content_id": content_id,
                "content_type": content_type,
                "psychology_stage": psychology_stage,
                "user_prompt": user_prompt,
                "system_message": system_message,
                "intelligence_variables": str(intelligence_variables),
                "prompt_template_id": prompt_template_id,
                "quality_score": quality_score,
                "variable_count": variable_count,
                "prompt_length": prompt_length,
                "ai_provider": ai_provider,
                "ai_model": ai_model,
                "tokens_used": tokens_used,
                "generation_cost": generation_cost,
                "generation_time": generation_time,
                "created_at": datetime.utcnow()
            })

            await self.db.commit()

            logger.info(f"✅ Saved prompt {prompt_id} for campaign {campaign_id}")
            return prompt_id

        except Exception as e:
            logger.error(f"❌ Failed to save prompt: {e}")
            await self.db.rollback()
            raise

    async def get_prompts_for_campaign(
        self,
        campaign_id: str,
        content_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve prompts for a specific campaign

        Args:
            campaign_id: Campaign identifier
            content_type: Optional filter by content type
            limit: Maximum number of prompts to return

        Returns:
            List of prompt dictionaries
        """

        try:
            if content_type:
                query = text("""
                    SELECT * FROM generated_prompts
                    WHERE campaign_id = :campaign_id
                    AND content_type = :content_type
                    ORDER BY created_at DESC
                    LIMIT :limit
                """)
                params = {
                    "campaign_id": campaign_id,
                    "content_type": content_type,
                    "limit": limit
                }
            else:
                query = text("""
                    SELECT * FROM generated_prompts
                    WHERE campaign_id = :campaign_id
                    ORDER BY created_at DESC
                    LIMIT :limit
                """)
                params = {
                    "campaign_id": campaign_id,
                    "limit": limit
                }

            result = await self.db.execute(query, params)
            rows = result.fetchall()

            prompts = []
            for row in rows:
                prompts.append({
                    "prompt_id": row.prompt_id,
                    "campaign_id": row.campaign_id,
                    "content_type": row.content_type,
                    "psychology_stage": row.psychology_stage,
                    "user_prompt": row.user_prompt,
                    "system_message": row.system_message,
                    "quality_score": row.quality_score,
                    "ai_provider": row.ai_provider,
                    "tokens_used": row.tokens_used,
                    "generation_cost": row.generation_cost,
                    "created_at": row.created_at.isoformat() if row.created_at else None
                })

            return prompts

        except Exception as e:
            logger.error(f"❌ Failed to retrieve prompts: {e}")
            return []

    async def get_best_prompts(
        self,
        content_type: str,
        min_quality_score: int = 70,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve highest-performing prompts for a content type

        Args:
            content_type: Type of content
            min_quality_score: Minimum quality score threshold
            limit: Maximum number of prompts to return

        Returns:
            List of best-performing prompts
        """

        try:
            query = text("""
                SELECT * FROM generated_prompts
                WHERE content_type = :content_type
                AND quality_score >= :min_quality_score
                ORDER BY quality_score DESC, user_satisfaction DESC NULLS LAST
                LIMIT :limit
            """)

            result = await self.db.execute(query, {
                "content_type": content_type,
                "min_quality_score": min_quality_score,
                "limit": limit
            })

            rows = result.fetchall()

            prompts = []
            for row in rows:
                prompts.append({
                    "prompt_id": row.prompt_id,
                    "user_prompt": row.user_prompt,
                    "system_message": row.system_message,
                    "quality_score": row.quality_score,
                    "content_quality_score": row.content_quality_score,
                    "user_satisfaction": row.user_satisfaction,
                    "reuse_count": row.reuse_count
                })

            return prompts

        except Exception as e:
            logger.error(f"❌ Failed to retrieve best prompts: {e}")
            return []

    async def update_prompt_performance(
        self,
        prompt_id: str,
        content_quality_score: Optional[int] = None,
        user_satisfaction: Optional[int] = None,
        was_regenerated: Optional[bool] = None
    ) -> bool:
        """
        Update performance metrics for a prompt

        Args:
            prompt_id: Prompt identifier
            content_quality_score: Quality score of generated content
            user_satisfaction: User rating (1-5)
            was_regenerated: Whether user regenerated content

        Returns:
            Success status
        """

        try:
            updates = []
            params = {"prompt_id": prompt_id}

            if content_quality_score is not None:
                updates.append("content_quality_score = :content_quality_score")
                params["content_quality_score"] = content_quality_score

            if user_satisfaction is not None:
                updates.append("user_satisfaction = :user_satisfaction")
                params["user_satisfaction"] = user_satisfaction

            if was_regenerated is not None:
                updates.append("was_regenerated = :was_regenerated")
                params["was_regenerated"] = was_regenerated

            if not updates:
                return False

            query = text(f"""
                UPDATE generated_prompts
                SET {', '.join(updates)}
                WHERE prompt_id = :prompt_id
            """)

            await self.db.execute(query, params)
            await self.db.commit()

            logger.info(f"✅ Updated prompt {prompt_id} performance metrics")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update prompt performance: {e}")
            await self.db.rollback()
            return False

    async def mark_prompt_as_favorite(self, prompt_id: str, user_id: str) -> bool:
        """
        Mark a prompt as favorite for reuse

        Args:
            prompt_id: Prompt identifier
            user_id: User identifier

        Returns:
            Success status
        """

        try:
            query = text("""
                UPDATE generated_prompts
                SET is_favorite = TRUE
                WHERE prompt_id = :prompt_id
                AND user_id = :user_id
            """)

            await self.db.execute(query, {
                "prompt_id": prompt_id,
                "user_id": user_id
            })
            await self.db.commit()

            logger.info(f"✅ Marked prompt {prompt_id} as favorite")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to mark prompt as favorite: {e}")
            await self.db.rollback()
            return False

    async def increment_reuse_count(self, prompt_id: str) -> bool:
        """
        Increment the reuse counter for a prompt

        Args:
            prompt_id: Prompt identifier

        Returns:
            Success status
        """

        try:
            query = text("""
                UPDATE generated_prompts
                SET reuse_count = reuse_count + 1,
                    last_used_at = :now
                WHERE prompt_id = :prompt_id
            """)

            await self.db.execute(query, {
                "prompt_id": prompt_id,
                "now": datetime.utcnow()
            })
            await self.db.commit()

            return True

        except Exception as e:
            logger.error(f"❌ Failed to increment reuse count: {e}")
            await self.db.rollback()
            return False
