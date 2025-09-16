# src/intelligence/generators/subject_line_ai_service.py
"""
AI service that uses database templates as reference patterns
"""

import logging
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.crud.subject_template_crud import SubjectTemplateCRUD, SubjectPerformanceCRUD
# from src.core.database.models.email_subject_templates import... # TODO: Fix this import

logger = logging.getLogger(__name__)

class AISubjectLineService:
    """AI service that uses database templates as reference patterns"""
    
    def __init__(self):
        self.template_crud = SubjectTemplateCRUD()
        self.performance_crud = SubjectPerformanceCRUD()
        
        # Map angle IDs to subject categories
        self.angle_to_categories = {
            "scientific_authority": [SubjectLineCategory.AUTHORITY_SCIENTIFIC, SubjectLineCategory.SOCIAL_PROOF],
            "emotional_transformation": [SubjectLineCategory.TRANSFORMATION, SubjectLineCategory.EMOTIONAL_TRIGGERS],
            "community_social_proof": [SubjectLineCategory.SOCIAL_PROOF, SubjectLineCategory.TRANSFORMATION],
            "urgency_scarcity": [SubjectLineCategory.URGENCY_SCARCITY, SubjectLineCategory.VALUE_PROMISE],
            "lifestyle_confidence": [SubjectLineCategory.TRANSFORMATION, SubjectLineCategory.CURIOSITY_GAP]
        }
    
    async def generate_ai_subject_with_reference(
        self,
        db: AsyncSession,
        product_name: str,
        angle_id: str,
        email_number: int,
        ai_generator_func,  # The AI generation function from base generator
        campaign_id: str
    ) -> Dict[str, Any]:
        """Generate AI subject line using database templates as reference patterns"""
        
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
        ai_prompt = self._create_reference_based_prompt(
            product_name, selected_category, reference_templates, email_number
        )
        
        try:
            # Generate with AI using templates as reference
            ai_result = await ai_generator_func(
                content_type="email_subject_with_reference",
                prompt=ai_prompt,
                system_message=f"You are an expert email subject line writer. Use the reference patterns to inspire a NEW, UNIQUE subject line for {product_name}. Do not copy directly - create something fresh that follows similar psychology.",
                max_tokens=80,
                temperature=0.9,  # High creativity
                task_complexity="simple"
            )
            
            if ai_result and ai_result.get("success"):
                subject_line = self._extract_and_clean_subject(ai_result["content"], product_name)
                
                if subject_line:
                    # Record the usage
                    template_id = reference_templates[0].id if reference_templates else None
                    performance_record = await self.performance_crud.record_subject_usage(
                        db=db,
                        subject_line=subject_line,
                        product_name=product_name,
                        category=selected_category,
                        campaign_id=campaign_id,
                        email_number=email_number,
                        strategic_angle=angle_id,
                        template_id=template_id,
                        ai_provider=ai_result.get("provider_used"),
                        generation_method="ai_with_template_reference"
                    )
                    
                    logger.info(f"✅ AI generated subject with template reference: '{subject_line}'")
                    
                    return {
                        "subject_line": subject_line,
                        "category_used": selected_category.value,
                        "reference_templates_count": len(reference_templates),
                        "performance_record_id": str(performance_record.id),
                        "ai_result": ai_result
                    }
            
            logger.warning(f"⚠️ AI subject generation failed for email #{email_number}")
            
        except Exception as e:
            logger.error(f"❌ AI subject generation error: {str(e)}")
        
        # Pure fallback (last resort)
        return await self._generate_template_based_fallback(
            db, product_name, selected_category, email_number, campaign_id, angle_id
        )
    
    def _create_reference_based_prompt(
        self,
        product_name: str,
        category: SubjectLineCategory,
        reference_templates: List,
        email_number: int
    ) -> str:
        """Create AI prompt using templates as reference patterns"""
        
        category_descriptions = {
            SubjectLineCategory.CURIOSITY_GAP: "creating curiosity and intrigue that makes people want to know more",
            SubjectLineCategory.URGENCY_SCARCITY: "creating urgency and scarcity to motivate immediate action",
            SubjectLineCategory.SOCIAL_PROOF: "leveraging social validation and community success",
            SubjectLineCategory.PERSONAL_BENEFIT: "highlighting personal benefits and value",
            SubjectLineCategory.TRANSFORMATION: "focusing on transformation and breakthrough stories",
            SubjectLineCategory.AUTHORITY_SCIENTIFIC: "using scientific authority and research backing",
            SubjectLineCategory.EMOTIONAL_TRIGGERS: "triggering emotional responses and connections",
            SubjectLineCategory.VALUE_PROMISE: "promising specific value and results",
            SubjectLineCategory.QUESTION_HOOKS: "using questions to engage and hook readers",
            SubjectLineCategory.INSIDER_SECRET: "revealing insider secrets and exclusive information"
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
CREATE A UNIQUE EMAIL SUBJECT LINE

PRODUCT: {product_name}
EMAIL #{email_number} in sequence
PSYCHOLOGY CATEGORY: {category.value}
GOAL: {category_descriptions.get(category, 'engaging the reader')}

REFERENCE PATTERNS (for inspiration only - DO NOT COPY):
{reference_examples}

YOUR TASK:
1. Study the psychology patterns in the reference examples
2. Create a COMPLETELY NEW subject line for {product_name}
3. Use similar psychological triggers but different wording
4. Make it unique, compelling, and specific to {product_name}
5. Keep under 50 characters for mobile optimization
6. NEVER use placeholders like [Product], Your, etc.

REQUIREMENTS:
- Use the exact product name: {product_name}
- Follow the {category.value} psychology approach
- Be creative and original
- Make people want to open the email
- Create intrigue and curiosity

Generate ONE unique subject line now:
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
            
            # Check if it's reasonable
            if 10 <= len(line) <= 100 and product_name.lower() in line.lower():
                return line
        
        return None
    
    async def _generate_template_based_fallback(
        self,
        db: AsyncSession,
        product_name: str,
        category: SubjectLineCategory,
        email_number: int,
        campaign_id: str,
        angle_id: str
    ) -> Dict[str, Any]:
        """Last resort: use template directly with product substitution"""
        
        # Get any template from this category
        templates = await self.template_crud.get_templates_by_category(
            db=db,
            category=category,
            limit=10
        )
        
        if templates:
            # Select template based on email number for variety
            template = templates[(email_number - 1) % len(templates)]
            subject_line = template.template_text.format(product=product_name)
            
            # Record usage
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
            
            logger.warning(f"🔄 Used template fallback: '{subject_line}'")
            
            return {
                "subject_line": subject_line,
                "category_used": category.value,
                "template_used": template.id,
                "performance_record_id": str(performance_record.id),
                "is_fallback": True
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
            "category_used": category.value,
            "performance_record_id": str(performance_record.id),
            "is_emergency_fallback": True
        }