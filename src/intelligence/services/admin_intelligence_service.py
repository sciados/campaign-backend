# =====================================
# File: src/intelligence/services/admin_intelligence_service.py
# =====================================

"""
Admin Intelligence Service for pre-populating the URL cache library.

Enables admins and product creators to pre-analyze high-value URLs before
launch, ensuring affiliate marketers get instant results from day one.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.core.shared.decorators import log_execution_time
from src.core.shared.exceptions import ValidationError, ServiceUnavailableError
from src.intelligence.models.intelligence_models import (
    IntelligenceRequest,
    AnalysisMethod,
    AnalysisResult
)
from src.intelligence.services.intelligence_service import IntelligenceService
from src.intelligence.repositories.intelligence_repository import IntelligenceRepository
from src.intelligence.models.product_creator_submission import ProductCreatorSubmission, SubmissionStatus

logger = logging.getLogger(__name__)


class AdminIntelligenceService:
    """Service for admin pre-population of URL intelligence cache."""

    def __init__(self):
        self.intelligence_service = IntelligenceService()
        self.intelligence_repo = IntelligenceRepository()

    @log_execution_time()
    async def bulk_analyze_urls(
        self,
        urls: List[str],
        admin_user_id: str,
        analysis_method: AnalysisMethod = AnalysisMethod.ENHANCED,
        batch_size: int = 5,
        delay_between_batches: float = 10.0,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Bulk analyze URLs for pre-populating the affiliate cache.

        Perfect for admins working with product creators to pre-analyze
        high-value sales pages before launch.

        Args:
            urls: List of URLs to analyze
            admin_user_id: Admin user performing the pre-population
            analysis_method: Analysis depth (recommend ENHANCED for cache)
            batch_size: URLs to process in parallel per batch
            delay_between_batches: Seconds to wait between batches
            session: Database session

        Returns:
            Dict with success/failure counts and detailed results
        """
        logger.info(f"🏭 ADMIN PRE-POPULATION: Starting bulk analysis of {len(urls)} URLs")

        results = {
            "total_urls": len(urls),
            "successful": 0,
            "failed": 0,
            "cached": 0,
            "processed": 0,
            "details": [],
            "start_time": datetime.now(),
            "admin_user": admin_user_id
        }

        # Process URLs in batches to prevent API overload
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(urls) + batch_size - 1) // batch_size

            logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} URLs)")

            # Process batch in parallel
            batch_tasks = []
            for url in batch:
                task = self._analyze_single_url_for_cache(
                    url=url,
                    admin_user_id=admin_user_id,
                    analysis_method=analysis_method,
                    session=session
                )
                batch_tasks.append(task)

            # Execute batch
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Process batch results
            for url, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"❌ Failed to analyze {url}: {result}")
                    results["failed"] += 1
                    results["details"].append({
                        "url": url,
                        "status": "failed",
                        "error": str(result),
                        "batch": batch_num
                    })
                else:
                    if result["cached"]:
                        results["cached"] += 1
                        status = "cached"
                    else:
                        results["processed"] += 1
                        status = "processed"

                    results["successful"] += 1
                    results["details"].append({
                        "url": url,
                        "status": status,
                        "intelligence_id": result["intelligence_id"],
                        "confidence_score": result["confidence_score"],
                        "processing_time_ms": result["processing_time_ms"],
                        "batch": batch_num
                    })

                    logger.info(f"✅ {url} - {status} (confidence: {result['confidence_score']})")

            # Delay between batches (except for last batch)
            if batch_num < total_batches:
                logger.info(f"⏱️  Batch delay: waiting {delay_between_batches}s before next batch...")
                await asyncio.sleep(delay_between_batches)

        results["end_time"] = datetime.now()
        results["total_duration"] = (results["end_time"] - results["start_time"]).total_seconds()

        logger.info(f"🎉 BULK ANALYSIS COMPLETE: {results['successful']}/{results['total_urls']} successful")
        logger.info(f"   📊 Processed: {results['processed']}, Cached: {results['cached']}, Failed: {results['failed']}")
        logger.info(f"   ⏱️  Total time: {results['total_duration']:.1f}s")

        return results

    async def _analyze_single_url_for_cache(
        self,
        url: str,
        admin_user_id: str,
        analysis_method: AnalysisMethod,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Analyze a single URL for cache pre-population."""
        request = IntelligenceRequest(
            salespage_url=url,
            analysis_method=analysis_method,
            force_refresh=False  # Use cache if available
        )

        result = await self.intelligence_service.analyze_url(
            request=request,
            user_id=admin_user_id,
            company_id="admin_pre_population",
            session=session
        )

        return {
            "intelligence_id": result.intelligence_id,
            "cached": result.cached,
            "confidence_score": result.analysis_result.confidence_score,
            "processing_time_ms": result.processing_time_ms
        }

    async def get_cache_statistics(
        self,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Get statistics about the current URL cache library."""

        # Get total intelligence records
        all_intelligence = await self.intelligence_repo.find_all(
            session=session,
            limit=10000  # Large limit to get all records
        )

        # Group by URL to get unique URLs
        url_stats = {}
        for intel in all_intelligence:
            url = intel.salespage_url
            if url not in url_stats:
                url_stats[url] = {
                    "url": url,
                    "analysis_count": 0,
                    "highest_confidence": 0,
                    "latest_analysis": None,
                    "analysis_methods": set()
                }

            url_stats[url]["analysis_count"] += 1
            url_stats[url]["highest_confidence"] = max(
                url_stats[url]["highest_confidence"],
                intel.confidence_score
            )
            url_stats[url]["analysis_methods"].add(intel.analysis_method)

            if (url_stats[url]["latest_analysis"] is None or
                intel.created_at > url_stats[url]["latest_analysis"]):
                url_stats[url]["latest_analysis"] = intel.created_at

        # Convert sets to lists for JSON serialization
        for stats in url_stats.values():
            stats["analysis_methods"] = list(stats["analysis_methods"])

        return {
            "total_unique_urls": len(url_stats),
            "total_intelligence_records": len(all_intelligence),
            "average_analyses_per_url": len(all_intelligence) / len(url_stats) if url_stats else 0,
            "url_details": list(url_stats.values())
        }

    async def suggest_high_value_urls(
        self,
        categories: List[str] = None,
        min_confidence: float = 0.8,
        session: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """
        Suggest high-value URLs that would benefit from pre-analysis.

        This could integrate with external data sources to identify
        trending products, high-converting sales pages, etc.
        """

        # For now, return URLs from existing high-confidence analyses
        filters = {"min_confidence": min_confidence}

        high_value_intelligence = await self.intelligence_repo.find_all(
            session=session,
            filters=filters,
            limit=50
        )

        suggestions = []
        for intel in high_value_intelligence:
            suggestions.append({
                "url": intel.salespage_url,
                "product_name": intel.product_name,
                "confidence_score": intel.confidence_score,
                "analysis_method": intel.analysis_method,
                "created_at": intel.created_at,
                "reason": f"High confidence analysis ({intel.confidence_score:.2f})"
            })

        return suggestions

    async def create_product_creator_submission(
        self,
        urls: List[str],
        product_name: str,
        category: str,
        contact_email: str,
        submitter_user_id: Optional[str] = None,
        launch_date: Optional[str] = None,
        notes: Optional[str] = None,
        session: AsyncSession = None
    ) -> ProductCreatorSubmission:
        """
        Create a new product creator URL submission.

        Args:
            urls: List of URLs to analyze
            product_name: Name of the product
            category: Product category
            contact_email: Contact email for updates
            submitter_user_id: ID of user submitting (if logged in)
            launch_date: Expected launch date
            notes: Additional notes
            session: Database session

        Returns:
            ProductCreatorSubmission: Created submission record
        """
        submission = ProductCreatorSubmission(
            product_name=product_name,
            category=category,
            urls=urls,
            contact_email=contact_email,
            submitter_user_id=submitter_user_id,
            launch_date=launch_date,
            notes=notes,
            status=SubmissionStatus.PENDING_REVIEW.value
        )

        session.add(submission)
        await session.commit()

        logger.info(f"📝 PRODUCT CREATOR SUBMISSION: Created {submission.id} for {product_name}")
        logger.info(f"   📧 Contact: {contact_email}")
        logger.info(f"   🔗 URLs: {len(urls)} URLs submitted")
        logger.info(f"   🗓️  Launch: {launch_date or 'Not specified'}")

        return submission

    async def process_product_creator_submission(
        self,
        submission_id: str,
        approve: bool,
        admin_user_id: str,
        admin_notes: Optional[str] = None,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Process a product creator submission (approve or reject).

        Args:
            submission_id: ID of submission to process
            approve: Whether to approve the submission
            admin_user_id: ID of admin processing the submission
            admin_notes: Optional notes from admin
            session: Database session

        Returns:
            Dict with processing results
        """
        # Get the submission
        submission = await session.get(ProductCreatorSubmission, submission_id)
        if not submission:
            raise ValueError(f"Submission {submission_id} not found")

        if approve:
            # Update submission status
            submission.status = SubmissionStatus.PROCESSING.value
            submission.processed_by_admin_id = admin_user_id
            submission.admin_notes = admin_notes
            submission.processed_at = datetime.now()

            await session.commit()

            # Process URLs with bulk analysis
            logger.info(f"🔄 PROCESSING SUBMISSION: {submission_id} approved, starting analysis...")

            try:
                bulk_results = await self.bulk_analyze_urls(
                    urls=submission.urls,
                    admin_user_id=admin_user_id,
                    analysis_method=AnalysisMethod.ENHANCED,
                    batch_size=3,  # Smaller batch for product creator submissions
                    delay_between_batches=15.0,  # Longer delay for quality
                    session=session
                )

                # Update submission with results
                submission.status = SubmissionStatus.COMPLETED.value
                submission.intelligence_ids = [
                    detail["intelligence_id"] for detail in bulk_results["details"]
                    if detail["status"] in ["processed", "cached"]
                ]
                submission.analysis_summary = {
                    "total_urls": bulk_results["total_urls"],
                    "successful": bulk_results["successful"],
                    "failed": bulk_results["failed"],
                    "cached": bulk_results["cached"],
                    "processed": bulk_results["processed"],
                    "processing_time_seconds": bulk_results["total_duration"]
                }
                submission.processing_time_seconds = str(bulk_results["total_duration"])
                submission.total_urls_processed = str(bulk_results["successful"])

                await session.commit()

                logger.info(f"✅ SUBMISSION COMPLETE: {submission_id} processed successfully")
                logger.info(f"   📊 Results: {bulk_results['successful']}/{bulk_results['total_urls']} successful")

                return {
                    "submission_id": submission_id,
                    "status": "approved_and_processed",
                    "bulk_results": bulk_results,
                    "intelligence_ids": submission.intelligence_ids
                }

            except Exception as e:
                # Mark submission as failed
                submission.status = SubmissionStatus.FAILED.value
                submission.admin_notes = f"{admin_notes or ''}\n\nProcessing failed: {str(e)}"
                await session.commit()

                logger.error(f"❌ SUBMISSION FAILED: {submission_id} - {str(e)}")
                raise

        else:
            # Reject submission
            submission.status = SubmissionStatus.REJECTED.value
            submission.processed_by_admin_id = admin_user_id
            submission.admin_notes = admin_notes
            submission.processed_at = datetime.now()

            await session.commit()

            logger.info(f"❌ SUBMISSION REJECTED: {submission_id}")

            return {
                "submission_id": submission_id,
                "status": "rejected",
                "admin_notes": admin_notes
            }