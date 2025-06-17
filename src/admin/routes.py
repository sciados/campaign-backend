@router.get("/companies/{company_id}", response_model=AdminCompanyResponse)
async def get_company_details(
    company_id: str,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed company information"""
    
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Get user count for this company
    user_count_query = select(func.count(User.id)).where(User.company_id == company.id)
    user_count = await db.scalar(user_count_query) or 0
    
    # Get campaign count for this company
    campaign_count_query = select(func.count(Campaign.id)).where(Campaign.company_id == company.id)
    campaign_count = await db.scalar(campaign_count_query) or 0
    
    return AdminCompanyResponse(
        id=company.id,
        company_name=company.company_name,
        company_slug=company.company_slug,
        industry=company.industry or "",
        company_size=company.company_size,
        subscription_tier=company.subscription_tier,
        subscription_status=company.subscription_status,
        monthly_credits_used=company.monthly_credits_used,
        monthly_credits_limit=company.monthly_credits_limit,
        total_campaigns=company.total_campaigns,
        created_at=company.created_at,
        user_count=user_count,
        campaign_count=campaign_count
    )

@router.put("/companies/{company_id}")
async def update_company_details(
    company_id: str,
    company_update: CompanyUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update company details"""
    
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Update company fields
    if company_update.company_name is not None:
        company.company_name = company_update.company_name
    if company_update.industry is not None:
        company.industry = company_update.industry
    if company_update.company_size is not None:
        company.company_size = company_update.company_size
    if company_update.website_url is not None:
        # Only update if the field exists on the model
        if hasattr(company, 'website_url'):
            company.website_url = company_update.website_url
    
    await db.commit()
    
    return {"message": "Company details updated successfully"}

@router.get("/companies/{company_id}", response_model=AdminCompanyResponse)
async def get_company_details(
    company_id: str,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed company information"""
    
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Get user count for this company
    user_count_query = select(func.count(User.id)).where(User.company_id == company.id)
    user_count = await db.scalar(user_count_query) or 0
    
    # Get campaign count for this company
    campaign_count_query = select(func.count(Campaign.id)).where(Campaign.company_id == company.id)
    campaign_count = await db.scalar(campaign_count_query) or 0
    
    return AdminCompanyResponse(
        id=company.id,
        company_name=company.company_name,
        company_slug=company.company_slug,
        industry=company.industry or "",
        company_size=company.company_size,
        subscription_tier=company.subscription_tier,
        subscription_status=company.subscription_status,
        monthly_credits_used=company.monthly_credits_used,
        monthly_credits_limit=company.monthly_credits_limit,
        total_campaigns=company.total_campaigns,
        created_at=company.created_at,
        user_count=user_count,
        campaign_count=campaign_count
    )

@router.put("/companies/{company_id}")
async def update_company_details(
    company_id: str,
    company_update: CompanyUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update company details"""
    
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Update company fields
    if company_update.company_name is not None:
        company.company_name = company_update.company_name
    if company_update.industry is not None:
        company.industry = company_update.industry
    if company_update.company_size is not None:
        company.company_size = company_update.company_size
    if company_update.website_url is not None:
        # Only update if the field exists on the model
        if hasattr(company, 'website_url'):
            company.website_url = company_update.website_url
    
    await db.commit()
    
    return {"message": "Company details updated successfully"}

@router.get("/roles")
async def get_available_roles(
    admin_user: User = Depends(require_admin)
):
    """Get list of available user roles"""
    
    roles = [
        {
            "value": "admin",
            "label": "Admin",
            "description": "Full platform access, can manage all users and companies"
        },
        {
            "value": "owner", 
            "label": "Company Owner",
            "description": "Company owner with full access to their company"
        },
        {
            "value": "member",
            "label": "Member", 
            "description": "Regular user with standard access"
        },
        {
            "value": "viewer",
            "label": "Viewer",
            "description": "Read-only access to company resources"
        }
    ]
    
    return {"roles": roles}