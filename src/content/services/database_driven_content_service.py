# src/content/services/database_driven_content_service.py
"""
Database-Driven Content Service - NO MOCK DATA
All content generation based on real intelligence data from database
"""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
import json

logger = logging.getLogger(__name__)

class DatabaseDrivenContentService:
    """
    Content service that generates content exclusively from database intelligence
    NO mock data - all content driven by real campaign intelligence
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_content_from_intelligence(
        self,
        content_type: str,
        campaign_id: Union[str, UUID],
        user_id: Union[str, UUID],
        company_id: Union[str, UUID],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate content using only real intelligence data from database
        Returns error if insufficient intelligence data available
        """
        try:
            # Get campaign intelligence from database
            intelligence_data = await self._get_campaign_intelligence_data(campaign_id)
            
            if not intelligence_data:
                return {
                    "success": False,
                    "error": "No intelligence data available for this campaign",
                    "message": "Content generation requires campaign intelligence data. Please run campaign analysis first.",
                    "required_action": "analyze_campaign_sources"
                }
            
            # Get email templates from database if generating emails
            if content_type in ["email", "email_sequence"]:
                template_data = await self._get_email_templates_from_database()
                if not template_data:
                    return {
                        "success": False,
                        "error": "No email templates available in database",
                        "message": "Email generation requires templates in email_subject_templates table",
                        "required_action": "seed_email_templates"
                    }
            
            # Route to appropriate generator based on content type
            if content_type in ["email", "email_sequence"]:
                result = await self._generate_email_from_intelligence(intelligence_data, template_data, preferences or {})
            elif content_type == "social_post":
                result = await self._generate_social_from_intelligence(intelligence_data, preferences or {})
            elif content_type == "blog_article":
                result = await self._generate_blog_from_intelligence(intelligence_data, preferences or {})
            elif content_type == "ad_copy":
                result = await self._generate_ad_copy_from_intelligence(intelligence_data, preferences or {})
            else:
                return {
                    "success": False,
                    "error": f"Unsupported content type: {content_type}",
                    "supported_types": ["email", "email_sequence", "social_post", "blog_article", "ad_copy"]
                }
            
            # Store in database
            content_id = await self._store_content_with_intelligence_tracking(
                campaign_id=campaign_id,
                user_id=user_id,
                company_id=company_id,
                content_type=content_type,
                content_data=result,
                intelligence_used=intelligence_data,
                generation_settings=preferences or {}
            )
            
            return {
                "success": True,
                "content_id": str(content_id),
                "content_type": content_type,
                "generated_content": result,
                "intelligence_sources_used": len(intelligence_data),
                "workflow_step": "1_text_generation_database_driven"
            }
            
        except Exception as e:
            logger.error(f"Database-driven content generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content_type": content_type
            }
    
    async def _get_campaign_intelligence_data(self, campaign_id: Union[str, UUID]) -> List[Dict[str, Any]]:
        """Get real intelligence data from database for campaign"""
        try:
            # Query intelligence data from existing tables
            query = text("""
                SELECT 
                    ic.id as intelligence_id,
                    ic.product_name,
                    ic.salespage_url,
                    ic.confidence_score,
                    ic.analysis_method,
                    pd.features,
                    pd.benefits,
                    pd.ingredients,
                    pd.conditions,
                    pd.usage_instructions,
                    md.category,
                    md.positioning,
                    md.competitive_advantages,
                    md.target_audience,
                    kb.content as research_content,
                    kb.research_type
                FROM intelligence_core ic
                LEFT JOIN product_data pd ON ic.id = pd.intelligence_id
                LEFT JOIN market_data md ON ic.id = md.intelligence_id
                LEFT JOIN intelligence_research ir ON ic.id = ir.intelligence_id
                LEFT JOIN knowledge_base kb ON ir.research_id = kb.id
                WHERE ic.user_id IN (
                    SELECT user_id FROM campaigns WHERE id = :campaign_id
                )
                OR EXISTS (
                    SELECT 1 FROM intelligence_core ci 
                    WHERE ci.campaign_id = :campaign_id 
                    AND ci.intelligence_id = ic.id
                )
                ORDER BY ic.confidence_score DESC, ic.created_at DESC
            """)
            
            result = await self.db.execute(query, {"campaign_id": UUID(str(campaign_id))})
            rows = result.fetchall()
            
            if not rows:
                logger.warning(f"No intelligence data found for campaign {campaign_id}")
                return []
            
            # Group by intelligence_id and aggregate data
            intelligence_map = {}
            for row in rows:
                intel_id = row.intelligence_id
                
                if intel_id not in intelligence_map:
                    intelligence_map[intel_id] = {
                        "intelligence_id": str(intel_id),
                        "product_name": row.product_name,
                        "salespage_url": row.salespage_url,
                        "confidence_score": float(row.confidence_score) if row.confidence_score else 0.0,
                        "analysis_method": row.analysis_method,
                        "features": row.features if row.features else [],
                        "benefits": row.benefits if row.benefits else [],
                        "ingredients": row.ingredients if row.ingredients else [],
                        "conditions": row.conditions if row.conditions else [],
                        "usage_instructions": row.usage_instructions if row.usage_instructions else [],
                        "category": row.category,
                        "positioning": row.positioning,
                        "competitive_advantages": row.competitive_advantages if row.competitive_advantages else [],
                        "target_audience": row.target_audience,
                        "research_content": []
                    }
                
                # Add research content if available
                if row.research_content and row.research_type:
                    intelligence_map[intel_id]["research_content"].append({
                        "content": row.research_content,
                        "research_type": row.research_type
                    })
            
            intelligence_list = list(intelligence_map.values())
            logger.info(f"Retrieved {len(intelligence_list)} intelligence records for campaign")
            
            return intelligence_list
            
        except Exception as e:
            logger.error(f"Failed to get campaign intelligence: {e}")
            return []
    
    async def _get_email_templates_from_database(self) -> List[Dict[str, Any]]:
        """Get email templates from database - NO mock templates"""
        try:
            query = text("""
                SELECT 
                    id,
                    template_text,
                    category,
                    performance_level,
                    avg_open_rate,
                    total_uses,
                    psychology_triggers,
                    keywords,
                    is_active,
                    source
                FROM email_subject_templates 
                WHERE is_active = TRUE
                ORDER BY performance_level DESC, avg_open_rate DESC
                LIMIT 50
            """)
            
            result = await self.db.execute(query)
            rows = result.fetchall()
            
            if not rows:
                logger.warning("No email templates found in database")
                return []
            
            templates = []
            for row in rows:
                template = {
                    "template_id": str(row.id),
                    "template_text": row.template_text,
                    "category": row.category,
                    "performance_level": row.performance_level,
                    "avg_open_rate": float(row.avg_open_rate) if row.avg_open_rate else 0.0,
                    "total_uses": row.total_uses or 0,
                    "psychology_triggers": row.psychology_triggers if row.psychology_triggers else [],
                    "keywords": row.keywords if row.keywords else [],
                    "source": row.source
                }
                templates.append(template)
            
            logger.info(f"Retrieved {len(templates)} email templates from database")
            return templates
            
        except Exception as e:
            logger.error(f"Failed to get email templates: {e}")
            return []
    
    async def _generate_email_from_intelligence(
        self, 
        intelligence_data: List[Dict[str, Any]], 
        template_data: List[Dict[str, Any]], 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate email sequence using real intelligence and template data"""
        
        if not intelligence_data:
            raise ValueError("No intelligence data available for email generation")
        
        if not template_data:
            raise ValueError("No email templates available for generation")
        
        # Extract primary intelligence source
        primary_intel = intelligence_data[0]  # Highest confidence score
        product_name = primary_intel.get("product_name", "").strip()
        
        if not product_name:
            raise ValueError("No product name found in intelligence data")
        
        # Determine series length from preferences or default to 5
        series_length = preferences.get("series_length", 5)
        
        # Generate email sequence using real data
        emails = []
        
        # Strategic sequence based on intelligence data
        strategic_sequence = self._determine_strategic_sequence(intelligence_data, series_length)
        
        for i in range(series_length):
            strategy = strategic_sequence[i]
            
            # Select template based on strategy and performance
            template = self._select_best_template(template_data, strategy["category"])
            
            if not template:
                raise ValueError(f"No template found for category: {strategy['category']}")
            
            # Generate subject using template and intelligence
            subject = self._generate_subject_from_template_and_intelligence(
                template, primary_intel, strategy
            )
            
            # Generate body using intelligence data
            body = self._generate_email_body_from_intelligence(
                primary_intel, strategy, intelligence_data, i + 1
            )
            
            email = {
                "email_number": i + 1,
                "strategic_angle": strategy["angle"],
                "subject": subject,
                "body": body,
                "send_delay": strategy["delay"],
                "template_used": {
                    "template_id": template["template_id"],
                    "template_text": template["template_text"],
                    "performance_level": template["performance_level"],
                    "avg_open_rate": template["avg_open_rate"]
                },
                "intelligence_source": {
                    "intelligence_id": primary_intel["intelligence_id"],
                    "product_name": primary_intel["product_name"],
                    "confidence_score": primary_intel["confidence_score"]
                }
            }
            emails.append(email)
        
        return {
            "content": {"emails": emails},
            "series_info": {
                "total_emails": len(emails),
                "product_name": product_name,
                "primary_intelligence_source": primary_intel["salespage_url"],
                "intelligence_confidence": primary_intel["confidence_score"],
                "templates_used": len(set(email["template_used"]["template_id"] for email in emails))
            },
            "intelligence_integration": {
                "sources_used": len(intelligence_data),
                "features_identified": len(primary_intel.get("features", [])),
                "benefits_identified": len(primary_intel.get("benefits", [])),
                "target_audience": primary_intel.get("target_audience"),
                "category": primary_intel.get("category")
            }
        }
    
    def _determine_strategic_sequence(self, intelligence_data: List[Dict[str, Any]], series_length: int) -> List[Dict[str, str]]:
        """Determine strategic sequence based on intelligence data analysis"""
        
        primary_intel = intelligence_data[0]
        
        # Analyze intelligence to determine strategy
        has_social_proof = len(primary_intel.get("research_content", [])) > 0
        has_benefits = len(primary_intel.get("benefits", [])) > 0
        has_features = len(primary_intel.get("features", [])) > 0
        positioning = primary_intel.get("positioning", "")
        
        # Base sequence
        base_sequence = [
            {"angle": "curiosity_introduction", "category": "curiosity_gap", "delay": "immediate"},
            {"angle": "problem_identification", "category": "problem_awareness", "delay": "2 days"},
            {"angle": "solution_presentation", "category": "solution_focus", "delay": "4 days"},
            {"angle": "benefit_emphasis", "category": "value_proposition", "delay": "7 days"},
            {"angle": "urgency_close", "category": "urgency_scarcity", "delay": "10 days"}
        ]
        
        # Modify based on intelligence data
        if has_social_proof:
            base_sequence.insert(3, {
                "angle": "social_proof", 
                "category": "social_proof", 
                "delay": "5 days"
            })
        
        if "premium" in positioning.lower() or "luxury" in positioning.lower():
            base_sequence[2] = {
                "angle": "authority_positioning", 
                "category": "authority_scientific", 
                "delay": "4 days"
            }
        
        # Return sequence limited to requested length
        return base_sequence[:series_length]
    
    def _select_best_template(self, template_data: List[Dict[str, Any]], category: str) -> Optional[Dict[str, Any]]:
        """Select best performing template for category"""
        
        # Filter templates by category
        category_templates = [t for t in template_data if t["category"] == category]
        
        if not category_templates:
            # Fallback to any high-performing template
            category_templates = [t for t in template_data if t["performance_level"] in ["high_performing", "top_tier"]]
        
        if not category_templates:
            return template_data[0] if template_data else None
        
        # Sort by performance and return best
        category_templates.sort(key=lambda x: (
            x["performance_level"] == "top_tier",
            x["performance_level"] == "high_performing", 
            x["avg_open_rate"]
        ), reverse=True)
        
        return category_templates[0]
    
    def _generate_subject_from_template_and_intelligence(
        self, 
        template: Dict[str, Any], 
        intelligence: Dict[str, Any], 
        strategy: Dict[str, str]
    ) -> str:
        """Generate subject line from template and intelligence data"""
        
        template_text = template["template_text"]
        product_name = intelligence["product_name"]
        
        # Replace product placeholder
        subject = template_text.replace("{product_name}", product_name)
        subject = subject.replace("[product_name]", product_name)
        subject = subject.replace("PRODUCT_NAME", product_name)
        
        # Replace other placeholders with intelligence data
        if "{category}" in subject and intelligence.get("category"):
            subject = subject.replace("{category}", intelligence["category"])
        
        if "{benefit}" in subject and intelligence.get("benefits"):
            benefits = intelligence["benefits"]
            if benefits:
                subject = subject.replace("{benefit}", benefits[0])
        
        return subject
    
    def _generate_email_body_from_intelligence(
        self, 
        primary_intel: Dict[str, Any], 
        strategy: Dict[str, str], 
        all_intelligence: List[Dict[str, Any]], 
        email_number: int
    ) -> str:
        """Generate email body using real intelligence data"""
        
        product_name = primary_intel["product_name"]
        benefits = primary_intel.get("benefits", [])
        features = primary_intel.get("features", [])
        target_audience = primary_intel.get("target_audience", "")
        positioning = primary_intel.get("positioning", "")
        
        if strategy["angle"] == "curiosity_introduction":
            opening = f"I wanted to share something about {product_name} that caught my attention..."
            
            if positioning:
                hook = f"What makes {product_name} different is {positioning.lower()}."
            elif benefits:
                hook = f"The thing about {product_name} is how it delivers {benefits[0].lower()}."
            else:
                hook = f"{product_name} approaches this challenge differently than anything else I've seen."
            
            return f"""Hi [Name],

{opening}

{hook}

{self._build_content_from_features(features[:3])}

I'll share more specific details in my next email.

Talk soon,
[Your Name]"""

        elif strategy["angle"] == "problem_identification":
            problems = self._extract_problems_from_intelligence(all_intelligence)
            
            return f"""Hi [Name],

Yesterday I introduced you to {product_name}, and I want to address something important...

{self._format_problem_section(problems, target_audience)}

{self._build_solution_preview(product_name, benefits)}

Tomorrow, I'll show you exactly how {product_name} addresses these challenges.

Best,
[Your Name]"""

        elif strategy["angle"] == "solution_presentation":
            return f"""Hi [Name],

Here's how {product_name} works...

{self._build_solution_explanation(product_name, features, benefits, positioning)}

{self._build_proof_elements(all_intelligence)}

Best regards,
[Your Name]"""
        
        elif strategy["angle"] == "benefit_emphasis":
            return f"""Hi [Name],

Let me share what {product_name} can do for you:

{self._format_benefits_list(benefits)}

{self._build_target_audience_connection(target_audience)}

Talk soon,
[Your Name]"""
        
        else:  # urgency_close
            return f"""Hi [Name],

I wanted to reach out about {product_name} one more time...

{self._build_urgency_from_intelligence(primary_intel)}

{self._build_final_value_proposition(benefits, features)}

Best,
[Your Name]"""
    
    def _build_content_from_features(self, features: List[str]) -> str:
        """Build content section from feature list"""
        if not features:
            return "Here's what makes this approach unique..."
        
        feature_bullets = "\n".join(f"• {feature}" for feature in features[:3])
        return f"Here's what makes it different:\n\n{feature_bullets}"
    
    def _extract_problems_from_intelligence(self, intelligence_data: List[Dict[str, Any]]) -> List[str]:
        """Extract problems from intelligence research content"""
        problems = []
        
        for intel in intelligence_data:
            research_content = intel.get("research_content", [])
            for research in research_content:
                if research.get("research_type") == "market" and "problem" in research.get("content", "").lower():
                    # Extract problem-related content
                    content = research["content"]
                    if len(content) > 100:  # Ensure substantial content
                        problems.append(content[:200] + "...")
        
        return problems[:2]  # Limit to top 2 problems
    
    def _format_problem_section(self, problems: List[str], target_audience: str) -> str:
        """Format problem section using extracted problems"""
        if not problems:
            return "Most people struggle with this challenge because they lack the right approach."
        
        audience_text = f"for {target_audience}" if target_audience else "for people like you"
        
        return f"The biggest challenge {audience_text} is:\n\n{problems[0]}"
    
    def _build_solution_explanation(self, product_name: str, features: List[str], benefits: List[str], positioning: str) -> str:
        """Build solution explanation from intelligence data"""
        
        explanation = f"{product_name} addresses this through"
        
        if positioning:
            explanation += f" its {positioning.lower()} approach."
        else:
            explanation += " a systematic method."
        
        if features:
            feature_text = "\n".join(f"→ {feature}" for feature in features[:3])
            explanation += f"\n\nKey components:\n{feature_text}"
        
        if benefits:
            benefit_text = "\n".join(f"✓ {benefit}" for benefit in benefits[:3])
            explanation += f"\n\nWhat this means for you:\n{benefit_text}"
        
        return explanation
    
    def _format_benefits_list(self, benefits: List[str]) -> str:
        """Format benefits list from intelligence data"""
        if not benefits:
            return "• Improved results\n• Better outcomes\n• Enhanced performance"
        
        return "\n".join(f"• {benefit}" for benefit in benefits[:4])
    
    def _build_target_audience_connection(self, target_audience: str) -> str:
        """Build target audience connection from intelligence"""
        if not target_audience:
            return "This is designed for people who want real results."
        
        return f"This is specifically designed for {target_audience.lower()}."
    
    def _build_urgency_from_intelligence(self, intelligence: Dict[str, Any]) -> str:
        """Build urgency messaging from intelligence data"""
        positioning = intelligence.get("positioning", "")
        category = intelligence.get("category", "")
        
        if "limited" in positioning.lower() or "exclusive" in positioning.lower():
            return "Due to the exclusive nature of this solution, availability is limited."
        elif "premium" in positioning.lower():
            return "This premium solution isn't for everyone, and spots are filling up."
        else:
            return "I wanted to make sure you didn't miss this opportunity."
    
    def _build_final_value_proposition(self, benefits: List[str], features: List[str]) -> str:
        """Build final value proposition from intelligence"""
        if benefits:
            return f"Remember, with this you get: {', '.join(benefits[:2])}."
        elif features:
            return f"You'll have access to: {', '.join(features[:2])}."
        else:
            return "This represents a unique opportunity for transformation."
    
    def _build_proof_elements(self, intelligence_data: List[Dict[str, Any]]) -> str:
        """Build proof elements from research content"""
        research_items = []
        
        for intel in intelligence_data:
            research_content = intel.get("research_content", [])
            for research in research_content:
                if research.get("research_type") == "scientific":
                    research_items.append("Backed by research")
                elif research.get("research_type") == "market":
                    research_items.append("Market-validated approach")
        
        if research_items:
            return f"This is {', '.join(research_items[:2])}."
        else:
            return "The results speak for themselves."
    
    async def _generate_social_from_intelligence(self, intelligence_data: List[Dict[str, Any]], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate social media content using real intelligence data"""
        
        if not intelligence_data:
            raise ValueError("No intelligence data available for social media generation")
        
        primary_intel = intelligence_data[0]
        product_name = primary_intel.get("product_name", "").strip()
        
        if not product_name:
            raise ValueError("No product name found in intelligence data")
        
        platform = preferences.get("platform", "general")
        benefits = primary_intel.get("benefits", [])
        features = primary_intel.get("features", [])
        target_audience = primary_intel.get("target_audience", "")
        positioning = primary_intel.get("positioning", "")
        
        # Generate platform-specific content using real data
        if platform.lower() == "linkedin":
            post_text = self._create_linkedin_post_from_intelligence(product_name, benefits, features, positioning, target_audience)
        elif platform.lower() == "facebook":
            post_text = self._create_facebook_post_from_intelligence(product_name, benefits, features, positioning)
        elif platform.lower() == "twitter":
            post_text = self._create_twitter_post_from_intelligence(product_name, benefits, features)
        else:
            post_text = self._create_general_post_from_intelligence(product_name, benefits, features)
        
        # Generate hashtags from intelligence data
        hashtags = self._generate_hashtags_from_intelligence(primary_intel, platform)
        
        return {
            "content": {
                "posts": [{
                    "platform": platform,
                    "text": post_text,
                    "hashtags": hashtags,
                    "character_count": len(post_text),
                    "intelligence_source": {
                        "intelligence_id": primary_intel["intelligence_id"],
                        "product_name": product_name,
                        "confidence_score": primary_intel["confidence_score"]
                    }
                }]
            },
            "intelligence_integration": {
                "benefits_used": len(benefits),
                "features_used": len(features),
                "target_audience": target_audience,
                "positioning": positioning
            }
        }
    
    def _create_linkedin_post_from_intelligence(self, product_name: str, benefits: List[str], features: List[str], positioning: str, target_audience: str) -> str:
        """Create LinkedIn post using intelligence data"""
        
        opening = f"Just discovered something interesting about {product_name}..."
        
        if positioning:
            hook = f"What caught my attention: {positioning}"
        elif benefits:
            hook = f"The key insight: {benefits[0]}"
        else:
            hook = f"{product_name} takes a different approach to this challenge"
        
        value_points = []
        if benefits:
            value_points.extend(f"→ {benefit}" for benefit in benefits[:3])
        if features and len(value_points) < 3:
            value_points.extend(f"→ {feature}" for feature in features[:3-len(value_points)])
        
        if not value_points:
            value_points = ["→ Innovative approach", "→ Proven methodology", "→ Real results"]
        
        audience_line = f"Especially relevant for {target_audience.lower()}." if target_audience else "Worth considering for anyone in this space."
        
        return f"""{opening}

{hook}

{chr(10).join(value_points)}

{audience_line}

What's your experience with similar solutions?"""
    
    def _create_facebook_post_from_intelligence(self, product_name: str, benefits: List[str], features: List[str], positioning: str) -> str:
        """Create Facebook post using intelligence data"""
        
        if benefits:
            main_benefit = benefits[0]
            return f"""Excited to share my discovery of {product_name}!

The biggest game-changer? {main_benefit}

{f"Plus: {', '.join(benefits[1:3])}" if len(benefits) > 1 else ""}

{f"What makes it unique: {positioning}" if positioning else ""}

Has anyone else tried this approach? Would love to hear your thoughts!"""
        else:
            return f"""Just learned about {product_name} and had to share...

{f"Their approach: {positioning}" if positioning else f"Interesting take on solving this challenge"}

{f"Key features: {', '.join(features[:3])}" if features else "Worth checking out if you're interested in this space"}

Thoughts?"""
    
    def _create_twitter_post_from_intelligence(self, product_name: str, benefits: List[str], features: List[str]) -> str:
        """Create Twitter post using intelligence data"""
        
        if benefits:
            return f"""{product_name} just changed how I think about {benefits[0].lower()}

→ {benefits[1] if len(benefits) > 1 else "Proven approach"}
→ {benefits[2] if len(benefits) > 2 else "Real results"}

Worth exploring."""
        else:
            return f"""Interesting approach from {product_name}

{f"Key insight: {features[0]}" if features else "Different take on this challenge"}

Thoughts?"""
    
    def _create_general_post_from_intelligence(self, product_name: str, benefits: List[str], features: List[str]) -> str:
        """Create general social post using intelligence data"""
        
        if benefits:
            benefit_text = f"delivers {benefits[0].lower()}"
            additional = f" Plus {', '.join(benefits[1:3]).lower()}." if len(benefits) > 1 else ""
        elif features:
            benefit_text = f"offers {features[0].lower()}"
            additional = f" Including {', '.join(features[1:3]).lower()}." if len(features) > 1 else ""
        else:
            benefit_text = "takes a unique approach"
            additional = ""
        
        return f"""Discovered {product_name} - {benefit_text}.{additional}

Worth checking out if you're looking for real solutions."""
    
    def _generate_hashtags_from_intelligence(self, intelligence: Dict[str, Any], platform: str) -> List[str]:
        """Generate hashtags from intelligence data"""
        
        hashtags = []
        
        # Add category-based hashtags
        category = intelligence.get("category", "")
        if category:
            hashtags.append(f"#{category.replace(' ', '').replace('-', '')}")
        
        # Add positioning-based hashtags
        positioning = intelligence.get("positioning", "")
        if "innovative" in positioning.lower():
            hashtags.append("#Innovation")
        if "premium" in positioning.lower():
            hashtags.append("#Premium")
        if "solution" in positioning.lower():
            hashtags.append("#Solutions")
        
        # Add platform-specific hashtags
        if platform.lower() == "linkedin":
            hashtags.extend(["#BusinessSolutions", "#Productivity", "#Innovation"])
        elif platform.lower() == "twitter":
            hashtags.extend(["#TechNews", "#Innovation", "#NewProduct"])
        else:
            hashtags.extend(["#Innovation", "#Solutions", "#GameChanger"])
        
        # Ensure we have hashtags even if intelligence is limited
        if not hashtags:
            hashtags = ["#Innovation", "#Solutions", "#NewApproach"]
        
        return hashtags[:5]  # Limit to 5 hashtags
    
    async def _store_content_with_intelligence_tracking(
        self,
        campaign_id: Union[str, UUID],
        user_id: Union[str, UUID],
        company_id: Union[str, UUID],
        content_type: str,
        content_data: Dict[str, Any],
        intelligence_used: List[Dict[str, Any]],
        generation_settings: Dict[str, Any]
    ) -> UUID:
        """Store content with intelligence tracking - database driven only"""
        
        content_id = uuid4()
        
        # Extract content for storage
        if content_type in ["email", "email_sequence"]:
            content_title = f"Email Sequence - {content_data.get('series_info', {}).get('product_name', 'Unknown Product')}"
            content_body = json.dumps(content_data.get('content', {}).get('emails', []))
        elif content_type == "social_post":
            posts = content_data.get('content', {}).get('posts', [])
            platform = posts[0].get('platform', 'general') if posts else 'general'
            content_title = f"Social Media Post - {platform.title()}"
            content_body = json.dumps(posts)
        elif content_type == "blog_article":
            article = content_data.get('content', {}).get('article', {})
            content_title = article.get('title', 'Blog Article')
            content_body = json.dumps(article)
        else:
            content_title = f"{content_type.title()} Content"
            content_body = json.dumps(content_data.get('content', {}))
        
        # Create metadata tracking intelligence usage
        content_metadata = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "intelligence_sources_used": len(intelligence_used),
            "primary_intelligence_id": intelligence_used[0]["intelligence_id"] if intelligence_used else None,
            "intelligence_confidence_scores": [intel["confidence_score"] for intel in intelligence_used],
            "product_name": intelligence_used[0].get("product_name") if intelligence_used else None,
            "intelligence_integration": content_data.get("intelligence_integration", {}),
            "workflow_step": "1_text_generation_database_driven",
            "generation_method": "database_intelligence_only"
        }
        
        # Store in existing generated_content table
        query = text("""
            INSERT INTO generated_content 
            (id, user_id, campaign_id, company_id, content_type, content_title, content_body,
             content_metadata, generation_settings, generation_method, content_status, intelligence_id)
            VALUES (:id, :user_id, :campaign_id, :company_id, :content_type, :content_title, 
                    :content_body, :content_metadata, :generation_settings, 'database_intelligence', 'generated', :intelligence_id)
        """)
        
        await self.db.execute(query, {
            "id": content_id,
            "user_id": UUID(str(user_id)),
            "campaign_id": UUID(str(campaign_id)),
            "company_id": UUID(str(company_id)),
            "content_type": content_type,
            "content_title": content_title,
            "content_body": content_body,
            "content_metadata": json.dumps(content_metadata),
            "generation_settings": json.dumps(generation_settings),
            "intelligence_id": intelligence_used[0]["intelligence_id"] if intelligence_used else None
        })
        
        await self.db.commit()
        return content_id
    
    async def _generate_blog_from_intelligence(self, intelligence_data: List[Dict[str, Any]], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate blog article using real intelligence data"""
        
        if not intelligence_data:
            raise ValueError("No intelligence data available for blog generation")
        
        primary_intel = intelligence_data[0]
        product_name = primary_intel.get("product_name", "").strip()
        
        if not product_name:
            raise ValueError("No product name found in intelligence data")
        
        article_type = preferences.get("article_type", "how_to")
        
        # Generate article using intelligence data
        if article_type == "how_to":
            article = self._create_how_to_article_from_intelligence(primary_intel, intelligence_data)
        elif article_type == "review":
            article = self._create_review_article_from_intelligence(primary_intel, intelligence_data)
        elif article_type == "comparison":
            article = self._create_comparison_article_from_intelligence(primary_intel, intelligence_data)
        else:
            article = self._create_general_article_from_intelligence(primary_intel, intelligence_data)
        
        return {
            "content": {"article": article},
            "intelligence_integration": {
                "sources_used": len(intelligence_data),
                "features_referenced": len(primary_intel.get("features", [])),
                "benefits_highlighted": len(primary_intel.get("benefits", [])),
                "research_content_used": sum(len(intel.get("research_content", [])) for intel in intelligence_data)
            }
        }
    
    def _create_how_to_article_from_intelligence(self, primary_intel: Dict[str, Any], all_intelligence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create how-to article from intelligence data"""
        
        product_name = primary_intel["product_name"]
        features = primary_intel.get("features", [])
        benefits = primary_intel.get("benefits", [])
        usage_instructions = primary_intel.get("usage_instructions", [])
        positioning = primary_intel.get("positioning", "")
        
        # Build title from intelligence
        if benefits:
            main_benefit = benefits[0]
            title = f"How to {main_benefit} with {product_name}: Complete Guide"
        else:
            title = f"How to Use {product_name}: Step-by-Step Guide"
        
        # Generate meta description from intelligence
        meta_description = f"Learn how to maximize your results with {product_name}. "
        if positioning:
            meta_description += f"Discover the {positioning.lower()} approach to achieving your goals."
        else:
            meta_description += "Complete guide with proven strategies and tips."
        
        # Build introduction from intelligence
        introduction = f"Getting the most out of {product_name} requires understanding its unique approach. "
        if positioning:
            introduction += f"As a {positioning.lower()} solution, it offers distinct advantages. "
        introduction += "This guide will show you exactly how to implement it effectively."
        
        # Build sections from intelligence data
        sections = []
        
        # Understanding section
        understanding_content = f"{product_name} works through "
        if features:
            understanding_content += f"its {len(features)} core components: {', '.join(features[:3])}."
        else:
            understanding_content += "a systematic approach to addressing your specific needs."
        
        sections.append({
            "heading": f"Understanding {product_name}",
            "content": understanding_content,
            "subsections": self._build_feature_subsections(features)
        })
        
        # Implementation section
        if usage_instructions:
            implementation_content = "Follow these steps for optimal results:\n\n"
            for i, instruction in enumerate(usage_instructions[:5], 1):
                implementation_content += f"{i}. {instruction}\n"
        else:
            implementation_content = f"To implement {product_name} effectively:\n\n"
            implementation_content += "1. Start with proper setup and configuration\n"
            implementation_content += "2. Follow the recommended approach\n"
            implementation_content += "3. Monitor your progress and adjust as needed"
        
        sections.append({
            "heading": "Step-by-Step Implementation",
            "content": implementation_content
        })
        
        # Benefits section
        if benefits:
            benefits_content = f"When you use {product_name} correctly, you can expect:\n\n"
            for benefit in benefits:
                benefits_content += f"• {benefit}\n"
        else:
            benefits_content = f"{product_name} is designed to deliver measurable improvements in your results."
        
        sections.append({
            "heading": "Expected Benefits",
            "content": benefits_content
        })
        
        # Advanced tips from research content
        advanced_tips = self._extract_advanced_tips_from_research(all_intelligence)
        if advanced_tips:
            sections.append({
                "heading": "Advanced Strategies",
                "content": advanced_tips
            })
        
        return {
            "title": title,
            "meta_description": meta_description,
            "introduction": introduction,
            "sections": sections,
            "conclusion": f"By following this guide, you'll be able to maximize the benefits of {product_name} and achieve your desired results.",
            "intelligence_source": {
                "intelligence_id": primary_intel["intelligence_id"],
                "confidence_score": primary_intel["confidence_score"],
                "salespage_url": primary_intel.get("salespage_url")
            }
        }
    
    def _build_feature_subsections(self, features: List[str]) -> List[Dict[str, str]]:
        """Build feature subsections from intelligence data"""
        subsections = []
        
        for feature in features[:5]:  # Limit to 5 features
            subsections.append({
                "subheading": feature,
                "content": f"This component focuses on {feature.lower()} to enhance your overall results."
            })
        
        return subsections
    
    def _extract_advanced_tips_from_research(self, intelligence_data: List[Dict[str, Any]]) -> str:
        """Extract advanced tips from research content"""
        tips = []
        
        for intel in intelligence_data:
            research_content = intel.get("research_content", [])
            for research in research_content:
                content = research.get("content", "")
                if len(content) > 50 and ("advanced" in content.lower() or "optimize" in content.lower()):
                    # Extract relevant portion
                    sentences = content.split('. ')
                    relevant_sentences = [s for s in sentences if any(word in s.lower() for word in ["tip", "strategy", "method", "approach"])]
                    if relevant_sentences:
                        tips.extend(relevant_sentences[:2])
        
        if tips:
            return "Advanced strategies based on research:\n\n" + "\n".join(f"• {tip.strip()}" for tip in tips[:4])
        else:
            return ""
    
    async def _generate_ad_copy_from_intelligence(self, intelligence_data: List[Dict[str, Any]], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ad copy using real intelligence data"""
        
        if not intelligence_data:
            raise ValueError("No intelligence data available for ad copy generation")
        
        primary_intel = intelligence_data[0]
        product_name = primary_intel.get("product_name", "").strip()
        
        if not product_name:
            raise ValueError("No product name found in intelligence data")
        
        ad_platform = preferences.get("platform", "facebook")
        benefits = primary_intel.get("benefits", [])
        features = primary_intel.get("features", [])
        target_audience = primary_intel.get("target_audience", "")
        positioning = primary_intel.get("positioning", "")
        
        # Generate headlines from intelligence
        headlines = self._generate_headlines_from_intelligence(product_name, benefits, features, positioning)
        
        # Generate descriptions from intelligence
        descriptions = self._generate_descriptions_from_intelligence(product_name, benefits, target_audience, positioning)
        
        # Create ad variations
        ads = []
        for i, (headline, description) in enumerate(zip(headlines, descriptions), 1):
            ad = {
                "ad_number": i,
                "platform": ad_platform,
                "headline": headline,
                "description": description,
                "call_to_action": self._generate_cta_from_intelligence(positioning),
                "intelligence_source": {
                    "intelligence_id": primary_intel["intelligence_id"],
                    "confidence_score": primary_intel["confidence_score"]
                }
            }
            ads.append(ad)
        
        return {
            "content": {"ads": ads},
            "intelligence_integration": {
                "benefits_used": len(benefits),
                "features_used": len(features),
                "target_audience": target_audience,
                "positioning_applied": bool(positioning)
            }
        }
    
    def _generate_headlines_from_intelligence(self, product_name: str, benefits: List[str], features: List[str], positioning: str) -> List[str]:
        """Generate ad headlines from intelligence data"""
        headlines = []
        
        # Benefit-focused headlines
        if benefits:
            for benefit in benefits[:2]:
                headlines.append(f"Finally: {benefit} with {product_name}")
                headlines.append(f"Discover How {product_name} Delivers {benefit}")
        
        # Feature-focused headlines
        if features and len(headlines) < 4:
            for feature in features[:2]:
                headlines.append(f"{product_name}: Now with {feature}")
        
        # Positioning-focused headlines
        if positioning:
            headlines.append(f"The {positioning} Solution: {product_name}")
            headlines.append(f"Why {product_name} is the {positioning} Choice")
        
        # Ensure we have headlines even with limited intelligence
        if not headlines:
            headlines = [
                f"Introducing {product_name}",
                f"Discover {product_name} Today",
                f"The {product_name} Advantage"
            ]
        
        return headlines[:4]  # Return top 4 headlines
    
    def _generate_descriptions_from_intelligence(self, product_name: str, benefits: List[str], target_audience: str, positioning: str) -> List[str]:
        """Generate ad descriptions from intelligence data"""
        descriptions = []
        
        # Benefit-driven descriptions
        if benefits:
            benefit_list = ", ".join(benefits[:3])
            desc = f"Experience {benefit_list} with {product_name}. "
            if target_audience:
                desc += f"Designed specifically for {target_audience.lower()}. "
            desc += "See the difference for yourself."
            descriptions.append(desc)
        
        # Positioning-driven description
        if positioning:
            desc = f"{product_name} offers a {positioning.lower()} approach to achieving your goals. "
            if benefits:
                desc += f"Get {benefits[0].lower()} and more. "
            desc += "Join thousands who have already made the switch."
            descriptions.append(desc)
        
        # Problem-solution description
        if target_audience and benefits:
            desc = f"If you're {target_audience.lower()} looking for {benefits[0].lower()}, "
            desc += f"{product_name} is your answer. Proven results, trusted by thousands."
            descriptions.append(desc)
        
        # Ensure we have descriptions
        if not descriptions:
            descriptions = [
                f"{product_name} - the solution you've been looking for.",
                f"Discover what makes {product_name} different.",
                f"Join the {product_name} community today."
            ]
        
        return descriptions[:4]  # Return top 4 descriptions
    
    def _generate_cta_from_intelligence(self, positioning: str) -> str:
        """Generate call-to-action from intelligence positioning"""
        
        if "premium" in positioning.lower():
            return "Get Premium Access"
        elif "innovative" in positioning.lower():
            return "Try Innovation"
        elif "proven" in positioning.lower():
            return "Get Proven Results"
        else:
            return "Learn More"


# ============================================================================
# VALIDATION SERVICE FOR DATABASE REQUIREMENTS
# ============================================================================

class ContentValidationService:
    """Validates database requirements before content generation"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def validate_campaign_readiness(self, campaign_id: Union[str, UUID]) -> Dict[str, Any]:
        """Validate that campaign has sufficient intelligence data for content generation"""
        
        # Check for intelligence data
        intelligence_count = await self._count_campaign_intelligence(campaign_id)
        
        # Check for email templates if needed
        template_count = await self._count_email_templates()
        
        # Generate readiness report
        readiness = {
            "campaign_id": str(campaign_id),
            "intelligence_available": intelligence_count > 0,
            "intelligence_count": intelligence_count,
            "email_templates_available": template_count > 0,
            "email_template_count": template_count,
            "ready_for_generation": intelligence_count > 0,
            "recommendations": []
        }
        
        if intelligence_count == 0:
            readiness["recommendations"].append("Run campaign analysis to generate intelligence data")
        
        if template_count == 0:
            readiness["recommendations"].append("Add email templates to email_subject_templates table")
        
        if intelligence_count > 0 and template_count > 0:
            readiness["recommendations"].append("Ready for content generation")
        
        return readiness
    
    async def _count_campaign_intelligence(self, campaign_id: Union[str, UUID]) -> int:
        """Count intelligence records for campaign"""
        query = text("""
            SELECT COUNT(DISTINCT ic.id)
            FROM intelligence_core ic
            WHERE ic.user_id IN (
                SELECT user_id FROM campaigns WHERE id = :campaign_id
            )
        """)
        
        result = await self.db.execute(query, {"campaign_id": UUID(str(campaign_id))})
        return result.scalar() or 0
    
    async def _count_email_templates(self) -> int:
        """Count available email templates"""
        query = text("""
            SELECT COUNT(*) FROM email_subject_templates 
            WHERE is_active = TRUE
        """)
        
        result = await self.db.execute(query)
        return result.scalar() or 0