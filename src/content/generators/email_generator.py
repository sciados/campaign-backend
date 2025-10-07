# src/content/generators/email_generator.py
"""
AI-Powered Email Generator with Intelligence Integration
Uses modular architecture: Intelligence → Prompt → AI → Content
"""

import logging
import re
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone
from uuid import UUID

from src.content.services.prompt_generation_service import (
    PromptGenerationService,
    ContentType,
    SalesPsychologyStage
)
from src.content.services.ai_provider_service import (
    AIProviderService,
    TaskComplexity
)

logger = logging.getLogger(__name__)


class EmailGenerator:
    """
    AI-powered Email Generator integrating with Intelligence Engine
    Implements modular architecture from content-generation-implementation-plan.md
    """

    def __init__(self, db_session=None):
        self.name = "email_generator"
        self.version = "3.0.0"

        # Initialize modular services
        self.prompt_service = PromptGenerationService()
        self.ai_service = AIProviderService()

        # Optional: Prompt storage service (if db session provided)
        self.db_session = db_session
        self.prompt_storage = None
        if db_session:
            from src.content.services.prompt_storage_service import PromptStorageService
            self.prompt_storage = PromptStorageService(db_session)

        self._generation_stats = {
            "sequences_generated": 0,
            "total_emails_created": 0,
            "ai_generations": 0,
            "total_cost": 0.0,
            "prompts_saved": 0
        }

        logger.info(f"✅ EmailGenerator v{self.version} - Modular architecture with AI")

    async def generate_email_sequence(
        self,
        campaign_id: Union[str, UUID],
        intelligence_data: Dict[str, Any],
        sequence_length: int = 7,
        tone: str = "conversational",
        target_audience: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        user_id: Optional[Union[str, UUID]] = None
    ) -> Dict[str, Any]:
        """
        Generate complete 7-email sales psychology sequence using AI
        Implements Intelligence → Prompt → AI → Content pipeline
        """

        if preferences is None:
            preferences = {}

        try:
            logger.info(f"🎯 Generating {sequence_length}-email sequence for campaign {campaign_id}")

            # Enhance intelligence data with preferences
            if target_audience:
                if "psychology_intelligence" not in intelligence_data:
                    intelligence_data["psychology_intelligence"] = {}
                intelligence_data["psychology_intelligence"]["target_audience"] = target_audience

            if tone:
                if "brand_intelligence" not in intelligence_data:
                    intelligence_data["brand_intelligence"] = {}
                intelligence_data["brand_intelligence"]["tone"] = tone

            # Step 1: Generate optimized prompt from intelligence
            prompt_result = await self.prompt_service.generate_prompt(
                content_type=ContentType.EMAIL_SEQUENCE,
                intelligence_data=intelligence_data,
                psychology_stage=SalesPsychologyStage.SOLUTION_REVEAL,
                preferences=preferences
            )

            if not prompt_result["success"]:
                raise Exception(f"Prompt generation failed: {prompt_result.get('error')}")

            logger.info(f"✅ Generated prompt with quality score: {prompt_result['quality_score']}")

            # Step 2: Generate content using AI
            ai_result = await self.ai_service.generate_text(
                prompt=prompt_result["prompt"],
                system_message=prompt_result["system_message"],
                max_tokens=4000,
                temperature=0.8,
                task_complexity=TaskComplexity.STANDARD
            )

            if not ai_result["success"]:
                raise Exception(f"AI generation failed: {ai_result.get('error')}")

            logger.info(f"✅ AI generated content using {ai_result['provider_name']} (cost: ${ai_result['cost']:.4f})")

            # Save prompt to database for future reuse (if storage available)
            prompt_id = None
            if self.prompt_storage:
                try:
                    # Use provided user_id or fallback to system UUID if not provided
                    storage_user_id = str(user_id) if user_id else "00000000-0000-0000-0000-000000000000"

                    prompt_id = await self.prompt_storage.save_prompt(
                        campaign_id=str(campaign_id),
                        user_id=storage_user_id,
                        content_type="email_sequence" if sequence_length > 1 else "email",
                        user_prompt=prompt_result["prompt"],
                        system_message=prompt_result["system_message"],
                        intelligence_variables=prompt_result["variables"],
                        prompt_result=prompt_result,
                        ai_result=ai_result,
                        content_id=None  # Will be linked later when content is saved
                    )
                    self._generation_stats["prompts_saved"] += 1
                    logger.info(f"✅ Saved prompt {prompt_id} for future reuse")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to save prompt (non-critical): {e}")

            # Step 3: Parse email sequence from AI response
            emails = self._parse_email_sequence(
                ai_response=ai_result["content"],
                sequence_length=sequence_length,
                product_name=prompt_result["variables"].get("PRODUCT_NAME", "this product")
            )

            if not emails or len(emails) < sequence_length:
                logger.warning(f"⚠️ Only parsed {len(emails)} emails, expected {sequence_length}")

            # Step 4: Add greeting and signature to emails
            formatted_emails = self._format_emails_with_greeting_and_signature(
                emails=emails,
                preferences=preferences
            )

            # Step 5: Enhance emails with metadata
            enhanced_emails = self._enhance_emails_with_metadata(
                emails=formatted_emails,
                intelligence_data=intelligence_data,
                prompt_result=prompt_result
            )

            # Update stats
            self._generation_stats["sequences_generated"] += 1
            self._generation_stats["total_emails_created"] += len(enhanced_emails)
            self._generation_stats["ai_generations"] += 1
            self._generation_stats["total_cost"] += ai_result["cost"]

            return {
                "success": True,
                "campaign_id": str(campaign_id),
                "emails": enhanced_emails,
                "sequence_info": {
                    "total_emails": len(enhanced_emails),
                    "product_name": prompt_result["variables"].get("PRODUCT_NAME"),
                    "tone": tone,
                    "target_audience": target_audience,
                    "generation_method": "ai_with_intelligence",
                    "ai_provider": ai_result["provider_name"]
                },
                "generation_metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "generator_version": self.version,
                    "prompt_quality_score": prompt_result["quality_score"],
                    "ai_cost": ai_result["cost"],
                    "ai_provider": ai_result["provider"],
                    "generation_time": ai_result["generation_time"],
                    "intelligence_sources": len(intelligence_data.get("intelligence_sources", [])),
                    "variables_used": len(prompt_result["variables"])
                }
            }

        except Exception as e:
            logger.error(f"❌ Email sequence generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "campaign_id": str(campaign_id)
            }

    def _parse_email_sequence(
        self,
        ai_response: str,
        sequence_length: int,
        product_name: str
    ) -> List[Dict[str, Any]]:
        """Parse AI response into structured email sequence"""

        emails = []

        # Try to parse structured format
        try:
            email_pattern = r'EMAIL_(\d+)\s*\n(.*?)(?=EMAIL_\d+|$)'
            matches = re.findall(email_pattern, ai_response, re.DOTALL | re.IGNORECASE)

            for match in matches:
                email_num = int(match[0])
                email_content = match[1].strip()

                email_data = self._extract_email_components(
                    content=email_content,
                    email_number=email_num,
                    product_name=product_name
                )

                if email_data:
                    emails.append(email_data)

            if emails:
                logger.info(f"✅ Parsed {len(emails)} emails using structured format")
                return emails[:sequence_length]

        except Exception as e:
            logger.warning(f"⚠️ Structured parsing failed: {e}")

        # Fallback: split by separators
        try:
            sections = re.split(r'\n---+\n|\n===+\n', ai_response)

            for idx, section in enumerate(sections):
                if len(section.strip()) < 50:
                    continue

                email_data = self._extract_email_components(
                    content=section,
                    email_number=idx + 1,
                    product_name=product_name
                )

                if email_data:
                    emails.append(email_data)

            if emails:
                logger.info(f"✅ Parsed {len(emails)} emails using fallback method")
                return emails[:sequence_length]

        except Exception as e:
            logger.error(f"❌ Fallback parsing failed: {e}")

        logger.warning("⚠️ Using emergency placeholder emails")
        return self._generate_placeholder_emails(sequence_length, product_name)

    def _extract_email_components(
        self,
        content: str,
        email_number: int,
        product_name: str
    ) -> Optional[Dict[str, Any]]:
        """Extract subject, body, and metadata from email content"""

        try:
            lines = content.split('\n')
            subject = ""
            body_lines = []
            send_delay = f"Day {email_number * 2 - 1}"
            psychology_stage = "solution_reveal"

            for line in lines:
                line_stripped = line.strip()

                if not line_stripped:
                    continue

                if line_stripped.lower().startswith('subject:'):
                    subject = line_stripped[8:].strip()
                elif line_stripped.lower().startswith('body:'):
                    body_lines.append(line_stripped[5:].strip())
                elif line_stripped.lower().startswith(('send_delay:', 'send delay:')):
                    send_delay = line_stripped.split(':', 1)[1].strip()
                elif line_stripped.lower().startswith(('psychology_stage:', 'psychology stage:')):
                    psychology_stage = line_stripped.split(':', 1)[1].strip()
                elif not any(line_stripped.lower().startswith(p) for p in ['email_', 'email ', '---', '===']):
                    if subject:
                        body_lines.append(line_stripped)
                    elif not subject and len(line_stripped) < 100:
                        subject = line_stripped

            body = '\n'.join(body_lines).strip()

            if not subject or not body:
                return None

            return {
                "email_number": email_number,
                "subject": subject,
                "body": body,
                "send_delay": send_delay,
                "psychology_stage": psychology_stage,
                "product_name": product_name,
                "generation_method": "ai"
            }

        except Exception as e:
            logger.warning(f"⚠️ Failed to extract email {email_number}: {e}")
            return None

    def _format_emails_with_greeting_and_signature(
        self,
        emails: List[Dict[str, Any]],
        preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Add greeting and signature to email bodies"""

        # Get greeting and signature from preferences, or use defaults
        greeting = preferences.get("email_greeting", "Hi,")
        signature = preferences.get("email_signature", "Best regards,\n[Your Name]")

        formatted_emails = []

        for email in emails:
            # Add greeting at the start and signature at the end of the body
            formatted_body = f"{greeting}\n\n{email['body']}\n\n{signature}"

            formatted_email = {
                **email,
                "body": formatted_body
            }
            formatted_emails.append(formatted_email)

        logger.info(f"✅ Added greeting and signature to {len(formatted_emails)} emails")
        return formatted_emails

    def _enhance_emails_with_metadata(
        self,
        emails: List[Dict[str, Any]],
        intelligence_data: Dict[str, Any],
        prompt_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Add rich metadata to each email"""

        enhanced = []

        for email in emails:
            enhanced_email = {
                **email,
                "metadata": {
                    "intelligence_enhanced": True,
                    "variables_used": prompt_result.get("variables", {}),
                    "prompt_quality_score": prompt_result.get("quality_score", 0),
                    "intelligence_sources": len(intelligence_data.get("intelligence_sources", [])),
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "generator_version": self.version
                }
            }
            enhanced.append(enhanced_email)

        return enhanced

    def _generate_placeholder_emails(
        self,
        count: int,
        product_name: str
    ) -> List[Dict[str, Any]]:
        """Generate placeholder emails as emergency fallback"""

        psychology_stages = [
            "problem_awareness",
            "problem_agitation",
            "solution_reveal",
            "benefit_proof",
            "social_validation",
            "urgency_creation",
            "objection_handling"
        ]

        emails = []
        for i in range(count):
            stage = psychology_stages[i % len(psychology_stages)]

            emails.append({
                "email_number": i + 1,
                "subject": f"Important Update About {product_name}",
                "body": f"Discover how {product_name} can help you achieve your goals.\n\nLearn more about the benefits and see why thousands of customers trust {product_name}.",
                "send_delay": f"Day {i * 2 + 1}",
                "psychology_stage": stage,
                "product_name": product_name,
                "generation_method": "placeholder_fallback"
            })

        return emails

    def get_stats(self) -> Dict[str, Any]:
        """Get email generator statistics"""
        return {
            "generator": self.name,
            "version": self.version,
            "stats": self._generation_stats,
            "ai_service_stats": self.ai_service.get_stats()
        }
