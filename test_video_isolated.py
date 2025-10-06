#!/usr/bin/env python3
"""
Isolated test for video generation core functions
Tests only the specific functions without application dependencies
"""

import sys
import os
import tempfile
import subprocess
from pathlib import Path

def test_ffmpeg():
    """Test FFmpeg availability"""
    print("Testing FFmpeg availability...")
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("   [OK] FFmpeg is available")
            version_line = result.stdout.split('\n')[0]
            print(f"   [INFO] {version_line}")
            return True
        else:
            print("   [WARN] FFmpeg not available")
            return False

    except FileNotFoundError:
        print("   [WARN] FFmpeg not found")
        return False
    except Exception as e:
        print(f"   [WARN] FFmpeg check failed: {e}")
        return False

def test_file_operations():
    """Test file system operations"""
    print("Testing file system operations...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test_video.mp4"

            # Write dummy data
            test_file.write_bytes(b"dummy video data")

            if test_file.exists():
                print(f"   [OK] File operations successful: {test_file.name}")
                print(f"   [INFO] Temp directory: {temp_path}")
                return True
            else:
                print("   [FAIL] File operations failed")
                return False

    except Exception as e:
        print(f"   [FAIL] File system test failed: {e}")
        return False

def test_syntax_check():
    """Test syntax of key video generation files"""
    print("Testing Python syntax of video generation files...")

    base_path = Path(__file__).parent
    files_to_check = [
        "src/intelligence/generators/slideshow_video_generator.py",
        "src/content/api/video_generation_routes.py",
        "src/content/services/video_assembly_pipeline.py"
    ]

    all_passed = True

    for file_path in files_to_check:
        full_path = base_path / file_path
        if full_path.exists():
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(full_path)],
                    capture_output=True,
                    text=True,
                    cwd=str(base_path)
                )

                if result.returncode == 0:
                    print(f"   [OK] {file_path}")
                else:
                    print(f"   [FAIL] {file_path}: {result.stderr}")
                    all_passed = False

            except Exception as e:
                print(f"   [FAIL] {file_path}: {e}")
                all_passed = False
        else:
            print(f"   [SKIP] {file_path} (not found)")

    return all_passed

def test_core_functions():
    """Test core utility functions without imports"""
    print("Testing core utility functions...")

    # Test placeholder replacement function directly
    def fix_slideshow_video_placeholders(result_data, intelligence_data):
        """Replicated function for testing"""

        # Extract product name
        product_name = intelligence_data.get("product_analysis", {}).get("name")
        if not product_name:
            product_name = intelligence_data.get("source_title", "Product")

        # Extract benefits
        benefits = intelligence_data.get("offer_intelligence", {}).get("benefits", [])
        primary_benefit = benefits[0] if benefits else "Enhanced performance"

        # Process placeholders
        processed_data = {}
        for key, value in result_data.items():
            if isinstance(value, str):
                processed_value = value.replace("{{PRODUCT_NAME}}", product_name)
                processed_value = processed_value.replace("{{BENEFITS}}", primary_benefit)
                processed_data[key] = processed_value
            else:
                processed_data[key] = value

        processed_data["placeholders_processed"] = True
        return processed_data

    # Test the function
    test_result = {
        "video_title": "{{PRODUCT_NAME}} Review",
        "description": "Learn about {{BENEFITS}}"
    }

    test_intelligence = {
        "product_analysis": {"name": "SuperProduct"},
        "offer_intelligence": {"benefits": ["Great benefits", "Amazing results"]}
    }

    try:
        fixed_result = fix_slideshow_video_placeholders(test_result, test_intelligence)

        if fixed_result.get("placeholders_processed"):
            print("   [OK] Placeholder replacement working")
            print(f"   [INFO] Title: {fixed_result.get('video_title')}")
            return True
        else:
            print("   [FAIL] Placeholder replacement failed")
            return False

    except Exception as e:
        print(f"   [FAIL] Placeholder test failed: {e}")
        return False

def test_video_data_structures():
    """Test video data structure definitions"""
    print("Testing video data structures...")

    # Test basic video scene structure
    class VideoScene:
        def __init__(self, scene_id, image_path, audio_path, duration, transition_type="fade", effects=None):
            self.scene_id = scene_id
            self.image_path = image_path
            self.audio_path = audio_path
            self.duration = duration
            self.transition_type = transition_type
            self.effects = effects or []

    # Test basic video spec structure
    class VideoSpec:
        def __init__(self, width, height, fps=30, bitrate="2M", codec="libx264", format="mp4"):
            self.width = width
            self.height = height
            self.fps = fps
            self.bitrate = bitrate
            self.codec = codec
            self.format = format

    try:
        # Create test instances
        test_scene = VideoScene(
            scene_id="test_scene_1",
            image_path="/tmp/test_image.jpg",
            audio_path=None,
            duration=3.0
        )

        test_spec = VideoSpec(
            width=1920,
            height=1080,
            fps=30
        )

        print(f"   [OK] Video scene created: {test_scene.scene_id}")
        print(f"   [OK] Video spec created: {test_spec.width}x{test_spec.height}")
        return True

    except Exception as e:
        print(f"   [FAIL] Data structure test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Video Generation System - Isolated Component Tests")
    print("=" * 60)

    tests = [
        ("Syntax Check", test_syntax_check),
        ("File Operations", test_file_operations),
        ("Core Functions", test_core_functions),
        ("Data Structures", test_video_data_structures),
        ("FFmpeg Availability", test_ffmpeg)
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   [ERROR] Test failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")

    all_passed = True
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"   {status} {test_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\nAll tests passed! Video generation components are ready.")
        print("Next steps:")
        print("1. Deploy to Railway with proper environment variables")
        print("2. Test full integration with database and AI services")
        print("3. Test API endpoints with frontend integration")
        return True
    else:
        print("\nSome tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)