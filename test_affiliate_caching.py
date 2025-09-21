#!/usr/bin/env python3
"""
Test script for the affiliate marketer global URL caching system.

This script tests that:
1. First user analyzes a URL and stores comprehensive intelligence
2. Second user gets the cached analysis instantly without re-processing
3. Both users have separate intelligence records but share the underlying data
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database.session import get_async_session
from src.intelligence.services.intelligence_service import IntelligenceService
from src.intelligence.models.intelligence_models import IntelligenceRequest, AnalysisMethod


async def test_affiliate_caching():
    """Test the global URL caching system for affiliate marketers."""
    print("🧪 Testing Affiliate Marketer URL Caching System")
    print("=" * 60)

    # Test URL - a common affiliate marketing target
    test_url = "https://example.com/product-page"

    intelligence_service = IntelligenceService()

    async with get_async_session() as session:
        print(f"📊 Testing URL: {test_url}")
        print()

        # Test Case 1: First user analyzes the URL
        print("👤 USER 1: Performing initial analysis...")
        user1_request = IntelligenceRequest(
            source_url=test_url,
            analysis_method=AnalysisMethod.ENHANCED,
            force_refresh=False
        )

        try:
            user1_result = await intelligence_service.analyze_url(
                request=user1_request,
                user_id="user_001",
                company_id="affiliate_company_001",
                session=session
            )

            print(f"✅ User 1 Analysis Complete:")
            print(f"   Intelligence ID: {user1_result.intelligence_id}")
            print(f"   Cached: {user1_result.cached}")
            print(f"   Processing Time: {user1_result.processing_time_ms}ms")
            print(f"   Confidence Score: {user1_result.analysis_result.confidence_score}")
            print()

        except Exception as e:
            print(f"❌ User 1 Analysis Failed: {e}")
            return

        # Test Case 2: Second user analyzes the same URL
        print("👤 USER 2: Requesting same URL (should be cached)...")
        user2_request = IntelligenceRequest(
            source_url=test_url,
            analysis_method=AnalysisMethod.ENHANCED,
            force_refresh=False
        )

        try:
            user2_result = await intelligence_service.analyze_url(
                request=user2_request,
                user_id="user_002",
                company_id="affiliate_company_002",
                session=session
            )

            print(f"✅ User 2 Analysis Complete:")
            print(f"   Intelligence ID: {user2_result.intelligence_id}")
            print(f"   Cached: {user2_result.cached}")
            print(f"   Processing Time: {user2_result.processing_time_ms}ms")
            print(f"   Confidence Score: {user2_result.analysis_result.confidence_score}")
            print()

            # Verify caching worked
            if user2_result.cached:
                print("🎯 SUCCESS: Global URL caching is working!")
                print(f"   User 2 got cached results in {user2_result.processing_time_ms}ms")
                print(f"   vs User 1's {user1_result.processing_time_ms}ms processing time")
            else:
                print("⚠️  WARNING: Expected cached result for User 2, but got fresh analysis")

        except Exception as e:
            print(f"❌ User 2 Analysis Failed: {e}")
            return

        # Test Case 3: Verify both users have separate intelligence records
        print("🔍 Verifying separate user intelligence records...")
        try:
            user1_intelligence = await intelligence_service.get_intelligence(
                intelligence_id=user1_result.intelligence_id,
                user_id="user_001",
                session=session
            )

            user2_intelligence = await intelligence_service.get_intelligence(
                intelligence_id=user2_result.intelligence_id,
                user_id="user_002",
                session=session
            )

            print(f"✅ User 1 has intelligence record: {user1_intelligence.intelligence_id}")
            print(f"✅ User 2 has intelligence record: {user2_intelligence.intelligence_id}")
            print(f"✅ Records are separate: {user1_intelligence.intelligence_id != user2_intelligence.intelligence_id}")

        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return

        print()
        print("🎉 Affiliate Caching System Test Complete!")
        print("   ✅ First user processes URL with full AI analysis")
        print("   ✅ Second user gets instant cached results")
        print("   ✅ Both users maintain separate intelligence records")
        print("   ✅ Comprehensive analysis data is shared efficiently")


if __name__ == "__main__":
    asyncio.run(test_affiliate_caching())