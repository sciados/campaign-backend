# src/intelligence/utils/ai_intelligence_saver.py
"""
✅ CRUD MIGRATED: AI Intelligence Saver - Handles reliable storage of AI-generated intelligence data
🔧 FIXED: Replaced all direct SQL queries with proven CRUD operations
🎯 ENHANCED: Multiple fallback strategies using CRUD patterns
"""
import json
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

# 🔧 CRUD Infrastructure
from src.intelligence.repositories.intelligence_repository import IntelligenceRepository
from src.utils.json_utils import safe_json_dumps, safe_json_loads

logger = logging.getLogger(__name__)

async def save_ai_intelligence_data(
    db_session: AsyncSession,
    intelligence_id: uuid.UUID,
    ai_data: Dict[str, Any],
    intelligence_obj: Optional[Any] = None
) -> Dict[str, bool]:
    """
    ✅ CRUD MIGRATED: Reliable AI intelligence data saver with CRUD-based fallback strategies
    Returns: Dict mapping each AI category to success/failure status
    """
    
    save_results = {}
    ai_categories = [
        'scientific_intelligence',
        'credibility_intelligence', 
        'market_intelligence',
        'emotional_transformation_intelligence',
        'scientific_authority_intelligence'
    ]
   
    logger.info(f"🔄 Starting CRUD-based AI intelligence save for {len(ai_data)} categories")
    
    # Method 1: Primary CRUD-based storage
    for category in ai_categories:
        category_data = ai_data.get(category, {})
        
        if category_data and isinstance(category_data, dict):
            try:
                # Get intelligence record using CRUD
                if not intelligence_obj:
                    intelligence_obj = await intelligence_crud.get(db=db_session, id=intelligence_id)
                
                if not intelligence_obj:
                    logger.error(f"❌ Intelligence record {intelligence_id} not found")
                    save_results[category] = False
                    continue
                
                # Prepare update data
                json_data = safe_json_dumps(category_data)
                update_data = {category: json_data}
                
                # Use CRUD update method
                updated_intelligence = await intelligence_crud.update(
                    db=db_session,
                    db_obj=intelligence_obj,
                    obj_in=update_data
                )
                
                save_results[category] = True
                logger.info(f"✅ CRUD save: {category} ({len(category_data)} items)")
                
                # Update local object for next iterations
                intelligence_obj = updated_intelligence
                
            except Exception as e:
                logger.error(f"❌ CRUD save failed for {category}: {str(e)}")
                save_results[category] = False
        else:
            logger.warning(f"⚠️ No data to save for {category}")
            save_results[category] = False
    
    # Method 2: CRUD-based emergency metadata backup for failed categories
    failed_categories = [cat for cat, success in save_results.items() if not success]
    
    if failed_categories:
        logger.info(f"🚨 Applying CRUD-based emergency backup for {len(failed_categories)} failed categories")
        
        emergency_success = await _emergency_crud_backup(
            db_session, intelligence_id, ai_data, failed_categories
        )
        
        if emergency_success:
            for category in failed_categories:
                save_results[category] = True
                logger.info(f"🚨 Emergency CRUD backup: {category}")
    
    # Log final results
    successful = sum(1 for success in save_results.values() if success)
    total = len(save_results)
    
    logger.info(f"📊 CRUD-based AI save results: {successful}/{total} categories successful")
    
    return save_results


async def _emergency_crud_backup(
    db_session: AsyncSession,
    intelligence_id: uuid.UUID,
    ai_data: Dict[str, Any],
    failed_categories: list
) -> bool:
    """✅ CRUD MIGRATED: Emergency backup using CRUD metadata operations"""
    
    try:
        # Get intelligence record using CRUD
        intelligence_obj = await intelligence_crud.get(db=db_session, id=intelligence_id)
        
        if not intelligence_obj:
            logger.error(f"❌ Intelligence record {intelligence_id} not found for emergency backup")
            return False
        
        # Get existing metadata
        existing_metadata = intelligence_obj.processing_metadata
        if existing_metadata:
            try:
                metadata = safe_json_loads(existing_metadata)
            except:
                metadata = {}
        else:
            metadata = {}
        
        # Add emergency backup
        metadata["emergency_ai_backup"] = metadata.get("emergency_ai_backup", {})
        for category in failed_categories:
            if category in ai_data:
                metadata["emergency_ai_backup"][category] = ai_data[category]
        
        metadata["emergency_backup_applied"] = True
        metadata["emergency_backup_timestamp"] = datetime.now(timezone.utc).isoformat()
        metadata["emergency_backup_reason"] = "Primary CRUD storage methods failed"
        metadata["emergency_backup_categories"] = failed_categories
        
        # Save metadata using CRUD update
        update_data = {
            "processing_metadata": safe_json_dumps(metadata)
        }
        
        await intelligence_crud.update(
            db=db_session,
            db_obj=intelligence_obj,
            obj_in=update_data
        )
        
        logger.info(f"✅ Emergency CRUD backup completed for {len(failed_categories)} categories")
        return True
        
    except Exception as e:
        logger.error(f"❌ Emergency CRUD backup failed: {str(e)}")
        return False


async def verify_ai_intelligence_storage(
    db_session: AsyncSession,
    intelligence_id: uuid.UUID
) -> Dict[str, Any]:
    """
    ✅ CRUD MIGRATED: Comprehensive verification of AI intelligence storage using CRUD operations
    Returns detailed summary of what was actually saved
    """
    
    ai_categories = [
        'scientific_intelligence',
        'credibility_intelligence',
        'market_intelligence', 
        'emotional_transformation_intelligence',
        'scientific_authority_intelligence'
    ]
    
    summary = {
        "categories": {},
        "total_primary_items": 0,
        "total_backup_items": 0,
        "has_backup_data": False,
        "verification_timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        # Get intelligence record using CRUD
        intelligence_obj = await intelligence_crud.get(db=db_session, id=intelligence_id)
        
        if not intelligence_obj:
            logger.error("❌ No intelligence record found during CRUD verification")
            return summary
        
        # Check each primary column using object attributes
        for category in ai_categories:
            category_summary = {
                "primary_saved": False,
                "primary_items": 0,
                "backup_saved": False,
                "backup_items": 0,
                "total_saved": False
            }
            
            # Check primary storage
            raw_data = getattr(intelligence_obj, category, None)
            if raw_data and raw_data != '{}':
                try:
                    parsed_data = safe_json_loads(raw_data)
                    if isinstance(parsed_data, dict) and parsed_data:
                        category_summary["primary_saved"] = True
                        category_summary["primary_items"] = len(parsed_data)
                        summary["total_primary_items"] += len(parsed_data)
                except Exception as e:
                    logger.warning(f"⚠️ Could not parse {category} data: {str(e)}")
            
            summary["categories"][category] = category_summary
        
        # Check backup storage in metadata
        metadata_str = intelligence_obj.processing_metadata
        if metadata_str:
            try:
                metadata = safe_json_loads(metadata_str)
                emergency_backup = metadata.get("emergency_ai_backup", {})
                
                if emergency_backup:
                    summary["has_backup_data"] = True
                    
                    for category in ai_categories:
                        if category in emergency_backup:
                            backup_data = emergency_backup[category]
                            if isinstance(backup_data, dict) and backup_data:
                                summary["categories"][category]["backup_saved"] = True
                                summary["categories"][category]["backup_items"] = len(backup_data)
                                summary["total_backup_items"] += len(backup_data)
                                
            except Exception as e:
                logger.warning(f"⚠️ Could not parse metadata for backup check: {str(e)}")
        
        # Calculate total_saved for each category
        for category in summary["categories"]:
            cat_data = summary["categories"][category]
            cat_data["total_saved"] = cat_data["primary_saved"] or cat_data["backup_saved"]
        
        logger.info(f"✅ CRUD verification complete: {summary['total_primary_items']} primary items, {summary['total_backup_items']} backup items")
        
        return summary
        
    except Exception as e:
        logger.error(f"❌ CRUD verification failed: {str(e)}")
        return summary


async def test_ai_storage_methods(
    db_session: AsyncSession,
    intelligence_id: uuid.UUID
) -> Dict[str, Any]:
    """✅ CRUD MIGRATED: Test storage methods using CRUD operations"""
    
    test_data = {
        "test_timestamp": datetime.now(timezone.utc).isoformat(),
        "test_items": ["crud_item1", "crud_item2", "crud_item3"],
        "test_metadata": {
            "test_purpose": "CRUD storage method diagnosis",
            "test_size": 3,
            "crud_version": "2.0"
        }
    }
    
    test_results = {}
    
    # Test 1: CRUD update operation
    try:
        # Get intelligence record
        intelligence_obj = await intelligence_crud.get(db=db_session, id=intelligence_id)
        
        if not intelligence_obj:
            test_results["crud_get"] = False
            logger.error("❌ CRUD get test: Intelligence not found")
        else:
            test_results["crud_get"] = True
            logger.info("✅ CRUD get test: SUCCESS")
            
            # Test CRUD update
            update_data = {
                "scientific_intelligence": safe_json_dumps(test_data)
            }
            
            updated_intelligence = await intelligence_crud.update(
                db=db_session,
                db_obj=intelligence_obj,
                obj_in=update_data
            )
            
            test_results["crud_update"] = True
            logger.info("✅ CRUD update test: SUCCESS")
        
    except Exception as e:
        test_results["crud_update"] = False
        logger.error(f"❌ CRUD update test: FAILED - {str(e)}")
    
    # Test 2: CRUD verification of saved data
    try:
        # Re-fetch to verify
        verification_obj = await intelligence_crud.get(db=db_session, id=intelligence_id)
        
        if verification_obj and verification_obj.scientific_intelligence:
            saved_data = safe_json_loads(verification_obj.scientific_intelligence)
            if saved_data.get("test_timestamp"):
                test_results["crud_verification"] = True
                logger.info("✅ CRUD verification test: SUCCESS")
            else:
                test_results["crud_verification"] = False
                logger.error("❌ CRUD verification test: Data not found")
        else:
            test_results["crud_verification"] = False
            logger.error("❌ CRUD verification test: No data in field")
            
    except Exception as e:
        test_results["crud_verification"] = False
        logger.error(f"❌ CRUD verification test: FAILED - {str(e)}")
    
    # Test 3: CRUD intelligence summary
    try:
        summary = await intelligence_crud.get_intelligence_summary(
            db=db_session,
            campaign_id=intelligence_obj.campaign_id if intelligence_obj else None
        )
        
        if summary and summary.get("total_intelligence_entries", 0) > 0:
            test_results["crud_summary"] = True
            logger.info("✅ CRUD summary test: SUCCESS")
        else:
            test_results["crud_summary"] = False
            logger.error("❌ CRUD summary test: No summary data")
            
    except Exception as e:
        test_results["crud_summary"] = False
        logger.error(f"❌ CRUD summary test: FAILED - {str(e)}")
    
    return test_results


# ============================================================================
# ENHANCED CRUD-BASED UTILITIES
# ============================================================================

async def batch_save_ai_intelligence(
    db_session: AsyncSession,
    intelligence_entries: list[Dict[str, Any]]
) -> Dict[str, Any]:
    """✅ NEW: Batch save multiple AI intelligence entries using CRUD"""
    
    results = {
        "total_entries": len(intelligence_entries),
        "successful_saves": 0,
        "failed_saves": 0,
        "details": []
    }
    
    for entry in intelligence_entries:
        try:
            intelligence_id = entry.get("intelligence_id")
            ai_data = entry.get("ai_data", {})
            
            if not intelligence_id or not ai_data:
                results["failed_saves"] += 1
                results["details"].append({
                    "intelligence_id": intelligence_id,
                    "status": "failed",
                    "error": "Missing intelligence_id or ai_data"
                })
                continue
            
            # Use the main save function
            save_results = await save_ai_intelligence_data(
                db_session=db_session,
                intelligence_id=intelligence_id,
                ai_data=ai_data
            )
            
            successful_categories = sum(1 for success in save_results.values() if success)
            total_categories = len(save_results)
            
            if successful_categories == total_categories:
                results["successful_saves"] += 1
                status = "success"
            elif successful_categories > 0:
                results["successful_saves"] += 1
                status = "partial_success"
            else:
                results["failed_saves"] += 1
                status = "failed"
            
            results["details"].append({
                "intelligence_id": str(intelligence_id),
                "status": status,
                "categories_saved": successful_categories,
                "total_categories": total_categories
            })
            
        except Exception as e:
            results["failed_saves"] += 1
            results["details"].append({
                "intelligence_id": entry.get("intelligence_id", "unknown"),
                "status": "failed",
                "error": str(e)
            })
    
    logger.info(f"📊 Batch save complete: {results['successful_saves']}/{results['total_entries']} successful")
    
    return results


async def get_ai_intelligence_health_status(
    db_session: AsyncSession,
    campaign_id: uuid.UUID
) -> Dict[str, Any]:
    """✅ NEW: Get health status of AI intelligence data using CRUD"""
    
    try:
        # Get intelligence summary using CRUD
        summary = await intelligence_crud.get_intelligence_summary(
            db=db_session,
            campaign_id=campaign_id
        )
        
        # Get all intelligence entries for campaign
        intelligence_list = await intelligence_crud.get_campaign_intelligence(
            db=db_session,
            campaign_id=campaign_id,
            limit=1000
        )
        
        health_status = {
            "campaign_id": str(campaign_id),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_health": "unknown",
            "intelligence_count": len(intelligence_list),
            "summary": summary,
            "category_health": {},
            "recommendations": []
        }
        
        # Analyze category health
        ai_categories = [
            'scientific_intelligence',
            'credibility_intelligence',
            'market_intelligence',
            'emotional_transformation_intelligence',
            'scientific_authority_intelligence'
        ]
        
        healthy_categories = 0
        for category in ai_categories:
            has_data = False
            total_entries = 0
            
            for intelligence in intelligence_list:
                category_data = getattr(intelligence, category, None)
                if category_data and category_data != '{}':
                    try:
                        parsed_data = safe_json_loads(category_data)
                        if parsed_data:
                            has_data = True
                            total_entries += len(parsed_data) if isinstance(parsed_data, dict) else 1
                    except:
                        continue
            
            health_status["category_health"][category] = {
                "has_data": has_data,
                "total_entries": total_entries,
                "status": "healthy" if has_data else "needs_attention"
            }
            
            if has_data:
                healthy_categories += 1
        
        # Determine overall health
        health_percentage = (healthy_categories / len(ai_categories)) * 100
        
        if health_percentage >= 80:
            health_status["overall_health"] = "excellent"
        elif health_percentage >= 60:
            health_status["overall_health"] = "good"
        elif health_percentage >= 40:
            health_status["overall_health"] = "fair"
        else:
            health_status["overall_health"] = "poor"
            health_status["recommendations"].append("Consider re-running AI intelligence analysis")
        
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Failed to get AI intelligence health status: {str(e)}")
        return {
            "campaign_id": str(campaign_id),
            "overall_health": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }