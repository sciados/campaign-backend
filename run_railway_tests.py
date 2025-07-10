#!/usr/bin/env python3
"""
Quick runner for Railway tests
"""
import subprocess
import sys
import os

def run_tests():
    print("🚂 Running Railway Ultra-Cheap AI Tests...")
    
    # Quick health check
    print("\n1️⃣ Running quick health check...")
    result1 = subprocess.run([
        sys.executable, 
        "src/intelligence/utils/railway_deployment_check.py"
    ], capture_output=True, text=True)
    
    print(result1.stdout)
    if result1.stderr:
        print("STDERR:", result1.stderr)
    
    # Full test
    print("\n2️⃣ Running full integration test...")
    result2 = subprocess.run([
        sys.executable, 
        "src/intelligence/utils/test_ultra_cheap_railway.py"
    ], capture_output=True, text=True)
    
    print(result2.stdout)
    if result2.stderr:
        print("STDERR:", result2.stderr)
    
    return result1.returncode == 0 and result2.returncode == 0

if __name__ == "__main__":
    success = run_tests()
    print(f"\n🎯 Tests {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)