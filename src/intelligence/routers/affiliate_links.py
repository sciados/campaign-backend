from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel, validator
import re
import urllib.parse
import base64
from datetime import datetime
import logging

# ✅ FIXED: Use absolute imports to prevent conflicts
from src.auth.dependencies import get_db, get_current_user
from src.models.user import User  # ✅ FIXED: Use src.models instead of models
from src.models.clickbank import (  # ✅ FIXED: Use src.models instead of models
    ClickBankProduct, 
    UserAffiliatePreferences, 
    AffiliateLinkClick,
    ProductPerformance
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic Models
class AffiliatePreferencesCreate(BaseModel):
    clickbank_affiliate_id: str
    clickbank_nickname: Optional[str] = None
    link_cloaking_enabled: bool = False
    custom_domain: Optional[str] = None
    preferred_commission_threshold: float = 50.0
    notify_new_products: bool = True
    notify_high_gravity_products: bool = True
    email_weekly_reports: bool = True
    auto_create_campaigns: bool = False
    default_campaign_tone: str = "professional"
    default_campaign_style: str = "persuasive"
    
    @validator('clickbank_affiliate_id')
    def validate_affiliate_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9]{6,50}$', v):
            raise ValueError('ClickBank affiliate ID must be 6-50 alphanumeric characters')
        return v.lower()

class AffiliateLinkRequest(BaseModel):
    product_id: Optional[str] = None
    sales_page_url: str
    custom_tracking: Optional[str] = None
    campaign_id: Optional[str] = None

class AffiliateLinkResponse(BaseModel):
    affiliate_url: str
    tracking_id: str
    commission_rate: float
    estimated_commission: float
    link_type: str
    product_title: Optional[str]
    vendor_name: Optional[str]
    gravity_score: Optional[float]

class AffiliateClickCreate(BaseModel):
    product_id: str
    affiliate_url: str
    original_url: str
    custom_tracking: Optional[str] = None

# Service Class
class ClickBankAffiliateLinkGenerator:
    @staticmethod
    def generate_affiliate_url(
        affiliate_id: str,
        sales_url: str,
        tracking_id: Optional[str] = None,
        vendor: Optional[str] = None
    ) -> str:
        if not tracking_id:
            tracking_id = f"camp_{int(datetime.now().timestamp())}"
        
        # ClickBank affiliate URL format
        if vendor:
            affiliate_url = f"https://{vendor}.pay.clickbank.net/?hop={affiliate_id}&tid={tracking_id}"
        else:
            encoded_url = base64.b64encode(sales_url.encode()).decode()
            affiliate_url = f"https://pay.clickbank.net/?cbaffi={affiliate_id}&cburi={encoded_url}&tid={tracking_id}"
        
        return affiliate_url
    
    @staticmethod
    def calculate_estimated_commission(commission_rate: float, estimated_product_price: float = 50.0) -> float:
        return (commission_rate / 100) * estimated_product_price

# API Endpoints
@router.post("/affiliate/preferences")
async def create_or_update_affiliate_preferences(
    preferences: AffiliatePreferencesCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(UserAffiliatePreferences).filter(
        UserAffiliatePreferences.user_id == current_user.id
    ).first()
    
    if existing:
        for field, value in preferences.dict().items():
            setattr(existing, field, value)
        existing.updated_at = datetime.utcnow()
        db.commit()
        return existing
    else:
        new_preferences = UserAffiliatePreferences(
            user_id=current_user.id,
            **preferences.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_preferences)
        db.commit()
        return new_preferences

@router.get("/affiliate/preferences")
async def get_affiliate_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    preferences = db.query(UserAffiliatePreferences).filter(
        UserAffiliatePreferences.user_id == current_user.id
    ).first()
    return preferences

@router.post("/affiliate/generate-link", response_model=AffiliateLinkResponse)
async def generate_affiliate_link(
    link_request: AffiliateLinkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get user's affiliate preferences
    preferences = db.query(UserAffiliatePreferences).filter(
        UserAffiliatePreferences.user_id == current_user.id
    ).first()
    
    if not preferences or not preferences.clickbank_affiliate_id:
        raise HTTPException(
            status_code=400, 
            detail="Please configure your ClickBank affiliate ID in your profile first"
        )
    
    # Get product information if available
    product = None
    if link_request.product_id:
        product = db.query(ClickBankProduct).filter(
            ClickBankProduct.product_id == link_request.product_id
        ).first()
    
    # Generate tracking ID
    tracking_id = link_request.custom_tracking or f"camp_{current_user.id}_{int(datetime.now().timestamp())}"
    
    # Generate affiliate URL
    affiliate_url = ClickBankAffiliateLinkGenerator.generate_affiliate_url(
        affiliate_id=preferences.clickbank_affiliate_id,
        sales_url=link_request.sales_page_url,
        tracking_id=tracking_id
    )
    
    # Apply cloaking if enabled
    if preferences.link_cloaking_enabled and preferences.custom_domain:
        affiliate_url = f"https://{preferences.custom_domain}/go/{tracking_id}"
        link_type = "cloaked"
    else:
        link_type = "direct"
    
    # Calculate commission information
    commission_rate = product.commission_rate if product else 50.0
    estimated_commission = ClickBankAffiliateLinkGenerator.calculate_estimated_commission(commission_rate)
    
    return AffiliateLinkResponse(
        affiliate_url=affiliate_url,
        tracking_id=tracking_id,
        commission_rate=commission_rate,
        estimated_commission=estimated_commission,
        link_type=link_type,
        product_title=product.title if product else None,
        vendor_name=product.vendor if product else None,
        gravity_score=product.gravity if product else None
    )

@router.post("/affiliate/track-click")
async def track_affiliate_click(
    click_data: AffiliateClickCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get product information
    product = db.query(ClickBankProduct).filter(
        ClickBankProduct.product_id == click_data.product_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Calculate estimated commission
    estimated_commission = ClickBankAffiliateLinkGenerator.calculate_estimated_commission(
        product.commission_rate
    )
    
    # Create click tracking record
    click_record = AffiliateLinkClick(
        user_id=current_user.id,
        product_id=click_data.product_id,
        category=product.category,
        original_url=click_data.original_url,
        affiliate_url=click_data.affiliate_url,
        click_ip=request.client.host,
        click_user_agent=request.headers.get("user-agent"),
        click_referrer=request.headers.get("referer"),
        estimated_commission=estimated_commission,
        click_timestamp=datetime.utcnow()
    )
    
    db.add(click_record)
    db.commit()
    
    return {
        "message": "Click tracked successfully",
        "tracking_id": str(click_record.id),
        "estimated_commission": estimated_commission
    }

@router.get("/affiliate/performance")
async def get_affiliate_performance(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from datetime import timedelta
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get basic performance metrics
    performance_query = db.query(
        func.count(AffiliateLinkClick.id).label('total_clicks'),
        func.count(func.nullif(AffiliateLinkClick.conversion_tracked, False)).label('conversions'),
        func.sum(AffiliateLinkClick.estimated_commission).label('estimated_earnings'),
        func.avg(AffiliateLinkClick.estimated_commission).label('avg_commission_per_click'),
        func.count(func.distinct(AffiliateLinkClick.product_id)).label('unique_products'),
        func.count(func.distinct(AffiliateLinkClick.category)).label('categories_promoted'),
        func.max(AffiliateLinkClick.click_timestamp).label('last_activity')
    ).filter(
        AffiliateLinkClick.user_id == current_user.id,
        AffiliateLinkClick.click_timestamp >= start_date
    ).first()
    
    # Get top performing products
    top_products = db.query(
        AffiliateLinkClick.product_id,
        ClickBankProduct.title,
        func.count(AffiliateLinkClick.id).label('clicks'),
        func.sum(AffiliateLinkClick.estimated_commission).label('total_commission')
    ).join(
        ClickBankProduct, AffiliateLinkClick.product_id == ClickBankProduct.product_id
    ).filter(
        AffiliateLinkClick.user_id == current_user.id,
        AffiliateLinkClick.click_timestamp >= start_date
    ).group_by(
        AffiliateLinkClick.product_id, ClickBankProduct.title
    ).order_by(
        func.count(AffiliateLinkClick.id).desc()
    ).limit(5).all()
    
    return {
        "total_clicks": performance_query.total_clicks or 0,
        "conversions": performance_query.conversions or 0,
        "estimated_earnings": float(performance_query.estimated_earnings or 0),
        "avg_commission_per_click": float(performance_query.avg_commission_per_click or 0),
        "unique_products_promoted": performance_query.unique_products or 0,
        "categories_promoted": performance_query.categories_promoted or 0,
        "last_activity": performance_query.last_activity,
        "top_performing_products": [
            {
                "product_id": p.product_id,
                "title": p.title,
                "clicks": p.clicks,
                "total_commission": float(p.total_commission)
            }
            for p in top_products
        ]
    }