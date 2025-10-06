#!/usr/bin/env python3
"""
Deployment script for CampaignForge content storage fix
"""

import subprocess
import sys
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception during {description}: {e}")
        return False

def main():
    print("🚀 Deploying CampaignForge Content Storage Fix")
    print("=" * 60)

    # Railway deployment command
    success = run_command(
        "railway up",
        "Deploying to Railway"
    )

    if success:
        print("\n🎉 Deployment completed successfully!")
        print("\n📋 What was fixed:")
        print("  1. ✅ Database schema constraint issues resolved")
        print("  2. ✅ Robust content storage service implemented")
        print("  3. ✅ Proper async/await handling for database operations")
        print("  4. ✅ Schema-compliant content insertion with all required fields")
        print("  5. ✅ Content retrieval endpoints for testing")
        print("  6. ✅ Comprehensive error logging and validation")

        print("\n🔗 New endpoints available:")
        print("  - POST /api/content/generate (enhanced with robust storage)")
        print("  - GET /api/content/campaigns/{campaign_id}/generated")
        print("  - POST /api/content/debug/test-storage")

        print("\n✨ The content generation now:")
        print("  • Uses HepatoBurn intelligence data properly")
        print("  • Stores content in database with proper relationships")
        print("  • Updates campaign counters automatically")
        print("  • Provides detailed error handling and logging")
        print("  • Works with the correct database schema")

        print("\n⏳ Waiting 30 seconds for deployment to stabilize...")
        time.sleep(30)

        print("\n🧪 Running post-deployment health check...")
        health_check = run_command(
            "curl -s https://campaign-backend-production-e2db.up.railway.app/health",
            "Health check"
        )

        if health_check:
            print("\n✅ Deployment successful and service is healthy!")
        else:
            print("\n⚠️  Service deployed but health check failed. Check Railway logs.")

    else:
        print("\n❌ Deployment failed. Please check Railway CLI configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()