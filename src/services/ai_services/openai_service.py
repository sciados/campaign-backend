"""
OpenAI service for text and image generation
"""

import openai
from typing import Dict, List, Optional
import structlog

from src.core.config import settings

logger = structlog.get_logger()

class OpenAIService:
    """OpenAI API service wrapper"""

    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_text(
        self,
        prompt: str,
        model: str = "gpt-4",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """Generate text using OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error("OpenAI text generation failed", error=str(e))
            raise

    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "hd",
        style: str = "vivid"
    ) -> str:
        """Generate image using DALL-E 3"""
        try:
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
                n=1
            )

            return response.data[0].url

        except Exception as e:
            logger.error("OpenAI image generation failed", error=str(e))
            raise
