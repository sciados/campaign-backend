# src/content/generators/__init__.py
"""
Content Generators Module

This module contains all content generation classes for different content types.
Text-based: Email, Social Media, Blog, Ad Copy
Multimedia: Image, Video Script
"""

from src.content.generators.email_generator import EmailGenerator
from src.content.generators.social_media_generator import SocialMediaGenerator
from src.content.generators.blog_content_generator import BlogContentGenerator
from src.content.generators.ad_copy_generator import AdCopyGenerator
from src.content.generators.image_generator import ImageGenerator
from src.content.generators.video_script_generator import VideoScriptGenerator


def get_available_generators():
    """
    Get list of available generator classes.

    Returns:
        List of available generator class names
    """
    return [
        "EmailGenerator",
        "SocialMediaGenerator",
        "BlogContentGenerator",
        "AdCopyGenerator",
        "ImageGenerator",
        "VideoScriptGenerator"
    ]


def get_generator_count():
    """Get the number of available generators"""
    return len(__all__)


__all__ = [
    "EmailGenerator",
    "SocialMediaGenerator",
    "BlogContentGenerator",
    "AdCopyGenerator",
    "ImageGenerator",
    "VideoScriptGenerator",
    "get_available_generators",
    "get_generator_count"
]