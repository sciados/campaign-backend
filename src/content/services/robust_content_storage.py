# src/content/services/robust_content_storage.py
"""
Robust content storage service that handles all database constraints properly
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Import the models from the correct location
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)

class ContentStorageService:
    """Robust service for storing generated content with proper error handling"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def store_generated_content(
        self,
        session: AsyncSession,
        campaign_id: str,
        user_id: str,
        content_type: str,
        content_data: Dict[str, Any],
        title: Optional[str] = None,
        word_count: Optional[int] = None,
        tokens_used: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Store generated content using proper schema and relationships

        Returns: {
            "success": bool,
            "content_id": str,
            "job_id": str,
            "error": Optional[str]
        }
        """
        try:
            # Generate unique IDs
            content_id = str(uuid.uuid4())
            job_id = str(uuid.uuid4())

            self.logger.info(f"Storing content for campaign {campaign_id}, type {content_type}")

            # Map content type to enum value
            content_type_enum = self._map_content_type(content_type)

            # 1. Create ContentGenerationJob first (required by foreign key)
            job_insert_stmt = text("""
                INSERT INTO content_generation_jobs (
                    job_id, campaign_id, user_id, content_type, generator_class,
                    status, progress_percentage, created_at, completed_at,
                    estimated_tokens, actual_tokens_used
                ) VALUES (
                    :job_id, :campaign_id, :user_id, :content_type, :generator_class,
                    :status, :progress_percentage, :created_at, :completed_at,
                    :estimated_tokens, :actual_tokens_used
                )
            """)

            await session.execute(job_insert_stmt, {
                "job_id": job_id,
                "campaign_id": campaign_id,
                "user_id": user_id,
                "content_type": content_type_enum,
                "generator_class": "IntelligenceEnhancedGenerator",
                "status": "completed",
                "progress_percentage": 100,
                "created_at": datetime.utcnow(),
                "completed_at": datetime.utcnow(),
                "estimated_tokens": tokens_used or 0,
                "actual_tokens_used": tokens_used or 0
            })

            # 2. Create GeneratedContent record
            content_insert_stmt = text("""
                INSERT INTO generated_content (
                    content_id, job_id, campaign_id, user_id, content_type,
                    title, content_data, word_count, tokens_used,
                    generation_model, generation_version, is_approved,
                    created_at, updated_at
                ) VALUES (
                    :content_id, :job_id, :campaign_id, :user_id, :content_type,
                    :title, :content_data, :word_count, :tokens_used,
                    :generation_model, :generation_version, :is_approved,
                    :created_at, :updated_at
                )
            """)

            await session.execute(content_insert_stmt, {
                "content_id": content_id,
                "job_id": job_id,
                "campaign_id": campaign_id,
                "user_id": user_id,
                "content_type": content_type_enum,
                "title": title or f"Generated {content_type.replace('_', ' ').title()}",
                "content_data": content_data,
                "word_count": word_count or self._calculate_word_count(content_data),
                "tokens_used": tokens_used or 0,
                "generation_model": "claude-3-sonnet",
                "generation_version": "2.0",
                "is_approved": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })

            # 3. Update campaign counters
            await self._update_campaign_counters(session, campaign_id)

            # Commit the transaction
            await session.commit()

            self.logger.info(f"Successfully stored content {content_id} for campaign {campaign_id}")

            return {
                "success": True,
                "content_id": content_id,
                "job_id": job_id,
                "message": "Content stored successfully"
            }

        except IntegrityError as e:
            await session.rollback()
            error_msg = f"Database integrity error: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}

        except SQLAlchemyError as e:
            await session.rollback()
            error_msg = f"Database error: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}

        except Exception as e:
            await session.rollback()
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {"success": False, "error": error_msg}

    def _map_content_type(self, content_type: str) -> str:
        """Map content type string to database enum value"""
        mapping = {
            "email": "email_sequence",
            "email_sequence": "email_sequence",
            "social": "social_posts",
            "social_posts": "social_posts",
            "ad_copy": "ad_copy",
            "blog": "blog_articles",
            "blog_articles": "blog_articles",
            "video_script": "video_scripts",
            "video_scripts": "video_scripts"
        }
        return mapping.get(content_type.lower(), "email_sequence")

    def _calculate_word_count(self, content_data: Dict[str, Any]) -> int:
        """Calculate word count from content data"""
        if isinstance(content_data, dict):
            if "content" in content_data:
                return len(str(content_data["content"]).split())
            elif "body" in content_data:
                return len(str(content_data["body"]).split())
            elif "text" in content_data:
                return len(str(content_data["text"]).split())
            else:
                # Count words in all string values
                total_words = 0
                for value in content_data.values():
                    if isinstance(value, str):
                        total_words += len(value.split())
                return total_words
        return 0

    async def _update_campaign_counters(self, session: AsyncSession, campaign_id: str):
        """Update campaign generated_content_count"""
        try:
            update_stmt = text("""
                UPDATE campaigns
                SET generated_content_count = (
                    SELECT COUNT(*) FROM generated_content
                    WHERE campaign_id = :campaign_id
                ),
                updated_at = :updated_at
                WHERE id = :campaign_id
            """)

            await session.execute(update_stmt, {
                "campaign_id": campaign_id,
                "updated_at": datetime.utcnow()
            })

        except Exception as e:
            self.logger.warning(f"Failed to update campaign counters: {e}")

    async def get_campaign_content(
        self,
        session: AsyncSession,
        campaign_id: str,
        content_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve generated content for a campaign"""
        try:
            query = """
                SELECT gc.content_id, gc.content_type, gc.title, gc.content_data,
                       gc.created_at, gc.is_approved, gc.word_count, gc.tokens_used,
                       cgj.status as job_status
                FROM generated_content gc
                LEFT JOIN content_generation_jobs cgj ON gc.job_id = cgj.job_id
                WHERE gc.campaign_id = :campaign_id
            """

            params = {"campaign_id": campaign_id}

            if content_type:
                query += " AND gc.content_type = :content_type"
                params["content_type"] = self._map_content_type(content_type)

            query += " ORDER BY gc.created_at DESC"

            result = await session.execute(text(query), params)

            return [
                {
                    "content_id": row.content_id,
                    "content_type": row.content_type,
                    "title": row.title,
                    "content_data": row.content_data,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "is_approved": row.is_approved,
                    "word_count": row.word_count,
                    "tokens_used": row.tokens_used,
                    "job_status": row.job_status
                }
                for row in result
            ]

        except Exception as e:
            self.logger.error(f"Error retrieving content: {e}")
            return []

    async def test_storage_capability(self, session: AsyncSession) -> Dict[str, Any]:
        """Test the storage system with a minimal record"""
        test_data = {
            "subject": "Test Email",
            "content": "This is a test email content.",
            "call_to_action": "Test CTA"
        }

        # Use a test campaign ID and user ID
        test_campaign_id = "test-campaign-" + str(uuid.uuid4())[:8]
        test_user_id = "test-user-" + str(uuid.uuid4())[:8]

        result = await self.store_generated_content(
            session=session,
            campaign_id=test_campaign_id,
            user_id=test_user_id,
            content_type="email",
            content_data=test_data,
            title="Test Content",
            word_count=10,
            tokens_used=50
        )

        return result