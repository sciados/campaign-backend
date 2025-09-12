# src/campaigns/workflows/campaign_workflows.py

import select
from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import asyncio

from src.campaigns.models.campaign import Campaign, CampaignWorkflowStateEnum, CampaignTypeEnum
from src.campaigns.services.workflow_service import WorkflowService
from src.campaigns.schemas.workflow import WorkflowProgress, WorkflowAction

logger = logging.getLogger(__name__)

class CampaignWorkflowEngine:
    """
    Main workflow engine for campaign automation
    Orchestrates workflow execution across different campaign types
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.workflow_service = WorkflowService(db)
        self._active_workflows: Dict[str, Dict[str, Any]] = {}
        
    # ============================================================================
    # PUBLIC WORKFLOW ORCHESTRATION METHODS
    # ============================================================================
    
    async def initialize_campaign_workflow(
        self,
        campaign: Campaign,
        auto_start: bool = True
    ) -> WorkflowProgress:
        """Initialize workflow for a new campaign"""
        try:
            logger.info(f"Initializing workflow for campaign {campaign.id}")
            
            campaign_type = campaign.campaign_type.value if campaign.campaign_type else "DEFAULT"
            
            # Register workflow in active workflows
            self._active_workflows[str(campaign.id)] = {
                "campaign_id": str(campaign.id),
                "campaign_type": campaign_type,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "status": "initializing"
            }
            
            if auto_start:
                progress = await self.workflow_service.start_workflow(
                    campaign_id=campaign.id,
                    campaign_type=campaign_type,
                    auto_proceed=True
                )
                
                self._active_workflows[str(campaign.id)]["status"] = "running"
                return progress
            else:
                # Just initialize without starting
                campaign.workflow_state = CampaignWorkflowStateEnum.INITIAL
                campaign.workflow_step = 0
                campaign.completion_percentage = 0
                campaign.workflow_data = {
                    "initialized_at": datetime.now(timezone.utc).isoformat(),
                    "auto_start": False
                }
                
                await self.db.commit()
                return await self.workflow_service.get_workflow_progress(campaign.id)
                
        except Exception as e:
            logger.error(f"Error initializing campaign workflow: {e}")
            raise
    
    async def execute_workflow_step(
        self,
        campaign_id: Union[str, UUID],
        step_type: str = "auto"
    ) -> WorkflowProgress:
        """Execute next workflow step for a campaign"""
        try:
            logger.info(f"Executing workflow step for campaign {campaign_id}")
            
            # Get current progress
            progress = await self.workflow_service.get_workflow_progress(campaign_id)
            
            if progress.is_complete:
                logger.info(f"Workflow already complete for campaign {campaign_id}")
                return progress
            
            if progress.has_errors:
                logger.warning(f"Workflow has errors for campaign {campaign_id}")
                return progress
            
            # Execute based on step type
            if step_type == "auto":
                return await self._execute_auto_step(campaign_id, progress)
            elif step_type == "manual":
                return await self._execute_manual_step(campaign_id, progress)
            elif step_type == "intelligence":
                return await self._execute_intelligence_step(campaign_id, progress)
            elif step_type == "content":
                return await self._execute_content_step(campaign_id, progress)
            elif step_type == "review":
                return await self._execute_review_step(campaign_id, progress)
            else:
                raise ValueError(f"Unknown step type: {step_type}")
                
        except Exception as e:
            logger.error(f"Error executing workflow step: {e}")
            raise
    
    async def handle_workflow_action(
        self,
        campaign_id: Union[str, UUID],
        action: WorkflowAction
    ) -> WorkflowProgress:
        """Handle workflow action (pause, resume, approve, etc.)"""
        try:
            logger.info(f"Handling workflow action {action.action_type} for campaign {campaign_id}")
            
            # Update active workflows tracking
            campaign_str = str(campaign_id)
            if campaign_str in self._active_workflows:
                self._active_workflows[campaign_str]["last_action"] = action.action_type
                self._active_workflows[campaign_str]["last_action_time"] = datetime.now(timezone.utc).isoformat()
            
            # Execute the action
            progress = await self.workflow_service.execute_workflow_action(campaign_id, action)
            
            # Update status based on action
            if campaign_str in self._active_workflows:
                if action.action_type == "pause":
                    self._active_workflows[campaign_str]["status"] = "paused"
                elif action.action_type == "resume":
                    self._active_workflows[campaign_str]["status"] = "running"
                elif action.action_type == "stop":
                    self._active_workflows[campaign_str]["status"] = "stopped"
                elif action.action_type in ["approve", "reject"]:
                    self._active_workflows[campaign_str]["status"] = "waiting_action"
            
            return progress
            
        except Exception as e:
            logger.error(f"Error handling workflow action: {e}")
            raise
    
    async def monitor_active_workflows(self) -> Dict[str, Any]:
        """Monitor all active workflows and return status"""
        try:
            logger.info("Monitoring active workflows")
            
            active_count = 0
            paused_count = 0
            error_count = 0
            completed_count = 0
            
            workflow_statuses = []
            
            for campaign_id, workflow_info in self._active_workflows.items():
                try:
                    progress = await self.workflow_service.get_workflow_progress(campaign_id)
                    
                    status_info = {
                        "campaign_id": campaign_id,
                        "current_step": progress.current_step,
                        "total_steps": progress.total_steps,
                        "completion_percentage": progress.completion_percentage,
                        "is_complete": progress.is_complete,
                        "is_paused": progress.is_paused,
                        "has_errors": progress.has_errors,
                        "workflow_info": workflow_info
                    }
                    
                    workflow_statuses.append(status_info)
                    
                    # Count statuses
                    if progress.is_complete:
                        completed_count += 1
                    elif progress.has_errors:
                        error_count += 1
                    elif progress.is_paused:
                        paused_count += 1
                    else:
                        active_count += 1
                        
                except Exception as e:
                    logger.error(f"Error monitoring workflow {campaign_id}: {e}")
                    error_count += 1
            
            # Clean up completed workflows from tracking
            await self._cleanup_completed_workflows()
            
            return {
                "total_workflows": len(self._active_workflows),
                "active_workflows": active_count,
                "paused_workflows": paused_count,
                "error_workflows": error_count,
                "completed_workflows": completed_count,
                "workflow_statuses": workflow_statuses,
                "monitoring_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error monitoring workflows: {e}")
            return {"error": str(e)}
    
    # ============================================================================
    # PRIVATE WORKFLOW EXECUTION METHODS
    # ============================================================================
    
    async def _execute_auto_step(
        self,
        campaign_id: Union[str, UUID],
        progress: WorkflowProgress
    ) -> WorkflowProgress:
        """Execute automatic workflow step"""
        try:
            # Auto steps should advance automatically
            return await self.workflow_service.advance_workflow(campaign_id)
            
        except Exception as e:
            logger.error(f"Error executing auto step: {e}")
            raise
    
    async def _execute_manual_step(
        self,
        campaign_id: Union[str, UUID],
        progress: WorkflowProgress
    ) -> WorkflowProgress:
        """Execute manual workflow step (requires human intervention)"""
        try:
            # Manual steps wait for explicit approval
            logger.info(f"Manual step {progress.current_step} requires human intervention")
            
            # Update workflow to indicate waiting for manual action
            campaign_str = str(campaign_id)
            if campaign_str in self._active_workflows:
                self._active_workflows[campaign_str]["status"] = "waiting_manual"
                self._active_workflows[campaign_str]["waiting_since"] = datetime.now(timezone.utc).isoformat()
            
            return progress
            
        except Exception as e:
            logger.error(f"Error executing manual step: {e}")
            raise
    
    async def _execute_intelligence_step(
        self,
        campaign_id: Union[str, UUID],
        progress: WorkflowProgress
    ) -> WorkflowProgress:
        """Execute intelligence analysis step"""
        try:
            logger.info(f"Executing intelligence analysis for campaign {campaign_id}")
            
            # Trigger intelligence analysis
            success = await self.workflow_service.trigger_intelligence_analysis(campaign_id)
            
            if success:
                # Advance workflow
                return await self.workflow_service.advance_workflow(campaign_id)
            else:
                # Handle intelligence failure
                error_action = WorkflowAction(
                    action_type="pause",
                    reason="Intelligence analysis failed"
                )
                return await self.workflow_service.execute_workflow_action(campaign_id, error_action)
                
        except Exception as e:
            logger.error(f"Error executing intelligence step: {e}")
            raise
    
    async def _execute_content_step(
        self,
        campaign_id: Union[str, UUID],
        progress: WorkflowProgress
    ) -> WorkflowProgress:
        """Execute content generation step"""
        try:
            logger.info(f"Executing content generation for campaign {campaign_id}")
            
            # Get campaign to determine content type
            campaign_uuid = UUID(str(campaign_id))
            query = select(Campaign).where(Campaign.id == campaign_uuid)
            result = await self.db.execute(query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            # Determine content type based on campaign type
            content_type = "email"  # default
            if campaign.campaign_type == CampaignTypeEnum.SOCIAL_MEDIA:
                content_type = "social_media"
            elif campaign.campaign_type == CampaignTypeEnum.CONTENT_MARKETING:
                content_type = "blog_content"
            elif campaign.campaign_type == CampaignTypeEnum.AFFILIATE_PROMOTION:
                content_type = "promotional"
            elif campaign.campaign_type == CampaignTypeEnum.PRODUCT_LAUNCH:
                content_type = "launch_materials"
            
            # Trigger content generation
            success = await self.workflow_service.trigger_content_generation(
                campaign_id, content_type
            )
            
            if success:
                return await self.workflow_service.advance_workflow(campaign_id)
            else:
                # Handle content generation failure
                error_action = WorkflowAction(
                    action_type="pause",
                    reason="Content generation failed"
                )
                return await self.workflow_service.execute_workflow_action(campaign_id, error_action)
                
        except Exception as e:
            logger.error(f"Error executing content step: {e}")
            raise
    
    async def _execute_review_step(
        self,
        campaign_id: Union[str, UUID],
        progress: WorkflowProgress
    ) -> WorkflowProgress:
        """Execute review step (requires approval)"""
        try:
            logger.info(f"Executing review step for campaign {campaign_id}")
            
            # Review steps require manual approval
            campaign_str = str(campaign_id)
            if campaign_str in self._active_workflows:
                self._active_workflows[campaign_str]["status"] = "waiting_review"
                self._active_workflows[campaign_str]["review_requested"] = datetime.now(timezone.utc).isoformat()
            
            return progress
            
        except Exception as e:
            logger.error(f"Error executing review step: {e}")
            raise
    
    async def _cleanup_completed_workflows(self):
        """Clean up completed workflows from active tracking"""
        try:
            completed_campaigns = []
            
            for campaign_id in list(self._active_workflows.keys()):
                try:
                    progress = await self.workflow_service.get_workflow_progress(campaign_id)
                    
                    if progress.is_complete:
                        completed_campaigns.append(campaign_id)
                        
                except Exception as e:
                    logger.error(f"Error checking workflow completion for {campaign_id}: {e}")
            
            # Remove completed workflows from tracking
            for campaign_id in completed_campaigns:
                if campaign_id in self._active_workflows:
                    logger.info(f"Removing completed workflow {campaign_id} from active tracking")
                    del self._active_workflows[campaign_id]
                    
        except Exception as e:
            logger.error(f"Error cleaning up completed workflows: {e}")
    
    # ============================================================================
    # WORKFLOW TEMPLATE MANAGEMENT
    # ============================================================================
    
    def get_available_workflow_types(self) -> List[str]:
        """Get list of available workflow types"""
        return self.workflow_service.get_available_workflow_types()
    
    def get_workflow_template(self, campaign_type: str) -> Optional[List[Dict[str, Any]]]:
        """Get workflow template for campaign type"""
        return self.workflow_service.get_workflow_template(campaign_type)
    
    async def validate_workflow_configuration(
        self,
        campaign: Campaign
    ) -> Dict[str, Any]:
        """Validate workflow configuration for campaign"""
        try:
            campaign_type = campaign.campaign_type.value if campaign.campaign_type else "DEFAULT"
            template = self.get_workflow_template(campaign_type)
            
            if not template:
                return {
                    "valid": False,
                    "error": f"No workflow template found for type: {campaign_type}"
                }
            
            # Check if campaign has required data for workflow
            validation_results = {
                "valid": True,
                "campaign_type": campaign_type,
                "total_steps": len(template),
                "requirements_met": True,
                "missing_requirements": []
            }
            
            # Check basic requirements
            if not campaign.name:
                validation_results["requirements_met"] = False
                validation_results["missing_requirements"].append("Campaign name/title required")
            
            if not campaign.campaign_type:
                validation_results["requirements_met"] = False
                validation_results["missing_requirements"].append("Campaign type required")
            
            validation_results["valid"] = validation_results["requirements_met"]
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating workflow configuration: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    # ============================================================================
    # BATCH WORKFLOW OPERATIONS
    # ============================================================================
    
    async def start_multiple_workflows(
        self,
        campaign_ids: List[Union[str, UUID]]
    ) -> Dict[str, Any]:
        """Start workflows for multiple campaigns"""
        try:
            results = {
                "started": [],
                "failed": [],
                "already_running": []
            }
            
            for campaign_id in campaign_ids:
                try:
                    campaign_str = str(campaign_id)
                    
                    # Check if already running
                    if campaign_str in self._active_workflows:
                        results["already_running"].append(campaign_str)
                        continue
                    
                    # Get campaign
                    campaign_uuid = UUID(campaign_str)
                    query = select(Campaign).where(Campaign.id == campaign_uuid)
                    result = await self.db.execute(query)
                    campaign = result.scalar_one_or_none()
                    
                    if campaign:
                        await self.initialize_campaign_workflow(campaign, auto_start=True)
                        results["started"].append(campaign_str)
                    else:
                        results["failed"].append({
                            "campaign_id": campaign_str,
                            "error": "Campaign not found"
                        })
                        
                except Exception as e:
                    results["failed"].append({
                        "campaign_id": str(campaign_id),
                        "error": str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error starting multiple workflows: {e}")
            return {"error": str(e)}
    
    async def pause_all_active_workflows(self) -> Dict[str, Any]:
        """Pause all currently active workflows"""
        try:
            results = {
                "paused": [],
                "failed": []
            }
            
            for campaign_id in list(self._active_workflows.keys()):
                try:
                    action = WorkflowAction(action_type="pause", reason="Batch pause operation")
                    await self.handle_workflow_action(campaign_id, action)
                    results["paused"].append(campaign_id)
                    
                except Exception as e:
                    results["failed"].append({
                        "campaign_id": campaign_id,
                        "error": str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error pausing all workflows: {e}")
            return {"error": str(e)}