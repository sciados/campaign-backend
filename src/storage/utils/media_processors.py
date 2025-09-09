# ============================================================================
# src/storage/utils/media_processors.py
# ============================================================================

"""
Media Processing Utilities

Helper functions for image and video processing, validation, and manipulation.
"""

import io
import logging
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageOps
from datetime import datetime

logger = logging.getLogger(__name__)

def resize_image(
    image_data: bytes,
    target_size: Tuple[int, int],
    maintain_aspect_ratio: bool = True,
    quality: int = 85
) -> Dict[str, Any]:
    """Resize image to target dimensions"""
    
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        original_size = image.size
        
        if maintain_aspect_ratio:
            # Calculate new size maintaining aspect ratio
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            new_size = image.size
        else:
            # Resize to exact dimensions
            image = image.resize(target_size, Image.Resampling.LANCZOS)
            new_size = target_size
        
        # Save to bytes
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='JPEG', quality=quality, optimize=True)
        resized_data = output_buffer.getvalue()
        
        return {
            "success": True,
            "image_data": resized_data,
            "original_size": original_size,
            "new_size": new_size,
            "original_file_size": len(image_data),
            "new_file_size": len(resized_data),
            "compression_ratio": round(len(resized_data) / len(image_data), 2)
        }
        
    except Exception as e:
        logger.error(f"Image resize failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def compress_image(
    image_data: bytes,
    quality: int = 85,
    optimize: bool = True
) -> Dict[str, Any]:
    """Compress image to reduce file size"""
    
    try:
        # Open image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Compress and save
        output_buffer = io.BytesIO()
        image.save(
            output_buffer, 
            format='JPEG', 
            quality=quality, 
            optimize=optimize
        )
        compressed_data = output_buffer.getvalue()
        
        return {
            "success": True,
            "image_data": compressed_data,
            "original_size": len(image_data),
            "compressed_size": len(compressed_data),
            "compression_ratio": round(len(compressed_data) / len(image_data), 2),
            "size_reduction_mb": round((len(image_data) - len(compressed_data)) / 1024 / 1024, 2),
            "quality_used": quality
        }
        
    except Exception as e:
        logger.error(f"Image compression failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def validate_image(image_data: bytes) -> Dict[str, Any]:
    """Validate image file and extract metadata"""
    
    try:
        # Open and validate image
        image = Image.open(io.BytesIO(image_data))
        
        # Extract metadata
        width, height = image.size
        format_name = image.format
        mode = image.mode
        
        # Check if image has transparency
        has_transparency = (
            mode in ('RGBA', 'LA') or 
            (mode == 'P' and 'transparency' in image.info)
        )
        
        # Calculate megapixels
        megapixels = round((width * height) / 1000000, 2)
        
        # Get file size info
        file_size = len(image_data)
        file_size_mb = round(file_size / 1024 / 1024, 2)
        
        # Check if image is valid
        image.verify()
        
        return {
            "is_valid": True,
            "width": width,
            "height": height,
            "format": format_name,
            "mode": mode,
            "has_transparency": has_transparency,
            "megapixels": megapixels,
            "file_size": file_size,
            "file_size_mb": file_size_mb,
            "aspect_ratio": round(width / height, 2) if height > 0 else 0,
            "is_square": width == height,
            "is_landscape": width > height,
            "is_portrait": height > width
        }
        
    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return {
            "is_valid": False,
            "error": str(e)
        }

def extract_video_metadata(file_path: str) -> Dict[str, Any]:
    """Extract video metadata (placeholder - requires ffprobe)"""
    
    try:
        # This would use ffprobe in a real implementation
        # For now, return basic info
        import os
        file_size = os.path.getsize(file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "file_size": file_size,
            "file_size_mb": round(file_size / 1024 / 1024, 2),
            "duration": None,  # Would extract with ffprobe
            "width": None,     # Would extract with ffprobe
            "height": None,    # Would extract with ffprobe
            "fps": None,       # Would extract with ffprobe
            "codec": None,     # Would extract with ffprobe
            "note": "Video metadata extraction requires ffprobe installation"
        }
        
    except Exception as e:
        logger.error(f"Video metadata extraction failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def validate_video_format(filename: str, file_data: bytes) -> Dict[str, Any]:
    """Validate video file format"""
    
    try:
        # Get file extension
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        # Supported video formats
        supported_formats = ['mp4', 'avi', 'mov', 'wmv', 'webm', 'mkv']
        
        # Check file signature (magic numbers)
        file_signatures = {
            'mp4': [b'\x00\x00\x00\x18ftypmp4', b'\x00\x00\x00\x20ftypmp4'],
            'avi': [b'RIFF'],
            'mov': [b'\x00\x00\x00\x14ftypqt'],
            'webm': [b'\x1a\x45\xdf\xa3']
        }
        
        is_valid_extension = extension in supported_formats
        
        # Check file signature
        signature_match = False
        detected_format = None
        
        for fmt, signatures in file_signatures.items():
            for signature in signatures:
                if file_data.startswith(signature):
                    signature_match = True
                    detected_format = fmt
                    break
            if signature_match:
                break
        
        return {
            "is_valid": is_valid_extension and signature_match,
            "filename": filename,
            "extension": extension,
            "detected_format": detected_format,
            "is_valid_extension": is_valid_extension,
            "signature_match": signature_match,
            "supported_formats": supported_formats,
            "file_size": len(file_data),
            "file_size_mb": round(len(file_data) / 1024 / 1024, 2)
        }
        
    except Exception as e:
        logger.error(f"Video validation failed: {e}")
        return {
            "is_valid": False,
            "error": str(e)
        }

def optimize_image_for_web(
    image_data: bytes,
    max_width: int = 1920,
    max_height: int = 1080,
    quality: int = 85
) -> Dict[str, Any]:
    """Optimize image for web usage"""
    
    try:
        # Validate image first
        validation = validate_image(image_data)
        if not validation["is_valid"]:
            return validation
        
        # Resize if too large
        if validation["width"] > max_width or validation["height"] > max_height:
            resize_result = resize_image(
                image_data, 
                (max_width, max_height), 
                maintain_aspect_ratio=True,
                quality=quality
            )
            if not resize_result["success"]:
                return resize_result
            optimized_data = resize_result["image_data"]
        else:
            # Just compress
            compress_result = compress_image(image_data, quality=quality)
            if not compress_result["success"]:
                return compress_result
            optimized_data = compress_result["image_data"]
        
        # Final validation
        final_validation = validate_image(optimized_data)
        
        return {
            "success": True,
            "optimized_image_data": optimized_data,
            "original_validation": validation,
            "final_validation": final_validation,
            "optimization_stats": {
                "original_size_mb": validation["file_size_mb"],
                "optimized_size_mb": final_validation["file_size_mb"],
                "size_reduction_percentage": round(
                    ((validation["file_size"] - final_validation["file_size"]) / validation["file_size"]) * 100, 2
                ),
                "space_saved_mb": round(
                    (validation["file_size"] - final_validation["file_size"]) / 1024 / 1024, 2
                )
            }
        }
        
    except Exception as e:
        logger.error(f"Image optimization failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def create_thumbnail(
    image_data: bytes,
    size: Tuple[int, int] = (150, 150),
    quality: int = 75
) -> Dict[str, Any]:
    """Create thumbnail from image"""
    
    try:
        # Open image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Create thumbnail
        image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Save to bytes
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='JPEG', quality=quality, optimize=True)
        thumbnail_data = output_buffer.getvalue()
        
        return {
            "success": True,
            "thumbnail_data": thumbnail_data,
            "thumbnail_size": image.size,
            "original_size": len(image_data),
            "thumbnail_file_size": len(thumbnail_data),
            "compression_ratio": round(len(thumbnail_data) / len(image_data), 3)
        }
        
    except Exception as e:
        logger.error(f"Thumbnail creation failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def get_image_dominant_colors(image_data: bytes, num_colors: int = 5) -> Dict[str, Any]:
    """Extract dominant colors from image"""
    
    try:
        # Open image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB
        image = image.convert('RGB')
        
        # Resize for faster processing
        image.thumbnail((150, 150))
        
        # Get colors (simplified approach)
        colors = image.getcolors(maxcolors=256*256*256)
        
        if colors:
            # Sort by frequency and get top colors
            sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
            dominant_colors = []
            
            for i, (count, color) in enumerate(sorted_colors[:num_colors]):
                dominant_colors.append({
                    "rank": i + 1,
                    "rgb": color,
                    "hex": "#{:02x}{:02x}{:02x}".format(*color),
                    "frequency": count
                })
            
            return {
                "success": True,
                "dominant_colors": dominant_colors,
                "total_colors_found": len(colors)
            }
        else:
            return {
                "success": False,
                "error": "Could not extract colors from image"
            }
        
    except Exception as e:
        logger.error(f"Color extraction failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def detect_image_content(image_data: bytes) -> Dict[str, Any]:
    """Basic image content detection"""
    
    try:
        validation = validate_image(image_data)
        if not validation["is_valid"]:
            return validation
        
        # Basic content analysis
        analysis = {
            "is_landscape": validation["is_landscape"],
            "is_portrait": validation["is_portrait"], 
            "is_square": validation["is_square"],
            "aspect_ratio": validation["aspect_ratio"],
            "megapixels": validation["megapixels"],
            "suitable_for_web": validation["width"] <= 1920 and validation["height"] <= 1080,
            "suitable_for_print": validation["width"] >= 300 and validation["height"] >= 300,
            "high_resolution": validation["megapixels"] > 2.0,
            "has_transparency": validation["has_transparency"]
        }
        
        # Determine likely use cases
        use_cases = []
        if analysis["suitable_for_web"]:
            use_cases.append("web_display")
        if analysis["is_landscape"] and analysis["high_resolution"]:
            use_cases.append("banner_header")
        if analysis["is_square"]:
            use_cases.append("social_media_post")
        if analysis["is_portrait"]:
            use_cases.append("mobile_display")
        if analysis["suitable_for_print"]:
            use_cases.append("print_material")
            
        return {
            "success": True,
            "content_analysis": analysis,
            "suggested_use_cases": use_cases,
            "optimization_recommendations": _get_optimization_recommendations(validation, analysis)
        }
        
    except Exception as e:
        logger.error(f"Image content detection failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def _get_optimization_recommendations(validation: Dict, analysis: Dict) -> List[str]:
    """Generate optimization recommendations"""
    recommendations = []
    
    if validation["file_size_mb"] > 5:
        recommendations.append("Consider compressing image to reduce file size")
    
    if validation["width"] > 1920 or validation["height"] > 1080:
        recommendations.append("Consider resizing for web usage")
    
    if not analysis["suitable_for_web"] and analysis["megapixels"] > 10:
        recommendations.append("Image may be too large for web display")
    
    if validation["format"] not in ["JPEG", "PNG", "WebP"]:
        recommendations.append("Consider converting to web-friendly format")
    
    if analysis["has_transparency"] and validation["format"] == "JPEG":
        recommendations.append("Consider PNG format to preserve transparency")
    
    return recommendations