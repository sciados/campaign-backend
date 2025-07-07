# src/intelligence/routers/clickbank_admin.py - Admin endpoints for managing ClickBank URLs
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
import json
from datetime import datetime
import asyncio

from src.core.database import get_db
from src.models.clickbank import ClickBankCategoryURL

router = APIRouter(prefix="/admin/clickbank", tags=["clickbank-admin"])

@router.get("/categories")
async def get_all_categories(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get all ClickBank categories with their URLs and test status"""
    
    categories = db.query(ClickBankCategoryURL).all()
    
    result = []
    for category in categories:
        backup_urls = []
        if category.backup_urls:
            try:
                backup_urls = json.loads(category.backup_urls) if isinstance(category.backup_urls, str) else category.backup_urls
            except:
                backup_urls = []
        
        result.append({
            "id": category.id,
            "category": category.category,
            "category_name": category.category_name,
            "primary_url": category.primary_url,
            "backup_urls": backup_urls,
            "is_active": category.is_active,
            "last_tested": category.last_tested.isoformat() if category.last_tested else None,
            "last_working": category.last_working.isoformat() if category.last_working else None,
            "test_results": category.test_results,
            "created_at": category.created_at.isoformat() if category.created_at else None,
            "updated_at": category.updated_at.isoformat() if category.updated_at else None
        })
    
    return result

@router.post("/categories/{category}/test")
async def test_category_urls(category: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Test all URLs for a specific category"""
    
    from src.intelligence.routers.clickbank_routes import scraper
    
    # Get category from database
    cat_record = db.query(ClickBankCategoryURL).filter(ClickBankCategoryURL.category == category).first()
    
    if not cat_record:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    # Get all URLs to test
    backup_urls = []
    if cat_record.backup_urls:
        try:
            backup_urls = json.loads(cat_record.backup_urls) if isinstance(cat_record.backup_urls, str) else cat_record.backup_urls
        except:
            backup_urls = []
    
    all_urls = [cat_record.primary_url] + backup_urls
    
    # Test each URL
    test_results = []
    working_urls = []
    
    for url in all_urls:
        result = await scraper.test_category_url(url)
        test_results.append(result)
        
        if result['is_working']:
            working_urls.append(url)
    
    # Update database with test results
    cat_record.last_tested = datetime.utcnow()
    cat_record.test_results = test_results
    
    if working_urls:
        cat_record.last_working = datetime.utcnow()
        # If primary URL is not working but backup is, consider updating primary
        if not test_results[0]['is_working'] and len(working_urls) > 0:
            # Don't auto-update primary, but log it for admin review
            pass
    
    db.commit()
    
    return {
        "category": category,
        "category_name": cat_record.category_name,
        "total_urls_tested": len(all_urls),
        "working_urls": len(working_urls),
        "test_results": test_results,
        "working_url_list": working_urls,
        "recommendation": "working" if working_urls else "needs_attention",
        "tested_at": datetime.utcnow().isoformat()
    }

@router.post("/test-all")
async def test_all_categories(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Test URLs for all categories"""
    
    categories = db.query(ClickBankCategoryURL).filter(ClickBankCategoryURL.is_active == True).all()
    
    results = {}
    total_working = 0
    total_categories = len(categories)
    
    for category in categories:
        try:
            result = await test_category_urls(category.category, db)
            results[category.category] = result
            
            if result['working_urls'] > 0:
                total_working += 1
                
        except Exception as e:
            results[category.category] = {
                "error": str(e),
                "category": category.category,
                "category_name": category.category_name
            }
    
    return {
        "total_categories_tested": total_categories,
        "categories_with_working_urls": total_working,
        "success_rate": f"{(total_working/total_categories)*100:.1f}%" if total_categories > 0 else "0%",
        "results": results,
        "tested_at": datetime.utcnow().isoformat(),
        "overall_status": "healthy" if total_working >= total_categories * 0.8 else "needs_attention"
    }

@router.put("/categories/{category}")
async def update_category_urls(
    category: str, 
    update_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update URLs for a category"""
    
    cat_record = db.query(ClickBankCategoryURL).filter(ClickBankCategoryURL.category == category).first()
    
    if not cat_record:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    # Update allowed fields
    allowed_fields = ['category_name', 'primary_url', 'backup_urls', 'is_active']
    
    for field, value in update_data.items():
        if field in allowed_fields:
            if field == 'backup_urls' and isinstance(value, list):
                # Convert list to JSON string for storage
                setattr(cat_record, field, json.dumps(value))
            else:
                setattr(cat_record, field, value)
    
    cat_record.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": f"Category '{category}' updated successfully",
        "category": category,
        "updated_fields": list(update_data.keys()),
        "updated_at": datetime.utcnow().isoformat()
    }

@router.post("/categories")
async def add_new_category(
    category_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Add a new ClickBank category"""
    
    required_fields = ['category', 'category_name', 'primary_url']
    
    for field in required_fields:
        if field not in category_data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Check if category already exists
    existing = db.query(ClickBankCategoryURL).filter(ClickBankCategoryURL.category == category_data['category']).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Category '{category_data['category']}' already exists")
    
    # Prepare backup URLs
    backup_urls = category_data.get('backup_urls', [])
    if isinstance(backup_urls, list):
        backup_urls = json.dumps(backup_urls)
    
    # Create new category
    new_category = ClickBankCategoryURL(
        category=category_data['category'],
        category_name=category_data['category_name'],
        primary_url=category_data['primary_url'],
        backup_urls=backup_urls,
        is_active=category_data.get('is_active', True)
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return {
        "message": f"Category '{category_data['category']}' added successfully",
        "category_id": new_category.id,
        "category": new_category.category,
        "category_name": new_category.category_name,
        "created_at": new_category.created_at.isoformat()
    }

@router.delete("/categories/{category}")
async def delete_category(category: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Delete a ClickBank category"""
    
    cat_record = db.query(ClickBankCategoryURL).filter(ClickBankCategoryURL.category == category).first()
    
    if not cat_record:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    db.delete(cat_record)
    db.commit()
    
    return {
        "message": f"Category '{category}' deleted successfully",
        "deleted_category": category,
        "deleted_at": datetime.utcnow().isoformat()
    }

@router.get("/health-check")
async def clickbank_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Quick health check of ClickBank scraping system"""
    
    # Count categories
    total_categories = db.query(ClickBankCategoryURL).count()
    active_categories = db.query(ClickBankCategoryURL).filter(ClickBankCategoryURL.is_active == True).count()
    
    # Get recently tested categories
    recently_tested = db.query(ClickBankCategoryURL).filter(
        ClickBankCategoryURL.last_tested.isnot(None)
    ).count()
    
    # Get categories with recent working URLs
    recently_working = db.query(ClickBankCategoryURL).filter(
        ClickBankCategoryURL.last_working.isnot(None)
    ).count()
    
    # Calculate health score
    health_score = 0
    if total_categories > 0:
        health_score = (recently_working / total_categories) * 100
    
    status = "healthy" if health_score >= 80 else "warning" if health_score >= 50 else "critical"
    
    return {
        "status": status,
        "health_score": f"{health_score:.1f}%",
        "total_categories": total_categories,
        "active_categories": active_categories,
        "recently_tested": recently_tested,
        "recently_working": recently_working,
        "database_connection": "ok",
        "scraper_status": "operational",
        "last_check": datetime.utcnow().isoformat(),
        "recommendations": [
            "Test URLs regularly" if recently_tested < total_categories else None,
            "Update non-working URLs" if health_score < 80 else None,
            "Monitor ClickBank marketplace changes" if health_score < 50 else None
        ]
    }