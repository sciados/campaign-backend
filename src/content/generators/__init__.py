# src/content/generators/__init__.py
"""
Content Generators Module

Contains all content generation classes for different content types.
Text-based: Email, Social Media, Blog, Ad Copy
Multimedia: Image, Video Script
"""

__all__ = [
    "get_available_generators",
    "get_generator_count"
]


def get_available_generators():
    """
    Return list of available generator classes.
    Classes are imported lazily to prevent circular imports.

    Returns:
        List[type]: Available generator classes
    """
    from src.content.generators.email_generator import EmailGenerator
    from src.content.generators.social_media_generator import SocialMediaGenerator
    from src.content.generators.blog_content_generator import BlogContentGenerator
    from src.content.generators.ad_copy_generator import AdCopyGenerator
    from src.content.generators.image_generator import ImageGenerator
    from src.content.generators.video_script_generator import VideoScriptGenerator
    from src.content.generators.long_form_article_generator import LongFormArticleGenerator

    return [
        EmailGenerator,
        SocialMediaGenerator,
        BlogContentGenerator,
        AdCopyGenerator,
        ImageGenerator,
        VideoScriptGenerator,
        LongFormArticleGenerator
    ]


def get_generator_count():
    """
    Get the number of available generator classes.

    Returns:
        int: Number of generators
    """
    return len(get_available_generators())
