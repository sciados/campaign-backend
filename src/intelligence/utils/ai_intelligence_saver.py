# src/intelligence/utils/ai_intelligence_saver.py
"""
Dedicated AI Intelligence Saver - Handles reliable storage of AI-generated intelligence data
CRITICAL MODULE: This handles the "NO DATA SAVED" issue by ensuring robust database storage
"""
import json
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import text

logger = logging.getLogger(__name__)

async def save_ai_intelligence_data(
    db_session: AsyncSession,
    intelligence_id: uuid.UUID,
    ai_data: Dict[str, Any],
    intelligence_obj: Any
) -> Dict[str, bool]:
    """
    FIXED: Reliable AI intelligence data saver with multiple fallback strategies
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
    
    logger.info(f"🔄 Starting AI intelligence save for {len(ai_data)} categories")
    
    # Method 1: Try ORM-based storage first
    for category in ai_categories:
        category_data = ai_data.get(category, {})
        
        if category_data and isinstance(category_data, dict):
            try:
                # Serialize and set on the intelligence object
                json_data = json.dumps(category_data)
                setattr(intelligence_obj, category, json_data)
                flag_modified(intelligence_obj, category)
                
                save_results[category] = True
                logger.info(f"✅ ORM save: {category} ({len(category_data)} items)")
                
            except Exception as e:
                logger.error(f"❌ ORM save failed for {category}: {str(e)}")
                save_results[category] = False
        else:
            logger.warning(f"⚠️ No data to save for {category}")
            save_results[category] = False
    
    # Method 2: If ORM failed, try direct SQL update
    failed_categories = [cat for cat, success in save_results.items() if not success]
    
    if failed_categories:
        logger.info(f"🔧 Trying direct SQL for {len(failed_categories)} failed categories")
        
        for category in failed_categories:
            category_data = ai_data.get(category, {})
            if category_data:
                try:
                    sql_success = await _direct_sql_update(
                        db_session, intelligence_id, category, category_data
                    )
                    if sql_success:
                        save_results[category] = True
                        logger.info(f"✅ SQL save: {category}")
                    else:
                        logger.error(f"❌ SQL save failed: {category}")
                        
                except Exception as e:
                    logger.error(f"❌ SQL save error for {category}: {str(e)}")
    
    # Method 3: Emergency metadata backup for any remaining failures
    still_failed = [cat for cat, success in save_results.items() if not success]
    
    if still_failed:
        logger.info(f"🚨 Emergency backup for {len(still_failed)} categories")
        
        emergency_success = await _emergency_metadata_backup(
            db_session, intelligence_obj, ai_data, still_failed
        )
        
        if emergency_success:
            for category in still_failed:
                save_results[category] = True
                logger.info(f"🚨 Emergency backup: {category}")
    
    # Log final results
    successful = sum(1 for success in save_results.values() if success)
    total = len(save_results)
    
    logger.info(f"📊 AI save results: {successful}/{total} categories successful")
    
    return save_results


async def _direct_sql_update(
    db_session: AsyncSession,
    intelligence_id: uuid.UUID,
    category: str,
    data: Dict[str, Any]
) -> bool:
    """Direct SQL update for a specific AI category"""
    
    try:
        json_data = json.dumps(data)
        
        update_sql = text(f"""
            UPDATE campaign_intelligence 
            SET {category} = :json_data::jsonb,
                updated_at = NOW()
            WHERE id = :intelligence_id
        """)
        
        await db_session.execute(update_sql, {
            'json_data': json_data,
            'intelligence_id': intelligence_id
        })
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Direct SQL update failed for {category}: {str(e)}")
        return False


async def _emergency_metadata_backup(
    db_session: AsyncSession,
    intelligence_obj: Any,
    ai_data: Dict[str, Any],
    failed_categories: list
) -> bool:
    """Emergency backup in processing_metadata"""
    
    try:
        # Get existing metadata
        existing_metadata = intelligence_obj.processing_metadata
        if existing_metadata:
            try:
                metadata = json.loads(existing_metadata)
            except:
                metadata = {}
        else:
            metadata = {}
        
        # Add emergency backup
        metadata["emergency_ai_backup"] = {}
        for category in failed_categories:
            if category in ai_data:
                metadata["emergency_ai_backup"][category] = ai_data[category]
        
        metadata["emergency_backup_applied"] = True
        metadata["emergency_backup_timestamp"] = datetime.datetime.now()
        metadata["emergency_backup_reason"] = "Primary AI storage methods failed"
        
        # Save metadata
        intelligence_obj.processing_metadata = json.dumps(metadata)
        flag_modified(intelligence_obj, 'processing_metadata')
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Emergency metadata backup failed: {str(e)}")
        return False


async def verify_ai_intelligence_storage(
    db_session: AsyncSession,
    intelligence_id: uuid.UUID
) -> Dict[str, Any]:
    """
    FIXED: Comprehensive verification of AI intelligence storage
    Returns detailed summary of what was actually saved
    """
    
    ai_categories = [
        'scientific_intelligence',
        'credibility_intelligence',
        'market_intelligence', 
        'emotional_transformation_intelligence',
        'scientific_authority_intelligence'
    ]
    
    # Check primary storage (individual columns)
    primary_query = text("""
        SELECT 
            scientific_intelligence::text,
            credibility_intelligence::text,
            market_intelligence::text,
            emotional_transformation_intelligence::text,
            scientific_authority_intelligence::text,
            processing_metadata::text
        FROM campaign_intelligence 
        WHERE id = :intelligence_id
    """)
    
    result = await db_session.execute(primary_query, {'intelligence_id': intelligence_id})
    row = result.fetchone()
    
    summary = {
        "categories": {},
        "total_primary_items": 0,
        "total_backup_items": 0,
        "has_backup_data": False
    }
    
    if not row:
        logger.error("❌ No intelligence record found during verification")
        return summary
    
    # Check each primary column
    for i, category in enumerate(ai_categories):
        category_summary = {
            "primary_saved": False,
            "primary_items": 0,
            "backup_saved": False,
            "backup_items": 0,
            "total_saved": False
        }
        
        # Check primary storage
        raw_data = row[i]
        if raw_data and raw_data != '{}':
            try:
                parsed_data = json.loads(raw_data)
                if isinstance(parsed_data, dict) and parsed_data:
                    category_summary["primary_saved"] = True
                    category_summary["primary_items"] = len(parsed_data)
                    summary["total_primary_items"] += len(parsed_data)
            except:
                pass
        
        summary["categories"][category] = category_summary
    
    # Check backup storage in metadata
    metadata_str = row[5]  # processing_metadata column
    if metadata_str:
        try:
            metadata = json.loads(metadata_str)
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
    
    return summary


async def test_ai_storage_methods(
    db_session: AsyncSession,
    intelligence_id: uuid.UUID
) -> Dict[str, Any]:
    """Test different storage methods to diagnose issues"""
    
    test_data = {
        "test_timestamp": datetime.datetime.now(),
        "test_items": ["item1", "item2", "item3"],
        "test_metadata": {
            "test_purpose": "Storage method diagnosis",
            "test_size": 3
        }
    }
    
    test_results = {}
    
    # Test 1: Direct SQL insert/update
    try:
        test_sql = text("""
            UPDATE campaign_intelligence 
            SET scientific_intelligence = :test_data::jsonb
            WHERE id = :intelligence_id
        """)
        
        await db_session.execute(test_sql, {
            'test_data': json.dumps(test_data),
            'intelligence_id': intelligence_id
        })
        await db_session.commit()
        
        test_results["direct_sql"] = True
        logger.info("✅ Direct SQL test: SUCCESS")
        
    except Exception as e:
        test_results["direct_sql"] = False
        logger.error(f"❌ Direct SQL test: FAILED - {str(e)}")
    
    # Test 2: Verify the test data was saved
    try:
        verify_sql = text("""
            SELECT scientific_intelligence::text
            FROM campaign_intelligence 
            WHERE id = :intelligence_id
        """)
        
        result = await db_session.execute(verify_sql, {'intelligence_id': intelligence_id})
        row = result.fetchone()
        
        if row and row[0]:
            saved_data = json.loads(row[0])
            if saved_data.get("test_timestamp"):
                test_results["data_verification"] = True
                logger.info("✅ Data verification test: SUCCESS")
            else:
                test_results["data_verification"] = False
                logger.error("❌ Data verification test: Data not found")
        else:
            test_results["data_verification"] = False
            logger.error("❌ Data verification test: No data in column")
            
    except Exception as e:
        test_results["data_verification"] = False
        logger.error(f"❌ Data verification test: FAILED - {str(e)}")
    
    return test_results