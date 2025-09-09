# =====================================
# File: src/intelligence/analysis/analyzers.py
# =====================================

"""
Content analyzers for extracting intelligence from web content.

Provides web scraping, content preprocessing, and basic analysis capabilities.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re

from src.core.shared.decorators import retry_on_failure
from src.core.shared.exceptions import ValidationError, ServiceUnavailableError

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """Analyzer for web content scraping and preprocessing."""
    
    def __init__(self):
        self.session_timeout = aiohttp.ClientTimeout(total=30)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    @retry_on_failure(max_retries=2)
    async def scrape_content(self, url: str) -> Dict[str, Any]:
        """
        Scrape and preprocess content from URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dict[str, Any]: Processed content data
            
        Raises:
            ServiceUnavailableError: If scraping fails
            ValidationError: If URL is invalid
        """
        try:
            async with aiohttp.ClientSession(
                timeout=self.session_timeout,
                headers=self.headers
            ) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise ServiceUnavailableError(f"Failed to fetch {url}: HTTP {response.status}")
                    
                    html_content = await response.text()
                    
            # Parse HTML content
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract structured data
            content_data = {
                "url": url,
                "title": self._extract_title(soup),
                "meta_description": self._extract_meta_description(soup),
                "text": self._extract_text_content(soup),
                "headings": self._extract_headings(soup),
                "links": self._extract_links(soup, url),
                "images": self._extract_images(soup, url),
                "structured_data": self._extract_structured_data(soup)
            }
            
            # Content quality metrics
            content_data["quality_metrics"] = self._calculate_quality_metrics(content_data)
            
            logger.info(f"Successfully scraped {url} - {len(content_data['text'])} characters")
            return content_data
            
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error scraping {url}: {e}")
            raise ServiceUnavailableError(f"Failed to scrape {url}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            raise ServiceUnavailableError(f"Scraping failed: {str(e)}")
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Fallback to h1
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Fallback to Open Graph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        return ""
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from page."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, list]:
        """Extract heading structure."""
        headings = {}
        for i in range(1, 7):
            tag_name = f'h{i}'
            headings[tag_name] = [h.get_text().strip() for h in soup.find_all(tag_name)]
        
        return headings
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list:
        """Extract internal and external links."""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            links.append({
                "text": link.get_text().strip(),
                "url": absolute_url,
                "internal": urlparse(absolute_url).netloc == urlparse(base_url).netloc
            })
        
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> list:
        """Extract image information."""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            absolute_url = urljoin(base_url, src)
            images.append({
                "src": absolute_url,
                "alt": img.get('alt', ''),
                "title": img.get('title', '')
            })
        
        return images
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract structured data (JSON-LD, microdata, etc.)."""
        structured_data = {}
        
        # JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        if json_ld_scripts:
            import json
            json_ld_data = []
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    json_ld_data.append(data)
                except json.JSONDecodeError:
                    continue
            if json_ld_data:
                structured_data['json_ld'] = json_ld_data
        
        # Open Graph
        og_data = {}
        for meta in soup.find_all('meta', attrs={'property': re.compile(r'^og:')}):
            if meta.get('content'):
                property_name = meta['property'][3:]  # Remove 'og:' prefix
                og_data[property_name] = meta['content']
        if og_data:
            structured_data['open_graph'] = og_data
        
        return structured_data
    
    def _calculate_quality_metrics(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate content quality metrics."""
        text_length = len(content_data['text'])
        word_count = len(content_data['text'].split())
        
        return {
            "text_length": text_length,
            "word_count": word_count,
            "has_title": bool(content_data['title']),
            "has_meta_description": bool(content_data['meta_description']),
            "heading_count": sum(len(headings) for headings in content_data['headings'].values()),
            "link_count": len(content_data['links']),
            "image_count": len(content_data['images']),
            "has_structured_data": bool(content_data['structured_data'])
        }