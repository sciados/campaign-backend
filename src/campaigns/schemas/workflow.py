# src/campaigns/schemas/workflow.py

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class WorkflowStateEnum(str, Enum):
    """Workflow state enumeration"""
    INITIAL = "INITIAL"
    ANALYZING = "ANALYZING"
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"
    GENERATING_CONTENT = "GENERATING_CONTENT"
    CONTENT_READY = "CONTENT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED = "APPROVED"
    DEPLOYED = "DEPLOYED"
    MONITORING = "MONITORING"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    PAUSED = "PAUSED"

class WorkflowStepTypeEnum(str, Enum):
    """Workflow step type enumeration"""
    ANALYSIS = "ANALYSIS"
    CONTENT_GENERATION = "CONTENT_GENERATION"
    REVIEW = "REVIEW"
    APPROVAL = "APPROVAL"
    DEPLOYMENT = "DEPLOYMENT"
    MONITORING = "MONITORING"
    COMPLETION = "COMPLETION"

class WorkflowPriorityEnum(str, Enum):
    """Workflow priority enumeration"""
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"

# ============================================================================
# BASE WORKFLOW SCHEMAS
# ============================================================================

class WorkflowStepBase(BaseModel):
    """Base workflow step schema"""
    step_number: int = Field(..., ge=0, description="Step number in the workflow")
    step_name: str = Field(..., min_length=1, max_length=100, description="Name of the step")
    step_type: WorkflowStepTypeEnum = Field(..., description="Type of workflow step")
    description: Optional[str] = Field(None, max_length=500, description="Step description")
    estimated_duration: Optional[int] = Field(None, ge=0, description="Estimated duration in minutes")
    required: bool = Field(default=True, description="Whether this step is required")

class WorkflowStepCreate(WorkflowStepBase):
    """Schema for creating a workflow step"""
    dependencies: Optional[List[int]] = Field(default_factory=list, description="Step numbers this step depends on")
    input_requirements: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Input requirements")
    output_expectations: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Expected outputs")

class WorkflowStepUpdate(BaseModel):
    """Schema for updating a workflow step"""
    step_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    estimated_duration: Optional[int] = Field(None, ge=0)
    required: Optional[bool] = None
    input_requirements: Optional[Dict[str, Any]] = None
    output_expectations: Optional[Dict[str, Any]] = None

# ============================================================================
# WORKFLOW EXECUTION SCHEMAS
# ============================================================================

class WorkflowExecutionStatus(BaseModel):
    """Workflow execution status schema"""
    step_number: int = Field(..., ge=0)
    status: WorkflowStateEnum = Field(...)
    started_at: Optional[str] = Field(None, description="When step started")
    completed_at: Optional[str] = Field(None, description="When step completed")
    duration: Optional[int] = Field(None, ge=0, description="Duration in seconds")
    success: bool = Field(default=False, description="Whether step completed successfully")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    output_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Step output data")

class WorkflowProgress(BaseModel):
    """Workflow progress schema"""
    campaign_id: str = Field(..., description="Campaign ID")
    current_step: int = Field(default=0, ge=0, description="Current step number")
    current_state: WorkflowStateEnum = Field(default=WorkflowStateEnum.INITIAL, description="Current workflow state")
    total_steps: int = Field(..., ge=0, description="Total number of steps")
    completed_steps: int = Field(default=0, ge=0, description="Number of completed steps")
    completion_percentage: int = Field(default=0, ge=0, le=100, description="Completion percentage")
    is_complete: bool = Field(default=False, description="Whether workflow is complete")
    is_paused: bool = Field(default=False, description="Whether workflow is paused")
    has_errors: bool = Field(default=False, description="Whether workflow has errors")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")
    step_statuses: List[WorkflowExecutionStatus] = Field(default_factory=list, description="Status of each step")

# ============================================================================
# WORKFLOW TEMPLATE SCHEMAS
# ============================================================================

class WorkflowTemplate(BaseModel):
    """Workflow template schema"""
    id: str = Field(..., description="Template ID")
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: Optional[str] = Field(None, max_length=1000, description="Template description")
    campaign_type: str = Field(..., description="Campaign type this template applies to")
    version: str = Field(default="1.0.0", description="Template version")
    is_active: bool = Field(default=True, description="Whether template is active")
    steps: List[WorkflowStepCreate] = Field(..., description="Workflow steps")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

class WorkflowTemplateCreate(BaseModel):
    """Schema for creating a workflow template"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    campaign_type: str = Field(...)
    steps: List[WorkflowStepCreate] = Field(...)

class WorkflowTemplateUpdate(BaseModel):
    """Schema for updating a workflow template"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None
    steps: Optional[List[WorkflowStepCreate]] = None

# ============================================================================
# WORKFLOW ACTION SCHEMAS
# ============================================================================

class WorkflowAction(BaseModel):
    """Workflow action schema"""
    action_type: str = Field(..., description="Type of action")
    target_step: Optional[int] = Field(None, description="Target step number")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Action parameters")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for action")

    @validator('action_type')
    def validate_action_type(cls, v):
        allowed_actions = [
            'start', 'pause', 'resume', 'stop', 'restart', 
            'skip_step', 'retry_step', 'reset', 'approve', 'reject'
        ]
        if v not in allowed_actions:
            raise ValueError(f'action_type must be one of: {allowed_actions}')
        return v

class WorkflowStartRequest(BaseModel):
    """Request to start a workflow"""
    campaign_id: str = Field(..., description="Campaign ID")
    template_id: Optional[str] = Field(None, description="Workflow template ID to use")
    priority: WorkflowPriorityEnum = Field(default=WorkflowPriorityEnum.NORMAL, description="Workflow priority")
    auto_proceed: bool = Field(default=True, description="Whether to auto-proceed through steps")
    initial_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Initial workflow data")

class WorkflowStepResult(BaseModel):
    """Result of a workflow step execution"""
    step_number: int = Field(..., ge=0)
    success: bool = Field(...)
    duration: int = Field(..., ge=0, description="Duration in seconds")
    output_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    error_message: Optional[str] = Field(None)
    next_step: Optional[int] = Field(None, description="Next step to execute")
    requires_review: bool = Field(default=False, description="Whether step requires human review")

# ============================================================================
# WORKFLOW ANALYTICS SCHEMAS
# ============================================================================

class WorkflowStepAnalytics(BaseModel):
    """Analytics for a workflow step"""
    step_number: int = Field(..., ge=0)
    step_name: str = Field(...)
    execution_count: int = Field(default=0, ge=0)
    success_count: int = Field(default=0, ge=0)
    failure_count: int = Field(default=0, ge=0)
    average_duration: float = Field(default=0.0, ge=0.0, description="Average duration in seconds")
    success_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Success rate percentage")

class WorkflowAnalytics(BaseModel):
    """Analytics for workflow execution"""
    campaign_id: str = Field(..., description="Campaign ID")
    template_id: Optional[str] = Field(None, description="Template ID used")
    total_executions: int = Field(default=0, ge=0)
    successful_executions: int = Field(default=0, ge=0)
    failed_executions: int = Field(default=0, ge=0)
    average_completion_time: float = Field(default=0.0, ge=0.0, description="Average completion time in seconds")
    success_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    step_analytics: List[WorkflowStepAnalytics] = Field(default_factory=list)
    bottlenecks: List[int] = Field(default_factory=list, description="Step numbers that are bottlenecks")
    generated_at: str = Field(..., description="When analytics were generated")

# ============================================================================
# WORKFLOW NOTIFICATION SCHEMAS
# ============================================================================

class WorkflowNotification(BaseModel):
    """Workflow notification schema"""
    id: str = Field(..., description="Notification ID")
    campaign_id: str = Field(..., description="Campaign ID")
    workflow_step: int = Field(..., ge=0, description="Workflow step number")
    notification_type: str = Field(..., description="Type of notification")
    title: str = Field(..., max_length=200, description="Notification title")
    message: str = Field(..., max_length=1000, description="Notification message")
    priority: WorkflowPriorityEnum = Field(default=WorkflowPriorityEnum.NORMAL)
    is_read: bool = Field(default=False, description="Whether notification has been read")
    requires_action: bool = Field(default=False, description="Whether notification requires user action")
    action_url: Optional[str] = Field(None, description="URL for required action")
    created_at: str = Field(..., description="Creation timestamp")
    expires_at: Optional[str] = Field(None, description="Expiration timestamp")

    @validator('notification_type')
    def validate_notification_type(cls, v):
        allowed_types = [
            'step_completed', 'step_failed', 'review_required', 
            'approval_needed', 'workflow_completed', 'workflow_failed',
            'workflow_paused', 'workflow_resumed'
        ]
        if v not in allowed_types:
            raise ValueError(f'notification_type must be one of: {allowed_types}')
        return v

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class WorkflowResponse(BaseModel):
    """Complete workflow response schema"""
    campaign_id: str = Field(..., description="Campaign ID")
    template_id: Optional[str] = Field(None, description="Template ID")
    progress: WorkflowProgress = Field(..., description="Workflow progress")
    analytics: Optional[WorkflowAnalytics] = Field(None, description="Workflow analytics")
    notifications: List[WorkflowNotification] = Field(default_factory=list, description="Active notifications")

class WorkflowListResponse(BaseModel):
    """Workflow list response schema"""
    workflows: List[WorkflowResponse] = Field(..., description="List of workflows")
    total: int = Field(..., ge=0, description="Total number of workflows")
    active: int = Field(..., ge=0, description="Number of active workflows")
    completed: int = Field(..., ge=0, description="Number of completed workflows")
    failed: int = Field(..., ge=0, description="Number of failed workflows")

# ============================================================================
# ERROR SCHEMAS
# ============================================================================

class WorkflowError(BaseModel):
    """Workflow error response schema"""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    campaign_id: Optional[str] = Field(None, description="Campaign ID")
    step_number: Optional[int] = Field(None, description="Step number where error occurred")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")
    recoverable: bool = Field(default=True, description="Whether error is recoverable")