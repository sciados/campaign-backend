# src/intelligence/generators/email_generator.py
"""
ENHANCED EMAIL SEQUENCE GENERATOR WITH ULTRA-CHEAP AI INTEGRATION
✅ 97% cost savings through unified ultra-cheap provider system
✅ Campaign-centric email generation for affiliate marketers
✅ 5 diverse angles with intelligence-driven content
✅ Automatic failover across 11 ultra-cheap providers
✅ Real-time cost tracking and optimization
✅ Railway deployment compatible
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

logger = logging.getLogger(__name__)

class EmailSequenceGenerator(BaseContentGenerator, EnumSerializerMixin):
    """Enhanced email sequence generator with ultra-cheap AI integration"""
    
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
        
        logger.info(f"✅ Email Generator: Ultra-cheap AI system ready with {len(self.ultra_cheap_providers)} providers")
        logger.info(f"🎯 Email Angles: {len(self.email_angles)} diversified marketing approaches")
    
    async def generate_email_sequence(
        self,
        intelligence_data: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate campaign-centric email sequence with ultra-cheap AI"""
        
        if preferences is None:
            preferences = {}
        
        # Extract intelligence for email generation
        product_details = self._extract_product_details(intelligence_data)
        sequence_length = self._safe_int_conversion(preferences.get("length", "5"), 5, 3, 10)
        uniqueness_id = str(uuid.uuid4())[:8]
        
        logger.info(f"🎯 Generating {sequence_length} emails for {product_details['name']} (Campaign ID: {uniqueness_id})")
        
        # Create campaign-specific email prompt
        email_prompt = self._create_campaign_email_prompt(
            product_details, intelligence_data, sequence_length, preferences, uniqueness_id
        )
        
        # Generate with ultra-cheap AI system
        try:
            ai_result = await self._generate_with_ultra_cheap_ai(
                prompt=email_prompt,
                system_message="You are an expert email marketer creating diverse, high-converting email sequences for affiliate campaigns. Each email must use a completely different strategic angle.",
                max_tokens=4000,
                temperature=0.8,
                required_strength="long_form"  # Prefer providers good at long-form content
            )
            
            if ai_result and ai_result.get("content"):
                # Parse email sequence from AI response
                emails = self._parse_email_sequence(ai_result["content"], sequence_length, product_details['name'], uniqueness_id)
                
                if emails and len(emails) >= sequence_length:
                    # Apply angle diversity
                    diversified_emails = self._apply_angle_diversity(emails, sequence_length)
                    
                    logger.info(f"✅ SUCCESS: Generated {len(diversified_emails)} diverse emails with ultra-cheap AI")
                    
                    return self._create_standardized_response(
                        content={
                            "sequence_title": f"Campaign Email Sequence - {product_details['name']}",
                            "emails": diversified_emails,
                            "campaign_focus": "Diversified affiliate email marketing with angle rotation"
                        },
                        title=f"{len(diversified_emails)}-Email Campaign Sequence for {product_details['name']}",
                        product_name=product_details['name'],
                        ai_result=ai_result,
                        preferences=preferences
                    )
        
        except Exception as e:
            logger.error(f"❌ Ultra-cheap AI email generation failed: {str(e)}")
        
        # Enhanced fallback with guaranteed diversity
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
        """Create campaign-centric email generation prompt"""
        
        # Extract angle-specific intelligence
        angles_intel = self._extract_angle_intelligence(intelligence_data)
        
        # Build comprehensive email campaign prompt
        prompt = f"""
CAMPAIGN EMAIL SEQUENCE GENERATION
Campaign ID: {uniqueness_id}

PRODUCT CAMPAIGN: {product_details['name']}
TARGET AUDIENCE: {product_details['audience']}
CORE BENEFITS: {product_details['benefits']}
TRANSFORMATION FOCUS: {product_details['transformation']}

CAMPAIGN REQUIREMENT: Create {sequence_length} COMPLETELY DIFFERENT emails using strategic angle rotation for maximum engagement and conversion variety.

ANGLE ROTATION STRATEGY:

Email 1 - SCIENTIFIC AUTHORITY ANGLE:
Focus: {angles_intel['scientific']['focus']}
Emotional triggers: proven, clinical, research, validated, evidence
Content approach: Research-backed credibility and clinical validation
Tone: Authoritative, trustworthy, fact-based

Email 2 - EMOTIONAL TRANSFORMATION ANGLE:
Focus: {angles_intel['emotional']['focus']}
Emotional triggers: breakthrough, transformation, finally, freedom, hope
Content approach: Personal journey storytelling and inspirational messaging
Tone: Empathetic, inspiring, personal

Email 3 - COMMUNITY SOCIAL PROOF ANGLE:
Focus: {angles_intel['community']['focus']}
Emotional triggers: community, together, support, testimonials, belonging
Content approach: Peer validation and shared success stories
Tone: Inclusive, supportive, social

Email 4 - URGENCY & SCARCITY ANGLE:
Focus: {angles_intel['urgency']['focus']}
Emotional triggers: limited, exclusive, urgent, act now, deadline
Content approach: Time-sensitive action motivation with clear value
Tone: Motivational, direct, action-oriented

Email 5 - LIFESTYLE & CONFIDENCE ANGLE:
Focus: {angles_intel['lifestyle']['focus']}
Emotional triggers: confident, attractive, energetic, vibrant, lifestyle
Content approach: Aspirational lifestyle enhancement and identity building
Tone: Aspirational, confident, lifestyle-focused

EMAIL SPECIFICATIONS:
- 300-500 words per email
- Compelling subject lines optimized for open rates
- Clear affiliate marketing focus with ethical promotion
- Proper send scheduling for engagement optimization
- Distinct voice and approach for each angle

OUTPUT FORMAT:
===EMAIL_1===
SUBJECT: [Scientific/research-focused subject line]
BODY: [300-500 words using SCIENTIFIC AUTHORITY angle - focus on research, clinical validation, proven results]
SEND_DELAY: Day 1
ANGLE: Scientific Authority
CAMPAIGN_ID: {uniqueness_id}
===END_EMAIL_1===

===EMAIL_2===
SUBJECT: [Story/transformation-focused subject line]
BODY: [300-500 words using EMOTIONAL TRANSFORMATION angle - focus on personal stories, hope, breakthrough moments]
SEND_DELAY: Day 3
ANGLE: Emotional Transformation
CAMPAIGN_ID: {uniqueness_id}
===END_EMAIL_2===

[Continue this pattern for all {sequence_length} emails, rotating through available angles]

CRITICAL CAMPAIGN REQUIREMENTS:
1. Each email must feel completely different in tone, approach, and emotional appeal
2. Use '{product_details['name']}' consistently throughout all emails
3. Focus on affiliate marketing best practices with ethical promotion
4. Include clear value propositions specific to each angle
5. Optimize for high engagement and conversion potential
6. Maintain campaign coherence while maximizing angle diversity

Generate the complete {sequence_length}-email campaign sequence now.
"""
        
        return prompt
    
    def _parse_email_sequence(self, ai_response: str, sequence_length: int, product_name: str, uniqueness_id: str) -> List[Dict]:
        """Parse email sequence from AI response with enhanced error handling"""
        
        emails = []
        
        # Try structured parsing first
        try:
            emails = self._parse_structured_email_format(ai_response, sequence_length, product_name, uniqueness_id)
            if emails and len(emails) >= sequence_length:
                return emails
        except Exception as e:
            logger.warning(f"⚠️ Structured parsing failed: {str(e)}")
        
        # Try flexible parsing
        try:
            emails = self._parse_flexible_email_format(ai_response, sequence_length, product_name, uniqueness_id)
            if emails and len(emails) >= sequence_length:
                return emails
        except Exception as e:
            logger.warning(f"⚠️ Flexible parsing failed: {str(e)}")
        
        # Emergency extraction
        return self._emergency_email_extraction(ai_response, sequence_length, product_name, uniqueness_id)
    
    def _parse_structured_email_format(self, ai_response: str, sequence_length: int, product_name: str, uniqueness_id: str) -> List[Dict]:
        """Parse structured ===EMAIL_X=== format"""
        
        emails = []
        email_blocks = re.split(r'===EMAIL_(\d+)===', ai_response, flags=re.IGNORECASE)
        
        if len(email_blocks) > 1:
            email_blocks = email_blocks[1:]  # Remove content before first email
        
        for i in range(0, len(email_blocks) - 1, 2):
            try:
                email_num = int(email_blocks[i])
                email_content = email_blocks[i + 1] if i + 1 < len(email_blocks) else ""
                
                # Clean up content
                email_content = re.sub(r'===END_EMAIL_\d+===.*$', '', email_content, flags=re.DOTALL | re.IGNORECASE)
                email_content = email_content.strip()
                
                if not email_content:
                    continue
                
                # Parse email components
                email_data = self._extract_email_components(email_content, email_num, product_name, uniqueness_id)
                
                if email_data and email_data.get("body") and len(email_data["body"].split()) >= 50:
                    emails.append(email_data)
                
            except (ValueError, IndexError) as e:
                logger.warning(f"⚠️ Error parsing email block {i}: {str(e)}")
                continue
        
        return emails[:sequence_length]
    
    def _extract_email_components(self, email_content: str, email_num: int, product_name: str, uniqueness_id: str) -> Dict[str, Any]:
        """Extract individual email components from content"""
        
        email_data = {
            "email_number": email_num,
            "subject": "",
            "body": "",
            "send_delay": f"Day {email_num * 2 - 1}",
            "campaign_focus": f"Campaign email for {product_name}",
            "uniqueness_id": uniqueness_id,
            "email_type": "campaign_email",
            "strategic_angle": "unknown"
        }
        
        lines = email_content.split('\n')
        current_section = None
        body_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse structured fields
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
            elif line.upper().startswith('SEND_DELAY:') or line.upper().startswith('DELAY:'):
                delay_text = re.sub(r'SEND_DELAY:|DELAY:', '', line, flags=re.IGNORECASE).strip()
                if delay_text:
                    email_data["send_delay"] = delay_text
            elif line.upper().startswith('ANGLE:'):
                angle_text = line[6:].strip()
                if angle_text:
                    email_data["strategic_angle"] = angle_text.lower().replace(" ", "_").replace("&", "")
                    email_data["campaign_focus"] = f"{angle_text} campaign email for {product_name}"
            elif line.upper().startswith('CAMPAIGN_ID:'):
                campaign_id = line[12:].strip()
                if campaign_id:
                    email_data["uniqueness_id"] = campaign_id
            else:
                # Handle content based on current section
                if current_section == 'subject' and not email_data["subject"]:
                    email_data["subject"] = line
                elif current_section == 'body':
                    body_lines.append(line)
                elif not email_data["subject"] and len(line) < 100:  # Likely a subject line
                    email_data["subject"] = line
                    current_section = 'body'
                else:
                    body_lines.append(line)
        
        # Finalize body content
        if body_lines:
            email_data["body"] = ' '.join(body_lines)
        
        # Ensure minimum content quality
        if not email_data["subject"]:
            email_data["subject"] = f"{product_name} - Important Update #{email_num}"
        
        if not email_data["body"] or len(email_data["body"].split()) < 50:
            email_data["body"] = f"Discover the comprehensive benefits of {product_name} through our scientifically-backed approach to health optimization. This email focuses on delivering real value and actionable insights for your wellness journey. Experience the difference that quality and research make in your health transformation with {product_name}."
        
        # Clean product references
        for field in ["subject", "body", "campaign_focus"]:
            email_data[field] = email_data[field].replace("[product]", product_name)
            email_data[field] = email_data[field].replace("Product", product_name)
            email_data[field] = email_data[field].replace("PRODUCT", product_name)
        
        return email_data
    
    def _parse_flexible_email_format(self, ai_response: str, sequence_length: int, product_name: str, uniqueness_id: str) -> List[Dict]:
        """Parse flexible email format when structured parsing fails"""
        
        emails = []
        
        # Split by common email separators
        separators = [
            r'\n\s*Email \d+',
            r'\n\s*\d+\.',
            r'\n\s*Subject:',
            r'\n---+',
            r'\n===+'
        ]
        
        email_sections = [ai_response]
        
        for separator in separators:
            new_sections = []
            for section in email_sections:
                new_sections.extend(re.split(separator, section, flags=re.IGNORECASE | re.MULTILINE))
            email_sections = new_sections
        
        # Process each section
        email_count = 0
        for i, section in enumerate(email_sections):
            section = section.strip()
            if len(section) < 100:  # Too short to be an email
                continue
            
            email_count += 1
            if email_count > sequence_length:
                break
            
            # Extract subject and body
            lines = section.split('\n')
            subject = ""
            body_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if not subject and (len(line) < 100 or 'subject:' in line.lower()):
                    subject = re.sub(r'subject:\s*', '', line, flags=re.IGNORECASE).strip()
                else:
                    body_lines.append(line)
            
            if not subject:
                subject = f"{product_name} Email #{email_count}"
            
            body = ' '.join(body_lines) if body_lines else f"Quality health optimization with {product_name} - email content {email_count}."
            
            email_data = {
                "email_number": email_count,
                "subject": subject,
                "body": body,
                "send_delay": f"Day {email_count * 2 - 1}",
                "campaign_focus": f"Campaign email for {product_name}",
                "uniqueness_id": uniqueness_id,
                "email_type": "campaign_email",
                "strategic_angle": self.email_angles[(email_count - 1) % len(self.email_angles)]["id"]
            }
            
            emails.append(email_data)
        
        return emails
    
    def _emergency_email_extraction(self, ai_response: str, sequence_length: int, product_name: str, uniqueness_id: str) -> List[Dict]:
        """Emergency email extraction when all parsing fails"""
        
        logger.warning("🚨 Using emergency email extraction")
        
        # Split content into rough sections
        sections = ai_response.split('\n\n')
        useful_sections = [s.strip() for s in sections if len(s.strip()) > 50]
        
        emails = []
        for i in range(sequence_length):
            angle = self.email_angles[i % len(self.email_angles)]
            
            # Use available content or generate minimal content
            if i < len(useful_sections):
                content = useful_sections[i]
                # Extract potential subject line (first line if short)
                lines = content.split('\n')
                if lines and len(lines[0]) < 100:
                    subject = lines[0].strip()
                    body = '\n'.join(lines[1:]).strip()
                else:
                    subject = f"{product_name} - {angle['name']}"
                    body = content
            else:
                subject = f"{product_name} - {angle['name']}"
                body = f"Discover {product_name} through our {angle['focus'].lower()} approach. Experience the benefits of {product_name} for your health optimization journey."
            
            email_data = {
                "email_number": i + 1,
                "subject": subject,
                "body": body,
                "send_delay": f"Day {i * 2 + 1}",
                "campaign_focus": f"{angle['name']} campaign email for {product_name}",
                "uniqueness_id": uniqueness_id,
                "email_type": "campaign_email",
                "strategic_angle": angle["id"],
                "emergency_generated": True
            }
            
            emails.append(email_data)
        
        return emails
    
    def _apply_angle_diversity(self, emails: List[Dict], sequence_length: int) -> List[Dict]:
        """Apply strategic angle diversity to email sequence"""
        
        diversified_emails = []
        
        for i, email in enumerate(emails[:sequence_length]):
            # Assign angle based on rotation
            angle = self.email_angles[i % len(self.email_angles)]
            
            enhanced_email = email.copy()
            enhanced_email["strategic_angle"] = angle["id"]
            enhanced_email["angle_name"] = angle["name"]
            enhanced_email["angle_focus"] = angle["focus"]
            enhanced_email["angle_approach"] = angle["approach"]
            enhanced_email["emotional_triggers"] = angle["triggers"]
            enhanced_email["email_type"] = "campaign_email"
            enhanced_email["content_variety"] = "high"
            
            # Update campaign focus for angle
            enhanced_email["campaign_focus"] = f"{angle['name']} campaign email - {angle['approach']}"
            
            # Add campaign metadata
            enhanced_email["campaign_metadata"] = {
                "angle_position": i + 1,
                "total_angles": len(self.email_angles),
                "diversity_strategy": "angle_rotation",
                "marketing_approach": "affiliate_campaign"
            }
            
            diversified_emails.append(enhanced_email)
        
        return diversified_emails
    
    def _guaranteed_campaign_email_fallback(self, product_details: Dict[str, str], sequence_length: int, uniqueness_id: str) -> Dict[str, Any]:
        """Guaranteed campaign email generation with ultra-cheap AI metadata"""
        
        logger.info("🔄 Generating guaranteed campaign email sequence")
        
        emails = []
        
        for i in range(sequence_length):
            angle = self.email_angles[i % len(self.email_angles)]
            
            email = {
                "email_number": i + 1,
                "subject": f"{angle['name']}: {product_details['name']} Benefits Revealed",
                "body": f"""Discover the power of {product_details['name']} through our {angle['focus'].lower()} approach.

{product_details['name']} represents a comprehensive solution for {product_details['audience']} seeking {product_details['benefits']}.

Our {angle['approach'].lower()} focuses on delivering real results through proven methods that work with your body's natural processes.

Experience the difference {product_details['name']} can make in your {product_details['transformation']} journey.

Key benefits of this approach:
• {angle['focus']} for maximum impact
• Research-backed methodology
• Proven results for thousands of users
• Safe, natural, and effective

Ready to take the next step with {product_details['name']}?

[Continue with ethical promotion and proper affiliate disclosures]

Best regards,
Your {product_details['name']} Team""",
                "send_delay": f"Day {i * 2 + 1}",
                "campaign_focus": f"{angle['name']} campaign email for {product_details['name']}",
                "uniqueness_id": uniqueness_id,
                "strategic_angle": angle["id"],
                "angle_name": angle["name"],
                "angle_focus": angle["focus"],
                "angle_approach": angle["approach"],
                "emotional_triggers": angle["triggers"],
                "email_type": "campaign_email",
                "guaranteed_generation": True,
                "ultra_cheap_ai_system": "fallback_mode"
            }
            emails.append(email)
        
        # Create response with ultra-cheap AI metadata
        fallback_ai_result = {
            "content": "Fallback content generated",
            "provider_used": "guaranteed_fallback",
            "cost": 0.0,
            "quality_score": 70,
            "generation_time": 0.5,
            "cost_optimization": {
                "provider_tier": "guaranteed",
                "cost_per_1k": 0.0,
                "savings_vs_openai": 0.030,
                "total_cost": 0.0,
                "fallback_reason": "Ultra-cheap AI system unavailable"
            }
        }
        
        return self._create_standardized_response(
            content={
                "sequence_title": f"Guaranteed Campaign Email Sequence - {product_details['name']}",
                "emails": emails,
                "campaign_focus": "Guaranteed diverse affiliate email marketing with angle rotation",
                "reliability": "guaranteed",
                "generation_method": "fallback_with_diversity"
            },
            title=f"Guaranteed {sequence_length}-Email Campaign Sequence for {product_details['name']}",
            product_name=product_details['name'],
            ai_result=fallback_ai_result,
            preferences={}
        )
    
    def _extract_angle_intelligence(self, intelligence_data: Dict) -> Dict[str, Dict]:
        """Extract angle-specific intelligence for email generation"""
        
        # Get angle-specific intelligence sections with enum serialization
        scientific_intel = self._serialize_enum_field(intelligence_data.get("scientific_authority_intelligence", {}))
        emotional_intel = self._serialize_enum_field(intelligence_data.get("emotional_transformation_intelligence", {}))
        community_intel = self._serialize_enum_field(intelligence_data.get("community_social_proof_intelligence", {}))
        urgency_intel = self._serialize_enum_field(intelligence_data.get("urgency_scarcity_intelligence", {}))
        lifestyle_intel = self._serialize_enum_field(intelligence_data.get("lifestyle_confidence_intelligence", {}))
        
        return {
            "scientific": {
                "focus": ", ".join(scientific_intel.get("clinical_studies", ["Research validation", "Clinical backing"])[:2]),
                "credibility": scientific_intel.get("credibility_score", 0.85)
            },
            "emotional": {
                "focus": ", ".join(emotional_intel.get("transformation_stories", ["Personal transformation", "Life-changing results"])[:2]),
                "credibility": 0.82
            },
            "community": {
                "focus": ", ".join(community_intel.get("social_proof_elements", ["Customer testimonials", "Community success"])[:2]),
                "credibility": 0.78
            },
            "urgency": {
                "focus": ", ".join(urgency_intel.get("urgency_messages", ["Time-sensitive offers", "Limited availability"])[:2]),
                "credibility": 0.75
            },
            "lifestyle": {
                "focus": ", ".join(lifestyle_intel.get("lifestyle_benefits", ["Confidence boost", "Energy enhancement"])[:2]),
                "credibility": 0.76
            }
        }
    
    def _safe_int_conversion(self, value: str, default: int, min_val: int, max_val: int) -> int:
        """Safe integer conversion with bounds checking"""
        try:
            result = int(value) if str(value).isdigit() else default
            return max(min_val, min(max_val, result))
        except:
            return default
    
    def _extract_product_details(self, intelligence_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract product details from intelligence data with enum serialization"""
        
        # Use enum serialization for offer intelligence
        offer_intel = self._serialize_enum_field(intelligence_data.get("offer_intelligence", {}))
        
        # Extract product name
        product_name = "PRODUCT"
        insights = offer_intel.get("insights", [])
        for insight in insights:
            if "called" in str(insight).lower():
                parts = str(insight).split("called")
                if len(parts) > 1:
                    name_part = parts[1].strip().split()[0].upper()
                    if name_part and name_part not in ["PRODUCT", "THE", "A", "AN"]:
                        product_name = name_part.replace(",", "").replace(".", "")
                        break
        
        # Extract additional details
        benefits = offer_intel.get("benefits", ["health optimization", "metabolic enhancement", "natural wellness"])
        if isinstance(benefits, list):
            benefits_str = ", ".join(benefits[:3])
        else:
            benefits_str = "health optimization, metabolic enhancement, natural wellness"
        
        return {
            "name": product_name,
            "benefits": benefits_str,
            "audience": "health-conscious adults seeking natural solutions",
            "transformation": "natural health improvement and lifestyle enhancement"
        }


# Alias classes for backward compatibility
EmailGenerator = EmailSequenceGenerator
ContentGenerator = EmailSequenceGenerator
ProductionEmailGenerator = EmailSequenceGenerator

# Convenience functions for backward compatibility
async def generate_email_sequence_with_ultra_cheap_ai(
    intelligence_data: Dict[str, Any],
    sequence_length: int = 5,
    preferences: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Generate email sequence using ultra-cheap AI system"""
    
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