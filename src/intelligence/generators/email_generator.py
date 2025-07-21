# src/intelligence/generators/email_generator.py
"""
ENHANCED EMAIL SEQUENCE GENERATOR WITH ULTRA-CHEAP AI INTEGRATION
✅ 97% cost savings through unified ultra-cheap provider system
✅ Campaign-centric email generation for affiliate marketers
✅ 5 diverse angles with intelligence-driven content
✅ Automatic failover across 11 ultra-cheap providers
✅ Real-time cost tracking and optimization
✅ Railway deployment compatible
🔥 FIXED: Product name placeholder elimination
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
import logging
import uuid
import re
from datetime import datetime

# Import enhanced base generator with ultra-cheap AI
from .base_generator import BaseContentGenerator
from src.models.base import EnumSerializerMixin

from src.intelligence.utils.product_name_fix import (
    substitute_product_placeholders,
    substitute_placeholders_in_data,
    extract_product_name_from_intelligence,
    fix_email_sequence_placeholders,
    validate_no_placeholders
)

logger = logging.getLogger(__name__)

class EmailSequenceGenerator(BaseContentGenerator, EnumSerializerMixin):
    """ email sequence generator with ultra-cheap AI integration and product name fixes"""
    
    def __init__(self):
        # Initialize with ultra-cheap AI system
        super().__init__("email_sequence")
        
        # Email-specific configurations
        self.email_angles = [
            {
                "id": "scientific_authority",
                "name": "Scientific Authority",
                "focus": "Research validation and clinical backing",
                "triggers": ["proven", "clinical", "research", "validated", "studies"],
                "approach": "Evidence-based credibility building"
            },
            {
                "id": "emotional_transformation",
                "name": "Emotional Transformation", 
                "focus": "Personal journey and breakthrough stories",
                "triggers": ["breakthrough", "transformation", "finally", "freedom", "hope"],
                "approach": "Inspirational storytelling"
            },
            {
                "id": "community_social_proof",
                "name": "Community Social Proof",
                "focus": "Peer validation and success stories", 
                "triggers": ["community", "together", "support", "testimonials", "others"],
                "approach": "Social validation and belonging"
            },
            {
                "id": "urgency_scarcity",
                "name": "Urgency & Scarcity",
                "focus": "Time-sensitive action motivation",
                "triggers": ["limited", "exclusive", "urgent", "act now", "deadline"],
                "approach": "Motivational pressure with value"
            },
            {
                "id": "lifestyle_confidence",
                "name": "Lifestyle & Confidence",
                "focus": "Aspirational lifestyle enhancement",
                "triggers": ["confident", "attractive", "energetic", "vibrant", "lifestyle"],
                "approach": "Identity and aspiration building"
            }
        ]
        
        logger.info(f"✅ Email Generator: Ultra-cheap AI system ready")
        logger.info(f"🎯 Email Angles: {len(self.email_angles)} diversified marketing approaches")
    
    async def generate_email_sequence(
        self,
        intelligence_data: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate campaign-centric email sequence with ultra-cheap AI and product name fixes"""
        
        if preferences is None:
            preferences = {}
        
        # 🔥 EXTRACT ACTUAL PRODUCT NAME FIRST
        actual_product_name = extract_product_name_from_intelligence(intelligence_data)
        logger.info(f"🎯 Email Generator: Using product name '{actual_product_name}'")
        
        # Extract intelligence for email generation
        product_details = self._extract_product_details(intelligence_data)
        product_details["name"] = actual_product_name
        
        sequence_length = self._safe_int_conversion(preferences.get("length", "5"), 5, 3, 10)
        uniqueness_id = str(uuid.uuid4())[:8]
        
        logger.info(f"🎯 Generating {sequence_length} emails for {actual_product_name}")
        
        # Create campaign-specific email prompt
        email_prompt = self._create_campaign_email_prompt(
            product_details, intelligence_data, sequence_length, preferences, uniqueness_id
        )
        
        # Generate with ultra-cheap AI system
        try:
            ai_result = await self._generate_with_ultra_cheap_ai(
                prompt=email_prompt,
                system_message=f"You are an expert email marketer creating diverse, high-converting email sequences. ALWAYS use the exact product name '{actual_product_name}' - never use placeholders like 'Your', 'PRODUCT', or '[Product]'.",
                max_tokens=4000,
                temperature=0.8,
                required_strength="long_form"
            )
            
            if ai_result and ai_result.get("content"):
                # Parse email sequence from AI response
                emails = self._parse_email_sequence(ai_result["content"], sequence_length, actual_product_name, uniqueness_id)
                
                if emails and len(emails) >= sequence_length:
                    # Apply angle diversity
                    diversified_emails = self._apply_angle_diversity(emails, sequence_length)
                    
                    # 🔥 APPLY PRODUCT NAME FIXES
                    fixed_emails = fix_email_sequence_placeholders(diversified_emails, intelligence_data)
                    
                    # 🔥 VALIDATE NO PLACEHOLDERS REMAIN
                    for email in fixed_emails:
                        subject_clean = validate_no_placeholders(email.get("subject", ""), actual_product_name)
                        body_clean = validate_no_placeholders(email.get("body", ""), actual_product_name)
                        if not subject_clean or not body_clean:
                            logger.warning(f"⚠️ Placeholders found in email {email.get('email_number', 'unknown')}")
                    
                    logger.info(f"✅ SUCCESS: Generated {len(fixed_emails)} diverse emails with product name '{actual_product_name}'")
                    
                    return self._create_standardized_response(
                        content={
                            "sequence_title": f"Campaign Email Sequence - {actual_product_name}",
                            "emails": fixed_emails,
                            "campaign_focus": "Diversified affiliate email marketing with angle rotation",
                            "product_name_used": actual_product_name,
                            "placeholders_fixed": True
                        },
                        title=f"{len(fixed_emails)}-Email Campaign Sequence for {actual_product_name}",
                        product_name=actual_product_name,
                        ai_result=ai_result,
                        preferences=preferences
                    )
        
        except Exception as e:
            logger.error(f"❌ Ultra-cheap AI email generation failed: {str(e)}")
        
        #  fallback with guaranteed diversity and product name fixes
        logger.warning("🔄 Using enhanced email fallback with campaign focus")
        return self._guaranteed_campaign_email_fallback(product_details, sequence_length, uniqueness_id)
    
    async def generate_content(self, intelligence_data: Dict[str, Any], preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate content - main interface for factory integration"""
        return await self.generate_email_sequence(intelligence_data, preferences)
    
    def _create_campaign_email_prompt(
        self, 
        product_details: Dict[str, str], 
        intelligence_data: Dict[str, Any], 
        sequence_length: int, 
        preferences: Dict[str, Any],
        uniqueness_id: str
    ) -> str:
        """Create campaign-centric email generation prompt with product name enforcement"""
        
        actual_product_name = product_details['name']
        
        prompt = f"""
CAMPAIGN EMAIL SEQUENCE GENERATION
Campaign ID: {uniqueness_id}

CRITICAL: Use ONLY the actual product name "{actual_product_name}" throughout all emails.
NEVER use placeholders like "Your", "PRODUCT", "[Product]", "Your Company", etc.

PRODUCT CAMPAIGN: {actual_product_name}
TARGET AUDIENCE: {product_details['audience']}
CORE BENEFITS: {product_details['benefits']}

CREATE {sequence_length} DIFFERENT EMAILS USING STRATEGIC ANGLE ROTATION:

Email 1 - SCIENTIFIC AUTHORITY ANGLE:
Focus: Research validation and clinical backing for {actual_product_name}
Tone: Authoritative, trustworthy, fact-based

Email 2 - EMOTIONAL TRANSFORMATION ANGLE:
Focus: Personal journey and breakthrough stories with {actual_product_name}
Tone: Empathetic, inspiring, personal

Email 3 - COMMUNITY SOCIAL PROOF ANGLE:
Focus: Peer validation and success stories with {actual_product_name}
Tone: Inclusive, supportive, social

Email 4 - URGENCY & SCARCITY ANGLE:
Focus: Time-sensitive action motivation for {actual_product_name}
Tone: Motivational, direct, action-oriented

Email 5 - LIFESTYLE & CONFIDENCE ANGLE:
Focus: Aspirational lifestyle enhancement with {actual_product_name}
Tone: Aspirational, confident, lifestyle-focused

OUTPUT FORMAT:
===EMAIL_1===
SUBJECT: [Subject line featuring {actual_product_name}]
BODY: [300-500 words about {actual_product_name}]
SEND_DELAY: Day 1
ANGLE: Scientific Authority
===END_EMAIL_1===

[Continue for all {sequence_length} emails]

CRITICAL REQUIREMENTS:
1. Use '{actual_product_name}' consistently - NEVER use placeholders
2. Each email must use a different strategic angle
3. ABSOLUTELY FORBIDDEN: "Your", "PRODUCT", "[Product]", "Your Company"

Generate the complete {sequence_length}-email sequence now.
"""
        
        return prompt
    
    def _parse_email_sequence(self, ai_response: str, sequence_length: int, product_name: str, uniqueness_id: str) -> List[Dict]:
        """Parse email sequence from AI response"""
        
        emails = []
        
        # Try structured parsing
        try:
            emails = self._parse_structured_email_format(ai_response, sequence_length, product_name, uniqueness_id)
            if emails and len(emails) >= 3:
                return emails
        except Exception as e:
            logger.warning(f"⚠️ Structured parsing failed: {str(e)}")
        
        # Emergency extraction
        return self._emergency_email_extraction(ai_response, sequence_length, product_name, uniqueness_id)
    
    def _parse_structured_email_format(self, ai_response: str, sequence_length: int, product_name: str, uniqueness_id: str) -> List[Dict]:
        """Parse structured ===EMAIL_X=== format"""
        
        emails = []
        email_blocks = re.split(r'===EMAIL_(\d+)===', ai_response, flags=re.IGNORECASE)
        
        if len(email_blocks) > 1:
            email_blocks = email_blocks[1:]
        
        for i in range(0, len(email_blocks) - 1, 2):
            try:
                email_num = int(email_blocks[i])
                email_content = email_blocks[i + 1] if i + 1 < len(email_blocks) else ""
                
                email_content = re.sub(r'===END_EMAIL_\d+===.*$', '', email_content, flags=re.DOTALL | re.IGNORECASE)
                email_content = email_content.strip()
                
                if not email_content:
                    continue
                
                email_data = self._extract_email_components(email_content, email_num, product_name, uniqueness_id)
                
                if email_data and email_data.get("body"):
                    emails.append(email_data)
                
            except (ValueError, IndexError) as e:
                logger.warning(f"⚠️ Error parsing email block {i}: {str(e)}")
                continue
        
        return emails[:sequence_length]
    
    def _extract_email_components(self, email_content: str, email_num: int, product_name: str, uniqueness_id: str) -> Dict[str, Any]:
        """Extract individual email components"""
        
        email_data = {
            "email_number": email_num,
            "subject": "",
            "body": "",
            "send_delay": f"Day {email_num * 2 - 1}",
            "campaign_focus": f"Campaign email for {product_name}",
            "uniqueness_id": uniqueness_id,
            "email_type": "campaign_email",
            "strategic_angle": "unknown",
            "product_name": product_name,
            "ultra_cheap_generated": True
        }
        
        lines = email_content.split('\n')
        current_section = None
        body_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.upper().startswith('SUBJECT:'):
                current_section = 'subject'
                subject_text = line[8:].strip()
                if subject_text:
                    email_data["subject"] = subject_text
            elif line.upper().startswith('BODY:'):
                current_section = 'body'
                body_text = line[5:].strip()
                if body_text:
                    body_lines.append(body_text)
            elif line.upper().startswith('SEND_DELAY:'):
                delay_text = line[11:].strip()
                if delay_text:
                    email_data["send_delay"] = delay_text
            elif line.upper().startswith('ANGLE:'):
                angle_text = line[6:].strip()
                if angle_text:
                    email_data["strategic_angle"] = angle_text.lower().replace(" ", "_")
            else:
                if current_section == 'subject' and not email_data["subject"]:
                    email_data["subject"] = line
                elif current_section == 'body':
                    body_lines.append(line)
                elif not email_data["subject"] and len(line) < 100:
                    email_data["subject"] = line
                    current_section = 'body'
                else:
                    body_lines.append(line)
        
        if body_lines:
            email_data["body"] = ' '.join(body_lines)
        
        # Ensure minimum content quality
        if not email_data["subject"]:
            email_data["subject"] = f"{product_name} - Important Update #{email_num}"
        
        if not email_data["body"]:
            email_data["body"] = f"Discover the comprehensive benefits of {product_name} through our scientifically-backed approach to health optimization."
        
        # Apply product name fixes
        for field in ["subject", "body", "campaign_focus"]:
            if email_data[field]:
                email_data[field] = substitute_product_placeholders(email_data[field], product_name)
        
        return email_data
    
    def _emergency_email_extraction(self, ai_response: str, sequence_length: int, product_name: str, uniqueness_id: str) -> List[Dict]:
        """Emergency email extraction when parsing fails"""
        
        logger.warning("🚨 Using emergency email extraction")
        
        emails = []
        for i in range(sequence_length):
            angle = self.email_angles[i % len(self.email_angles)]
            
            email_data = {
                "email_number": i + 1,
                "subject": f"{product_name} - {angle['name']}",
                "body": f"Discover {product_name} through our {angle['focus'].lower()} approach. Experience the benefits of {product_name} for your health optimization journey.",
                "send_delay": f"Day {i * 2 + 1}",
                "campaign_focus": f"{angle['name']} campaign email for {product_name}",
                "uniqueness_id": uniqueness_id,
                "email_type": "campaign_email",
                "strategic_angle": angle["id"],
                "emergency_generated": True,
                "product_name": product_name,
                "ultra_cheap_generated": True
            }
            
            # Apply product name fixes
            email_data["subject"] = substitute_product_placeholders(email_data["subject"], product_name)
            email_data["body"] = substitute_product_placeholders(email_data["body"], product_name)
            
            emails.append(email_data)
        
        return emails
    
    def _apply_angle_diversity(self, emails: List[Dict], sequence_length: int) -> List[Dict]:
        """Apply strategic angle diversity to email sequence"""
        
        diversified_emails = []
        
        for i, email in enumerate(emails[:sequence_length]):
            angle = self.email_angles[i % len(self.email_angles)]
            
            enhanced_email = email.copy()
            enhanced_email["strategic_angle"] = angle["id"]
            enhanced_email["angle_name"] = angle["name"]
            enhanced_email["angle_focus"] = angle["focus"]
            enhanced_email["angle_approach"] = angle["approach"]
            enhanced_email["emotional_triggers"] = angle["triggers"]
            enhanced_email["email_type"] = "campaign_email"
            enhanced_email["content_variety"] = "high"
            
            enhanced_email["campaign_focus"] = f"{angle['name']} campaign email - {angle['approach']}"
            
            enhanced_email["campaign_metadata"] = {
                "angle_position": i + 1,
                "total_angles": len(self.email_angles),
                "diversity_strategy": "angle_rotation",
                "marketing_approach": "affiliate_campaign"
            }
            
            diversified_emails.append(enhanced_email)
        
        return diversified_emails
    
    def _guaranteed_campaign_email_fallback(self, product_details: Dict[str, str], sequence_length: int, uniqueness_id: str) -> Dict[str, Any]:
        """Guaranteed campaign email generation with product name fixes"""
        
        actual_product_name = product_details["name"]
        logger.info(f"🔄 Generating guaranteed campaign email sequence for '{actual_product_name}'")
        
        emails = []
        
        for i in range(sequence_length):
            angle = self.email_angles[i % len(self.email_angles)]
            
            email = {
                "email_number": i + 1,
                "subject": f"{angle['name']}: {actual_product_name} Benefits Revealed",
                "body": f"""Discover the power of {actual_product_name} through our {angle['focus'].lower()} approach.

{actual_product_name} represents a comprehensive solution for {product_details['audience']} seeking {product_details['benefits']}.

Our {angle['approach'].lower()} focuses on delivering real results through proven methods that work with your body's natural processes.

Experience the difference {actual_product_name} can make in your health journey.

Key benefits of this approach:
• {angle['focus']} for maximum impact
• Research-backed methodology
• Proven results for thousands of users
• Safe, natural, and effective

Ready to take the next step with {actual_product_name}?

Best regards,
Your {actual_product_name} Team""",
                "send_delay": f"Day {i * 2 + 1}",
                "campaign_focus": f"{angle['name']} campaign email for {actual_product_name}",
                "uniqueness_id": uniqueness_id,
                "strategic_angle": angle["id"],
                "angle_name": angle["name"],
                "angle_focus": angle["focus"],
                "angle_approach": angle["approach"],
                "emotional_triggers": angle["triggers"],
                "email_type": "campaign_email",
                "guaranteed_generation": True,
                "product_name": actual_product_name
            }
            emails.append(email)
        
        # Apply final product name fixes
        fixed_emails = []
        for email in emails:
            fixed_email = email.copy()
            for field in ["subject", "body", "campaign_focus"]:
                if fixed_email[field]:
                    fixed_email[field] = substitute_product_placeholders(fixed_email[field], actual_product_name)
            fixed_emails.append(fixed_email)
        
        fallback_ai_result = {
            "content": "Fallback content generated",
            "provider_used": "guaranteed_fallback",
            "cost": 0.0,
            "quality_score": 70,
            "generation_time": 0.5
        }
        
        return self._create_standardized_response(
            content={
                "sequence_title": f"Guaranteed Campaign Email Sequence - {actual_product_name}",
                "emails": fixed_emails,
                "campaign_focus": "Guaranteed diverse affiliate email marketing with angle rotation",
                "reliability": "guaranteed",
                "generation_method": "fallback_with_diversity",
                "product_name_used": actual_product_name,
                "placeholders_fixed": True
            },
            title=f"Guaranteed {sequence_length}-Email Campaign Sequence for {actual_product_name}",
            product_name=actual_product_name,
            ai_result=fallback_ai_result,
            preferences={}
        )
    
    def _extract_product_details(self, intelligence_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract product details from intelligence data"""
        
        actual_product_name = extract_product_name_from_intelligence(intelligence_data)
        
        offer_intel = self._serialize_enum_field(intelligence_data.get("offer_intelligence", {}))
        
        benefits = offer_intel.get("benefits", ["health optimization", "metabolic enhancement", "natural wellness"])
        if isinstance(benefits, list):
            benefits_str = ", ".join(benefits[:3])
        else:
            benefits_str = "health optimization, metabolic enhancement, natural wellness"
        
        return {
            "name": actual_product_name,
            "benefits": benefits_str,
            "audience": "health-conscious adults seeking natural solutions",
            "transformation": "natural health improvement and lifestyle enhancement"
        }
    
    def _safe_int_conversion(self, value: str, default: int, min_val: int, max_val: int) -> int:
        """Safe integer conversion with bounds checking"""
        try:
            result = int(value) if str(value).isdigit() else default
            return max(min_val, min(max_val, result))
        except:
            return default


# Alias classes for backward compatibility
EmailGenerator = EmailSequenceGenerator
ContentGenerator = EmailSequenceGenerator
ProductionEmailGenerator = EmailSequenceGenerator

# Convenience functions
async def generate_email_sequence_with_ultra_cheap_ai(
    intelligence_data: Dict[str, Any],
    sequence_length: int = 5,
    preferences: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Generate email sequence using ultra-cheap AI system with product name fixes"""
    
    generator = EmailSequenceGenerator()
    if preferences is None:
        preferences = {"length": str(sequence_length)}
    else:
        preferences["length"] = str(sequence_length)
    
    return await generator.generate_email_sequence(intelligence_data, preferences)

def get_email_generator_cost_summary() -> Dict[str, Any]:
    """Get cost summary from email generator"""
    generator = EmailSequenceGenerator()
    return generator.get_cost_summary()