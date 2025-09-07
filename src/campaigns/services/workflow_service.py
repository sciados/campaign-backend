# src/campaigns/services/workflow_service.py

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
import logging
import asyncio

from ..schemas.workflow import (
    WorkflowStateEnum, WorkflowProgress, WorkflowStepResult,
    WorkflowAction, WorkflowAnalytics, WorkflowNotification
)
from ..models.campaign import Campaign, CampaignWorkflowStateEnum

logger = logging.getLogger(__name__)

class WorkflowService:
    """Campaign workflow management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._workflow_steps = self._initialize_workflow_steps()
        
    def _initialize_workflow_steps(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize workflow step definitions"""
        return {
            "EMAIL_SEQUENCE": [
                {
                    "step_number": 1,
                    "step_name": "Intelligence Analysis",
                    "step_type": "ANALYSIS",
                    "state": CampaignWorkflowStateEnum.ANALYZING,
                    "estimated_duration": 120,  # 2 minutes
                    "required": True,
                    "auto_proceed": True
                },
                {
                    "step_number": 2,
                    "step_name": "Email Content Generation",
                    "step_type": "CONTENT_GENERATION",
                    "state": CampaignWorkflowStateEnum.GENERATING_CONTENT,
                    "estimated_duration": 180,  # 3 minutes
                    "required": True,
                    "auto_proceed": True
                },
                {
                    "step_number": 3,
                    "step_name": "Content Review",
                    "step_type": "REVIEW",
                    "state": CampaignWorkflowStateEnum.REVIEW_REQUIRED,
                    "estimated_duration": 300,  # 5 minutes (human review)
                    "required": True,
                    "auto_proceed": False
                },
                {
                    "step_number": 4,
                    "step_name": "Final Approval",
                    "step_type": "APPROVAL",
                    "state": CampaignWorkflowStateEnum.APPROVED,
                    "estimated_duration": 60,   # 1 minute
                    "required": True,
                    "auto_proceed": False
                },
                {
                    "step_number": 5,
                    "step_name": "Campaign Ready",
                    "step_type": "COMPLETION",
                    "state": CampaignWorkflowStateEnum.COMPLETE,
                    "estimated_duration": 30,   # 30 seconds
                    "required": True,
                    "auto_proceed": True
                }
            ],
            "SOCIAL_MEDIA": [
                {
                    "step_number": 1,
                    "step_name": "Intelligence Analysis", 
                    "step_type": "ANALYSIS",
                    "state": CampaignWorkflowStateEnum.ANALYZING,
                    "estimated_duration": 120,
                    "required": True,
                    "auto_proceed": True
                },
                {
                    "step_number": 2,
                    "step_name": "Social Media Content Generation",
                    "step_type": "CONTENT_GENERATION", 
                    "state": CampaignWorkflowStateEnum.GENERATING_CONTENT,
                    "estimated_duration": 150,
                    "required": True,
                    "auto_proceed": True
                },
                {
                    "step_number": 3,
                    "step_name": "Content Review",
                    "step_type": "REVIEW",
                    "state": CampaignWorkflowStateEnum.REVIEW_REQUIRED,
                    "estimated_duration": 240,
                    "required": True,
                    "auto_proceed": False
                },
                {
                    "step_number": 4,
                    "step_name": "Campaign Ready",
                    "step_type": "COMPLETION",
                    "state": CampaignWorkflowStateEnum.COMPLETE,
                    "estimated_duration": 30,
                    "required": True,
                    "auto_proceed": True
                }
            ],
            "CONTENT_MARKETING": [
                {
                    "step_number": 1,
                    "step_name": "Intelligence Analysis",
                    "step_type": "ANALYSIS",
                    "state": CampaignWorkflowStateEnum.ANALYZING,
                    "estimated_duration": 180,  # Longer for content marketing
                    "required": True,
                    "auto_proceed": True
                },
                {
                    "step_number": 2,
                    "step_name": "Content Strategy Development",
                    "step_type": "CONTENT_GENERATION",
                    "state": CampaignWorkflowStateEnum.GENERATING_CONTENT,
                    "estimated_duration": 300,
                    "required": True,
                    "auto_proceed": True
                },
                {
                    "step_number": 3,
                    "step_name": "Content Creation",
                    "step_type": "CONTENT_GENERATION",
                    "state": CampaignWorkflowStateEnum.GENERATING_CONTENT,
                    "estimated_duration": 420,  # 7 minutes
                    "required": True,
                    "auto_proceed": True
                },
                {
                    "step_number": 4,
                    "step_name": "Editorial Review",
                    "step_type": "REVIEW",
                    "state": CampaignWorkflowStateEnum.REVIEW_REQUIRED,
                    "estimated_duration": 600,  # 10 minutes for thorough review
                    "required": True,
                    "auto_proceed": False
                },
                {
                    "step_number": 5,
                    "step_name": "Campaign Ready",
                    "step_type": "COMPLETION",
                    "state": CampaignWorkflowStateEnum.COMPLETE,
                    "estimated_duration": 30,
                    "required": True,
                    "auto_proceed": True
                }
            ],
            "AFFILIATE_PROMOTION": [
                {
                    "step_number": 1,
                    "step_name": "Intelligence Analysis",
                    "step_type": "ANALYSIS",
                    "state": CampaignWorkflowStateEnum.ANALYZING,
                    "estimated_duration": 120,
                    "required": True,
                    "auto_proceed": True
                },
                {
                    "step_number": 2,
                    "step_name": "Promotional Content Generation",
                    "step_type": "CONTENT_GENERATION",
                    "state": CampaignWorkflowStateEnum.GENERATING_CONTENT,
                    "estimated_duration": 150,
                    "required": True,
                    "auto_proceed": True
                },
                {
                    "step_number": 3,
                    "step_name": "Compliance Review",
                    "step_type": "REVIEW",
                    "state": CampaignWorkflowStateEnum.REVIEW_REQUIRED,
                    "estimated_duration": 180,
                    "required": True,
                    "auto_proceed": False
                },
                {
                    "step_number": 4,
                    "step_name": "Campaign Ready",
                    "step_type": "COMPLETION",
                    "state": CampaignWorkflowStateEnum.COMPLETE,
                    "estimated_duration": 30,
                    "required": True,
                    "auto_proceed": True
                }
            ],
            "PRODUCT_LAUNCH": [
                {
                    "step_number": 1,
                    "step_name": "Intelligence Analysis",
                    "step_type": "ANALYSIS",
                    "state": CampaignWorkflowStateEnum.ANALYZING,
                    "estimated_duration": 240,  # Longer for product launches
                    "required": True,
                    "auto_proceed": True
                },
                {
                    "step_number": 2,
                    "step_name": "Launch Strategy Development",
                    "step_type": "CONTENT_GENERATION",
                    "state": CampaignWorkflowStateEnum.GENERATING_CONTENT,
                    "estimated_duration": 360,
                    "required": True,
                    "auto_proceed": True
                },
                {
                    "step_number": 3,
                    "step_name": "Marketing Asset Creation",
                    "step_type": "CONTENT_GENERATION",
                    "state": CampaignWorkflowStateEnum.GENERATING_CONTENT,
                    "estimated_duration": 480,  # 8 minutes
                    "required": True,
                    "auto_proceed": True
                },
                {
                    "step_number": 4,
                    "step_name": "Stakeholder Review",
                    "step_type": "REVIEW",
                    "state": CampaignWorkflowStateEnum.REVIEW_REQUIRED,
                    "estimated_duration": 720,  # 12 minutes for stakeholder review
                    "required": True,
                    "auto_proceed": False
                },
                {
                    "step_number": 5,
                    "step_name": "Final Approval",
                    "step_type": "APPROVAL",
                    "state": CampaignWorkflowStateEnum.APPROVED,
                    "estimated_duration": 120,
                    "required": True,
                    "auto_proceed": False
                },
                {
                    "step_number": 6,
                    "step_name": "Launch Ready",
                    "step_type": "COMPLETION",
                    "state": CampaignWorkflowStateEnum.COMPLETE,
                    "estimated_duration": 30,
                    "required": True,
                    "auto_proceed": True
                }
            ],
            "DEFAULT": [
                {
                    "step_number": 1,
                    "step_name": "Intelligence Analysis",
                    "step_type": "ANALYSIS",
                    "state": CampaignWorkflowStateEnum.ANALYZING,
                    "estimated_duration": 120,
                    "required": True,
                    "auto_proceed": True
                },
                {
                    "step_number": 2,
                    "step_name": "Content Generation",
                    "step_type": "CONTENT_GENERATION",
                    "state": CampaignWorkflowStateEnum.GENERATING_CONTENT,
                    "estimated_duration": 180,
                    "required": True,
                    "auto_proceed": True
                },
                {
                    "step_number": 3,
                    "step_name": "Review & Approval",
                    "step_type": "REVIEW",
                    "state": CampaignWorkflowStateEnum.REVIEW_REQUIRED,
                    "estimated_duration": 300,
                    "required": True,
                    "auto_proceed": False
                },
                {
                    "step_number": 4,
                    "step_name": "Campaign Ready",
                    "step_type": "COMPLETION",
                    "state": CampaignWorkflowStateEnum.COMPLETE,
                    "estimated_duration": 30,
                    "required": True,
                    "auto_proceed": True
                }
            ]
        }
    
    # ============================================================================
    # WORKFLOW MANAGEMENT METHODS
    # ============================================================================
    
    async def start_workflow(
        self,
        campaign_id: Union[str, UUID],
        campaign_type: str = "DEFAULT",
        auto_proceed: bool = True
    ) -> WorkflowProgress:
        """Start workflow for a campaign"""
        try:
            logger.info(f"Starting workflow for campaign {campaign_id}")
            
            campaign_uuid = UUID(str(campaign_id)) if isinstance(campaign_id, str) else campaign_id
            
            # Get campaign
            query = select(Campaign).where(Campaign.id == campaign_uuid)
            result = await self.db.execute(query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            # Get workflow steps for campaign type
            steps = self._workflow_steps.get(campaign_type, self._workflow_steps["DEFAULT"])
            
            # Initialize workflow
            campaign.workflow_step = 1
            campaign.workflow_state = CampaignWorkflowStateEnum.INITIAL
            campaign.completion_percentage = 0
            campaign.is_workflow_complete = False
            campaign.workflow_data = {
                "started_at": datetime.now(timezone.utc).isoformat(),
                "total_steps": len(steps),
                "auto_proceed": auto_proceed,
                "step_history": []
            }
            
            await self.db.commit()
            await self.db.refresh(campaign)
            
            # Start first step if auto_proceed
            if auto_proceed:
                await self._execute_step(campaign, 1, steps)
            
            return await self.get_workflow_progress(campaign_id)
            
        except Exception as e:
            logger.error(f"Error starting workflow: {e}")
            await self.db.rollback()
            raise
    
    async def get_workflow_progress(
        self,
        campaign_id: Union[str, UUID]
    ) -> WorkflowProgress:
        """Get workflow progress for a campaign"""
        try:
            campaign_uuid = UUID(str(campaign_id)) if isinstance(campaign_id, str) else campaign_id
            
            query = select(Campaign).where(Campaign.id == campaign_uuid)
            result = await self.db.execute(query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            workflow_data = campaign.workflow_data or {}
            total_steps = workflow_data.get("total_steps", 4)
            
            return WorkflowProgress(
                campaign_id=str(campaign.id),
                current_step=campaign.workflow_step,
                current_state=campaign.workflow_state or CampaignWorkflowStateEnum.INITIAL,
                total_steps=total_steps,
                completed_steps=self._calculate_completed_steps(campaign),
                completion_percentage=campaign.completion_percentage,
                is_complete=campaign.is_workflow_complete,
                is_paused=campaign.workflow_state == CampaignWorkflowStateEnum.PAUSED,
                has_errors=campaign.workflow_state == CampaignWorkflowStateEnum.ERROR,
                estimated_completion=self._calculate_estimated_completion(campaign),
                step_statuses=self._get_step_statuses(campaign)
            )
            
        except Exception as e:
            logger.error(f"Error getting workflow progress: {e}")
            raise
    
    async def execute_workflow_action(
        self,
        campaign_id: Union[str, UUID],
        action: WorkflowAction
    ) -> WorkflowProgress:
        """Execute a workflow action"""
        try:
            logger.info(f"Executing workflow action {action.action_type} for campaign {campaign_id}")
            
            campaign_uuid = UUID(str(campaign_id)) if isinstance(campaign_id, str) else campaign_id
            
            query = select(Campaign).where(Campaign.id == campaign_uuid)
            result = await self.db.execute(query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            # Execute the action
            if action.action_type == "start":
                return await self.start_workflow(campaign_id)
            elif action.action_type == "pause":
                await self._pause_workflow(campaign)
            elif action.action_type == "resume":
                await self._resume_workflow(campaign)
            elif action.action_type == "stop":
                await self._stop_workflow(campaign)
            elif action.action_type == "restart":
                return await self.start_workflow(campaign_id)
            elif action.action_type == "skip_step":
                await self._skip_step(campaign, action.target_step)
            elif action.action_type == "retry_step":
                await self._retry_step(campaign, action.target_step)
            elif action.action_type == "approve":
                await self._approve_step(campaign, action.target_step)
            elif action.action_type == "reject":
                await self._reject_step(campaign, action.target_step, action.reason)
            else:
                raise ValueError(f"Unknown action type: {action.action_type}")
            
            return await self.get_workflow_progress(campaign_id)
            
        except Exception as e:
            logger.error(f"Error executing workflow action: {e}")
            await self.db.rollback()
            raise
    
    async def advance_workflow(
        self,
        campaign_id: Union[str, UUID],
        step_result: Optional[WorkflowStepResult] = None
    ) -> WorkflowProgress:
        """Advance workflow to next step"""
        try:
            logger.info(f"Advancing workflow for campaign {campaign_id}")
            
            campaign_uuid = UUID(str(campaign_id)) if isinstance(campaign_id, str) else campaign_id
            
            query = select(Campaign).where(Campaign.id == campaign_uuid)
            result = await self.db.execute(query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            workflow_data = campaign.workflow_data or {}
            total_steps = workflow_data.get("total_steps", 4)
            current_step = campaign.workflow_step
            
            # Record step result if provided
            if step_result:
                await self._record_step_result(campaign, step_result)
            
            # Advance to next step
            if current_step < total_steps:
                next_step = current_step + 1
                campaign.workflow_step = next_step
                campaign.completion_percentage = int((next_step / total_steps) * 100)
                
                # Get campaign type and steps
                campaign_type = campaign.campaign_type.value if campaign.campaign_type else "DEFAULT"
                steps = self._workflow_steps.get(campaign_type, self._workflow_steps["DEFAULT"])
                
                # Execute next step if auto_proceed is enabled
                auto_proceed = workflow_data.get("auto_proceed", True)
                if auto_proceed and next_step <= len(steps):
                    await self._execute_step(campaign, next_step, steps)
                
            else:
                # Workflow complete
                campaign.is_workflow_complete = True
                campaign.completion_percentage = 100
                campaign.workflow_state = CampaignWorkflowStateEnum.COMPLETE
                
                workflow_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                campaign.workflow_data = workflow_data
            
            await self.db.commit()
            await self.db.refresh(campaign)
            
            return await self.get_workflow_progress(campaign_id)
            
        except Exception as e:
            logger.error(f"Error advancing workflow: {e}")
            await self.db.rollback()
            raise
    
    async def get_workflow_analytics(
        self,
        campaign_id: Union[str, UUID]
    ) -> WorkflowAnalytics:
        """Get workflow analytics for a campaign"""
        try:
            campaign_uuid = UUID(str(campaign_id)) if isinstance(campaign_id, str) else campaign_id
            
            query = select(Campaign).where(Campaign.id == campaign_uuid)
            result = await self.db.execute(query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            workflow_data = campaign.workflow_data or {}
            step_history = workflow_data.get("step_history", [])
            
            # Calculate analytics
            total_executions = 1 if step_history else 0
            successful_executions = 1 if campaign.is_workflow_complete else 0
            failed_executions = 1 if campaign.workflow_state == CampaignWorkflowStateEnum.ERROR else 0
            
            # Calculate completion time
            started_at = workflow_data.get("started_at")
            completed_at = workflow_data.get("completed_at")
            
            average_completion_time = 0.0
            if started_at and completed_at:
                start_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                end_time = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                average_completion_time = (end_time - start_time).total_seconds()
            
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
            
            return WorkflowAnalytics(
                campaign_id=str(campaign.id),
                template_id=None,  # We don't have templates yet
                total_executions=total_executions,
                successful_executions=successful_executions,
                failed_executions=failed_executions,
                average_completion_time=average_completion_time,
                success_rate=success_rate,
                step_analytics=[],  # Would need historical data for this
                bottlenecks=[],     # Would need analysis across multiple campaigns
                generated_at=datetime.now(timezone.utc).isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error getting workflow analytics: {e}")
            raise
    
    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================
    
    async def _execute_step(
        self,
        campaign: Campaign,
        step_number: int,
        steps: List[Dict[str, Any]]
    ):
        """Execute a specific workflow step"""
        try:
            if step_number > len(steps):
                return
            
            step_config = steps[step_number - 1]
            
            # Update campaign state
            campaign.workflow_state = step_config["state"]
            campaign.workflow_step = step_number
            
            # Record step start
            workflow_data = campaign.workflow_data or {}
            step_history = workflow_data.get("step_history", [])
            
            step_record = {
                "step_number": step_number,
                "step_name": step_config["step_name"],
                "started_at": datetime.now(timezone.utc).isoformat(),
                "status": "in_progress"
            }
            step_history.append(step_record)
            
            workflow_data["step_history"] = step_history
            campaign.workflow_data = workflow_data
            
            logger.info(f"Executing step {step_number}: {step_config['step_name']}")
            
            # For non-auto steps, just update state and wait for manual action
            if not step_config.get("auto_proceed", True):
                logger.info(f"Step {step_number} requires manual action")
                return
            
            # Simulate step execution for auto steps
            await asyncio.sleep(1)  # Simulate processing time
            
            # Mark step as completed
            step_record["completed_at"] = datetime.now(timezone.utc).isoformat()
            step_record["status"] = "completed"
            step_record["success"] = True
            
            workflow_data["step_history"] = step_history
            campaign.workflow_data = workflow_data
            
        except Exception as e:
            logger.error(f"Error executing step {step_number}: {e}")
            campaign.workflow_state = CampaignWorkflowStateEnum.ERROR
            raise
    
    async def _pause_workflow(self, campaign: Campaign):
        """Pause workflow execution"""
        campaign.workflow_state = CampaignWorkflowStateEnum.PAUSED
        
        workflow_data = campaign.workflow_data or {}
        workflow_data["paused_at"] = datetime.now(timezone.utc).isoformat()
        campaign.workflow_data = workflow_data
        
        await self.db.commit()
        logger.info(f"Workflow paused for campaign {campaign.id}")
    
    async def _resume_workflow(self, campaign: Campaign):
        """Resume workflow execution"""
        # Determine appropriate state based on current step
        current_step = campaign.workflow_step
        campaign_type = campaign.campaign_type.value if campaign.campaign_type else "DEFAULT"
        steps = self._workflow_steps.get(campaign_type, self._workflow_steps["DEFAULT"])
        
        if current_step <= len(steps):
            step_config = steps[current_step - 1]
            campaign.workflow_state = step_config["state"]
        else:
            campaign.workflow_state = CampaignWorkflowStateEnum.COMPLETE
        
        workflow_data = campaign.workflow_data or {}
        workflow_data["resumed_at"] = datetime.now(timezone.utc).isoformat()
        campaign.workflow_data = workflow_data
        
        await self.db.commit()
        logger.info(f"Workflow resumed for campaign {campaign.id}")
    
    async def _stop_workflow(self, campaign: Campaign):
        """Stop workflow execution"""
        campaign.workflow_state = CampaignWorkflowStateEnum.ERROR
        campaign.is_workflow_complete = True
        
        workflow_data = campaign.workflow_data or {}
        workflow_data["stopped_at"] = datetime.now(timezone.utc).isoformat()
        campaign.workflow_data = workflow_data
        
        await self.db.commit()
        logger.info(f"Workflow stopped for campaign {campaign.id}")
    
    async def _skip_step(self, campaign: Campaign, step_number: Optional[int]):
        """Skip a workflow step"""
        if step_number and step_number == campaign.workflow_step:
            await self.advance_workflow(str(campaign.id))
        
    async def _retry_step(self, campaign: Campaign, step_number: Optional[int]):
        """Retry a workflow step"""
        if step_number:
            campaign.workflow_step = step_number
            campaign_type = campaign.campaign_type.value if campaign.campaign_type else "DEFAULT"
            steps = self._workflow_steps.get(campaign_type, self._workflow_steps["DEFAULT"])
            await self._execute_step(campaign, step_number, steps)
    
    async def _approve_step(self, campaign: Campaign, step_number: Optional[int]):
        """Approve a workflow step"""
        if step_number and step_number == campaign.workflow_step:
            # Mark current step as approved and advance
            workflow_data = campaign.workflow_data or {}
            step_history = workflow_data.get("step_history", [])
            
            for step_record in step_history:
                if step_record["step_number"] == step_number:
                    step_record["approved_at"] = datetime.now(timezone.utc).isoformat()
                    step_record["status"] = "approved"
                    break
            
            workflow_data["step_history"] = step_history
            campaign.workflow_data = workflow_data
            
            await self.advance_workflow(str(campaign.id))
    
    async def _reject_step(self, campaign: Campaign, step_number: Optional[int], reason: Optional[str]):
        """Reject a workflow step"""
        if step_number and step_number == campaign.workflow_step:
            workflow_data = campaign.workflow_data or {}
            step_history = workflow_data.get("step_history", [])
            
            for step_record in step_history:
                if step_record["step_number"] == step_number:
                    step_record["rejected_at"] = datetime.now(timezone.utc).isoformat()
                    step_record["status"] = "rejected"
                    step_record["rejection_reason"] = reason
                    break
            
            workflow_data["step_history"] = step_history
            campaign.workflow_data = workflow_data
            campaign.workflow_state = CampaignWorkflowStateEnum.ERROR
    
    async def _record_step_result(self, campaign: Campaign, step_result: WorkflowStepResult):
        """Record the result of a workflow step"""
        workflow_data = campaign.workflow_data or {}
        step_history = workflow_data.get("step_history", [])
        
        for step_record in step_history:
            if step_record["step_number"] == step_result.step_number:
                step_record["completed_at"] = datetime.now(timezone.utc).isoformat()
                step_record["duration"] = step_result.duration
                step_record["success"] = step_result.success
                step_record["status"] = "completed" if step_result.success else "failed"
                
                if step_result.error_message:
                    step_record["error_message"] = step_result.error_message
                
                if step_result.output_data:
                    step_record["output_data"] = step_result.output_data
                
                break
        
        workflow_data["step_history"] = step_history
        campaign.workflow_data = workflow_data
    
    def _calculate_completed_steps(self, campaign: Campaign) -> int:
        """Calculate number of completed steps"""
        workflow_data = campaign.workflow_data or {}
        step_history = workflow_data.get("step_history", [])
        
        completed_count = 0
        for step_record in step_history:
            if step_record.get("status") in ["completed", "approved"]:
                completed_count += 1
        
        return completed_count
    
    def _calculate_estimated_completion(self, campaign: Campaign) -> Optional[str]:
        """Calculate estimated completion time"""
        try:
            workflow_data = campaign.workflow_data or {}
            total_steps = workflow_data.get("total_steps", 4)
            current_step = campaign.workflow_step
            
            if campaign.is_workflow_complete:
                return None
            
            # Simple estimation based on remaining steps
            remaining_steps = total_steps - current_step
            estimated_minutes = remaining_steps * 3  # Average 3 minutes per step
            
            estimated_completion = datetime.now(timezone.utc) + timedelta(minutes=estimated_minutes)
            return estimated_completion.isoformat()
            
        except Exception:
            return None
    
    def _get_step_statuses(self, campaign: Campaign) -> List[Dict[str, Any]]:
        """Get status of all workflow steps"""
        workflow_data = campaign.workflow_data or {}
        step_history = workflow_data.get("step_history", [])
        
        # Convert to step status dictionaries
        step_statuses = []
        for step_record in step_history:
            step_statuses.append({
                "step_number": step_record.get("step_number", 0),
                "status": step_record.get("status", "pending"),
                "started_at": step_record.get("started_at"),
                "completed_at": step_record.get("completed_at"),
                "duration": step_record.get("duration", 0),
                "success": step_record.get("success", False),
                "error_message": step_record.get("error_message"),
                "output_data": step_record.get("output_data", {})
            })
        
        return step_statuses
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def get_available_workflow_types(self) -> List[str]:
        """Get list of available workflow types"""
        return list(self._workflow_steps.keys())
    
    def get_workflow_template(self, workflow_type: str) -> Optional[List[Dict[str, Any]]]:
        """Get workflow template for a specific type"""
        return self._workflow_steps.get(workflow_type)
    
    async def validate_workflow_step(
        self,
        campaign_id: Union[str, UUID],
        step_number: int
    ) -> bool:
        """Validate if a workflow step can be executed"""
        try:
            campaign_uuid = UUID(str(campaign_id)) if isinstance(campaign_id, str) else campaign_id
            
            query = select(Campaign).where(Campaign.id == campaign_uuid)
            result = await self.db.execute(query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                return False
            
            workflow_data = campaign.workflow_data or {}
            total_steps = workflow_data.get("total_steps", 4)
            
            # Step must be within valid range
            if step_number < 1 or step_number > total_steps:
                return False
            
            # Step must be current step or next step
            current_step = campaign.workflow_step
            if step_number > current_step + 1:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating workflow step: {e}")
            return False
    
    async def get_workflow_notifications(
        self,
        campaign_id: Union[str, UUID]
    ) -> List[WorkflowNotification]:
        """Get workflow notifications for a campaign"""
        try:
            campaign_uuid = UUID(str(campaign_id)) if isinstance(campaign_id, str) else campaign_id
            
            query = select(Campaign).where(Campaign.id == campaign_uuid)
            result = await self.db.execute(query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                return []
            
            notifications = []
            
            # Check for pending reviews
            if campaign.workflow_state == CampaignWorkflowStateEnum.REVIEW_REQUIRED:
                notifications.append(WorkflowNotification(
                    id=f"review_{campaign.id}_{campaign.workflow_step}",
                    campaign_id=str(campaign.id),
                    workflow_step=campaign.workflow_step,
                    notification_type="review_required",
                    title="Review Required",
                    message=f"Campaign '{campaign.display_name}' requires review at step {campaign.workflow_step}",
                    requires_action=True,
                    action_url=f"/campaigns/{campaign.id}/review",
                    created_at=datetime.now(timezone.utc).isoformat()
                ))
            
            # Check for approvals needed
            if campaign.workflow_state == CampaignWorkflowStateEnum.APPROVED:
                notifications.append(WorkflowNotification(
                    id=f"approval_{campaign.id}_{campaign.workflow_step}",
                    campaign_id=str(campaign.id),
                    workflow_step=campaign.workflow_step,
                    notification_type="approval_needed",
                    title="Approval Needed",
                    message=f"Campaign '{campaign.display_name}' needs final approval",
                    requires_action=True,
                    action_url=f"/campaigns/{campaign.id}/approve",
                    created_at=datetime.now(timezone.utc).isoformat()
                ))
            
            # Check for errors
            if campaign.workflow_state == CampaignWorkflowStateEnum.ERROR:
                notifications.append(WorkflowNotification(
                    id=f"error_{campaign.id}_{campaign.workflow_step}",
                    campaign_id=str(campaign.id),
                    workflow_step=campaign.workflow_step,
                    notification_type="workflow_failed",
                    title="Workflow Error",
                    message=f"Campaign '{campaign.display_name}' encountered an error",
                    priority="HIGH",
                    requires_action=True,
                    action_url=f"/campaigns/{campaign.id}/retry",
                    created_at=datetime.now(timezone.utc).isoformat()
                ))
            
            # Check for completed workflows
            if campaign.is_workflow_complete:
                notifications.append(WorkflowNotification(
                    id=f"complete_{campaign.id}",
                    campaign_id=str(campaign.id),
                    workflow_step=campaign.workflow_step,
                    notification_type="workflow_completed",
                    title="Workflow Complete",
                    message=f"Campaign '{campaign.display_name}' workflow completed successfully",
                    requires_action=False,
                    created_at=datetime.now(timezone.utc).isoformat()
                ))
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error getting workflow notifications: {e}")
            return []
    
    async def cleanup_completed_workflows(
        self,
        older_than_days: int = 30
    ) -> int:
        """Clean up old completed workflow data"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)
            
            query = select(Campaign).where(
                and_(
                    Campaign.is_workflow_complete == True,
                    Campaign.completed_at < cutoff_date
                )
            )
            
            result = await self.db.execute(query)
            completed_campaigns = list(result.scalars().all())
            
            cleanup_count = 0
            for campaign in completed_campaigns:
                # Clear detailed workflow data but keep basic info
                if campaign.workflow_data:
                    workflow_data = campaign.workflow_data
                    # Keep only essential data
                    essential_data = {
                        "started_at": workflow_data.get("started_at"),
                        "completed_at": workflow_data.get("completed_at"),
                        "total_steps": workflow_data.get("total_steps"),
                        "cleaned_up": True,
                        "cleanup_date": datetime.now(timezone.utc).isoformat()
                    }
                    campaign.workflow_data = essential_data
                    cleanup_count += 1
            
            if cleanup_count > 0:
                await self.db.commit()
                logger.info(f"Cleaned up {cleanup_count} completed workflows")
            
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Error cleaning up workflows: {e}")
            return 0
    
    # ============================================================================
    # INTEGRATION METHODS
    # ============================================================================
    
    async def trigger_intelligence_analysis(
        self,
        campaign_id: Union[str, UUID]
    ) -> bool:
        """Trigger intelligence analysis for a campaign"""
        try:
            # This would integrate with the Intelligence Engine module
            # For now, simulate the process
            logger.info(f"Triggering intelligence analysis for campaign {campaign_id}")
            
            # Simulate analysis time
            await asyncio.sleep(2)
            
            # Update campaign intelligence status
            campaign_uuid = UUID(str(campaign_id)) if isinstance(campaign_id, str) else campaign_id
            query = select(Campaign).where(Campaign.id == campaign_uuid)
            result = await self.db.execute(query)
            campaign = result.scalar_one_or_none()
            
            if campaign:
                campaign.intelligence_status = "completed"
                campaign.intelligence_count = (campaign.intelligence_count or 0) + 1
                await self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error triggering intelligence analysis: {e}")
            return False
    
    async def trigger_content_generation(
        self,
        campaign_id: Union[str, UUID],
        content_type: str = "email"
    ) -> bool:
        """Trigger content generation for a campaign"""
        try:
            # This would integrate with the Content Generation module
            # For now, simulate the process
            logger.info(f"Triggering {content_type} content generation for campaign {campaign_id}")
            
            # Simulate generation time
            await asyncio.sleep(3)
            
            # Update campaign content count
            campaign_uuid = UUID(str(campaign_id)) if isinstance(campaign_id, str) else campaign_id
            query = select(Campaign).where(Campaign.id == campaign_uuid)
            result = await self.db.execute(query)
            campaign = result.scalar_one_or_none()
            
            if campaign:
                campaign.generated_content_count = (campaign.generated_content_count or 0) + 1
                await self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error triggering content generation: {e}")
            return False
    
    # ============================================================================
    # BATCH OPERATIONS
    # ============================================================================
    
    async def get_all_active_workflows(
        self,
        company_id: Optional[Union[str, UUID]] = None
    ) -> List[WorkflowProgress]:
        """Get all active workflows"""
        try:
            query = select(Campaign).where(
                and_(
                    Campaign.is_workflow_complete == False,
                    Campaign.workflow_state != CampaignWorkflowStateEnum.ERROR
                )
            )
            
            if company_id:
                company_uuid = UUID(str(company_id)) if isinstance(company_id, str) else company_id
                query = query.where(Campaign.company_id == company_uuid)
            
            result = await self.db.execute(query)
            campaigns = list(result.scalars().all())
            
            workflows = []
            for campaign in campaigns:
                progress = await self.get_workflow_progress(str(campaign.id))
                workflows.append(progress)
            
            return workflows
            
        except Exception as e:
            logger.error(f"Error getting active workflows: {e}")
            return []
    
    async def pause_all_workflows(
        self,
        company_id: Union[str, UUID]
    ) -> int:
        """Pause all active workflows for a company"""
        try:
            company_uuid = UUID(str(company_id)) if isinstance(company_id, str) else company_id
            
            query = select(Campaign).where(
                and_(
                    Campaign.company_id == company_uuid,
                    Campaign.is_workflow_complete == False,
                    Campaign.workflow_state != CampaignWorkflowStateEnum.PAUSED,
                    Campaign.workflow_state != CampaignWorkflowStateEnum.ERROR
                )
            )
            
            result = await self.db.execute(query)
            campaigns = list(result.scalars().all())
            
            paused_count = 0
            for campaign in campaigns:
                await self._pause_workflow(campaign)
                paused_count += 1
            
            logger.info(f"Paused {paused_count} workflows for company {company_id}")
            return paused_count
            
        except Exception as e:
            logger.error(f"Error pausing workflows: {e}")
            return 0
    
    async def resume_all_workflows(
        self,
        company_id: Union[str, UUID]
    ) -> int:
        """Resume all paused workflows for a company"""
        try:
            company_uuid = UUID(str(company_id)) if isinstance(company_id, str) else company_id
            
            query = select(Campaign).where(
                and_(
                    Campaign.company_id == company_uuid,
                    Campaign.workflow_state == CampaignWorkflowStateEnum.PAUSED
                )
            )
            
            result = await self.db.execute(query)
            campaigns = list(result.scalars().all())
            
            resumed_count = 0
            for campaign in campaigns:
                await self._resume_workflow(campaign)
                resumed_count += 1
            
            logger.info(f"Resumed {resumed_count} workflows for company {company_id}")
            return resumed_count
            
        except Exception as e:
            logger.error(f"Error resuming workflows: {e}")
            return 0