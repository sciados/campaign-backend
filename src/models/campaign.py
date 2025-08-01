# src/models/campaign.py - FIXED TO PREVENT DUPLICATE TABLE DEFINITION
"""
Campaign models - Enhanced for streamlined workflow with auto-analysis + Storage Integration
🎯 NEW: Support for Campaign Creation → Auto-Analysis → Content Generation
🔧 FIXED: Consistent timezone-aware datetime fields + duplicate table prevention
📁 NEW: Storage file integration for user quota system - TEMPORARILY DISABLED
"""
from sqlalchemy import Column, String, Text, Enum, ForeignKey, Integer, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime, timezone
from uuid import uuid4

# Import from our clean base module
from .base import BaseModel

# Campaign-specific enums
class CampaignStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"  # 🆕 NEW: Auto-analysis in progress
    REVIEW = "REVIEW"  # 🆕
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"  # 🆕 NEW: Ready for content generation
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"

class WorkflowPreference(str, enum.Enum):
    QUICK = "QUICK"           # User wants to rush through steps
    METHODICAL = "METHODICAL" # User wants to take time at each step
    FLEXIBLE = "FLEXIBLE"     # User switches between modes

class CampaignWorkflowState(str, enum.Enum):
    # Streamlined workflow states
    BASIC_SETUP = "BASIC_SETUP"              # Step 1: Campaign created
    AUTO_ANALYZING = "AUTO_ANALYZING"        # 🆕 NEW: Auto-analysis running
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"   # Analysis done, ready for content
    GENERATING_CONTENT = "GENERATING_CONTENT" # Step 2: Creating content
    CAMPAIGN_COMPLETE = "CAMPAIGN_COMPLETE"   # All done

# 🆕 NEW: Analysis status for auto-analysis tracking
class AutoAnalysisStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS" 
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Campaign(BaseModel):
    """Enhanced Campaign model - Streamlined 2-step workflow with FIXED timezone fields + Storage Integration"""
    __tablename__ = "campaigns"
    # 🔧 FIXED: Prevent duplicate table definition
    __table_args__ = {'extend_existing': True}
    
    # Basic Campaign Information
    title = Column(String(500), nullable=False)
    description = Column(Text)
    keywords = Column(JSONB, default=[])
    target_audience = Column(JSONB, default={})
    
    # 🆕 NEW: Auto-Analysis Fields (from frontend Step1Setup)
    salespage_url = Column(String(1000))  # Primary competitor URL for analysis
    auto_analysis_enabled = Column(Boolean, default=True)  # Enable auto-analysis
    auto_analysis_status = Column(Enum(AutoAnalysisStatus, name='autoanalysisstatus'), default=AutoAnalysisStatus.PENDING)
    # 🔧 FIXED: All datetime fields now timezone-aware
    auto_analysis_started_at = Column(DateTime(timezone=True))
    auto_analysis_completed_at = Column(DateTime(timezone=True))
    auto_analysis_results = Column(JSONB, default={})  # Store analysis results
    auto_analysis_error = Column(Text)  # Store any analysis errors
    
    # 🆕 NEW: Content Generation Preferences
    content_types = Column(JSONB, default=["email", "social_post", "ad_copy"])  # What content to generate
    content_tone = Column(String(100), default="conversational")
    content_style = Column(String(100), default="modern")
    generate_content_after_analysis = Column(Boolean, default=False)  # Auto-generate content
    
    # Status and workflow
    status = Column(Enum(CampaignStatus, name='campaignstatus'), default=CampaignStatus.DRAFT)
    tone = Column(String(100), default="conversational")
    style = Column(String(100), default="modern")
    
    # Campaign Settings and Configuration
    settings = Column(JSONB, default={})
    
    # 🆕 UPDATED: Streamlined workflow tracking (2 steps instead of 4)
    workflow_state = Column(Enum(CampaignWorkflowState, name='campaignworkflowstate'), default=CampaignWorkflowState.BASIC_SETUP)
    workflow_preference = Column(Enum(WorkflowPreference, name='workflowpreference'), default=WorkflowPreference.FLEXIBLE)
    
    # 🆕 SIMPLIFIED: 2-step workflow
    active_steps = Column(JSONB, default=[1])  # Which steps user is currently working on
    completed_steps = Column(JSONB, default=[])  # Which steps are fully complete
    available_steps = Column(JSONB, default=[1, 2])  # Step 1 (setup+analysis) and Step 2 (content)
    
    # 🆕 UPDATED: 2-step progress tracking
    step_states = Column(JSONB, default={
        "step_1": {"status": "active", "progress": 0, "can_skip": False, "description": "Campaign Setup & Analysis"},
        "step_2": {"status": "locked", "progress": 0, "can_skip": False, "description": "Content Generation"}
    })
    
    # User session management
    current_session = Column(JSONB, default={})
    session_history = Column(JSONB, default=[])
    
    # Quick vs Methodical mode settings
    quick_mode_enabled = Column(Boolean, default=False)
    auto_advance_steps = Column(Boolean, default=True)  # 🆕 DEFAULT: Auto-advance enabled
    skip_confirmations = Column(Boolean, default=False)
    
    # Methodical mode settings  
    show_detailed_guidance = Column(Boolean, default=True)
    require_step_completion = Column(Boolean, default=False)
    save_frequently = Column(Boolean, default=True)
    
    # 🆕 UPDATED: Simplified progress tracking
    sources_count = Column(Integer, default=0)  # Will be 1 after auto-analysis
    sources_processed = Column(Integer, default=0)
    intelligence_extracted = Column(Integer, default=0)
    content_generated = Column(Integer, default=0)
    
    # 🆕 NEW: Analysis-specific data storage
    analysis_intelligence_id = Column(UUID(as_uuid=True))  # Link to CampaignIntelligence record
    analysis_confidence_score = Column(Float, default=0.0)
    analysis_summary = Column(JSONB, default={})  # Key insights for content generation
    
    # Step-specific data (simplified for 2 steps)
    step_1_data = Column(JSONB, default={})  # Setup + Analysis data
    step_2_data = Column(JSONB, default={})  # Content generation data
    
    # Progress percentages for UI
    step_1_progress = Column(JSONB, default={"setup": 0, "analysis": 0})
    step_2_progress = Column(JSONB, default={"content": 0})
    
    # Resume data
    last_active_step = Column(Integer, default=1)
    resume_data = Column(JSONB, default={})
    
    # Performance and Analytics
    confidence_score = Column(Float)
    intelligence_count = Column(Integer, default=0)
    generated_content_count = Column(Integer, default=0)
    # 🔧 FIXED: Changed to timezone-aware to match database schema
    last_activity = Column(DateTime(timezone=True))
    
    # Content storage
    content = Column(JSONB, default={})
    
    # Foreign Keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Relationships - 🔧 FIXED: Use string references to avoid circular imports
    user = relationship("User", back_populates="campaigns")
    company = relationship("Company", back_populates="campaigns")
    
    # Intelligence and content relationships
    intelligence_sources = relationship("CampaignIntelligence", back_populates="campaign", cascade="all, delete-orphan")
    generated_content = relationship("GeneratedContent", back_populates="campaign", cascade="all, delete-orphan")
    smart_urls = relationship("SmartURL", back_populates="campaign", cascade="all, delete-orphan")
    
    # 🆕 NEW: Storage integration for user quota system - TEMPORARILY DISABLED TO FIX REGISTRATION
    storage_files = relationship("UserStorageUsage", back_populates="campaign", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        # Set default ID if not provided
        if 'id' not in kwargs:
            kwargs['id'] = uuid4()
        
        # 🆕 UPDATED: Initialize 2-step workflow states
        if 'step_states' not in kwargs:
            kwargs['step_states'] = {
                "step_1": {"status": "active", "progress": 0, "can_skip": False, "description": "Campaign Setup & Analysis"},
                "step_2": {"status": "locked", "progress": 0, "can_skip": False, "description": "Content Generation"}
            }
        
        super().__init__(**kwargs)
    
    # 🆕 NEW: Auto-analysis workflow methods with FIXED timezone handling
    def start_auto_analysis(self):
        """Start auto-analysis process - FIXED timezone"""
        self.auto_analysis_status = AutoAnalysisStatus.IN_PROGRESS
        self.auto_analysis_started_at = datetime.now(timezone.utc)  # ✅ Always UTC timezone-aware
        self.status = CampaignStatus.IN_PROGRESS
        self.workflow_state = CampaignWorkflowState.AUTO_ANALYZING
        
        # Update step 1 progress
        if self.step_states is None:
            self.step_states = {}
        if "step_1" not in self.step_states:
            self.step_states["step_1"] = {"status": "analyzing", "progress": 50, "can_skip": False, "description": "Campaign Setup & Analysis"}
        else:
            self.step_states["step_1"]["progress"] = 50  # Setup done, analysis starting
            self.step_states["step_1"]["status"] = "analyzing"
        
        self.last_activity = datetime.now(timezone.utc)  # ✅ Always UTC timezone-aware
    
    def complete_auto_analysis(self, intelligence_id: str, confidence_score: float, analysis_summary: dict):
        """Complete auto-analysis process - FIXED timezone"""
        self.auto_analysis_status = AutoAnalysisStatus.COMPLETED
        self.auto_analysis_completed_at = datetime.now(timezone.utc)  # ✅ Always UTC timezone-aware
        self.analysis_intelligence_id = intelligence_id
        self.analysis_confidence_score = confidence_score
        self.analysis_summary = analysis_summary
        
        # Update progress
        self.sources_count = 1  # One competitor URL analyzed
        self.sources_processed = 1
        self.intelligence_extracted = 1
        self.intelligence_count = 1
        
        # Update workflow state
        self.status = CampaignStatus.ANALYSIS_COMPLETE
        self.workflow_state = CampaignWorkflowState.ANALYSIS_COMPLETE
        
        # Complete step 1, unlock step 2
        if self.step_states is None:
            self.step_states = {}
        
        # Ensure step_1 exists
        if "step_1" not in self.step_states:
            self.step_states["step_1"] = {"status": "completed", "progress": 100, "can_skip": False, "description": "Campaign Setup & Analysis"}
        else:
            self.step_states["step_1"]["status"] = "completed"
            self.step_states["step_1"]["progress"] = 100
        
        # Ensure step_2 exists
        if "step_2" not in self.step_states:
            self.step_states["step_2"] = {"status": "available", "progress": 0, "can_skip": False, "description": "Content Generation"}
        else:
            self.step_states["step_2"]["status"] = "available"
        
        self.completed_steps = [1]
        self.available_steps = [1, 2]
        self.last_activity = datetime.now(timezone.utc)  # ✅ Always UTC timezone-aware
    
    def fail_auto_analysis(self, error_message: str):
        """Handle auto-analysis failure - FIXED timezone"""
        self.auto_analysis_status = AutoAnalysisStatus.FAILED
        self.auto_analysis_error = error_message
        self.status = CampaignStatus.DRAFT  # Back to draft for manual retry
        
        # Update step 1 to show error
        if self.step_states is None:
            self.step_states = {}
        
        if "step_1" not in self.step_states:
            self.step_states["step_1"] = {"status": "error", "progress": 25, "can_skip": False, "description": "Campaign Setup & Analysis"}
        else:
            self.step_states["step_1"]["status"] = "error"
            self.step_states["step_1"]["progress"] = 25  # Partial progress
        
        self.last_activity = datetime.now(timezone.utc)  # ✅ Always UTC timezone-aware
    
    def start_content_generation(self):
        """Start content generation (Step 2) - FIXED timezone"""
        self.workflow_state = CampaignWorkflowState.GENERATING_CONTENT
        self.status = CampaignStatus.ACTIVE
        
        # Update step 2
        if self.step_states is None:
            self.step_states = {}
        
        if "step_2" not in self.step_states:
            self.step_states["step_2"] = {"status": "active", "progress": 25, "can_skip": False, "description": "Content Generation"}
        else:
            self.step_states["step_2"]["status"] = "active"
            self.step_states["step_2"]["progress"] = 25
        
        self.active_steps = [2]
        self.last_active_step = 2
        self.last_activity = datetime.now(timezone.utc)  # ✅ Always UTC timezone-aware
    
    def complete_content_generation(self, content_count: int):
        """Complete content generation - FIXED timezone"""
        self.content_generated = content_count
        self.generated_content_count = content_count
        
        # Complete workflow
        self.workflow_state = CampaignWorkflowState.CAMPAIGN_COMPLETE
        self.status = CampaignStatus.COMPLETED
        
        # Complete step 2
        if self.step_states is None:
            self.step_states = {}
        
        if "step_2" not in self.step_states:
            self.step_states["step_2"] = {"status": "completed", "progress": 100, "can_skip": False, "description": "Content Generation"}
        else:
            self.step_states["step_2"]["status"] = "completed"
            self.step_states["step_2"]["progress"] = 100
        
        self.completed_steps = [1, 2]
        self.last_activity = datetime.now(timezone.utc)  # ✅ Always UTC timezone-aware
    
    def update_workflow_progress(self):
        """🆕 UPDATED: Update workflow progress for 2-step workflow - FIXED timezone"""
        # Auto-update based on analysis and content status
        if self.auto_analysis_status == AutoAnalysisStatus.COMPLETED:
            if self.step_states and self.step_states.get("step_1", {}).get("status") != "completed":
                self.complete_auto_analysis(
                    str(self.analysis_intelligence_id) if self.analysis_intelligence_id else "",
                    self.analysis_confidence_score or 0.0,
                    self.analysis_summary or {}
                )
        
        if self.content_generated and self.content_generated > 0:
            if self.step_states and self.step_states.get("step_2", {}).get("status") != "completed":
                self.complete_content_generation(self.content_generated)
        
        self.last_activity = datetime.now(timezone.utc)  # ✅ Always UTC timezone-aware
    
    def calculate_completion_percentage(self):
        """🆕 UPDATED: Calculate completion percentage for 2-step workflow"""
        progress = 0
        
        # Ensure step_states exists
        if not self.step_states:
            return 25.0  # Basic setup
        
        # Step 1: Setup + Analysis (60% weight)
        step_1_progress = self.step_states.get("step_1", {}).get("progress", 0)
        progress += (step_1_progress / 100) * 60
        
        # Step 2: Content Generation (40% weight)
        step_2_progress = self.step_states.get("step_2", {}).get("progress", 0)
        progress += (step_2_progress / 100) * 40
        
        return min(progress, 100)
    
    def get_suggested_next_step(self):
        """🆕 UPDATED: Get suggested next step for 2-step workflow"""
        if self.auto_analysis_status == AutoAnalysisStatus.PENDING:
            return 1, "Complete campaign setup to trigger auto-analysis"
        elif self.auto_analysis_status == AutoAnalysisStatus.IN_PROGRESS:
            return 1, "Auto-analysis in progress - please wait"
        elif self.auto_analysis_status == AutoAnalysisStatus.FAILED:
            return 1, "Fix analysis errors and retry"
        elif self.auto_analysis_status == AutoAnalysisStatus.COMPLETED and self.content_generated == 0:
            return 2, "Generate content using your analysis insights"
        else:
            return 2, "Add more content or refine existing content"
    
    def can_quick_complete(self):
        """🆕 UPDATED: Check if campaign can be quickly completed"""
        # Can quick complete if analysis is done and ready for content
        return self.auto_analysis_status == AutoAnalysisStatus.COMPLETED
    
    def get_workflow_summary(self):
        """🆕 UPDATED: Get workflow summary for 2-step process"""
        return {
            "workflow_state": self.workflow_state.value if self.workflow_state else "basic_setup",
            "completion_percentage": self.calculate_completion_percentage(),
            "suggested_step": self.get_suggested_next_step()[0],
            "suggested_action": self.get_suggested_next_step()[1],
            "can_quick_complete": self.can_quick_complete(),
            "auto_analysis_status": self.auto_analysis_status.value if self.auto_analysis_status else "pending",
            "analysis_confidence": self.analysis_confidence_score or 0.0,
            "content_count": self.content_generated or 0,
            "workflow_preference": self.workflow_preference.value if self.workflow_preference else "flexible",
            "total_steps": 2,  # 🆕 NEW: Streamlined to 2 steps
            "current_step": 2 if self.auto_analysis_status == AutoAnalysisStatus.COMPLETED else 1
        }
    
    def get_auto_analysis_status(self):
        """🆕 NEW: Get detailed auto-analysis status"""
        return {
            "status": self.auto_analysis_status.value if self.auto_analysis_status else "pending",
            "salespage_url": self.salespage_url,
            "started_at": self.auto_analysis_started_at.isoformat() if self.auto_analysis_started_at else None,
            "completed_at": self.auto_analysis_completed_at.isoformat() if self.auto_analysis_completed_at else None,
            "confidence_score": self.analysis_confidence_score or 0.0,
            "intelligence_id": str(self.analysis_intelligence_id) if self.analysis_intelligence_id else None,
            "error_message": self.auto_analysis_error,
            "summary": self.analysis_summary or {},
            "can_generate_content": self.auto_analysis_status == AutoAnalysisStatus.COMPLETED
        }
    
    # 🆕 NEW: Storage utility methods for user quota system (SAFE VERSIONS - handle missing relationship)
    def get_total_storage_used(self) -> int:
        """Get total storage used by this campaign in bytes"""
        try:
            if hasattr(self, 'storage_files') and self.storage_files:
                return sum(file.file_size for file in self.storage_files if not file.is_deleted)
            return 0
        except:
            return 0
    
    def get_total_storage_used_mb(self) -> float:
        """Get total storage used by this campaign in MB"""
        return round(self.get_total_storage_used() / 1024 / 1024, 2)
    
    def get_total_storage_used_gb(self) -> float:
        """Get total storage used by this campaign in GB"""
        return round(self.get_total_storage_used() / 1024 / 1024 / 1024, 2)
    
    def get_file_count_by_type(self) -> dict:
        """Get count of files by content category"""
        counts = {"image": 0, "document": 0, "video": 0}
        try:
            if hasattr(self, 'storage_files') and self.storage_files:
                for file in self.storage_files:
                    if not file.is_deleted:
                        counts[file.content_category] = counts.get(file.content_category, 0) + 1
        except:
            pass
        return counts
    
    def get_campaign_files(self, content_category: str = None, include_deleted: bool = False):
        """Get files associated with this campaign"""
        try:
            if not hasattr(self, 'storage_files') or not self.storage_files:
                return []
                
            files = self.storage_files
            if not include_deleted:
                files = [f for f in files if not f.is_deleted]
            if content_category:
                files = [f for f in files if f.content_category == content_category]
            return files
        except:
            return []
    
    def get_storage_summary(self) -> dict:
        """Get comprehensive storage summary for this campaign"""
        file_counts = self.get_file_count_by_type()
        return {
            "total_files": sum(file_counts.values()),
            "file_counts_by_type": file_counts,
            "total_storage_bytes": self.get_total_storage_used(),
            "total_storage_mb": self.get_total_storage_used_mb(),
            "total_storage_gb": self.get_total_storage_used_gb(),
            "has_files": self.get_total_storage_used() > 0
        }
    
    # Helper property for backward compatibility
    @property
    def campaign_type(self):
        """All campaigns are universal - for backward compatibility"""
        return "universal"
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, title='{self.title}', status='{self.status}', analysis_status='{self.auto_analysis_status}', storage={self.get_total_storage_used_mb()}MB)>"