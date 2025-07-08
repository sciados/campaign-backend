# src/intelligence/affiliate_networks/clickbank_community.py
"""
CLICKBANK COMMUNITY-DRIVEN SYSTEM
✅ Manual product submissions by users
✅ Product creator self-submissions
✅ Community verification and ratings
✅ Admin approval workflow
✅ Builds relationships while pursuing official API
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from dependencies import get_current_user
from sqlalchemy import Column, String, Text, Boolean, DateTime, Float, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from src.models.base import BaseModel, EnumSerializerMixin

logger = logging.getLogger(__name__)

class ClickBankSubmissionStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"

class ClickBankSubmissionType(str, Enum):
    PRODUCT_CREATOR = "product_creator"     # Vendor submitting their own product
    AFFILIATE_RECOMMENDATION = "affiliate_recommendation"  # Affiliate recommending product
    COMMUNITY_DISCOVERY = "community_discovery"  # User found interesting product

class ClickBankCommunityProduct(BaseModel, EnumSerializerMixin):
    """Community-submitted ClickBank products"""
    __tablename__ = "clickbank_community_products"
    
    # Product Information
    clickbank_product_id = Column(String(100), nullable=False, index=True)
    vendor_nickname = Column(String(100), nullable=False)
    product_title = Column(String(500), nullable=False)
    product_description = Column(Text)
    category = Column(String(100))
    
    # URLs and Links
    salespage_url = Column(String(1000), nullable=False)
    affiliate_url = Column(String(1000))
    vendor_website = Column(String(500))
    
    # Performance Data
    gravity = Column(Float, default=0.0)
    commission_rate = Column(Float, default=0.0)
    price_range = Column(String(50))  # "$37-$197"
    refund_rate = Column(Float)
    
    # Submission Metadata
    submission_type = Column(String(50), nullable=False)  # product_creator, affiliate_recommendation, etc.
    submission_status = Column(String(50), default="pending")
    submitted_by_user_id = Column(UUID(as_uuid=True), nullable=False)
    submitted_by_company_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Verification Data
    verified_by_admin = Column(Boolean, default=False)
    admin_notes = Column(Text)
    verification_date = Column(DateTime)
    verification_admin_id = Column(UUID(as_uuid=True))
    
    # Community Features
    community_rating = Column(Float, default=0.0)
    community_reviews_count = Column(Integer, default=0)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    
    # Analysis Status
    intelligence_extracted = Column(Boolean, default=False)
    analysis_date = Column(DateTime)
    analysis_confidence = Column(Float)
    
    # Marketing Intelligence (JSON storage)
    marketing_angles = Column(JSON, default={})
    target_audience_notes = Column(Text)
    competitive_advantages = Column(JSON, default=[])
    promotion_tips = Column(JSON, default=[])
    
    # Quality Scores
    url_validity_checked = Column(Boolean, default=False)
    url_accessibility_score = Column(Float)
    content_quality_score = Column(Float)
    
    # Relationships (will be defined when other models are available)
    # submitted_by = relationship("User", foreign_keys=[submitted_by_user_id])
    # verified_by = relationship("User", foreign_keys=[verification_admin_id])

class ClickBankCommunityReview(BaseModel):
    """Community reviews for ClickBank products"""
    __tablename__ = "clickbank_community_reviews"
    
    product_id = Column(UUID(as_uuid=True), nullable=False)  # References clickbank_community_products
    reviewer_user_id = Column(UUID(as_uuid=True), nullable=False)
    reviewer_company_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Review Content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review_title = Column(String(200))
    review_text = Column(Text)
    
    # Reviewer Context
    reviewer_type = Column(String(50))  # affiliate, customer, vendor
    promotion_experience = Column(Boolean, default=False)  # Has reviewer promoted this?
    conversion_rate = Column(Float)  # If they promoted it
    
    # Review Metadata
    is_verified = Column(Boolean, default=False)
    helpful_votes = Column(Integer, default=0)
    reported_count = Column(Integer, default=0)

class ClickBankCommunityManager:
    """Manage community-driven ClickBank product submissions"""
    
    def __init__(self):
        self.submission_validators = [
            self._validate_clickbank_url,
            self._validate_product_data,
            self._check_duplicate_submission,
            self._verify_url_accessibility
        ]
    
    async def submit_product(
        self, 
        user_id: str,
        company_id: str,
        submission_data: Dict[str, Any],
        submission_type: str = "community_discovery"
    ) -> Dict[str, Any]:
        """Submit a ClickBank product for community review"""
        
        # Validate submission
        validation_result = await self._validate_submission(submission_data)
        if not validation_result["is_valid"]:
            return {
                "success": False,
                "errors": validation_result["errors"],
                "submission_id": None
            }
        
        # Extract ClickBank product ID from URL
        product_id = self._extract_clickbank_id(submission_data["salespage_url"])
        if not product_id:
            return {
                "success": False,
                "errors": ["Could not extract ClickBank product ID from URL"],
                "submission_id": None
            }
        
        # Create submission record
        submission = ClickBankCommunityProduct(
            id=uuid.uuid4(),
            clickbank_product_id=product_id,
            vendor_nickname=submission_data.get("vendor_nickname", ""),
            product_title=submission_data.get("product_title", ""),
            product_description=submission_data.get("product_description", ""),
            category=submission_data.get("category", "health"),
            salespage_url=submission_data["salespage_url"],
            affiliate_url=submission_data.get("affiliate_url", ""),
            vendor_website=submission_data.get("vendor_website", ""),
            gravity=float(submission_data.get("gravity", 0)),
            commission_rate=float(submission_data.get("commission_rate", 0)),
            price_range=submission_data.get("price_range", ""),
            submission_type=submission_type,
            submission_status="pending",
            submitted_by_user_id=user_id,
            submitted_by_company_id=company_id,
            created_at=datetime.utcnow()
        )
        
        # Save to database (pseudo-code - implement with your ORM)
        # await self._save_submission(submission)
        
        # Start background verification
        asyncio.create_task(self._background_verification(submission.id))
        
        return {
            "success": True,
            "submission_id": str(submission.id),
            "status": "pending",
            "message": "Product submitted for community review",
            "estimated_review_time": "24-48 hours",
            "next_steps": [
                "Community members will review and rate your submission",
                "Admin will verify product details and URL accessibility", 
                "You'll receive email notification when approved",
                "Approved products become available for campaign creation"
            ]
        }
    
    async def get_pending_submissions(self, admin_user_id: str = None) -> List[Dict[str, Any]]:
        """Get products pending admin review"""
        
        # Pseudo-query - implement with your database
        pending_products = []  # Query for submission_status = "pending"
        
        return [
            {
                "submission_id": str(product.id),
                "product_title": product.product_title,
                "vendor_nickname": product.vendor_nickname,
                "salespage_url": product.salespage_url,
                "submitted_by": "User Name",  # Join with user table
                "submission_date": product.created_at.isoformat(),
                "submission_type": product.submission_type,
                "category": product.category,
                "gravity": product.gravity,
                "commission_rate": product.commission_rate,
                "community_rating": product.community_rating,
                "url_accessibility": product.url_accessibility_score,
                "requires_action": self._calculate_review_priority(product)
            }
            for product in pending_products
        ]
    
    async def approve_submission(
        self, 
        submission_id: str, 
        admin_user_id: str,
        approval_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Approve a community submission"""
        
        if approval_data is None:
            approval_data = {}
        
        # Update submission status
        update_data = {
            "submission_status": "approved",
            "verified_by_admin": True,
            "verification_date": datetime.utcnow(),
            "verification_admin_id": admin_user_id,
            "admin_notes": approval_data.get("admin_notes", ""),
            # Update any corrected product data
            "product_title": approval_data.get("product_title"),
            "product_description": approval_data.get("product_description"),
            "category": approval_data.get("category"),
            "gravity": approval_data.get("gravity"),
            "commission_rate": approval_data.get("commission_rate")
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        # Pseudo-update - implement with your ORM
        # await self._update_submission(submission_id, update_data)
        
        # Trigger intelligence extraction
        asyncio.create_task(self._extract_product_intelligence(submission_id))
        
        # Notify submitter
        await self._notify_submission_approved(submission_id)
        
        return {
            "success": True,
            "submission_id": submission_id,
            "status": "approved",
            "message": "Product approved and added to marketplace",
            "next_steps": [
                "Product is now available for campaign creation",
                "Intelligence extraction started",
                "Submitter has been notified"
            ]
        }
    
    async def get_approved_products(
        self, 
        category: str = None,
        limit: int = 50,
        sort_by: str = "community_rating"
    ) -> List[Dict[str, Any]]:
        """Get approved ClickBank products from community"""
        
        # Pseudo-query - implement with your database
        query_filters = {"submission_status": "approved"}
        if category:
            query_filters["category"] = category
        
        # Mock approved products
        approved_products = []  # Your database query here
        
        return [
            {
                "product_id": str(product.id),
                "clickbank_product_id": product.clickbank_product_id,
                "product_title": product.product_title,
                "vendor_nickname": product.vendor_nickname,
                "category": product.category,
                "salespage_url": product.salespage_url,
                "gravity": product.gravity,
                "commission_rate": product.commission_rate,
                "price_range": product.price_range,
                "community_rating": product.community_rating,
                "community_reviews": product.community_reviews_count,
                "intelligence_available": product.intelligence_extracted,
                "submission_type": product.submission_type,
                "approved_date": product.verification_date.isoformat() if product.verification_date else None,
                "marketing_angles": product.marketing_angles,
                "target_audience": product.target_audience_notes,
                "promotion_ready": product.intelligence_extracted and product.community_rating >= 3.0
            }
            for product in approved_products
        ]
    
    async def add_product_review(
        self,
        product_id: str,
        user_id: str,
        company_id: str,
        review_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add community review for a product"""
        
        # Check if user already reviewed this product
        existing_review = None  # Query for existing review
        if existing_review:
            return {
                "success": False,
                "error": "You have already reviewed this product",
                "can_edit": True
            }
        
        # Create review
        review = ClickBankCommunityReview(
            id=uuid.uuid4(),
            product_id=product_id,
            reviewer_user_id=user_id,
            reviewer_company_id=company_id,
            rating=int(review_data["rating"]),
            review_title=review_data.get("review_title", ""),
            review_text=review_data.get("review_text", ""),
            reviewer_type=review_data.get("reviewer_type", "affiliate"),
            promotion_experience=review_data.get("promotion_experience", False),
            conversion_rate=review_data.get("conversion_rate"),
            created_at=datetime.utcnow()
        )
        
        # Save review and update product rating
        # await self._save_review(review)
        await self._update_product_community_rating(product_id)
        
        return {
            "success": True,
            "review_id": str(review.id),
            "message": "Review added successfully",
            "community_impact": "Product rating and visibility updated"
        }
    
    async def search_community_products(
        self,
        search_query: str,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Search approved community products"""
        
        if filters is None:
            filters = {}
        
        # Build search criteria
        search_criteria = {
            "submission_status": "approved",
            "search_terms": search_query.lower()
        }
        
        # Apply filters
        if filters.get("category"):
            search_criteria["category"] = filters["category"]
        if filters.get("min_rating"):
            search_criteria["min_community_rating"] = filters["min_rating"]
        if filters.get("min_gravity"):
            search_criteria["min_gravity"] = filters["min_gravity"]
        
        # Mock search results
        search_results = []  # Your search implementation here
        
        return search_results
    
    # Validation Methods
    async def _validate_submission(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate product submission data"""
        
        errors = []
        
        # Required fields
        required_fields = ["salespage_url", "product_title", "vendor_nickname"]
        for field in required_fields:
            if not submission_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # URL validation
        salespage_url = submission_data.get("salespage_url", "")
        if salespage_url and not self._is_valid_clickbank_url(salespage_url):
            errors.append("URL does not appear to be a valid ClickBank sales page")
        
        # Gravity validation
        gravity = submission_data.get("gravity")
        if gravity and (not isinstance(gravity, (int, float)) or gravity < 0 or gravity > 1000):
            errors.append("Gravity must be a number between 0 and 1000")
        
        # Commission rate validation
        commission = submission_data.get("commission_rate")
        if commission and (not isinstance(commission, (int, float)) or commission < 0 or commission > 100):
            errors.append("Commission rate must be a percentage between 0 and 100")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    def _is_valid_clickbank_url(self, url: str) -> bool:
        """Check if URL appears to be a ClickBank sales page"""
        url_lower = url.lower()
        clickbank_indicators = [
            "clickbank.net",
            "cbankoffers.com", 
            "paydotcom.com",
            "hop.clickbank.net",
            "cb-analytics.com"
        ]
        
        return any(indicator in url_lower for indicator in clickbank_indicators)
    
    def _extract_clickbank_id(self, url: str) -> Optional[str]:
        """Extract ClickBank product ID from URL"""
        import re
        
        # Common ClickBank URL patterns
        patterns = [
            r'[?&]tid=([A-Za-z0-9]+)',
            r'[?&]pid=([A-Za-z0-9]+)', 
            r'/([A-Za-z0-9]+)\.html',
            r'clickbank\.net/[^/]+/([A-Za-z0-9]+)',
            r'hop\.clickbank\.net/([A-Za-z0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _calculate_review_priority(self, product) -> str:
        """Calculate priority level for admin review"""
        
        priority_factors = []
        
        # High priority if submitted by product creator
        if product.submission_type == "product_creator":
            priority_factors.append("creator_submission")
        
        # High priority if high gravity
        if product.gravity and product.gravity > 50:
            priority_factors.append("high_gravity")
        
        # Medium priority if has community engagement
        if product.community_reviews_count > 0:
            priority_factors.append("community_engagement")
        
        # Low priority if URL accessibility issues
        if product.url_accessibility_score and product.url_accessibility_score < 0.5:
            priority_factors.append("url_issues")
        
        if "creator_submission" in priority_factors or "high_gravity" in priority_factors:
            return "high"
        elif "community_engagement" in priority_factors:
            return "medium"
        else:
            return "normal"
    
    async def _background_verification(self, submission_id: str):
        """Background verification of submission"""
        try:
            # Verify URL accessibility
            # Check for duplicate submissions
            # Basic content analysis
            # Update submission with verification results
            pass
        except Exception as e:
            logger.error(f"Background verification failed for {submission_id}: {str(e)}")
    
    async def _extract_product_intelligence(self, submission_id: str):
        """Extract marketing intelligence from approved product"""
        try:
            # Use your existing intelligence extraction system
            # Save results to marketing_angles, target_audience_notes, etc.
            pass
        except Exception as e:
            logger.error(f"Intelligence extraction failed for {submission_id}: {str(e)}")
    
    async def _update_product_community_rating(self, product_id: str):
        """Update product's community rating based on reviews"""
        # Calculate average rating from all reviews
        # Update community_rating and community_reviews_count
        pass
    
    async def _notify_submission_approved(self, submission_id: str):
        """Notify submitter that their product was approved"""
        # Send email notification
        # Create in-app notification
        pass


# FastAPI routes for community system
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel as PydanticBaseModel

community_router = APIRouter()

class ProductSubmissionRequest(PydanticBaseModel):
    salespage_url: str
    product_title: str
    vendor_nickname: str
    product_description: Optional[str] = None
    category: Optional[str] = "health"
    gravity: Optional[float] = None
    commission_rate: Optional[float] = None
    price_range: Optional[str] = None
    affiliate_url: Optional[str] = None
    vendor_website: Optional[str] = None

class ProductReviewRequest(PydanticBaseModel):
    rating: int  # 1-5
    review_title: Optional[str] = None
    review_text: Optional[str] = None
    reviewer_type: str = "affiliate"  # affiliate, customer, vendor
    promotion_experience: bool = False
    conversion_rate: Optional[float] = None

@community_router.post("/clickbank/community/submit")
async def submit_clickbank_product(
    submission: ProductSubmissionRequest,
    current_user: dict = Depends(get_current_user)  # Your auth dependency
):
    """Submit ClickBank product for community review"""
    
    manager = ClickBankCommunityManager()
    
    result = await manager.submit_product(
        user_id=current_user["id"],
        company_id=current_user["company_id"],
        submission_data=submission.dict(),
        submission_type="community_discovery"
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["errors"])
    
    return result

@community_router.get("/clickbank/community/products")
async def get_community_products(
    category: Optional[str] = None,
    limit: int = 50,
    sort_by: str = "community_rating"
):
    """Get approved ClickBank products from community"""
    
    manager = ClickBankCommunityManager()
    products = await manager.get_approved_products(category, limit, sort_by)
    
    return {
        "products": products,
        "total_count": len(products),
        "category": category or "all",
        "sort_by": sort_by
    }

@community_router.post("/clickbank/community/products/{product_id}/review")
async def add_product_review(
    product_id: str,
    review: ProductReviewRequest,
    current_user: dict = Depends(get_current_user)
):
    """Add review for community product"""
    
    manager = ClickBankCommunityManager()
    
    result = await manager.add_product_review(
        product_id=product_id,
        user_id=current_user["id"],
        company_id=current_user["company_id"],
        review_data=review.dict()
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@community_router.get("/clickbank/community/search")
async def search_community_products(
    q: str,
    category: Optional[str] = None,
    min_rating: Optional[float] = None,
    min_gravity: Optional[float] = None
):
    """Search community ClickBank products"""
    
    manager = ClickBankCommunityManager()
    
    filters = {}
    if category:
        filters["category"] = category
    if min_rating:
        filters["min_rating"] = min_rating
    if min_gravity:
        filters["min_gravity"] = min_gravity
    
    results = await manager.search_community_products(q, filters)
    
    return {
        "search_query": q,
        "filters_applied": filters,
        "results": results,
        "total_results": len(results)
    }

# Admin routes
@community_router.get("/clickbank/community/admin/pending")
async def get_pending_submissions(
    current_user: dict = Depends(get_admin_user)  # Admin auth dependency
):
    """Get products pending admin review"""
    
    manager = ClickBankCommunityManager()
    pending = await manager.get_pending_submissions(current_user["id"])
    
    return {
        "pending_submissions": pending,
        "total_pending": len(pending),
        "review_queue_status": "active"
    }

@community_router.post("/clickbank/community/admin/approve/{submission_id}")
async def approve_submission(
    submission_id: str,
    approval_data: Optional[dict] = None,
    current_user: dict = Depends(get_admin_user)
):
    """Approve community submission"""
    
    manager = ClickBankCommunityManager()
    
    result = await manager.approve_submission(
        submission_id=submission_id,
        admin_user_id=current_user["id"],
        approval_data=approval_data or {}
    )
    
    return result


# Integration with existing campaign creation
async def create_campaign_from_community_product(
    product_id: str,
    campaign_data: Dict[str, Any],
    user_id: str,
    company_id: str
) -> Dict[str, Any]:
    """Create campaign from community-approved ClickBank product"""
    
    manager = ClickBankCommunityManager()
    
    # Get approved product
    products = await manager.get_approved_products()
    product = next((p for p in products if p["product_id"] == product_id), None)
    
    if not product:
        raise ValueError("Product not found or not approved")
    
    # Enhanced campaign data with community intelligence
    enhanced_campaign_data = {
        **campaign_data,
        "clickbank_product_id": product["clickbank_product_id"],
        "source_network": "clickbank_community",
        "settings": {
            **campaign_data.get("settings", {}),
            "community_product": True,
            "community_rating": product["community_rating"],
            "marketing_angles": product["marketing_angles"],
            "target_audience_notes": product["target_audience"],
            "salespage_url": product["salespage_url"]
        }
    }
    
    # Create campaign using your existing system
    # return await create_campaign(enhanced_campaign_data, user_id, company_id)
    
    return {
        "success": True,
        "campaign_id": "generated_campaign_id",
        "message": "Campaign created from community product",
        "community_features": {
            "intelligence_available": product["intelligence_available"],
            "marketing_angles": len(product["marketing_angles"]),
            "community_rating": product["community_rating"]
        }
    }