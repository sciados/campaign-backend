"""
src/content/generators/__init__.py
Centralized, lazy-loaded generator exports for CampaignForge.
Prevents circular imports between content and generator factory modules.
"""

from typing import Any

__all__ = [
    "get_email_generator",
    "get_blog_generator",
    "get_video_generator",
    "get_social_generator",
    "get_factory",
]


def get_email_generator() -> Any:
    """Lazy import for EmailGenerator to avoid circular imports."""
    from src.content.generators.email_generator import EmailGenerator
    return EmailGenerator


def get_blog_generator() -> Any:
    """Lazy import for BlogGenerator."""
    from src.content.generators.blog_content_generator import BlogContentGenerator
    return BlogContentGenerator


def get_video_generator() -> Any:
    """Lazy import for VideoGenerator."""
    from src.content.generators.video_script_generator import VideoScriptGenerator
    return VideoScriptGenerator


def get_social_generator() -> Any:
    """Lazy import for SocialGenerator."""
    from src.content.generators.social_media_generator import SocialMediaGenerator
    return SocialMediaGenerator


def get_factory() -> Any:
    """Lazy import for ContentGeneratorFactory."""
    from src.content.generators.factory import ContentGeneratorFactory
    return ContentGeneratorFactory
