"""
Product Image Scraper Service - Enhanced for SaaS Integration

Extracts product images from sales pages and saves to R2/Cloudflare storage.
Associates images with campaigns for later use in mockup generation.

Improvements:
- Async operations for better performance
- R2/Cloudflare storage integration
- Database persistence (campaign association)
- Smart product image detection (ML-ready)
- Duplicate detection
- Image quality analysis
- Automatic tagging (hero, product, lifestyle, etc.)
"""

from typing import List, Dict, Optional, Any, Tuple
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import urllib.parse
import re
from PIL import Image
import io
import logging
from dataclasses import dataclass
from datetime import datetime
import hashlib
import uuid

from src.storage.services.cloudflare_service import CloudflareService

logger = logging.getLogger(__name__)


@dataclass
class ScrapedImage:
    """Scraped image with metadata"""
    url: str
    width: int
    height: int
    file_size: int
    format: str
    alt_text: Optional[str]
    context: Optional[str]  # Surrounding text/heading
    is_hero: bool = False
    is_product: bool = False
    is_lifestyle: bool = False
    quality_score: float = 0.0
    duplicate_of: Optional[str] = None


@dataclass
class ScrapingResult:
    """Result of scraping operation"""
    success: bool
    campaign_id: str
    images_found: int
    images_saved: int
    images_skipped: int
    r2_paths: List[str]
    image_urls: List[str]
    metadata: List[Dict[str, Any]]
    error: Optional[str] = None


class ProductImageScraper:
    """
    Intelligent product image scraper with SaaS integration

    Features:
    - Async scraping for performance
    - R2 storage with CDN URLs
    - Smart filtering (product vs non-product)
    - Quality scoring
    - Duplicate detection
    - Campaign association
    """

    def __init__(self):
        self.r2_service = CloudflareService()
        self.session: Optional[aiohttp.ClientSession] = None
        self.seen_hashes: set = set()

        # Size thresholds - VERY RELAXED to capture more product images
        self.min_width = 100  # Minimum width (very permissive - just filter tiny icons)
        self.min_height = 100  # Minimum height (very permissive)
        self.min_file_size = 1 * 1024  # 1KB minimum (very small)
        self.max_file_size = 20 * 1024 * 1024  # 20MB maximum (very large)

        # Skip patterns (non-product images) - REDUCED to only obvious non-product images
        self.skip_patterns = [
            r'1x1\.',  # 1x1 tracking pixels
            r'pixel\.', r'tracker\.', r'analytics\.',
            r'favicon\.', r'spinner\.', r'loading\.',
            r'placeholder\.'
        ]

        # Product indicators (higher scores)
        self.product_indicators = [
            r'product', r'bottle', r'box', r'package',
            r'supplement', r'cover', r'mockup', r'hero',
            r'main', r'featured'
        ]

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def scrape_sales_page(
        self,
        url: str,
        campaign_id: str,
        max_images: int = 10
    ) -> ScrapingResult:
        """
        Scrape product images from sales page

        Args:
            url: Sales page URL
            campaign_id: Campaign to associate images with
            max_images: Maximum number of images to save

        Returns:
            ScrapingResult with saved image URLs and metadata
        """

        logger.info(f"🔍 Scraping product images from: {url}")
        logger.info(f"📁 Campaign ID: {campaign_id}")

        # Clear seen hashes for this scraping session (allow re-scraping same images)
        self.seen_hashes.clear()

        try:
            # Fetch page HTML
            html = await self._fetch_html(url)
            if not html:
                return ScrapingResult(
                    success=False,
                    campaign_id=campaign_id,
                    images_found=0,
                    images_saved=0,
                    images_skipped=0,
                    r2_paths=[],
                    image_urls=[],
                    metadata=[],
                    error="Failed to fetch page HTML"
                )

            # Parse and extract images
            soup = BeautifulSoup(html, 'html.parser')
            raw_images = self._extract_image_elements(soup)

            logger.info(f"📸 Found {len(raw_images)} potential images")

            # Analyze and score images
            analyzed_images = []
            skipped_reasons = {
                'no_url': 0,
                'skip_pattern': 0,
                'download_failed': 0,
                'file_size': 0,
                'duplicate': 0,
                'dimensions': 0,
                'analysis_error': 0
            }

            for img_element in raw_images:
                img_data = await self._analyze_image(img_element, url, skipped_reasons)
                if img_data:
                    analyzed_images.append(img_data)

            # Log filtering statistics
            logger.info(f"📊 Image analysis results:")
            logger.info(f"   - Total found: {len(raw_images)}")
            logger.info(f"   - Passed analysis: {len(analyzed_images)}")
            logger.info(f"   - Skipped reasons: {skipped_reasons}")

            if analyzed_images:
                scores = [img.quality_score for img in analyzed_images]
                logger.info(f"   - Quality scores: min={min(scores):.1f}, max={max(scores):.1f}, avg={sum(scores)/len(scores):.1f}")

            # Sort by quality score (best first)
            analyzed_images.sort(key=lambda x: x.quality_score, reverse=True)

            # Filter and limit
            selected_images = self._select_best_images(analyzed_images, max_images)

            logger.info(f"✅ Selected {len(selected_images)} high-quality product images")

            # Download and save to R2
            saved_images = []
            skipped = len(analyzed_images) - len(selected_images)

            for i, img_data in enumerate(selected_images):
                result = await self._download_and_save(
                    img_data,
                    campaign_id,
                    index=i
                )
                if result:
                    saved_images.append(result)

            # Extract URLs and metadata
            r2_paths = [img["r2_path"] for img in saved_images]
            image_urls = [img["url"] for img in saved_images]
            metadata = [img["metadata"] for img in saved_images]

            logger.info(f"💾 Saved {len(saved_images)} images to R2 storage")

            return ScrapingResult(
                success=True,
                campaign_id=campaign_id,
                images_found=len(raw_images),
                images_saved=len(saved_images),
                images_skipped=skipped,
                r2_paths=r2_paths,
                image_urls=image_urls,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"❌ Scraping error: {e}")
            return ScrapingResult(
                success=False,
                campaign_id=campaign_id,
                images_found=0,
                images_saved=0,
                images_skipped=0,
                r2_paths=[],
                image_urls=[],
                metadata=[],
                error=str(e)
            )

    async def _fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL"""
        try:
            # Follow redirects and get final URL
            async with self.session.get(url, allow_redirects=True) as response:
                final_url = str(response.url)
                if final_url != url:
                    logger.info(f"📍 Followed redirect: {url} → {final_url}")

                if response.status == 200:
                    html = await response.text()
                    logger.info(f"✅ Fetched HTML: {len(html)} bytes from {final_url}")
                    return html

                logger.error(f"HTTP {response.status} for {url} (final: {final_url})")
                return None
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def _extract_image_elements(self, soup: BeautifulSoup) -> List:
        """Extract all image elements from page"""
        images = []

        # Standard <img> tags
        for img in soup.find_all('img'):
            images.append(img)

        # Background images in style attributes
        for elem in soup.find_all(style=re.compile(r'background.*image')):
            images.append(elem)

        return images

    async def _analyze_image(
        self,
        img_element,
        base_url: str,
        skipped_reasons: dict = None
    ) -> Optional[ScrapedImage]:
        """
        Analyze image element and score quality

        Returns ScrapedImage or None if should be skipped
        """

        # Extract URL
        img_url = self._extract_image_url(img_element)
        if not img_url:
            if skipped_reasons is not None:
                skipped_reasons['no_url'] += 1
            return None

        # Make absolute URL
        img_url = urllib.parse.urljoin(base_url, img_url)

        # Check skip patterns
        if self._should_skip_url(img_url):
            if skipped_reasons is not None:
                skipped_reasons['skip_pattern'] += 1
            logger.debug(f"⏩ Skipped (pattern match): {img_url}")
            return None

        # Download for analysis
        img_data = await self._download_image(img_url)
        if not img_data:
            if skipped_reasons is not None:
                skipped_reasons['download_failed'] += 1
            return None

        # Check file size
        if len(img_data) < self.min_file_size or len(img_data) > self.max_file_size:
            if skipped_reasons is not None:
                skipped_reasons['file_size'] += 1
            logger.debug(f"⏩ Skipped (file size {len(img_data)} bytes): {img_url}")
            return None

        # Check for duplicate
        img_hash = hashlib.md5(img_data).hexdigest()
        if img_hash in self.seen_hashes:
            if skipped_reasons is not None:
                skipped_reasons['duplicate'] += 1
            logger.debug(f"⏩ Duplicate image skipped: {img_url}")
            return None
        self.seen_hashes.add(img_hash)

        # Analyze dimensions and format
        try:
            image = Image.open(io.BytesIO(img_data))
            width, height = image.size
            img_format = image.format.lower() if image.format else 'unknown'

            # Check dimensions
            if width < self.min_width or height < self.min_height:
                if skipped_reasons is not None:
                    skipped_reasons['dimensions'] += 1
                logger.debug(f"⏩ Skipped (dimensions {width}x{height}): {img_url}")
                return None

            # Extract metadata
            alt_text = img_element.get('alt', '') or img_element.get('title', '')
            context = self._extract_context(img_element)

            # Calculate quality score
            quality_score = self._calculate_quality_score(
                width, height, len(img_data), img_url, alt_text, context
            )

            # Determine image type
            is_hero = self._is_hero_image(img_element, width, height, context)
            is_product = self._is_product_image(img_url, alt_text, context)
            is_lifestyle = self._is_lifestyle_image(img_url, alt_text, context)

            return ScrapedImage(
                url=img_url,
                width=width,
                height=height,
                file_size=len(img_data),
                format=img_format,
                alt_text=alt_text,
                context=context,
                is_hero=is_hero,
                is_product=is_product,
                is_lifestyle=is_lifestyle,
                quality_score=quality_score
            )

        except Exception as e:
            if skipped_reasons is not None:
                skipped_reasons['analysis_error'] += 1
            logger.debug(f"Failed to analyze image: {e}")
            return None

    def _extract_image_url(self, img_element) -> Optional[str]:
        """Extract image URL from element"""

        # Try various attributes
        for attr in ['src', 'data-src', 'data-original', 'data-lazy-src', 'data-srcset']:
            url = img_element.get(attr)
            if url:
                # Handle srcset (take first URL)
                if 'srcset' in attr and ' ' in url:
                    url = url.split()[0]
                return url

        # Check style attribute for background-image
        style = img_element.get('style', '')
        match = re.search(r'url\([\'"]?([^\'"]+)[\'"]?\)', style)
        if match:
            return match.group(1)

        return None

    def _should_skip_url(self, url: str) -> bool:
        """Check if URL matches skip patterns"""
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in self.skip_patterns)

    async def _download_image(self, url: str) -> Optional[bytes]:
        """Download image data"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                return None
        except Exception as e:
            logger.debug(f"Download failed for {url}: {e}")
            return None

    def _extract_context(self, img_element) -> Optional[str]:
        """Extract surrounding text context"""
        try:
            # Look for nearby headings or text
            parent = img_element.parent
            for _ in range(3):  # Check up to 3 levels
                if parent:
                    heading = parent.find(['h1', 'h2', 'h3'])
                    if heading:
                        return heading.get_text().strip()
                    parent = parent.parent
            return None
        except:
            return None

    def _calculate_quality_score(
        self,
        width: int,
        height: int,
        file_size: int,
        url: str,
        alt_text: str,
        context: Optional[str]
    ) -> float:
        """
        Calculate quality score (0-100)

        Factors:
        - Resolution (higher is better)
        - Aspect ratio (square/portrait better for products)
        - File size (not too small, not too large)
        - URL/alt text indicators
        - Context indicators
        """

        score = 0.0

        # Resolution score (0-30 points) - More generous scoring
        pixels = width * height
        if pixels >= 1000000:  # 1MP+
            score += 30
        elif pixels >= 500000:  # 500K+
            score += 28
        elif pixels >= 250000:  # 250K+
            score += 25
        elif pixels >= 100000:  # 100K+ (added tier)
            score += 20
        else:
            score += 15  # Base score increased from 10

        # Aspect ratio score (0-20 points) - More lenient
        aspect = width / height
        if 0.7 <= aspect <= 1.3:  # Square-ish (good for products)
            score += 20
        elif 0.4 <= aspect <= 2.5:  # Portrait/landscape (decent) - wider range
            score += 18
        else:
            score += 12  # Even extreme ratios get decent score

        # File size score (0-15 points) - More lenient
        if 20 * 1024 <= file_size <= 5 * 1024 * 1024:  # 20KB-5MB (wider sweet spot)
            score += 15
        elif file_size < 20 * 1024:
            score += 10  # Increased from 5
        else:
            score += 13  # Increased from 10

        # Product indicator score (0-20 points)
        text_to_check = f"{url} {alt_text} {context or ''}".lower()
        indicator_matches = sum(
            1 for indicator in self.product_indicators
            if re.search(indicator, text_to_check)
        )
        score += min(indicator_matches * 5, 20)

        # Position bonus (0-15 points)
        # Images earlier in page are often more important
        if 'hero' in text_to_check or 'main' in text_to_check:
            score += 15
        elif 'featured' in text_to_check:
            score += 10

        return min(score, 100.0)

    def _is_hero_image(
        self,
        img_element,
        width: int,
        height: int,
        context: Optional[str]
    ) -> bool:
        """Detect if image is likely a hero/main product image"""

        # Large dimensions
        if width >= 800 and height >= 600:
            return True

        # Hero indicators in context
        if context:
            hero_keywords = ['hero', 'main', 'featured', 'banner']
            if any(kw in context.lower() for kw in hero_keywords):
                return True

        # Check parent classes/IDs
        parent = img_element.parent
        if parent:
            classes = ' '.join(parent.get('class', []))
            elem_id = parent.get('id', '')
            if any(kw in f"{classes} {elem_id}".lower() for kw in ['hero', 'main', 'featured']):
                return True

        return False

    def _is_product_image(
        self,
        url: str,
        alt_text: str,
        context: Optional[str]
    ) -> bool:
        """Detect if image is likely a product shot"""

        text = f"{url} {alt_text} {context or ''}".lower()
        product_keywords = [
            'product', 'bottle', 'box', 'package', 'supplement',
            'jar', 'container', 'cover', 'book'
        ]

        return any(kw in text for kw in product_keywords)

    def _is_lifestyle_image(
        self,
        url: str,
        alt_text: str,
        context: Optional[str]
    ) -> bool:
        """Detect if image is a lifestyle/contextual shot"""

        text = f"{url} {alt_text} {context or ''}".lower()
        lifestyle_keywords = [
            'lifestyle', 'gym', 'fitness', 'workout', 'kitchen',
            'hand', 'person', 'using', 'holding', 'scene'
        ]

        return any(kw in text for kw in lifestyle_keywords)

    def _select_best_images(
        self,
        images: List[ScrapedImage],
        max_images: int
    ) -> List[ScrapedImage]:
        """
        Select best images with diversity - RELAXED CRITERIA

        Strategy:
        - Prioritize hero images (take more)
        - Include all product images up to limit
        - Include lifestyle images
        - Take images with quality_score > 40 (lowered threshold)
        - Favor diversity over perfect quality
        """

        selected = []

        # First priority: ALL hero images (they're usually good)
        hero_images = [img for img in images if img.is_hero]
        for img in hero_images[:max_images]:
            if len(selected) < max_images:
                selected.append(img)

        # Second priority: Product images (ANY quality score)
        product_images = [
            img for img in images
            if img.is_product and img not in selected
        ]
        for img in product_images[:max_images - len(selected)]:
            if len(selected) < max_images:
                selected.append(img)

        # Third priority: Lifestyle images (ANY quality score)
        lifestyle_images = [
            img for img in images
            if img.is_lifestyle and img not in selected
        ]
        for img in lifestyle_images[:max_images - len(selected)]:
            if len(selected) < max_images:
                selected.append(img)

        # Fill remaining slots with ANY image (no quality threshold)
        remaining = [img for img in images if img not in selected]
        for img in remaining[:max_images - len(selected)]:
            if len(selected) < max_images:
                selected.append(img)

        logger.info(f"📊 Selected breakdown: {len([i for i in selected if i.is_hero])} hero, "
                   f"{len([i for i in selected if i.is_product])} product, "
                   f"{len([i for i in selected if i.is_lifestyle])} lifestyle")

        return selected

    async def _download_and_save(
        self,
        img_data: ScrapedImage,
        campaign_id: str,
        index: int
    ) -> Optional[Dict[str, Any]]:
        """
        Download image and save to R2 storage

        Returns dict with r2_path, url, and metadata
        """

        try:
            # Download image
            image_bytes = await self._download_image(img_data.url)
            if not image_bytes:
                return None

            # Generate R2 key
            extension = f".{img_data.format}" if img_data.format != 'unknown' else '.jpg'

            # Create descriptive filename
            image_type = 'hero' if img_data.is_hero else ('product' if img_data.is_product else 'image')
            filename = f"{image_type}_{index+1:02d}{extension}"

            r2_key = f"campaigns/{campaign_id}/scraped-images/{filename}"

            # Upload to R2
            upload_result = await self.r2_service.upload_file(
                file_data=image_bytes,
                file_path=r2_key,
                content_type=f"image/{img_data.format}"
            )

            if not upload_result.get("success"):
                logger.error(f"R2 upload failed for {img_data.url}")
                return None

            logger.info(f"✅ Saved: {filename} ({img_data.width}x{img_data.height}, score: {img_data.quality_score:.1f})")

            return {
                "r2_path": r2_key,
                "url": upload_result.get("public_url") or upload_result.get("url", ""),
                "metadata": {
                    "original_url": img_data.url,
                    "width": img_data.width,
                    "height": img_data.height,
                    "file_size": img_data.file_size,
                    "format": img_data.format,
                    "alt_text": img_data.alt_text,
                    "context": img_data.context,
                    "is_hero": img_data.is_hero,
                    "is_product": img_data.is_product,
                    "is_lifestyle": img_data.is_lifestyle,
                    "quality_score": img_data.quality_score,
                    "scraped_at": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return None


# Factory function
def get_product_image_scraper() -> ProductImageScraper:
    """Get product image scraper instance"""
    return ProductImageScraper()
