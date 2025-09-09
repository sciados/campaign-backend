# src/intelligence/generators/self_learning_subject_service.py
"""
Self-Improving AI Subject Line System
✅ AI references existing templates to create unique subjects
✅ High-performing AI-generated subjects get added back to database
✅ Continuous learning loop improves template quality over time
✅ Automatic promotion of successful patterns
✅ Quality filtering prevents poor subjects from being stored
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.core.crud.subject_template_crud import SubjectTemplateCRUD, SubjectPerformanceCRUD
from src.models.email_subject_templates import (
    EmailSubjectTemplate, 
    SubjectLineCategory, 
    PerformanceLevel,
    EmailSubjectPerformance
)
import re
import uuid

logger = logging.getLogger(__name__)

class SelfLearningSubjectService:
    """AI service that learns from its own successful subject line creations"""
    
    def __init__(self):
        self.template_crud = SubjectTemplateCRUD()
        self.performance_crud = SubjectPerformanceCRUD()
        
        # Quality thresholds for adding AI-generated subjects back to database
        self.min_open_rate_for_storage = 25.0  # Only store subjects with 25%+ open rate
        self.min_emails_sent_for_evaluation = 50  # Need meaningful sample size
        self.excellent_performance_threshold = 30.0  # 30%+ gets marked as high_performing
        self.top_tier_threshold = 35.0  # 35%+ gets marked as top_tier
        
        # Map angle IDs to subject categories
        self.angle_to_categories = {
            "scientific_authority": [SubjectLineCategory.AUTHORITY_SCIENTIFIC, SubjectLineCategory.SOCIAL_PROOF],
            "emotional_transformation": [SubjectLineCategory.TRANSFORMATION, SubjectLineCategory.EMOTIONAL_TRIGGERS],
            "community_social_proof": [SubjectLineCategory.SOCIAL_PROOF, SubjectLineCategory.TRANSFORMATION],
            "urgency_scarcity": [SubjectLineCategory.URGENCY_SCARCITY, SubjectLineCategory.VALUE_PROMISE],
            "lifestyle_confidence": [SubjectLineCategory.TRANSFORMATION, SubjectLineCategory.CURIOSITY_GAP]
        }
    
    async def generate_and_learn_subject(
        self,
        db: AsyncSession,
        product_name: str,
        angle_id: str,
        email_number: int,
        ai_generator_func,
        campaign_id: str
    ) -> Dict[str, Any]:
        """Generate AI subject using templates as reference, with learning capability"""
        
        # Get relevant template categories for this angle
        categories = self.angle_to_categories.get(angle_id, [SubjectLineCategory.CURIOSITY_GAP])
        selected_category = categories[(email_number - 1) % len(categories)]
        
        # Get high-performing templates as reference
        reference_templates = await self.template_crud.get_templates_by_category(
            db=db,
            category=selected_category,
            performance_level=PerformanceLevel.HIGH_PERFORMING,
            limit=5
        )
        
        # If no high-performing templates, get any good ones
        if not reference_templates:
            reference_templates = await self.template_crud.get_templates_by_category(
                db=db,
                category=selected_category,
                limit=5
            )
        
        # Create AI prompt with template references
        ai_prompt = self._create_learning_prompt(
            product_name, selected_category, reference_templates, email_number
        )
        
        try:
            # Generate with AI using templates as reference
            ai_result = await ai_generator_func(
                content_type="learning_email_subject",
                prompt=ai_prompt,
                system_message=f"You are an expert email subject line writer that learns from proven patterns. Create a NEW, UNIQUE subject line for {product_name} inspired by successful templates. Focus on psychology and engagement.",
                max_tokens=80,
                temperature=0.85,  # Balanced creativity
                task_complexity="simple"
            )
            
            if ai_result and ai_result.get("success"):
                subject_line = self._extract_and_clean_subject(ai_result["content"], product_name)
                
                if subject_line and self._validate_subject_quality(subject_line, product_name):
                    # Create generalized template version for potential future storage
                    template_version = self._create_template_from_subject(subject_line, product_name)
                    
                    # Record the usage with learning metadata
                    performance_record = await self.performance_crud.record_subject_usage(
                        db=db,
                        subject_line=subject_line,
                        product_name=product_name,
                        category=selected_category,
                        campaign_id=campaign_id,
                        email_number=email_number,
                        strategic_angle=angle_id,
                        template_id=reference_templates[0].id if reference_templates else None,
                        ai_provider=ai_result.get("provider_used"),
                        generation_method="ai_with_learning"
                    )
                    
                    logger.info(f"✅ Generated learning subject: '{subject_line}'")
                    logger.info(f"📝 Template version: '{template_version}'")
                    
                    return {
                        "subject_line": subject_line,
                        "template_version": template_version,
                        "category_used": selected_category.value,
                        "reference_templates_count": len(reference_templates),
                        "performance_record_id": str(performance_record.id),
                        "can_learn_from": True,
                        "ai_result": ai_result
                    }
            
            logger.warning(f"⚠️ Learning subject generation failed for email #{email_number}")
            
        except Exception as e:
            logger.error(f"❌ Learning subject generation error: {str(e)}")
        
        # Fallback generation
        return await self._generate_template_based_fallback(
            db, product_name, selected_category, email_number, campaign_id, angle_id
        )
    
    async def evaluate_and_store_successful_subjects(
        self,
        db: AsyncSession,
        performance_record_ids: List[str] = None,
        auto_evaluate_recent: bool = True
    ) -> Dict[str, Any]:
        """Evaluate AI-generated subjects and store successful ones as new templates"""
        
        results = {
            "evaluated_count": 0,
            "stored_as_templates": 0,
            "promoted_to_high_performing": 0,
            "promoted_to_top_tier": 0,
            "new_templates": []
        }
        
        # Get performance records to evaluate
        if performance_record_ids:
            # Evaluate specific records
            performance_records = []
            for record_id in performance_record_ids:
                record = await self.performance_crud.get(db=db, id=record_id)
                if record:
                    performance_records.append(record)
        elif auto_evaluate_recent:
            # Auto-evaluate recent records that haven't been processed
            performance_records = await self._get_recent_performance_records(db)
        else:
            return results
        
        for record in performance_records:
            results["evaluated_count"] += 1
            
            # Check if this subject meets storage criteria
            if await self._should_store_as_template(record):
                # Create new template from successful AI-generated subject
                new_template = await self._store_subject_as_template(db, record)
                
                if new_template:
                    results["stored_as_templates"] += 1
                    results["new_templates"].append({
                        "template_text": new_template.template_text,
                        "category": new_template.category.value,
                        "performance_level": new_template.performance_level.value,
                        "open_rate": record.open_rate
                    })
                    
                    # Track promotion level
                    if new_template.performance_level == PerformanceLevel.TOP_TIER:
                        results["promoted_to_top_tier"] += 1
                    elif new_template.performance_level == PerformanceLevel.HIGH_PERFORMING:
                        results["promoted_to_high_performing"] += 1
                    
                    logger.info(f"🎯 Stored successful subject as template: '{new_template.template_text}'")
        
        logger.info(f"📊 Learning evaluation complete: {results}")
        return results
    
    async def _get_recent_performance_records(
        self,
        db: AsyncSession,
        days_back: int = 7
    ) -> List[EmailSubjectPerformance]:
        """Get recent performance records that are ready for evaluation"""
        
        query = select(EmailSubjectPerformance).where(
            EmailSubjectPerformance.was_ai_generated == True,
            EmailSubjectPerformance.generation_method.in_(['ai_with_learning', 'ai_with_template_reference']),
            EmailSubjectPerformance.emails_sent >= self.min_emails_sent_for_evaluation,
            EmailSubjectPerformance.open_rate > 0,
            # Not already stored as template (check if template_id is from original reference, not created from this record)
            EmailSubjectPerformance.created_at >= func.now() - func.interval(f'{days_back} days')
        ).order_by(EmailSubjectPerformance.open_rate.desc()).limit(50)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def _should_store_as_template(self, performance_record: EmailSubjectPerformance) -> bool:
        """Determine if a subject line performance qualifies for template storage"""
        
        # Basic criteria
        if performance_record.emails_sent < self.min_emails_sent_for_evaluation:
            return False
        
        if performance_record.open_rate < self.min_open_rate_for_storage:
            return False
        
        # Check if we already have this pattern
        template_version = self._create_template_from_subject(
            performance_record.subject_line, 
            performance_record.product_name
        )
        
        # Don't store if it's too similar to existing templates
        if await self._is_too_similar_to_existing(template_version):
            return False
        
        return True
    
    async def _store_subject_as_template(
        self,
        db: AsyncSession,
        performance_record: EmailSubjectPerformance
    ) -> Optional[EmailSubjectTemplate]:
        """Store a successful AI-generated subject as a new template"""
        
        # Create template version
        template_text = self._create_template_from_subject(
            performance_record.subject_line,
            performance_record.product_name
        )
        
        # Determine performance level based on open rate
        if performance_record.open_rate >= self.top_tier_threshold:
            performance_level = PerformanceLevel.TOP_TIER
        elif performance_record.open_rate >= self.excellent_performance_threshold:
            performance_level = PerformanceLevel.HIGH_PERFORMING
        else:
            performance_level = PerformanceLevel.GOOD
        
        # Extract psychology triggers and keywords
        psychology_triggers = self._extract_psychology_triggers(performance_record.subject_line)
        keywords = self._extract_keywords(performance_record.subject_line)
        
        # Create new template
        new_template = EmailSubjectTemplate(
            template_text=template_text,
            category=performance_record.category_used,
            performance_level=performance_level,
            avg_open_rate=performance_record.open_rate,
            total_uses=performance_record.emails_sent,
            total_opens=performance_record.emails_opened,
            psychology_triggers=psychology_triggers,
            keywords=keywords,
            character_count=len(template_text),
            is_active=True,
            is_verified=False,  # AI-generated templates start unverified
            source=f"ai_learned_from_campaign_{performance_record.campaign_id}"
        )
        
        try:
            saved_template = await self.template_crud.create(db=db, obj_in=new_template)
            logger.info(f"🎯 Created new template from successful subject: '{template_text}' (Open Rate: {performance_record.open_rate:.1f}%)")
            return saved_template
        
        except Exception as e:
            logger.error(f"❌ Failed to store template: {str(e)}")
            return None
    
    def _create_template_from_subject(self, subject_line: str, product_name: str) -> str:
        """Convert a specific subject line back to a template with {product} placeholder"""
        
        # Replace the specific product name with {product} placeholder
        template = subject_line.replace(product_name, "{product}")
        
        # Handle case variations
        template = template.replace(product_name.lower(), "{product}")
        template = template.replace(product_name.upper(), "{product}")
        template = template.replace(product_name.title(), "{product}")
        
        # Clean up any double placeholders
        template = re.sub(r'\{product\}\s*\{product\}', '{product}', template)
        
        return template
    
    def _extract_psychology_triggers(self, subject_line: str) -> List[str]:
        """Extract psychology triggers from subject line"""
        
        triggers = []
        subject_lower = subject_line.lower()
        
        # Define trigger patterns
        trigger_patterns = {
            "curiosity": ["why", "what", "how", "secret", "revealed", "discover", "truth"],
            "urgency": ["last", "final", "expires", "deadline", "hurry", "limited time", "don't miss"],
            "scarcity": ["only", "exclusive", "limited", "few left", "while supplies"],
            "social_proof": ["people", "users", "thousands", "millions", "others", "everyone"],
            "authority": ["study", "research", "scientists", "experts", "proven", "clinical"],
            "transformation": ["transform", "change", "breakthrough", "revolution", "new you"],
            "emotional": ["amazing", "incredible", "shocking", "unbelievable", "life-changing"],
            "benefit": ["save", "gain", "boost", "improve", "increase", "better", "faster"]
        }
        
        for trigger_type, patterns in trigger_patterns.items():
            if any(pattern in subject_lower for pattern in patterns):
                triggers.append(trigger_type)
        
        return triggers
    
    def _extract_keywords(self, subject_line: str) -> List[str]:
        """Extract key words and phrases from subject line"""
        
        # Remove common words and extract meaningful terms
        common_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        
        # Split into words and filter
        words = re.findall(r'\b\w+\b', subject_line.lower())
        keywords = [word for word in words if len(word) > 2 and word not in common_words]
        
        # Also extract quoted phrases
        phrases = re.findall(r'"([^"]*)"', subject_line)
        keywords.extend(phrases)
        
        return keywords[:10]  # Limit to top 10 keywords
    
    async def _is_too_similar_to_existing(self, template_text: str) -> bool:
        """Check if template is too similar to existing ones"""
        
        # Simple similarity check - could be enhanced with more sophisticated algorithms
        words = set(template_text.lower().split())
        
        # For now, just check if it's identical
        # In production, you might want more sophisticated similarity detection
        return False  # Allow all for now, but this is where you'd add similarity logic
    
    def _create_learning_prompt(
        self,
        product_name: str,
        category: SubjectLineCategory,
        reference_templates: List,
        email_number: int
    ) -> str:
        """Create AI prompt that encourages learning from templates"""
        
        category_descriptions = {
            SubjectLineCategory.CURIOSITY_GAP: "creating irresistible curiosity that makes people need to know more",
            SubjectLineCategory.URGENCY_SCARCITY: "creating urgency and scarcity to motivate immediate action",
            SubjectLineCategory.SOCIAL_PROOF: "leveraging social validation and community success",
            SubjectLineCategory.PERSONAL_BENEFIT: "highlighting clear personal benefits and value",
            SubjectLineCategory.TRANSFORMATION: "focusing on transformation and breakthrough stories",
            SubjectLineCategory.AUTHORITY_SCIENTIFIC: "using scientific authority and research backing",
            SubjectLineCategory.EMOTIONAL_TRIGGERS: "triggering strong emotional responses",
            SubjectLineCategory.VALUE_PROMISE: "promising specific, measurable value"
        }
        
        reference_examples = ""
        if reference_templates:
            reference_examples = "\n".join([
                f"• {template.template_text} (Open Rate: {template.avg_open_rate:.1f}%)"
                for template in reference_templates[:3]
            ])
        else:
            reference_examples = "No specific templates available - be creative!"
        
        prompt = f"""
CREATE A UNIQUE EMAIL SUBJECT LINE THAT LEARNS FROM PROVEN PATTERNS

PRODUCT: {product_name}
EMAIL #{email_number} in sequence
PSYCHOLOGY CATEGORY: {category.value}
GOAL: {category_descriptions.get(category, 'engaging the reader')}

PROVEN PATTERNS TO LEARN FROM:
{reference_examples}

LEARNING INSTRUCTIONS:
1. Study the psychological patterns in these successful examples
2. Identify what makes them convert at high rates
3. Create a COMPLETELY NEW subject line for {product_name}
4. Use similar psychological triggers but with fresh, original wording
5. Make it unique and specific to {product_name}
6. Aim for maximum curiosity and engagement

QUALITY STANDARDS:
- Under 50 characters for mobile optimization
- Use exact product name: {product_name}
- NEVER use placeholders like [Product], Your, etc.
- Make people feel they MUST open this email
- Create genuine intrigue and value promise

Your goal is to create something that could become a new proven template if it performs well.

Generate ONE unique, high-converting subject line now:
"""
        
        return prompt
    
    def _extract_and_clean_subject(self, ai_content: str, product_name: str) -> Optional[str]:
        """Extract and clean subject line from AI response"""
        
        lines = ai_content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove common prefixes
            line = re.sub(r'^(subject:?|subject line:?|\d+\.\s*)', '', line, flags=re.IGNORECASE).strip()
            line = re.sub(r'^["\']|["\']$', '', line)  # Remove quotes
            
            # Check quality
            if self._validate_subject_quality(line, product_name):
                return line
        
        return None
    
    def _validate_subject_quality(self, subject_line: str, product_name: str) -> bool:
        """Validate that subject line meets quality standards"""
        
        # Basic length check
        if not (10 <= len(subject_line) <= 80):
            return False
        
        # Must contain product name
        if product_name.lower() not in subject_line.lower():
            return False
        
        # Should not contain obvious placeholder text
        placeholder_patterns = [r'\[.*?\]', r'your company', r'product name', r'insert.*']
        for pattern in placeholder_patterns:
            if re.search(pattern, subject_line, re.IGNORECASE):
                return False
        
        # Should have at least some engaging words
        engaging_words = ['discover', 'secret', 'breakthrough', 'transform', 'amazing', 'proven', 
                         'exclusive', 'limited', 'why', 'how', 'what', 'finally', 'reveal']
        if not any(word in subject_line.lower() for word in engaging_words):
            return False
        
        return True
    
    async def _generate_template_based_fallback(
        self,
        db: AsyncSession,
        product_name: str,
        category: SubjectLineCategory,
        email_number: int,
        campaign_id: str,
        angle_id: str
    ) -> Dict[str, Any]:
        """Fallback generation using existing templates"""
        
        templates = await self.template_crud.get_templates_by_category(
            db=db,
            category=category,
            limit=10
        )
        
        if templates:
            template = templates[(email_number - 1) % len(templates)]
            subject_line = template.template_text.format(product=product_name)
            
            performance_record = await self.performance_crud.record_subject_usage(
                db=db,
                subject_line=subject_line,
                product_name=product_name,
                category=category,
                campaign_id=campaign_id,
                email_number=email_number,
                strategic_angle=angle_id,
                template_id=template.id,
                generation_method="template_fallback"
            )
            
            return {
                "subject_line": subject_line,
                "template_version": template.template_text,
                "category_used": category.value,
                "template_used": template.id,
                "performance_record_id": str(performance_record.id),
                "is_fallback": True,
                "can_learn_from": False
            }
        
        # Ultimate fallback
        subject_line = f"Important {product_name} Update #{email_number}"
        
        performance_record = await self.performance_crud.record_subject_usage(
            db=db,
            subject_line=subject_line,
            product_name=product_name,
            category=category,
            campaign_id=campaign_id,
            email_number=email_number,
            strategic_angle=angle_id,
            generation_method="emergency_fallback"
        )
        
        return {
            "subject_line": subject_line,
            "template_version": subject_line,
            "category_used": category.value,
            "performance_record_id": str(performance_record.id),
            "is_emergency_fallback": True,
            "can_learn_from": False
        }

# Integration with your existing email generator
class LearningEmailGenerator:
    """Email generator that learns from its own successful subject lines"""
    
    def __init__(self):
        self.learning_service = SelfLearningSubjectService()
    
    async def generate_learning_subject(
        self,
        db: AsyncSession,
        product_name: str,
        angle: Dict[str, Any],
        email_number: int,
        campaign_id: str,
        ai_generator_func
    ) -> Dict[str, Any]:
        """Generate subject that can learn from its own success"""
        
        return await self.learning_service.generate_and_learn_subject(
            db=db,
            product_name=product_name,
            angle_id=angle["id"],
            email_number=email_number,
            ai_generator_func=ai_generator_func,
            campaign_id=campaign_id
        )
    
    async def learn_from_performance(
        self,
        db: AsyncSession,
        performance_record_ids: List[str] = None
    ) -> Dict[str, Any]:
        """Learn from recent subject line performance and store successful patterns"""
        
        return await self.learning_service.evaluate_and_store_successful_subjects(
            db=db,
            performance_record_ids=performance_record_ids,
            auto_evaluate_recent=performance_record_ids is None
        )

# Convenience functions for easy integration
async def generate_learning_subject_line(
    db: AsyncSession,
    product_name: str,
    psychology_category: str,
    ai_generator_func,
    campaign_id: str = "test"
) -> str:
    """Quick function to generate a learning subject line"""
    
    service = SelfLearningSubjectService()
    result = await service.generate_and_learn_subject(
        db=db,
        product_name=product_name,
        angle_id="scientific_authority",  # Default angle
        email_number=1,
        ai_generator_func=ai_generator_func,
        campaign_id=campaign_id
    )
    
    return result.get("subject_line", f"Important {product_name} Update")

async def learn_from_recent_performance(db: AsyncSession) -> Dict[str, Any]:
    """Learn from recent subject line performance"""
    
    service = SelfLearningSubjectService()
    return await service.evaluate_and_store_successful_subjects(
        db=db,
        auto_evaluate_recent=True
    )