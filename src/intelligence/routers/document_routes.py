# src/intelligence/routers/document_routes.py
"""
DOCUMENT MANAGEMENT ROUTES
✅ Complete document upload and management API
✅ Support for PDF, DOC, DOCX, TXT, MD files
✅ Dual storage with automatic failover
✅ Document preview generation
✅ Text extraction for search
✅ Metadata management and tagging
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from typing import Dict, List, Any, Optional
import logging
import json
import io
from datetime import datetime

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models import CampaignAsset
from src.storage.document_manager import DocumentManager
from src.storage.universal_dual_storage import get_storage_manager

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    campaign_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string array
    metadata: Optional[str] = Form(None),  # JSON string
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload document with validation and dual storage"""
    
    try:
        # Parse optional fields
        document_tags = []
        if tags:
            try:
                document_tags = json.loads(tags)
            except json.JSONDecodeError:
                document_tags = [tag.strip() for tag in tags.split(",")]
        
        file_metadata = {}
        if metadata:
            try:
                file_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                logger.warning(f"Invalid metadata JSON: {metadata}")
        
        # Initialize document manager
        document_manager = DocumentManager()
        
        # Upload document
        result = await document_manager.upload_document(
            file=file,
            user_id=str(current_user.id),
            campaign_id=campaign_id,
            metadata=file_metadata
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Document upload failed"))
        
        # Save to database
        asset = CampaignAsset(
            campaign_id=campaign_id,
            uploaded_by=current_user.id,
            company_id=current_user.company_id,
            asset_name=result["document"]["filename"],
            original_filename=file.filename,
            asset_type="document",
            mime_type=file.content_type,
            file_size=result["document"]["file_size"],
            file_url_primary=result["document"]["providers"]["primary"]["url"],
            file_url_backup=result["document"]["providers"]["backup"]["url"],
            storage_status=result["document"]["storage_status"],
            content_category="user_uploaded",
            asset_metadata=result["metadata"],
            tags=document_tags,
            description=description or f"Document: {file.filename}"
        )
        
        db.add(asset)
        await db.commit()
        
        # Create response
        response_data = {
            "success": True,
            "document_id": str(asset.id),
            "filename": asset.asset_name,
            "original_filename": file.filename,
            "file_size": asset.file_size,
            "file_type": result["file_type"],
            "storage_status": asset.storage_status,
            "primary_url": asset.file_url_primary,
            "backup_url": asset.file_url_backup,
            "preview_available": result["preview"] is not None,
            "text_extracted": len(result["text_content"]) > 0,
            "word_count": result["metadata"].get("word_count", 0),
            "page_count": result["metadata"].get("page_count", 1),
            "tags": document_tags,
            "description": description,
            "created_at": asset.created_at.isoformat()
        }
        
        # Add preview URL if available
        if result["preview"]:
            preview_asset = CampaignAsset(
                campaign_id=campaign_id,
                uploaded_by=current_user.id,
                company_id=current_user.company_id,
                asset_name=result["preview"]["filename"],
                original_filename=f"preview_{file.filename}.jpg",
                asset_type="image",
                mime_type="image/jpeg",
                file_size=result["preview"]["file_size"],
                file_url_primary=result["preview"]["providers"]["primary"]["url"],
                file_url_backup=result["preview"]["providers"]["backup"]["url"],
                storage_status=result["preview"]["storage_status"],
                content_category="system_generated",
                asset_metadata={"preview_for": str(asset.id)},
                description=f"Preview for {file.filename}"
            )
            
            db.add(preview_asset)
            await db.commit()
            
            response_data["preview_id"] = str(preview_asset.id)
            response_data["preview_url"] = preview_asset.file_url_primary
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    download: bool = Query(False, description="Download file instead of redirect"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document with automatic failover"""
    
    try:
        # Get document from database
        asset_query = select(CampaignAsset).where(
            and_(
                CampaignAsset.id == document_id,
                CampaignAsset.uploaded_by == current_user.id,
                CampaignAsset.asset_type == "document"
            )
        )
        result = await db.execute(asset_query)
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update access statistics
        asset.access_count += 1
        asset.last_accessed = datetime.utcnow()
        await db.commit()
        
        # Get best available URL with failover
        storage_manager = get_storage_manager()
        best_url = await storage_manager.get_content_url_with_failover(
            primary_url=asset.file_url_primary,
            backup_url=asset.file_url_backup,
            preferred_provider=asset.active_provider
        )
        
        if download:
            # Stream the file for download
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(best_url) as response:
                        if response.status == 200:
                            content = await response.read()
                            
                            return StreamingResponse(
                                io.BytesIO(content),
                                media_type=asset.mime_type,
                                headers={
                                    "Content-Disposition": f"attachment; filename={asset.original_filename}"
                                }
                            )
                        else:
                            raise HTTPException(status_code=response.status, detail="Failed to download document")
            except Exception as e:
                logger.error(f"Document download failed: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Document download failed: {str(e)}")
        else:
            # Redirect to document URL
            return RedirectResponse(url=best_url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document retrieval failed: {str(e)}")

@router.get("/{document_id}/info")
async def get_document_info(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document information and metadata"""
    
    try:
        # Get document from database
        asset_query = select(CampaignAsset).where(
            and_(
                CampaignAsset.id == document_id,
                CampaignAsset.uploaded_by == current_user.id,
                CampaignAsset.asset_type == "document"
            )
        )
        result = await db.execute(asset_query)
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get preview if available
        preview_query = select(CampaignAsset).where(
            and_(
                CampaignAsset.asset_metadata["preview_for"].astext == document_id,
                CampaignAsset.uploaded_by == current_user.id,
                CampaignAsset.asset_type == "image"
            )
        )
        preview_result = await db.execute(preview_query)
        preview_asset = preview_result.scalar_one_or_none()
        
        return {
            "document_id": str(asset.id),
            "filename": asset.asset_name,
            "original_filename": asset.original_filename,
            "file_size": asset.file_size,
            "mime_type": asset.mime_type,
            "storage_status": asset.storage_status,
            "primary_url": asset.file_url_primary,
            "backup_url": asset.file_url_backup,
            "active_provider": asset.active_provider,
            "content_category": asset.content_category,
            "tags": asset.tags,
            "description": asset.description,
            "metadata": asset.asset_metadata,
            "access_count": asset.access_count,
            "last_accessed": asset.last_accessed.isoformat() if asset.last_accessed else None,
            "created_at": asset.created_at.isoformat(),
            "updated_at": asset.updated_at.isoformat(),
            "preview": {
                "available": preview_asset is not None,
                "preview_id": str(preview_asset.id) if preview_asset else None,
                "preview_url": preview_asset.file_url_primary if preview_asset else None
            } if preview_asset else {"available": False},
            "capabilities": {
                "can_download": True,
                "can_preview": preview_asset is not None,
                "can_search": asset.asset_metadata.get("word_count", 0) > 0,
                "can_edit_metadata": True,
                "can_delete": True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document info retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document info retrieval failed: {str(e)}")

@router.get("/{document_id}/preview")
async def get_document_preview(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document preview image"""
    
    try:
        # Get preview asset
        preview_query = select(CampaignAsset).where(
            and_(
                CampaignAsset.asset_metadata["preview_for"].astext == document_id,
                CampaignAsset.uploaded_by == current_user.id,
                CampaignAsset.asset_type == "image"
            )
        )
        result = await db.execute(preview_query)
        preview_asset = result.scalar_one_or_none()
        
        if not preview_asset:
            raise HTTPException(status_code=404, detail="Document preview not found")
        
        # Get best available URL with failover
        storage_manager = get_storage_manager()
        best_url = await storage_manager.get_content_url_with_failover(
            primary_url=preview_asset.file_url_primary,
            backup_url=preview_asset.file_url_backup,
            preferred_provider=preview_asset.active_provider
        )
        
        return RedirectResponse(url=best_url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document preview retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document preview retrieval failed: {str(e)}")

@router.post("/{document_id}/regenerate-preview")
async def regenerate_document_preview(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Regenerate document preview"""
    
    try:
        # Get document
        asset_query = select(CampaignAsset).where(
            and_(
                CampaignAsset.id == document_id,
                CampaignAsset.uploaded_by == current_user.id,
                CampaignAsset.asset_type == "document"
            )
        )
        result = await db.execute(asset_query)
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Download document content
        storage_manager = get_storage_manager()
        content_url = await storage_manager.get_content_url_with_failover(
            primary_url=asset.file_url_primary,
            backup_url=asset.file_url_backup
        )
        
        # Download and regenerate preview
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(content_url) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Initialize document manager and regenerate preview
                    document_manager = DocumentManager()
                    file_type = asset.asset_metadata.get("document_type", "unknown")
                    
                    preview_data = await document_manager._generate_document_preview(content, file_type)
                    
                    if preview_data:
                        # Save new preview
                        preview_filename = f"preview_{asset.asset_name}.jpg"
                        preview_result = await storage_manager.save_content_dual_storage(
                            content_data=preview_data,
                            content_type="image",
                            filename=preview_filename,
                            user_id=str(current_user.id),
                            campaign_id=asset.campaign_id,
                            metadata={"preview_for": document_id, "regenerated": True}
                        )
                        
                        # Delete old preview if exists
                        old_preview_query = select(CampaignAsset).where(
                            and_(
                                CampaignAsset.asset_metadata["preview_for"].astext == document_id,
                                CampaignAsset.uploaded_by == current_user.id,
                                CampaignAsset.asset_type == "image"
                            )
                        )
                        old_preview_result = await db.execute(old_preview_query)
                        old_preview = old_preview_result.scalar_one_or_none()
                        
                        if old_preview:
                            await db.delete(old_preview)
                        
                        # Create new preview asset
                        new_preview = CampaignAsset(
                            campaign_id=asset.campaign_id,
                            uploaded_by=current_user.id,
                            company_id=current_user.company_id,
                            asset_name=preview_result["filename"],
                            original_filename=f"preview_{asset.original_filename}.jpg",
                            asset_type="image",
                            mime_type="image/jpeg",
                            file_size=preview_result["file_size"],
                            file_url_primary=preview_result["providers"]["primary"]["url"],
                            file_url_backup=preview_result["providers"]["backup"]["url"],
                            storage_status=preview_result["storage_status"],
                            content_category="system_generated",
                            asset_metadata=preview_result["metadata"],
                            description=f"Regenerated preview for {asset.original_filename}"
                        )
                        
                        db.add(new_preview)
                        await db.commit()
                        
                        return {
                            "success": True,
                            "preview_id": str(new_preview.id),
                            "preview_url": new_preview.file_url_primary,
                            "regenerated_at": datetime.utcnow().isoformat()
                        }
                    else:
                        raise HTTPException(status_code=400, detail="Preview generation failed")
                else:
                    raise HTTPException(status_code=response.status, detail="Failed to download document")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Preview regeneration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Preview regeneration failed: {str(e)}")

@router.get("/search")
async def search_documents(
    query: str = Query(..., description="Search query"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign"),
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search documents by content and metadata"""
    
    try:
        # Build search query
        search_query = select(CampaignAsset).where(
            and_(
                CampaignAsset.uploaded_by == current_user.id,
                CampaignAsset.asset_type == "document"
            )
        )
        
        # Add text search
        if query:
            search_conditions = [
                CampaignAsset.asset_name.ilike(f"%{query}%"),
                CampaignAsset.original_filename.ilike(f"%{query}%"),
                CampaignAsset.description.ilike(f"%{query}%"),
                CampaignAsset.asset_metadata["text_content"].astext.ilike(f"%{query}%")
            ]
            search_query = search_query.where(or_(*search_conditions))
        
        # Add campaign filter
        if campaign_id:
            search_query = search_query.where(CampaignAsset.campaign_id == campaign_id)
        
        # Add file type filter
        if file_type:
            search_query = search_query.where(
                CampaignAsset.asset_metadata["document_type"].astext == file_type
            )
        
        # Add tags filter
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            for tag in tag_list:
                search_query = search_query.where(
                    CampaignAsset.tags.op("@>")(json.dumps([tag]))
                )
        
        # Apply pagination
        search_query = search_query.offset(offset).limit(limit)
        
        # Execute search
        result = await db.execute(search_query)
        documents = result.scalars().all()
        
        # Format results
        search_results = []
        for doc in documents:
            search_results.append({
                "document_id": str(doc.id),
                "filename": doc.asset_name,
                "original_filename": doc.original_filename,
                "file_size": doc.file_size,
                "file_type": doc.asset_metadata.get("document_type", "unknown"),
                "word_count": doc.asset_metadata.get("word_count", 0),
                "page_count": doc.asset_metadata.get("page_count", 1),
                "tags": doc.tags,
                "description": doc.description,
                "campaign_id": str(doc.campaign_id) if doc.campaign_id else None,
                "created_at": doc.created_at.isoformat(),
                "last_accessed": doc.last_accessed.isoformat() if doc.last_accessed else None,
                "access_count": doc.access_count,
                "storage_status": doc.storage_status,
                "preview_available": any(
                    asset.asset_metadata.get("preview_for") == str(doc.id)
                    for asset in documents if asset.asset_type == "image"
                )
            })
        
        # Get total count for pagination
        count_query = select(func.count(CampaignAsset.id)).where(
            and_(
                CampaignAsset.uploaded_by == current_user.id,
                CampaignAsset.asset_type == "document"
            )
        )
        
        if query:
            count_query = count_query.where(or_(*search_conditions))
        if campaign_id:
            count_query = count_query.where(CampaignAsset.campaign_id == campaign_id)
        if file_type:
            count_query = count_query.where(
                CampaignAsset.asset_metadata["document_type"].astext == file_type
            )
        
        total_count = await db.scalar(count_query)
        
        return {
            "success": True,
            "query": query,
            "results": search_results,
            "total_count": total_count,
            "returned_count": len(search_results),
            "offset": offset,
            "limit": limit,
            "has_more": (offset + len(search_results)) < total_count,
            "filters": {
                "campaign_id": campaign_id,
                "file_type": file_type,
                "tags": tags
            }
        }
        
    except Exception as e:
        logger.error(f"Document search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document search failed: {str(e)}")

@router.put("/{document_id}/metadata")
async def update_document_metadata(
    document_id: str,
    metadata_update: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update document metadata, tags, and description"""
    
    try:
        # Get document
        asset_query = select(CampaignAsset).where(
            and_(
                CampaignAsset.id == document_id,
                CampaignAsset.uploaded_by == current_user.id,
                CampaignAsset.asset_type == "document"
            )
        )
        result = await db.execute(asset_query)
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update allowed fields
        if "description" in metadata_update:
            asset.description = metadata_update["description"]
        
        if "tags" in metadata_update:
            asset.tags = metadata_update["tags"]
        
        if "custom_metadata" in metadata_update:
            # Merge custom metadata
            current_metadata = asset.asset_metadata or {}
            current_metadata.update(metadata_update["custom_metadata"])
            asset.asset_metadata = current_metadata
        
        # Update timestamp
        asset.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "success": True,
            "document_id": document_id,
            "updated_fields": list(metadata_update.keys()),
            "updated_at": asset.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document metadata update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document metadata update failed: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    delete_preview: bool = Query(True, description="Also delete preview image"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete document and optionally its preview"""
    
    try:
        # Get document
        asset_query = select(CampaignAsset).where(
            and_(
                CampaignAsset.id == document_id,
                CampaignAsset.uploaded_by == current_user.id,
                CampaignAsset.asset_type == "document"
            )
        )
        result = await db.execute(asset_query)
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete preview if requested
        if delete_preview:
            preview_query = select(CampaignAsset).where(
                and_(
                    CampaignAsset.asset_metadata["preview_for"].astext == document_id,
                    CampaignAsset.uploaded_by == current_user.id,
                    CampaignAsset.asset_type == "image"
                )
            )
            preview_result = await db.execute(preview_query)
            preview_asset = preview_result.scalar_one_or_none()
            
            if preview_asset:
                await db.delete(preview_asset)
        
        # Delete document
        await db.delete(asset)
        await db.commit()
        
        return {
            "success": True,
            "document_id": document_id,
            "deleted_at": datetime.utcnow().isoformat(),
            "preview_deleted": delete_preview
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document deletion failed: {str(e)}")

@router.get("/stats")
async def get_document_stats(
    campaign_id: Optional[str] = Query(None, description="Filter by campaign"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document statistics"""
    
    try:
        # Build base query
        base_query = select(CampaignAsset).where(
            and_(
                CampaignAsset.uploaded_by == current_user.id,
                CampaignAsset.asset_type == "document"
            )
        )
        
        if campaign_id:
            base_query = base_query.where(CampaignAsset.campaign_id == campaign_id)
        
        # Get all documents
        result = await db.execute(base_query)
        documents = result.scalars().all()
        
        # Calculate statistics
        total_documents = len(documents)
        total_size = sum(doc.file_size for doc in documents)
        total_words = sum(doc.asset_metadata.get("word_count", 0) for doc in documents)
        total_pages = sum(doc.asset_metadata.get("page_count", 1) for doc in documents)
        
        # File type distribution
        file_types = {}
        for doc in documents:
            file_type = doc.asset_metadata.get("document_type", "unknown")
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        # Storage status distribution
        storage_status = {}
        for doc in documents:
            status = doc.storage_status
            storage_status[status] = storage_status.get(status, 0) + 1
        
        # Recent activity
        recent_documents = sorted(documents, key=lambda x: x.created_at, reverse=True)[:5]
        
        return {
            "success": True,
            "stats": {
                "total_documents": total_documents,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "total_words": total_words,
                "total_pages": total_pages,
                "average_words_per_document": round(total_words / max(total_documents, 1), 2),
                "average_pages_per_document": round(total_pages / max(total_documents, 1), 2)
            },
            "distribution": {
                "file_types": file_types,
                "storage_status": storage_status
            },
            "recent_documents": [
                {
                    "document_id": str(doc.id),
                    "filename": doc.original_filename,
                    "created_at": doc.created_at.isoformat(),
                    "file_size": doc.file_size,
                    "file_type": doc.asset_metadata.get("document_type", "unknown")
                }
                for doc in recent_documents
            ],
            "campaign_id": campaign_id,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Document stats failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document stats failed: {str(e)}")

@router.get("/health")
async def document_system_health(
    current_user: User = Depends(get_current_user)
):
    """Get document system health status"""
    
    try:
        # Check storage health
        storage_manager = get_storage_manager()
        storage_health = await storage_manager.get_storage_health()
        
        # Check document manager
        document_manager = DocumentManager()
        
        return {
            "success": True,
            "system_health": {
                "document_manager": "operational",
                "storage_system": storage_health["overall_status"],
                "supported_formats": list(document_manager.supported_formats.keys()),
                "storage_providers": storage_health["providers"]
            },
            "capabilities": {
                "upload": True,
                "preview_generation": True,
                "text_extraction": True,
                "search": True,
                "dual_storage": True,
                "automatic_failover": True
            },
            "user_id": str(current_user.id),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Document health check failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }