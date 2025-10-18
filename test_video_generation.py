#!/usr/bin/env python3
"""
Simple test script for video generation system
Tests core components without full application dependencies
"""

import sys
import os
import tempfile
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_video_generation_components():
    """Test video generation components in isolation"""

    print("Testing Video Generation System Components...")
    print("=" * 50)

    # Test 1: Import test for core video generation modules
    try:
        print("1. Testing imports...")

        # Test slideshow generator import (without database dependencies)
        print("   -> Testing slideshow generator components...")

        # Test individual functions that don't require DB
        from src.intelligence.utils.product_name_fix import extract_product_name_from_intelligence

        # Test sample intelligence data processing
        sample_intelligence = {
            "product_analysis": {"name": "Test Product"},
            "source_title": "Amazing Product Sales Page",
            "offer_intelligence": {"benefits": ["Benefit 1", "Benefit 2"]}
        }

        product_name = extract_product_name_from_intelligence(sample_intelligence)
        print(f"   [OK] Product name extraction: {product_name}")

        # Test enum serializer
        from src.intelligence.utils.enum_serializer import EnumSerializerMixin
        print("   [OK] Enum serializer import successful")

        print("   [OK] Core imports successful")

    except ImportError as e:
        print(f"   [FAIL] Import failed: {e}")
        return False
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False

    # Test 2: Video specification and data structures
    try:
        print("\n2. Testing video data structures...")

        # Test video assembly pipeline structures
        from src.content.services.video_assembly_pipeline import VideoScene, VideoSpec

        # Create test video scene
        test_scene = VideoScene(
            scene_id="test_scene_1",
            image_path="/tmp/test_image.jpg",
            audio_path=None,
            duration=3.0,
            transition_type="fade"
        )

        # Create test video spec
        test_spec = VideoSpec(
            width=1920,
            height=1080,
            fps=30,
            bitrate="2M"
        )

        print(f"   [OK] Video scene created: {test_scene.scene_id}")
        print(f"   [OK] Video spec created: {test_spec.width}x{test_spec.height}")

    except Exception as e:
        print(f"   [FAIL] Data structure test failed: {e}")
        return False

    # Test 3: Test utility functions
    try:
        print("\n3. Testing utility functions...")

        # Test placeholder fix function
        from src.content.generators.slideshow_video_generator import fix_slideshow_video_placeholders

        test_result = {
            "video_title": "{{PRODUCT_NAME}} Review",
            "description": "Learn about {{BENEFITS}}"
        }

        test_intelligence = {
            "product_analysis": {"name": "SuperProduct"},
            "offer_intelligence": {"benefits": ["Great benefits", "Amazing results"]}
        }

        fixed_result = fix_slideshow_video_placeholders(test_result, test_intelligence)
        print(f"   [OK] Placeholder fix test: {fixed_result.get('placeholders_processed', False)}")

    except Exception as e:
        print(f"   [FAIL] Utility function test failed: {e}")
        return False

    # Test 4: FFmpeg availability check
    try:
        print("\n4. Testing FFmpeg availability...")

        import subprocess
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("   [OK] FFmpeg is available")
            # Get version info
            version_line = result.stdout.split('\n')[0]
            print(f"   [INFO] {version_line}")
        else:
            print("   [WARN] FFmpeg not available - video generation will use fallback")

    except FileNotFoundError:
        print("   [WARN] FFmpeg not found - video generation will use cloud providers")
    except Exception as e:
        print(f"   [WARN] FFmpeg check failed: {e}")

    # Test 5: File system operations
    try:
        print("\n5. Testing file system operations...")

        # Test temporary directory creation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test_video.mp4"

            # Write dummy data
            test_file.write_bytes(b"dummy video data")

            if test_file.exists():
                print(f"   [OK] File operations successful: {test_file.name}")
                print(f"   [INFO] Temp directory: {temp_path}")
            else:
                print("   [FAIL] File operations failed")
                return False

    except Exception as e:
        print(f"   [FAIL] File system test failed: {e}")
        return False

    print("\n" + "=" * 50)
    print("All component tests completed successfully!")
    print("\nSummary:")
    print("   [OK] Core imports working")
    print("   [OK] Data structures functional")
    print("   [OK] Utility functions operational")
    print("   [OK] System dependencies checked")
    print("   [OK] File operations working")

    print("\nVideo generation system is ready for integration testing!")
    return True

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_video_generation_components())

    if success:
        print("\nTest passed - Video generation system components are functional")
        sys.exit(0)
    else:
        print("\nTest failed - Check error messages above")
        sys.exit(1)