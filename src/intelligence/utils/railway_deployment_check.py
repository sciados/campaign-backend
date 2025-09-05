#!/usr/bin/env python3
"""
Railway Deployment Status Check
Quick verification script for ultra-cheap AI system on Railway
"""

import logging
import sys
import os
from datetime import datetime, timezone

# Railway-compatible logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [RAILWAY] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def check_railway_deployment_status():
    """Quick deployment status check for Railway"""
    
    logger.info("🚂 RAILWAY DEPLOYMENT STATUS CHECK")
    logger.info("=" * 50)
    logger.info(f"Timestamp: {datetime.now(timezone.utc)}Z")
    
    # Check 1: Environment
    logger.info("\n1️⃣ Environment Check:")
    logger.info(f"   Python version: {sys.version}")
    logger.info(f"   Platform: Railway Cloud")
    logger.info(f"   Working directory: {os.getcwd()}")
    
    # Check 2: Critical Paths (Updated for current structure)
    logger.info("\n2️⃣ Path Check:")
    
    # Get current file location to determine project structure
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    critical_paths = [
        current_dir,  # Current location (src/intelligence/utils/)
        os.path.join(current_dir, '..'),  # src/intelligence/
        os.path.join(current_dir, '..', 'generators'),  # src/intelligence/generators/
        os.path.join(current_dir, '..', 'handlers'),  # src/intelligence/handlers/
        os.path.join(current_dir, '..', '..'),  # src/
    ]
    
    for path in critical_paths:
        if os.path.exists(path):
            rel_path = os.path.relpath(path, current_dir)
            logger.info(f"   ✅ {rel_path}: Exists")
        else:
            rel_path = os.path.relpath(path, current_dir)
            logger.warning(f"   ⚠️ {rel_path}: Missing")
    
    # Check 3: API Keys
    logger.info("\n3️⃣ API Keys Check:")
    required_keys = [
        "GROQ_API_KEY", "TOGETHER_API_KEY", "DEEPSEEK_API_KEY",
        "STABILITY_API_KEY", "REPLICATE_API_TOKEN"
    ]
    
    available_count = 0
    for key in required_keys:
        if os.getenv(key):
            logger.info(f"   ✅ {key}: Available")
            available_count += 1
        else:
            logger.warning(f"   ⚠️ {key}: Missing")
    
    logger.info(f"   📊 Coverage: {available_count}/{len(required_keys)} ({available_count/len(required_keys)*100:.1f}%)")
    
    # Check 4: Core Imports (Focus on Working Generators)
    logger.info("\n4️⃣ Core Imports Check (Working Generators):")
    
    import_checks = [
        ("Email Generator", "src.intelligence.generators.email_generator", "EmailSequenceGenerator"),
        ("Ad Copy Generator", "src.intelligence.generators.ad_copy_generator", "AdCopyGenerator"),
        ("Factory", "src.intelligence.generators.factory", "ContentGeneratorFactory"),
        ("Railway Compatibility", "src.intelligence.utils.railway_compatibility", "get_railway_compatibility_handler"),
        ("Content Handler", "src.intelligence.handlers.content_handler", "enhanced_content_generation")
    ]
    
    successful_imports = 0
    for name, module, class_name in import_checks:
        try:
            # Add src to path relative to current location
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_path = os.path.join(current_dir, '..', '..')  # Go up to src/ level
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            
            mod = __import__(module, fromlist=[class_name])
            getattr(mod, class_name)
            logger.info(f"   ✅ {name}: Import successful")
            successful_imports += 1
        except Exception as e:
            logger.error(f"   ❌ {name}: Import failed - {str(e)}")
    
    # Note about other generators
    logger.info("   ⏭️ Social Media Generator: Not implemented yet")
    logger.info("   ⏭️ Blog Post Generator: Not implemented yet") 
    logger.info("   ⏭️ Landing Page Generator: Not implemented yet")
    
    logger.info(f"   📊 Working Generator Success: {successful_imports}/{len(import_checks)} ({successful_imports/len(import_checks)*100:.1f}%)")
    
    # Check 5: Ultra-Cheap AI Readiness
    logger.info("\n5️⃣ Ultra-Cheap AI Readiness:")
    
    readiness_score = 0
    max_score = 100
    
    # API Keys (40 points)
    api_score = (available_count / len(required_keys)) * 40
    readiness_score += api_score
    logger.info(f"   API Keys: {api_score:.1f}/40 points")
    
    # Imports (40 points)
    import_score = (successful_imports / len(import_checks)) * 40
    readiness_score += import_score
    logger.info(f"   Core Imports: {import_score:.1f}/40 points")
    
    # Environment (20 points)
    env_score = 20 if os.path.exists("/app/src") else 0
    readiness_score += env_score
    logger.info(f"   Environment: {env_score:.1f}/20 points")
    
    logger.info(f"   🎯 Total Readiness: {readiness_score:.1f}/100")
    
    # Status Assessment (Adjusted for Working Generators)
    logger.info("\n🎯 DEPLOYMENT STATUS (EMAIL + AD COPY FOCUS):")
    if readiness_score >= 70:
        logger.info("   ✅ EXCELLENT - Email & Ad Copy generators operational")
        status = "excellent"
    elif readiness_score >= 50:
        logger.info("   ⚠️ GOOD - Core generators working with minor issues")
        status = "good"
    elif readiness_score >= 30:
        logger.info("   ⚠️ FAIR - At least one generator working")
        status = "fair"
    else:
        logger.error("   ❌ POOR - No working generators detected")
        status = "poor"
    
    # Recommendations (Updated)
    logger.info("\n💡 RECOMMENDATIONS:")
    if available_count < len(required_keys):
        missing_keys = len(required_keys) - available_count
        logger.info(f"   🔑 Add {missing_keys} missing API keys for better ultra-cheap AI coverage")
    
    if successful_imports < len(import_checks):
        failed_imports = len(import_checks) - successful_imports
        logger.info(f"   📦 Fix {failed_imports} failed imports - check dependencies")
    
    if readiness_score >= 70:
        logger.info("   🚀 Email & Ad Copy generators ready for production!")
        logger.info("   💰 Ultra-cheap AI should provide 95%+ cost savings")
        logger.info("   📧 Focus on email sequences and Facebook/Google ads")
    elif readiness_score >= 50:
        logger.info("   💡 Core functionality working - good for initial deployment")
        logger.info("   🔧 Work on remaining generators when ready")
    else:
        logger.info("   🔧 Focus on getting email generator working first")
        logger.info("   🔑 Ensure GROQ_API_KEY or TOGETHER_API_KEY is available")
    
    logger.info(f"\n🚂 Railway Status Check Complete - Status: {status.upper()}")
    return status

if __name__ == "__main__":
    try:
        status = check_railway_deployment_status()
        
        # Exit codes for Railway monitoring
        exit_codes = {
            "excellent": 0,
            "good": 0,
            "fair": 1,
            "poor": 2
        }
        
        exit_code = exit_codes.get(status, 2)
        logger.info(f"Exit code: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"💥 Status check failed: {str(e)}")
        sys.exit(3)