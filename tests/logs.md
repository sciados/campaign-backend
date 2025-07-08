@router.get("", response_model=List[CampaignResponse])
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all campaigns for the current user's company"""
    try:
        logger.info(f"Getting campaigns for user {current_user.id}, company {current_user.company_id}")
        
        # Build query for FULL Campaign objects (not just specific columns)
        query = select(Campaign).where(Campaign.company_id == current_user.company_id)
        
        # Add status filter if provided
        if status:
            try:
                status_enum = normalize_campaign_status(status)
                query = query.where(Campaign.status == status_enum)
                logger.info(f"Applied status filter: {status}")
            except Exception as status_error:
                logger.warning(f"Invalid status filter '{status}': {status_error}")
                # Don't fail the request, just ignore the filter
        
        # Add pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        campaigns = result.scalars().all()
        
        logger.info(f"Found {len(campaigns)} campaigns")
        
        # Convert to response format with proper error handling
        campaign_responses = []
        for campaign in campaigns:
            try:
                # Safely handle status enum
                try:
                    if hasattr(campaign.status, 'value'):
                        status_value = campaign.status.value
                    else:
                        status_value = str(campaign.status)
                except (AttributeError, TypeError):
                    status_value = "draft"  # Default fallback
                
                # Safely calculate completion percentage
                try:
                    completion_percentage = campaign.calculate_completion_percentage()
                except (AttributeError, TypeError, Exception):
                    completion_percentage = 25.0  # Default fallback
                
                # Safely get workflow state
                try:
                    if hasattr(campaign.workflow_state, 'value'):
                        workflow_state = campaign.workflow_state.value
                    else:
                        workflow_state = str(campaign.workflow_state) if campaign.workflow_state else "basic_setup"
                except (AttributeError, TypeError):
                    workflow_state = "basic_setup"
                
                # Create response object with safe field access
                campaign_response = CampaignResponse(
                    id=str(campaign.id),
                    title=campaign.title or "Untitled Campaign",
                    description=campaign.description or "",
                    keywords=campaign.keywords if isinstance(campaign.keywords, list) else [],
                    target_audience=campaign.target_audience,
                    campaign_type="universal",
                    status=status_value,
                    tone=campaign.tone or "conversational",
                    style=campaign.style or "modern",
                    created_at=campaign.created_at,
                    updated_at=campaign.updated_at,
                    workflow_state=workflow_state,
                    completion_percentage=completion_percentage,
                    sources_count=getattr(campaign, 'sources_count', 0) or 0,
                    intelligence_count=getattr(campaign, 'intelligence_extracted', 0) or 0,
                    content_count=getattr(campaign, 'content_generated', 0) or 0
                )
                campaign_responses.append(campaign_response)
                
            except Exception as campaign_error:
                logger.error(f"Error processing campaign {campaign.id}: {campaign_error}")
                # Skip this campaign but continue with others
                continue
        
        logger.info(f"Successfully processed {len(campaign_responses)} campaigns")
        
        # ✅ CRITICAL FIX: Add the missing return statement
        return campaign_responses
        
    except Exception as e:
        logger.error(f"Error getting campaigns: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign stats: {str(e)}"
        )