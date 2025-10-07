# src/content/models/content_generation.py
"""
Database models for content generation tracking and storage
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class GenerationStatus(enum.Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ContentType(enum.Enum):
    EMAIL_SEQUENCE = "email_sequence"
    EMAIL_NEWSLETTER = "email_newsletter"
    SOCIAL_POSTS = "social_posts"
    INSTAGRAM_CAPTIONS = "instagram_captions"
    LINKEDIN_POSTS = "linkedin_posts"
    TWITTER_THREADS = "twitter_threads"
    AD_COPY = "ad_copy"
    GOOGLE_ADS = "google_ads"
    FACEBOOK_ADS = "facebook_ads"
    BLOG_ARTICLES = "blog_articles"
    SALES_PAGES = "sales_pages"
    PRODUCT_DESCRIPTIONS = "product_descriptions"
    VIDEO_SCRIPTS = "video_scripts"
    YOUTUBE_SCRIPTS = "youtube_scripts"
    TIKTOK_SCRIPTS = "tiktok_scripts"
    IMAGE_CONCEPTS = "image_concepts"
    THUMBNAIL_IDEAS = "thumbnail_ideas"
    INFOGRAPHIC_CONCEPTS = "infographic_concepts"
    MARKET_ANALYSIS_REPORT = "market_analysis_report"
    COMPETITOR_INTELLIGENCE = "competitor_intelligence"
    STRATEGY_DOCUMENT = "strategy_document"
    BRAND_GUIDELINES = "brand_guidelines"
    CONVERSION_OPTIMIZATION = "conversion_optimization"

class ContentGenerationJob(Base):
    """
    Tracks content generation jobs in the queue
    """
    __tablename__ = "content_generation_jobs"
    
    # Primary identifiers
    job_id = Column(String(255), primary_key=True)
    campaign_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Job details
    content_type = Column(SQLEnum(ContentType), nullable=False)
    generator_class = Column(String(255), nullable=False)
    priority = Column(Integer, default=5)  # 1 = highest, 10 = lowest
    
    # Configuration and data
    generation_config = Column(JSON)  # Generator-specific configuration
    intelligence_data = Column(JSON)  # Intelligence analysis results
    user_modifications = Column(JSON)  # User-requested modifications
    
    # Status tracking
    status = Column(SQLEnum(GenerationStatus), default=GenerationStatus.QUEUED)
    progress_percentage = Column(Integer, default=0)
    error_message = Column(Text)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_completion_at = Column(DateTime)
    
    # Resource tracking
    estimated_tokens = Column(Integer, default=0)
    actual_tokens_used = Column(Integer, default=0)
    
    # Relationship to generated content
    generated_content = relationship("GeneratedContent", back_populates="generation_job")
    
    def to_dict(self):
        return {
            "job_id": self.job_id,
            "campaign_id": self.campaign_id,
            "user_id": self.user_id,
            "content_type": self.content_type.value if self.content_type else None,
            "status": self.status.value if self.status else None,
            "progress_percentage": self.progress_percentage,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "estimated_completion_at": self.estimated_completion_at.isoformat() if self.estimated_completion_at else None,
            "estimated_tokens": self.estimated_tokens,
            "actual_tokens_used": self.actual_tokens_used
        }

class GeneratedContent(Base):
    """
    Stores the actual generated content results
    """
    __tablename__ = "generated_content"
    
    # Primary identifiers
    content_id = Column(String(255), primary_key=True)
    job_id = Column(String(255), ForeignKey("content_generation_jobs.job_id"), nullable=False)
    campaign_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Content details
    content_type = Column(SQLEnum(ContentType), nullable=False)
    title = Column(String(500))
    content_data = Column(JSON, nullable=False)  # The actual generated content
    
    # Quality metrics
    performance_score = Column(Integer)  # AI-calculated quality score (1-100)
    readability_score = Column(Integer)
    engagement_prediction = Column(Integer)
    
    # Metadata
    word_count = Column(Integer)
    character_count = Column(Integer)
    tokens_used = Column(Integer)
    generation_model = Column(String(100))  # Which AI model was used
    generation_version = Column(String(50))  # Version of generation system
    
    # User interaction
    user_rating = Column(Integer)  # User's rating (1-5 stars)
    user_feedback = Column(Text)
    is_approved = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime)
    
    # Recommendations and improvements
    ai_recommendations = Column(JSON)  # AI suggestions for improvement
    a_b_variations = Column(JSON)  # Alternative versions for A/B testing
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    generation_job = relationship("ContentGenerationJob", back_populates="generated_content")
    
    def to_dict(self):
        return {
            "content_id": self.content_id,
            "job_id": self.job_id,
            "campaign_id": self.campaign_id,
            "content_type": self.content_type.value if self.content_type else None,
            "title": self.title,
            "content_data": self.content_data,
            "performance_score": self.performance_score,
            "word_count": self.word_count,
            "tokens_used": self.tokens_used,
            "user_rating": self.user_rating,
            "is_approved": self.is_approved,
            "is_published": self.is_published,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "ai_recommendations": self.ai_recommendations
        }

class UserContentUsage(Base):
    """
    Tracks user's content generation usage for billing and limits
    """
    __tablename__ = "user_content_usage"
    
    # Composite primary key
    user_id = Column(String(255), primary_key=True)
    month_year = Column(String(7), primary_key=True)  # Format: "2024-01"
    
    # Usage counters
    total_tokens_used = Column(Integer, default=0)
    total_jobs_created = Column(Integer, default=0)
    total_content_pieces = Column(Integer, default=0)
    regenerations_used = Column(Integer, default=0)
    
    # Content type breakdown
    email_content_count = Column(Integer, default=0)
    social_content_count = Column(Integer, default=0)
    ad_content_count = Column(Integer, default=0)
    premium_content_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "month_year": self.month_year,
            "total_tokens_used": self.total_tokens_used,
            "total_jobs_created": self.total_jobs_created,
            "total_content_pieces": self.total_content_pieces,
            "regenerations_used": self.regenerations_used,
            "email_content_count": self.email_content_count,
            "social_content_count": self.social_content_count,
            "ad_content_count": self.ad_content_count,
            "premium_content_count": self.premium_content_count
        }

class GeneratedPrompt(Base):
    """
    Stores AI-generated prompts for reuse and analytics
    Links prompts to campaigns and content types for easy retrieval
    """
    __tablename__ = "generated_prompts"

    # Primary identifiers
    prompt_id = Column(String(255), primary_key=True)
    campaign_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    content_id = Column(String(255), ForeignKey("generated_content.content_id"), nullable=True)

    # Prompt details
    content_type = Column(SQLEnum(ContentType), nullable=False, index=True)
    psychology_stage = Column(String(50))  # e.g., "solution_reveal", "problem_agitation"

    # The prompts
    user_prompt = Column(Text, nullable=False)  # The actual prompt sent to AI
    system_message = Column(Text)  # System message for context

    # Intelligence variables used
    intelligence_variables = Column(JSON)  # Variables extracted from intelligence
    prompt_template_id = Column(String(100))  # Which template was used

    # Quality metrics
    quality_score = Column(Integer)  # Prompt quality score (0-100)
    variable_count = Column(Integer)  # Number of variables utilized
    prompt_length = Column(Integer)  # Character length

    # AI generation metadata
    ai_provider = Column(String(50))  # e.g., "deepseek", "gpt4o_mini", "claude"
    ai_model = Column(String(100))  # Specific model used
    tokens_used = Column(Integer)  # Total tokens (prompt + completion)
    generation_cost = Column(String(20))  # Cost in dollars (stored as string for precision)
    generation_time = Column(String(20))  # Time taken in seconds

    # Performance tracking
    content_quality_score = Column(Integer)  # Quality of content generated from this prompt
    user_satisfaction = Column(Integer)  # User rating of the generated content (1-5)
    was_regenerated = Column(Boolean, default=False)  # Whether user requested regeneration

    # Reuse tracking
    reuse_count = Column(Integer, default=0)  # Times this prompt was reused
    is_favorite = Column(Boolean, default=False)  # User marked as favorite

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_used_at = Column(DateTime)

    def to_dict(self):
        return {
            "prompt_id": self.prompt_id,
            "campaign_id": self.campaign_id,
            "content_id": self.content_id,
            "content_type": self.content_type.value if self.content_type else None,
            "psychology_stage": self.psychology_stage,
            "user_prompt": self.user_prompt,
            "system_message": self.system_message,
            "intelligence_variables": self.intelligence_variables,
            "quality_score": self.quality_score,
            "variable_count": self.variable_count,
            "ai_provider": self.ai_provider,
            "ai_model": self.ai_model,
            "tokens_used": self.tokens_used,
            "generation_cost": self.generation_cost,
            "generation_time": self.generation_time,
            "content_quality_score": self.content_quality_score,
            "user_satisfaction": self.user_satisfaction,
            "reuse_count": self.reuse_count,
            "is_favorite": self.is_favorite,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None
        }

class ContentTemplate(Base):
    """
    Stores reusable content templates and user favorites
    """
    __tablename__ = "content_templates"

    template_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)

    # Template details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    template_data = Column(JSON, nullable=False)

    # Usage tracking
    usage_count = Column(Integer, default=0)
    success_rate = Column(Integer)  # Percentage of successful uses

    # Sharing
    is_public = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "template_id": self.template_id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "content_type": self.content_type.value if self.content_type else None,
            "template_data": self.template_data,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }