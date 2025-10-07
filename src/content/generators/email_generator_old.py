# src/content/generators/email_generator.py
"""Remove ALL tempalate mock data and generate content using the campaign intelligence data"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone
from uuid import UUID

logger = logging.getLogger(__name__)

class EmailGenerator:
    """Enhanced Email Generator integrating with Intelligence Engine"""
    
    def __init__(self):
        self.name = "email_generator"
        self.version = "2.0.0"
        self._generation_stats = {
            "sequences_generated": 0,
            "total_emails_created": 0,
            "learning_enabled_count": 0
        }
    
    async def generate_email_sequence(
        self,
        campaign_id: Union[str, UUID],
        product_name: str,
        sequence_length: int = 5,
        tone: str = "conversational",
        target_audience: Optional[str] = None,
        use_intelligence: bool = True,
        enable_learning: bool = True
    ) -> Dict[str, Any]:
        """Generate complete email sequence with intelligence integration"""
        try:
            logger.info(f"Generating email sequence for campaign {campaign_id}")
            
            # Get campaign intelligence if available
            campaign_intelligence = None
            if use_intelligence:
                campaign_intelligence = await self._get_campaign_intelligence(campaign_id)
            
            # Generate sequence
            emails = []
            for i in range(sequence_length):
                email = await self._generate_single_email(
                    email_number=i + 1,
                    product_name=product_name,
                    tone=tone,
                    target_audience=target_audience,
                    campaign_intelligence=campaign_intelligence,
                    total_in_sequence=sequence_length
                )
                emails.append(email)
            
            # Update stats
            self._generation_stats["sequences_generated"] += 1
            self._generation_stats["total_emails_created"] += len(emails)
            if enable_learning:
                self._generation_stats["learning_enabled_count"] += 1
            
            return {
                "success": True,
                "campaign_id": str(campaign_id),
                "emails": emails,
                "sequence_info": {
                    "total_emails": len(emails),
                    "product_name": product_name,
                    "tone": tone,
                    "intelligence_used": use_intelligence,
                    "learning_enabled": enable_learning,
                    "generation_method": "enhanced_ai"
                },
                "generation_metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "generator_version": self.version,
                    "intelligence_sources": len(campaign_intelligence) if campaign_intelligence else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Email sequence generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "campaign_id": str(campaign_id)
            }
    
    async def _get_campaign_intelligence(self, campaign_id: Union[str, UUID]) -> Optional[List[Dict]]:
        """Get campaign intelligence for email generation"""
        try:
            # This would integrate with the Intelligence Module
            # For now, return None - will be implemented when services are re-enabled
            return None
        except Exception as e:
            logger.error(f"Failed to get campaign intelligence: {e}")
            return None
    
    async def _generate_single_email(
        self,
        email_number: int,
        product_name: str,
        tone: str,
        target_audience: Optional[str],
        campaign_intelligence: Optional[List[Dict]],
        total_in_sequence: int
    ) -> Dict[str, Any]:
        """Generate a single email in the sequence"""
        
        # Email timing strategy
        send_delays = ["immediate", "2 days", "4 days", "7 days", "10 days", "14 days", "21 days"]
        strategic_angles = [
            "curiosity_introduction",
            "problem_awareness", 
            "solution_presentation",
            "social_proof",
            "urgency_close",
            "bonus_offer",
            "final_opportunity"
        ]
        
        delay = send_delays[min(email_number - 1, len(send_delays) - 1)]
        angle = strategic_angles[min(email_number - 1, len(strategic_angles) - 1)]
        
        # Generate subject line
        subject = await self._generate_subject_line(
            email_number=email_number,
            product_name=product_name,
            strategic_angle=angle,
            intelligence=campaign_intelligence
        )
        
        # Generate email body
        body = await self._generate_email_body(
            email_number=email_number,
            product_name=product_name,
            tone=tone,
            target_audience=target_audience,
            strategic_angle=angle,
            intelligence=campaign_intelligence
        )
        
        return {
            "email_number": email_number,
            "subject": subject,
            "body": body,
            "send_delay": delay,
            "strategic_angle": angle,
            "metadata": {
                "total_in_sequence": total_in_sequence,
                "intelligence_enhanced": campaign_intelligence is not None,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    
    async def _generate_subject_line(
        self,
        email_number: int,
        product_name: str,
        strategic_angle: str,
        intelligence: Optional[List[Dict]]
    ) -> str:
        """Last resort fallback is to generate subject line using templates and intelligence"""
        """Ai should always generate subject lines using the stored campaign intelligence and introduce the product_name"""
        
        # Subject line templates by strategic angle
        templates = {
            "curiosity_introduction": [
                f"The {product_name} secret nobody talks about",
                f"What {product_name} users wish they knew sooner",
                f"Inside: The {product_name} approach that changes everything"
            ],
            "problem_awareness": [
                f"Why {product_name} might not work for you (unless...)",
                f"The {product_name} mistake 90% of people make",
                f"Warning: Don't try {product_name} until you read this"
            ],
            "solution_presentation": [
                f"How {product_name} solves your biggest challenge",
                f"The {product_name} method that actually works",
                f"{product_name}: Your step-by-step solution"
            ],
            "social_proof": [
                f"Why thousands choose {product_name} over alternatives",
                f"Real {product_name} results from real people",
                f"Case study: How {product_name} transformed [specific result]"
            ],
            "urgency_close": [
                f"Last chance for {product_name} at this price",
                f"Your {product_name} discount expires tomorrow",
                f"Final hours: {product_name} limited availability"
            ]
        }
        
        # Select template based on angle
        angle_templates = templates.get(strategic_angle, templates["curiosity_introduction"])
        
        # For now, return first template - in full implementation, would use AI
        return angle_templates[0]
    
    async def _generate_email_body(
        self,
        email_number: int,
        product_name: str,
        tone: str,
        target_audience: Optional[str],
        strategic_angle: str,
        intelligence: Optional[List[Dict]]
    ) -> str:
        """Generate email body content"""
        
        # Email structure templates
        if strategic_angle == "curiosity_introduction":
            body = f"""Hi there,

I wanted to share something with you about {product_name} that most people don't realize...

[Opening hook based on intelligence insights]

The truth is, {product_name} isn't just another solution. It's designed specifically for people who [target audience insight].

Here's what makes it different:

• [Key differentiator 1]
• [Key differentiator 2]  
• [Key differentiator 3]

I'll share more details in my next email, including [specific benefit preview].

Talk soon,
[Sender Name]

P.S. Keep an eye out for tomorrow's email - I'm sharing [curiosity hook for next email]."""

        elif strategic_angle == "problem_awareness":
            body = f"""Hi [Name],

Yesterday I introduced you to {product_name}, and I want to address something important...

Most people try {product_name} and don't get the results they expect. Here's why:

[Problem identification based on intelligence]

The issue isn't with {product_name} itself - it's how people approach it.

Common mistakes I see:
1. [Mistake 1 from intelligence insights]
2. [Mistake 2 from audience analysis]
3. [Mistake 3 from market research]

But here's the good news...

When you use {product_name} correctly, [specific transformation promise].

Tomorrow, I'll show you exactly how to avoid these pitfalls and get maximum results.

Best,
[Sender Name]"""

        else:
            # Default template
            body = f"""Hi [Name],

Here's what I want to share with you about {product_name}...

[Content based on strategic angle and intelligence]

[Main message body]

[Call to action]

Best regards,
[Sender Name]"""

        return body
    
    def get_stats(self) -> Dict[str, Any]:
        """Get email generator statistics"""
        return {
            "generator": self.name,
            "version": self.version,
            "stats": self._generation_stats
        }