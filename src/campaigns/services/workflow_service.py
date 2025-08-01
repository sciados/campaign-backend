# src/campaigns/services/workflow_service.py
"""
Workflow Service - 2-step workflow logic and progress management
🎯 HANDLES: Workflow state transitions, progress calculation, intelligence aggregation
Following intelligence/handlers/ pattern for workflow functionality
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm.attributes import flag_modified

from src.models import Campaign
from src.models.campaign import CampaignWorkflowState, AutoAnalysisStatus
from src.models.intelligence import CampaignIntelligence
from src.campaigns.schemas.workflow_schemas import WorkflowProgressData
from src.utils.demo_campaign_seeder import is_demo_campaign

logger = logging.getLogger(__name__)


class WorkflowService:
    """
    Workflow service handling 2-step workflow logic
    🎯 INCLUDES: State management, progress calculation, intelligence aggregation
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ========================================================================
    # WORKFLOW STATE MANAGEMENT
    # ========================================================================
    
    async def get_workflow_state(self, campaign_id: UUID, company_id: UUID) -> Optional[Dict[str, Any]]:
        """Get detailed workflow state and progress for a campaign"""
        try:
            logger.info(f"Getting workflow state for campaign {campaign_id}")
            
            # Get campaign
            query = select(Campaign).where(
                Campaign.id == campaign_id,
                Campaign.company_id == company_id
            )
            
            result = await self.db.execute(query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                return None
            
            # Get related data counts
            intelligence_count = campaign.intelligence_extracted or 0
            content_count = campaign.content_generated or 0
            sources_count = campaign.sources_count or 0
            
            # Determine workflow state
            workflow_state = campaign.workflow_state.value if hasattr(campaign.workflow_state, 'value') else "BASIC_SETUP"
            
            # Calculate completion percentage
            completion_percentage = self._calculate_completion_percentage(campaign, workflow_state)
            
            # Determine next steps based on auto-analysis status
            next_steps = self._get_next_steps(campaign)
            
            # Auto-analysis info
            auto_analysis_info = self._get_auto_analysis_info(campaign)
            
            # Current step calculation
            current_step = 1
            auto_status = campaign.auto_analysis_status.value if hasattr(campaign.auto_analysis_status, 'value') else "PENDING"
            if auto_status == "COMPLETED":
                current_step = 2
            
            return {
                "campaign_id": str(campaign.id),
                "workflow_state": workflow_state.lower(),
                "completion_percentage": completion_percentage,
                "total_steps": 2,
                "current_step": current_step,
                
                # Progress metrics
                "metrics": {
                    "sources_count": sources_count,
                    "intelligence_count": intelligence_count,
                    "content_count": content_count
                },
                
                # Auto-analysis info
                "auto_analysis": auto_analysis_info,
                
                # Next recommended actions
                "next_steps": next_steps,
                
                # Workflow capabilities
                "can_analyze": bool(campaign.salespage_url and campaign.salespage_url.strip()),
                "can_generate_content": auto_status == "COMPLETED",
                "is_demo": is_demo_campaign(campaign),
                
                # Step states from campaign
                "step_states": campaign.step_states or {},
                
                # Timestamps
                "created_at": campaign.created_at.isoformat(),
                "updated_at": campaign.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow state: {e}")
            raise e
    
    async def save_workflow_progress(
        self, 
        campaign_id: UUID, 
        company_id: UUID, 
        progress_data: WorkflowProgressData
    ) -> Optional[Dict[str, Any]]:
        """Save workflow progress with timezone and async fixes"""
        try:
            logger.info(f"Saving workflow progress for campaign {campaign_id}")
            
            # Get campaign
            query = select(Campaign).where(
                Campaign.id == campaign_id,
                Campaign.company_id == company_id
            )
            
            result = await self.db.execute(query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                return None
            
            # Create timezone-aware datetime once
            now_utc = datetime.now(timezone.utc)
            
            # Update workflow state if provided
            if progress_data.workflow_state:
                self._update_workflow_state(campaign, progress_data.workflow_state)
            
            # Update auto-analysis settings if provided
            if progress_data.auto_analysis_enabled is not None:
                campaign.auto_analysis_enabled = progress_data.auto_analysis_enabled
                logger.info(f"Updated auto_analysis_enabled to: {progress_data.auto_analysis_enabled}")
                
            if progress_data.generate_content_after_analysis is not None:
                campaign.generate_content_after_analysis = progress_data.generate_content_after_analysis
                logger.info(f"Updated generate_content_after_analysis to: {progress_data.generate_content_after_analysis}")
            
            # Store step data in campaign settings
            if progress_data.step_data:
                self._store_step_data(campaign, progress_data.step_data, now_utc)
            
            # Update step states if available on the model
            if hasattr(campaign, 'step_states') and campaign.step_states:
                self._update_step_states(campaign)
            
            # Update timestamps
            campaign.updated_at = now_utc
            
            # Update last activity
            if hasattr(campaign, 'last_activity'):
                campaign.last_activity = now_utc
            
            # Commit changes
            await self.db.commit()
            await self.db.refresh(campaign)
            
            # Calculate updated completion percentage
            completion_percentage = self._calculate_completion_percentage(
                campaign, 
                campaign.workflow_state.value if hasattr(campaign.workflow_state, 'value') else "BASIC_SETUP"
            )
            
            logger.info(f"✅ Workflow progress saved for campaign {campaign_id}")
            
            return {
                "success": True,
                "message": "Workflow progress saved successfully",
                "campaign_id": str(campaign_id),
                "updated_workflow_state": campaign.workflow_state.value if hasattr(campaign.workflow_state, 'value') else progress_data.workflow_state,
                "completion_percentage": completion_percentage,
                "step_states": campaign.step_states if hasattr(campaign, 'step_states') else {},
                "auto_analysis_status": campaign.auto_analysis_status.value if hasattr(campaign.auto_analysis_status, 'value') else "pending",
                "updated_at": campaign.updated_at.isoformat(),
                "last_activity": campaign.last_activity.isoformat() if hasattr(campaign, 'last_activity') and campaign.last_activity else None,
                "is_demo": is_demo_campaign(campaign)
            }
            
        except Exception as e:
            logger.error(f"Error saving workflow progress: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            await self.db.rollback()
            raise e
    
    # ========================================================================
    # INTELLIGENCE AGGREGATION
    # ========================================================================
    
    async def get_campaign_intelligence(
        self, 
        campaign_id: UUID, 
        company_id: UUID,
        skip: int = 0,
        limit: int = 50,
        intelligence_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get intelligence entries for a campaign"""
        try:
            # Verify campaign ownership
            campaign_query = select(Campaign).where(
                Campaign.id == campaign_id,
                Campaign.company_id == company_id
            )
            campaign_result = await self.db.execute(campaign_query)
            campaign = campaign_result.scalar_one_or_none()
            
            if not campaign:
                raise ValueError("Campaign not found")
            
            # Build intelligence query
            intelligence_query = select(CampaignIntelligence).where(
                CampaignIntelligence.campaign_id == campaign_id
            )
            
            # Add type filter if specified
            if intelligence_type:
                intelligence_query = intelligence_query.where(
                    CampaignIntelligence.source_type == intelligence_type
                )
            
            # Add pagination and ordering
            intelligence_query = intelligence_query.offset(skip).limit(limit).order_by(
                CampaignIntelligence.created_at.desc()
            )
            
            # Execute query
            result = await self.db.execute(intelligence_query)
            intelligence_entries = result.scalars().all()
            
            # Format intelligence data
            intelligence_data = []
            for entry in intelligence_entries:
                try:
                    # Parse stored JSON intelligence data
                    offer_intel = self._parse_json_field(getattr(entry, 'offer_intelligence', None))
                    psychology_intel = self._parse_json_field(getattr(entry, 'psychology_intelligence', None))
                    
                    intelligence_data.append({
                        "id": str(entry.id),
                        "source_type": entry.source_type.value if hasattr(entry.source_type, 'value') else str(entry.source_type),
                        "source_url": getattr(entry, 'source_url', None),
                        "source_title": getattr(entry, 'source_title', None),
                        "confidence_score": getattr(entry, 'confidence_score', 0.0) or 0.0,
                        "analysis_status": entry.analysis_status.value if hasattr(entry.analysis_status, 'value') else str(entry.analysis_status),
                        "offer_intelligence": offer_intel,
                        "psychology_intelligence": psychology_intel,
                        "processing_metadata": self._parse_json_field(getattr(entry, 'processing_metadata', None)),
                        "created_at": entry.created_at.isoformat(),
                        "updated_at": entry.updated_at.isoformat() if hasattr(entry, 'updated_at') else None
                    })
                except Exception as entry_error:
                    logger.warning(f"Error processing intelligence entry {entry.id}: {entry_error}")
                    continue
            
            # Get summary stats
            total_query = select(func.count(CampaignIntelligence.id)).where(
                CampaignIntelligence.campaign_id == campaign_id
            )
            total_result = await self.db.execute(total_query)
            total_intelligence = total_result.scalar() or 0
            
            # Get available source types
            types_query = select(CampaignIntelligence.source_type).where(
                CampaignIntelligence.campaign_id == campaign_id
            ).distinct()
            types_result = await self.db.execute(types_query)
            available_types = []
            for row in types_result.fetchall():
                source_type = row[0]
                if hasattr(source_type, 'value'):
                    available_types.append(source_type.value)
                else:
                    available_types.append(str(source_type))
            
            return {
                "campaign_id": str(campaign_id),
                "intelligence_entries": intelligence_data,
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "total": total_intelligence,
                    "returned": len(intelligence_data)
                },
                "summary": {
                    "total_intelligence_entries": total_intelligence,
                    "available_types": available_types,
                    "campaign_title": campaign.title,
                    "auto_analysis_status": campaign.auto_analysis_status.value if hasattr(campaign.auto_analysis_status, 'value') else "pending",
                    "analysis_confidence_score": campaign.analysis_confidence_score or 0.0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign intelligence: {e}")
            raise e
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    def _calculate_completion_percentage(self, campaign: Campaign, workflow_state: str) -> float:
        """Calculate completion percentage based on workflow state"""
        try:
            if hasattr(campaign, 'calculate_completion_percentage'):
                return campaign.calculate_completion_percentage()
            else:
                # Fallback calculation
                state_percentages = {
                    "BASIC_SETUP": 25.0,
                    "ANALYZING_SOURCES": 50.0,
                    "ANALYSIS_COMPLETE": 75.0,
                    "GENERATING_CONTENT": 85.0,
                    "CAMPAIGN_COMPLETE": 100.0
                }
                return state_percentages.get(workflow_state, 25.0)
        except Exception as e:
            logger.warning(f"Error calculating completion percentage: {e}")
            return 25.0
    
    def _get_next_steps(self, campaign: Campaign) -> List[Dict[str, Any]]:
        """Determine next steps based on campaign state"""
        next_steps = []
        auto_status = campaign.auto_analysis_status.value if hasattr(campaign.auto_analysis_status, 'value') else "PENDING"
        content_count = campaign.content_generated or 0
        
        if auto_status == "PENDING":
            if campaign.salespage_url:
                next_steps.append({
                    "action": "analyze_url",
                    "label": "Analyze Sales Page",
                    "description": "Run competitor analysis on your sales page",
                    "priority": "high"
                })
            else:
                next_steps.append({
                    "action": "add_url",
                    "label": "Add Sales Page URL",
                    "description": "Add your competitor's sales page for analysis",
                    "priority": "high"
                })
        elif auto_status == "IN_PROGRESS":
            next_steps.append({
                "action": "wait_analysis",
                "label": "Analysis In Progress",
                "description": "Auto-analysis is running - please wait",
                "priority": "info"
            })
        elif auto_status == "COMPLETED" and content_count == 0:
            next_steps.append({
                "action": "generate_content",
                "label": "Generate Content",
                "description": "Create marketing content based on analysis",
                "priority": "high"
            })
        elif auto_status == "FAILED":
            next_steps.append({
                "action": "retry_analysis",
                "label": "Retry Analysis",
                "description": "Fix issues and retry the analysis",
                "priority": "high"
            })
        
        return next_steps
    
    def _get_auto_analysis_info(self, campaign: Campaign) -> Dict[str, Any]:
        """Get auto-analysis information"""
        auto_status = campaign.auto_analysis_status.value if hasattr(campaign.auto_analysis_status, 'value') else "PENDING"
        
        return {
            "enabled": getattr(campaign, 'auto_analysis_enabled', False),
            "status": auto_status,
            "confidence_score": getattr(campaign, 'analysis_confidence_score', 0.0) or 0.0,
            "url": getattr(campaign, 'salespage_url', None),
            "started_at": campaign.auto_analysis_started_at.isoformat() if campaign.auto_analysis_started_at else None,
            "completed_at": campaign.auto_analysis_completed_at.isoformat() if campaign.auto_analysis_completed_at else None,
            "error_message": getattr(campaign, 'auto_analysis_error', None)
        }
    
    def _update_workflow_state(self, campaign: Campaign, workflow_state: str):
        """Update workflow state with proper enum handling"""
        try:
            # Map to correct enum values 
            valid_states = {
                "basic_setup": "BASIC_SETUP",
                "auto_analyzing": "ANALYZING_SOURCES", 
                "analysis_complete": "ANALYSIS_COMPLETE",
                "generating_content": "GENERATING_CONTENT",
                "campaign_complete": "CAMPAIGN_COMPLETE"
            }
            
            # Normalize the state name
            state_key = workflow_state.lower()
            if state_key in valid_states:
                enum_value = valid_states[state_key]
                
                if hasattr(campaign, 'workflow_state'):
                    try:
                        campaign.workflow_state = CampaignWorkflowState(enum_value)
                        logger.info(f"Updated workflow state to: {enum_value}")
                    except (ValueError, AttributeError) as enum_error:
                        logger.warning(f"Enum update failed: {enum_error}, storing in settings")
                        # Store in settings as fallback
                        if not campaign.settings:
                            campaign.settings = {}
                        campaign.settings["workflow_state"] = enum_value
                        flag_modified(campaign, 'settings')
                else:
                    logger.warning("Campaign model doesn't have workflow_state attribute")
            else:
                logger.warning(f"Invalid workflow state: {workflow_state}")
                
        except Exception as state_error:
            logger.warning(f"Error updating workflow state: {state_error}")
    
    def _store_step_data(self, campaign: Campaign, step_data: Dict[str, Any], now_utc: datetime):
        """Store step data in campaign settings"""
        if not campaign.settings:
            campaign.settings = {}
        
        if "workflow_progress" not in campaign.settings:
            campaign.settings["workflow_progress"] = {}
            
        # Merge step data
        campaign.settings["workflow_progress"].update(step_data)
        campaign.settings["workflow_progress"]["last_updated"] = now_utc.isoformat()
        
        # Mark settings as modified
        flag_modified(campaign, 'settings')
        
        logger.info(f"Stored step data: {list(step_data.keys())}")
    
    def _update_step_states(self, campaign: Campaign):
        """Update step states based on workflow state"""
        # Update step progress based on workflow state
        current_state = campaign.workflow_state.value if hasattr(campaign.workflow_state, 'value') else "BASIC_SETUP"
        
        if current_state in ["ANALYZING_SOURCES"]:
            campaign.step_states["step_1"]["status"] = "analyzing"
            campaign.step_states["step_1"]["progress"] = 50
        elif current_state in ["ANALYSIS_COMPLETE"]:
            campaign.step_states["step_1"]["status"] = "completed"
            campaign.step_states["step_1"]["progress"] = 100
            campaign.step_states["step_2"]["status"] = "available"
        elif current_state in ["GENERATING_CONTENT"]:
            campaign.step_states["step_2"]["status"] = "active"
            campaign.step_states["step_2"]["progress"] = 50
        elif current_state in ["CAMPAIGN_COMPLETE"]:
            campaign.step_states["step_2"]["status"] = "completed"
            campaign.step_states["step_2"]["progress"] = 100
        
        # Mark step_states as modified
        flag_modified(campaign, 'step_states')
    
    def _parse_json_field(self, field_value):
        """Helper to parse JSON fields safely"""
        if field_value is None:
            return {}
        
        if isinstance(field_value, str):
            try:
                return json.loads(field_value)
            except (json.JSONDecodeError, ValueError):
                return {"raw_value": field_value}
        
        if isinstance(field_value, dict):
            return field_value
        
        return {"value": str(field_value)}