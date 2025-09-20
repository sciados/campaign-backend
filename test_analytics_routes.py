#!/usr/bin/env python3
"""
Quick test script to verify analytics routes are working
Run this after backend is deployed to test the endpoints
"""

import requests
import json

# Base URL - update this to your deployed backend URL
BASE_URL = "https://campaign-backend-production-e2db.up.railway.app"

def test_analytics_endpoints():
    """Test all analytics endpoints"""

    # You'll need a valid auth token to test these endpoints
    # This is just a structure - replace with actual testing

    endpoints = [
        "/api/analytics/dashboard",
        "/api/analytics/products",
        "/api/clickbank/connect",
        "/api/analytics/refresh"
    ]

    print("🧪 Testing Analytics Endpoints")
    print("=" * 50)

    for endpoint in endpoints:
        url = BASE_URL + endpoint
        print(f"Testing: {endpoint}")

        try:
            # Test without auth to see if endpoint exists (will return 401 if exists)
            response = requests.get(url, timeout=5)

            if response.status_code == 404:
                print(f"❌ {endpoint} - NOT FOUND (404)")
            elif response.status_code == 401:
                print(f"✅ {endpoint} - EXISTS (needs auth)")
            elif response.status_code == 405:
                print(f"✅ {endpoint} - EXISTS (wrong method)")
            else:
                print(f"✅ {endpoint} - EXISTS (status: {response.status_code})")

        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - ERROR: {e}")

    print("\n🎯 Summary:")
    print("- If endpoints show '404', routes aren't registered")
    print("- If endpoints show '401', routes are working (need auth)")
    print("- If endpoints show '405', routes exist but wrong HTTP method")

if __name__ == "__main__":
    test_analytics_endpoints()