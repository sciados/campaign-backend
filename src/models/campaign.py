# src/models/campaign.py - FIXED to remove circular import
"""
Campaign models - Updated enum values to match database - FIXED CIRCULAR IMPORT
"""
from sqlalchemy import Column, String, Text, Enum, ForeignKey, Integer, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from uuid import uuid4

# EMERGENCY FIX: Create BaseModel locally to avoid circular import
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseModel(Base):
    """Emergency base model to avoid circular imports"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# ✅ FIXED: Match the actual database enum values
class CampaignStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS" 
    REVIEW = "REVIEW"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"

class WorkflowPreference(str, enum.Enum):
    QUICK = "QUICK"           # User wants to rush through steps
    METHODICAL = "METHODICAL" # User wants to take time at each step
    FLEXIBLE = "FLEXIBLE"     # User switches between modes

class CampaignWorkflowState(str, enum.Enum):
    # User can be at any of these states and move freely between them
    BASIC_SETUP = "BASIC_SETUP"              # Step 1: Campaign created
    COLLECTING_SOURCES = "COLLECTING_SOURCES" # Step 2: Adding sources (can be ongoing)
    SOURCES_READY = "SOURCES_READY"          # Step 2: Has sources, ready for analysis
    ANALYZING_SOURCES = "ANALYZING_SOURCES"   # Step 3: AI processing (can be ongoing)
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"   # Step 3: Intelligence extracted
    GENERATING_CONTENT = "GENERATING_CONTENT" # Step 4: Creating content (can be ongoing)
    CONTENT_AVAILABLE = "CONTENT_AVAILABLE"   # Step 4: Has generated content
    CAMPAIGN_COMPLETE = "CAMPAIGN_COMPLETE"   # All steps done, can still add more

class Campaign(BaseModel):
    """Simplified Campaign model - All campaigns are universal"""
    __tablename__ = "campaigns"
    
    # Basic Campaign Information
    title = Column(String(500), nullable=False)
    description = Column(Text)
    keywords = Column(JSONB, default=[])  # List of keywords
    target_audience = Column(JSONB, default={})
    
    # ✅ FIXED: Use enum values that match database
    status = Column(Enum(CampaignStatus, name='campaignstatus'), default=CampaignStatus.DRAFT)
    
    tone = Column(String(100), default="conversational")  # conversational, professional, casual, etc.
    style = Column(String(100), default="modern")  # modern, classic, bold, etc.
    
    # Campaign Settings and Configuration
    settings = Column(JSONB, default={})  # Flexible settings storage
    
    # Flexible workflow tracking
    workflow_state = Column(Enum(CampaignWorkflowState, name='campaignworkflowstate'), default=CampaignWorkflowState.BASIC_SETUP)
    workflow_preference = Column(Enum(WorkflowPreference, name='workflowpreference'), default=WorkflowPreference.FLEXIBLE)
    
    # Allow users to work on multiple steps simultaneously
    active_steps = Column(JSONB, default=[1])  # Which steps user is currently working on
    completed_steps = Column(JSONB, default=[])  # Which steps are fully complete
    available_steps = Column(JSONB, default=[1, 2])  # Which steps user can access
    
    # Flexible progress tracking
    step_states = Column(JSONB, default={
        "step_1": {"status": "active", "progress": 100, "can_skip": False},
        "step_2": {"status": "available", "progress": 0, "can_skip": False}, 
        "step_3": {"status": "locked", "progress": 0, "can_skip": True},
        "step_4": {"status": "locked", "progress": 0, "can_skip": True}
    })
    
    # User session management
    current_session = Column(JSONB, default={})  # What user is working on right now
    session_history = Column(JSONB, default=[])  # Track user's work patterns
    
    # Quick vs Methodical mode settings
    quick_mode_enabled = Column(Boolean, default=False)
    auto_advance_steps = Column(Boolean, default=False)
    skip_confirmations = Column(Boolean, default=False)
    
    # Methodical mode settings  
    show_detailed_guidance = Column(Boolean, default=True)
    require_step_completion = Column(Boolean, default=False)
    save_frequently = Column(Boolean, default=True)
    
    # Progress tracking
    sources_count = Column(Integer, default=0)
    sources_processed = Column(Integer, default=0)
    intelligence_extracted = Column(Integer, default=0)
    content_generated = Column(Integer, default=0)
    
    # Step-specific data
    step_2_data = Column(JSONB, default={})  # Source upload preferences, etc.
    step_3_data = Column(JSONB, default={})  # Analysis results, extracted insights
    step_4_data = Column(JSONB, default={})  # Content generation preferences
    
    # Progress percentages for UI
    step_2_progress = Column(JSONB, default={})
    step_3_progress = Column(JSONB, default={})
    step_4_progress = Column(JSONB, default={})
    
    # Resume data - what user was working on when they left
    last_active_step = Column(Integer, default=1)
    resume_data = Column(JSONB, default={})  # Context for resuming where they left off
    
    # Performance and Analytics
    confidence_score = Column(Float)  # Overall campaign confidence
    intelligence_count = Column(Integer, default=0)
    generated_content_count = Column(Integer, default=0)
    last_activity = Column(DateTime)
    
    # Content storage (flexible JSON structure)
    content = Column(JSONB, default={})  # Store campaign-related content and metadata
    
    # Foreign Keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # EMERGENCY FIX: Remove relationships to avoid circular imports
    # Relationships will be defined elsewhere if needed
    
    def __init__(self, **kwargs):
        # Set default ID if not provided
        if 'id' not in kwargs:
            kwargs['id'] = uuid4()
        
        # Initialize step states for new campaigns
        if 'step_states' not in kwargs:
            kwargs['step_states'] = {
                "step_1": {"status": "completed", "progress": 100, "can_skip": False},
                "step_2": {"status": "available", "progress": 0, "can_skip": False}, 
                "step_3": {"status": "locked", "progress": 0, "can_skip": True},
                "step_4": {"status": "locked", "progress": 0, "can_skip": True}
            }
        
        super().__init__(**kwargs)
    
    def update_workflow_progress(self):
        """Update workflow progress based on current data"""
        # Count actual sources and content
        sources_count = self.sources_count or 0
        content_count = self.content_generated or 0
        
        # Update step states based on actual progress
        if sources_count > 0:
            self.step_states["step_2"]["status"] = "completed"
            self.step_states["step_2"]["progress"] = 100
            self.step_states["step_3"]["status"] = "available"
        
        if self.intelligence_extracted and self.intelligence_extracted > 0:
            self.step_states["step_3"]["status"] = "completed" 
            self.step_states["step_3"]["progress"] = 100
            self.step_states["step_4"]["status"] = "available"
        
        if content_count > 0:
            self.step_states["step_4"]["status"] = "completed"
            self.step_states["step_4"]["progress"] = 100
            self.workflow_state = CampaignWorkflowState.CAMPAIGN_COMPLETE
        
        # Update available steps
        available = [1]  # Step 1 always available
        if self.step_states["step_2"]["status"] in ["available", "completed"]:
            available.append(2)
        if self.step_states["step_3"]["status"] in ["available", "completed"]:
            available.append(3)
        if self.step_states["step_4"]["status"] in ["available", "completed"]:
            available.append(4)
        
        self.available_steps = available
        self.last_activity = datetime.utcnow()
    
    def calculate_completion_percentage(self):
        """Calculate overall completion percentage"""
        total_weight = 100
        progress = 0
        
        # Step 1: Always complete (25%)
        progress += 25
        
        # Step 2: Sources (25% weight)
        if self.step_states.get("step_2", {}).get("status") == "completed":
            progress += 25
        elif self.sources_count and self.sources_count > 0:
            progress += 12.5  # Partial credit
        
        # Step 3: Analysis (25% weight) 
        if self.step_states.get("step_3", {}).get("status") == "completed":
            progress += 25
        elif self.intelligence_extracted and self.intelligence_extracted > 0:
            progress += 12.5  # Partial credit
        
        # Step 4: Content (25% weight)
        if self.step_states.get("step_4", {}).get("status") == "completed":
            progress += 25
        elif self.content_generated and self.content_generated > 0:
            progress += 12.5  # Partial credit
        
        return min(progress, 100)
    
    def get_suggested_next_step(self):
        """Get the suggested next step for the user"""
        if not self.sources_count or self.sources_count == 0:
            return 2, "Add input sources to analyze"
        elif not self.intelligence_extracted or self.intelligence_extracted == 0:
            return 3, "Analyze your sources to extract intelligence"
        elif not self.content_generated or self.content_generated == 0:
            return 4, "Generate marketing content from your intelligence"
        else:
            return 2, "Add more sources or generate additional content"
    
    def can_quick_complete(self):
        """Determine if user can quickly complete remaining steps"""
        remaining_steps = []
        
        if not self.sources_count or self.sources_count == 0:
            remaining_steps.append("add_sources")
        if not self.intelligence_extracted or self.intelligence_extracted == 0:
            remaining_steps.append("analyze_sources")
        if not self.content_generated or self.content_generated == 0:
            remaining_steps.append("generate_content")
        
        # Can quick complete if 2 or fewer steps remain
        return len(remaining_steps) <= 2
    
    def get_workflow_summary(self):
        """Get a summary of the current workflow state"""
        return {
            "workflow_state": self.workflow_state.value if self.workflow_state else "basic_setup",
            "completion_percentage": self.calculate_completion_percentage(),
            "suggested_step": self.get_suggested_next_step()[0],
            "suggested_action": self.get_suggested_next_step()[1],
            "can_quick_complete": self.can_quick_complete(),
            "sources_count": self.sources_count or 0,
            "intelligence_count": self.intelligence_extracted or 0,
            "content_count": self.content_generated or 0,
            "workflow_preference": self.workflow_preference.value if self.workflow_preference else "flexible"
        }
    
    # ✅ Helper property for backward compatibility
    @property
    def campaign_type(self):
        """All campaigns are universal - for backward compatibility"""
        return "universal"
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, title='{self.title}', status='{self.status}')>"