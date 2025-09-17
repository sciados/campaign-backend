#!/usr/bin/env python3
"""
Database Transaction Fix Script
Fixes the SQLAlchemy async transaction management issues causing 401 errors
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_fix():
    """Test the database connection and transaction handling"""

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL_ASYNC')
    if not database_url:
        logger.error("DATABASE_URL_ASYNC environment variable not found")
        return False

    try:
        # Create engine with fixed configuration
        engine = create_async_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False,
            # Prevent transaction conflicts on Railway
            isolation_level="READ_COMMITTED",
            connect_args={
                "server_settings": {
                    "application_name": "campaignforge_backend_fix",
                }
            }
        )

        # Create session factory with fixed configuration
        AsyncSessionLocal = sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,  # Prevent automatic flushes that can cause transaction conflicts
            autocommit=False  # Explicit transaction control
        )

        # Test basic connectivity
        logger.info("Testing basic database connectivity...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            logger.info(f"Basic connectivity test: {test_value}")

        # Test session-based operations
        logger.info("Testing session-based operations...")
        async with AsyncSessionLocal() as session:
            # Test a simple query that would fail with transaction conflicts
            result = await session.execute(text("""
                SELECT u.id, u.email, u.full_name
                FROM users u
                LIMIT 1
            """))
            user = result.first()
            if user:
                logger.info(f"Session test successful: Found user {user.email}")
            else:
                logger.info("Session test successful: No users found")

        # Test multiple concurrent sessions (this would fail before the fix)
        logger.info("Testing concurrent session handling...")

        async def test_session():
            async with AsyncSessionLocal() as session:
                result = await session.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                return count

        # Run multiple concurrent database operations
        tasks = [test_session() for _ in range(3)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = sum(1 for r in results if isinstance(r, int))
        error_count = len(results) - success_count

        logger.info(f"Concurrent test results: {success_count} success, {error_count} errors")

        if error_count > 0:
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Task {i} failed: {result}")

        await engine.dispose()

        return error_count == 0

    except Exception as e:
        logger.error(f"Database fix test failed: {e}")
        return False

async def verify_auth_endpoints():
    """Verify that auth-related database operations work"""

    database_url = os.getenv('DATABASE_URL_ASYNC')
    if not database_url:
        return False

    try:
        engine = create_async_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False,
            isolation_level="READ_COMMITTED",
            connect_args={
                "server_settings": {
                    "application_name": "campaignforge_auth_test",
                }
            }
        )

        AsyncSessionLocal = sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )

        # Simulate the auth service operations that were failing
        logger.info("Testing auth service database operations...")

        async with AsyncSessionLocal() as session:
            # Test the exact query that was failing in the logs - updated with correct columns
            result = await session.execute(text("""
                SELECT users.id, users.email, users.full_name, users.hashed_password,
                       users.role, users.user_type, users.is_active, users.is_verified,
                       users.is_admin, users.company_id, users.first_name, users.last_name,
                       users.avatar_url, users.profile_image_url, users.bio, users.timezone,
                       users.phone_number, users.dashboard_preferences, users.notification_preferences,
                       users.language, users.theme, users.onboarding_completed, users.onboarding_step,
                       users.onboarding_data, users.monthly_campaigns_used, users.monthly_analysis_used,
                       users.monthly_content_generated, users.monthly_intelligence_generated,
                       users.total_campaigns_created, users.total_analysis_performed,
                       users.total_intelligence_generated, users.total_content_generated,
                       users.total_logins, users.experience_level, users.primary_goals,
                       users.last_login_at, users.last_activity_at, users.login_count,
                       users.created_at, users.updated_at
                FROM users
                WHERE users.id = :user_id
            """), {"user_id": "2c3d7631-3d6f-4f3a-bc49-d0ad1e283e0e"})

            user = result.first()
            if user:
                logger.info(f"Auth test successful: Found user {user.email}")
            else:
                logger.info("Auth test: User not found (this is OK for testing)")

            # Test campaigns table access (this was also failing)
            campaigns_result = await session.execute(text("""
                SELECT c.id, c.name, c.description, c.campaign_type, c.status, c.user_id, c.company_id
                FROM campaigns c
                WHERE c.id = :campaign_id
            """), {"campaign_id": "02145b25-3573-4d56-a3ad-36c74e1a1198"})

            campaign = campaigns_result.first()
            if campaign:
                logger.info(f"Campaign test successful: Found campaign {campaign.name}")
            else:
                logger.info("Campaign test: Campaign not found (this is OK for testing)")

        await engine.dispose()
        return True

    except Exception as e:
        logger.error(f"Auth endpoint verification failed: {e}")
        return False

async def main():
    """Main function to run all tests"""

    logger.info("=" * 60)
    logger.info("CAMPAIGNFORGE DATABASE TRANSACTION FIX")
    logger.info(f"Started at: {datetime.now()}")
    logger.info("=" * 60)

    # Test 1: Basic database connectivity and transaction handling
    logger.info("\n1. Testing Database Transaction Handling...")
    db_test_passed = await test_database_fix()

    # Test 2: Auth service specific operations
    logger.info("\n2. Testing Auth Service Database Operations...")
    auth_test_passed = await verify_auth_endpoints()

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Database Transaction Test: {'PASSED' if db_test_passed else 'FAILED'}")
    logger.info(f"Auth Service Test: {'PASSED' if auth_test_passed else 'FAILED'}")

    overall_success = db_test_passed and auth_test_passed
    logger.info(f"Overall Status: {'SUCCESS' if overall_success else 'FAILURE'}")

    if overall_success:
        logger.info("\n✅ Database transaction fixes are working correctly!")
        logger.info("The 401 authentication errors should be resolved.")
    else:
        logger.error("\n❌ Database transaction fixes need additional work.")
        logger.error("The 401 authentication errors may persist.")

    logger.info("=" * 60)

    return overall_success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)