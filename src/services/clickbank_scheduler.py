# src/services/clickbank_scheduler.py - Enhanced High-Converting Categories Scraper
import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import List, Dict, Any, Optional
from core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from bs4 import BeautifulSoup
import httpx
import re
from urllib.parse import urljoin, urlparse

# Import your database models
from models.clickbank import (
    ClickBankProduct, 
    ClickBankCategoryURL, 
    ScrapingSchedule, 
    ScrapingLog,
    ProductPerformance,
    UserClickBankFavorites
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedClickBankScheduler:
    """
    Enhanced scheduler for high-converting ClickBank categories
    Prioritizes top-performing niches and handles dynamic URL generation
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.scraper = EnhancedClickBankScraper(db)
        self.high_priority_categories = ['mmo', 'weightloss', 'relationships']
        self.medium_priority_categories = ['top', 'health', 'selfhelp', 'manifestation', 'anxiety']
    
    async def run_scheduled_scrapes(self):
        """Main scheduler loop with priority-based execution"""
        logger.info("Starting enhanced ClickBank scheduler...")
        
        while True:
            try:
                # Check for due scrapes every 5 minutes
                await self.check_and_run_due_scrapes()
                
                # Health check every hour
                if datetime.utcnow().minute == 0:
                    await self.perform_health_check()
                
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def check_and_run_due_scrapes(self):
        """Check for categories due for scraping, prioritizing high-converting niches"""
        now = datetime.utcnow()
        
        # Get due schedules ordered by priority
        due_schedules = self.db.query(ScrapingSchedule).filter(
            and_(
                ScrapingSchedule.is_enabled == True,
                or_(
                    ScrapingSchedule.next_scrape_at <= now,
                    ScrapingSchedule.next_scrape_at.is_(None)
                )
            )
        ).order_by(ScrapingSchedule.priority_level.desc()).all()
        
        # Process high-priority categories first
        for schedule in due_schedules:
            try:
                await self.scrape_category_enhanced(schedule)
                
                # Add delay between scrapes to avoid overwhelming ClickBank
                if schedule.category in self.high_priority_categories:
                    await asyncio.sleep(10)  # 10 second delay for high priority
                else:
                    await asyncio.sleep(30)  # 30 second delay for others
                    
            except Exception as e:
                logger.error(f"Failed to scrape {schedule.category}: {e}")
                await self.log_scraping_failure(schedule.category, str(e))
    
    async def scrape_category_enhanced(self, schedule: ScrapingSchedule):
        """Enhanced category scraping with performance tracking"""
        # Get category URL configuration
        category_config = self.db.query(ClickBankCategoryURL).filter(
            ClickBankCategoryURL.category == schedule.category
        ).first()
        
        if not category_config:
            logger.error(f"No URL configuration found for category: {schedule.category}")
            return
        
        # Create scraping log
        log = ScrapingLog(
            category=schedule.category,
            started_at=datetime.utcnow(),
            status='running'
        )
        self.db.add(log)
        self.db.commit()
        
        try:
            # Get dynamic URLs for this category
            urls = await self.get_dynamic_category_urls(category_config)
            
            all_products = []
            successful_urls = 0
            
            # Try each URL until we get sufficient products
            for url in urls:
                try:
                    logger.info(f"Scraping {schedule.category} from: {url}")
                    products = await self.scraper.scrape_url_products(
                        url, 
                        schedule.max_products_per_scrape
                    )
                    
                    if products:
                        all_products.extend(products)
                        successful_urls += 1
                        logger.info(f"Found {len(products)} products from {url}")
                        
                        # If we have enough products, stop trying more URLs
                        if len(all_products) >= schedule.max_products_per_scrape:
                            break
                            
                except Exception as e:
                    logger.warning(f"URL failed {url}: {e}")
                    continue
            
            # Store/update products in database
            added, updated = await self.store_products_enhanced(all_products, schedule.category)
            
            # Mark inactive products that weren't seen
            inactive_count = await self.mark_unseen_products_inactive(schedule.category, all_products)
            
            # Update performance scores
            await self.update_product_performance_scores(schedule.category, all_products)
            
            # Update schedule for next run
            schedule.last_scraped_at = datetime.utcnow()
            schedule.next_scrape_at = self.calculate_next_scrape_time(schedule)
            
            # Calculate success rate
            success_rate = (successful_urls / len(urls)) * 100 if urls else 0
            schedule.success_rate = success_rate
            
            # Complete log
            log.completed_at = datetime.utcnow()
            log.status = 'completed'
            log.products_found = len(all_products)
            log.products_added = added
            log.products_updated = updated
            log.products_marked_inactive = inactive_count
            log.scraping_duration_seconds = (log.completed_at - log.started_at).total_seconds()
            log.success_rate = success_rate
            log.data_quality_score = self.calculate_data_quality_score(all_products)
            
            self.db.commit()
            
            logger.info(f"✅ Scraped {schedule.category}: {added} added, {updated} updated, {inactive_count} marked inactive")
            
        except Exception as e:
            log.status = 'failed'
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()
            log.scraping_duration_seconds = (log.completed_at - log.started_at).total_seconds()
            self.db.commit()
            logger.error(f"❌ Scraping failed for {schedule.category}: {e}")
            raise
    
    async def get_dynamic_category_urls(self, category_config: ClickBankCategoryURL) -> List[str]:
        """Generate dynamic URLs for categories that need date/keyword updates"""
        urls = [category_config.primary_url]
        
        # Add backup URLs
        if category_config.backup_urls:
            urls.extend(category_config.backup_urls)
        
        # Handle dynamic URL generation for specific categories
        if category_config.category == 'new':
            # Update date for "new offers" to last 30 days
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            dynamic_url = f"https://accounts.clickbank.com/marketplace.htm#/results?activatedMin={thirty_days_ago}&sortField=popularity&sortDescending=false"
            urls.insert(0, dynamic_url)  # Try dynamic URL first
            
        elif category_config.category == 'mmo':
            # Update year for "make money online" searches
            current_year = datetime.now().year
            dynamic_url = f"https://accounts.clickbank.com/marketplace.htm#/results?includeKeywords=make+money+online+{current_year}&sortField=relevance"
            urls.insert(0, dynamic_url)
        
        return urls
    
    async def store_products_enhanced(self, products_data: List[dict], category: str) -> tuple[int, int]:
        """Enhanced product storage with duplicate prevention and data quality checks"""
        added = 0
        updated = 0
        
        for product_data in products_data:
            try:
                # Enhanced data validation
                if not self.validate_product_data(product_data):
                    logger.warning(f"Invalid product data skipped: {product_data.get('title', 'Unknown')}")
                    continue
                
                # Check if product exists by salespage_url (prevents duplicates)
                existing = self.db.query(ClickBankProduct).filter(
                    ClickBankProduct.salespage_url == product_data['salespage_url']
                ).first()
                
                if existing:
                    # Update existing product with enhanced data
                    self.update_existing_product(existing, product_data, category)
                    updated += 1
                else:
                    # Add new product with enhanced fields
                    new_product = self.create_new_product(product_data, category)
                    self.db.add(new_product)
                    added += 1
                    
            except Exception as e:
                logger.error(f"Error processing product {product_data.get('title', 'Unknown')}: {e}")
                continue
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Database commit failed: {e}")
            
        return added, updated
    
    def validate_product_data(self, product_data: dict) -> bool:
        """Validate product data quality"""
        required_fields = ['title', 'vendor', 'salespage_url']
        
        # Check required fields
        for field in required_fields:
            if not product_data.get(field):
                return False
        
        # Validate URL format
        salespage_url = product_data.get('salespage_url', '')
        if not salespage_url.startswith(('http://', 'https://')):
            return False
        
        # Validate gravity score (should be numeric)
        gravity = product_data.get('gravity', 0)
        try:
            float(gravity)
        except (ValueError, TypeError):
            product_data['gravity'] = 0
        
        # Validate commission rate (should be between 0-100)
        commission_rate = product_data.get('commission_rate', 0)
        try:
            rate = float(commission_rate)
            if rate < 0 or rate > 100:
                product_data['commission_rate'] = 50  # Default
        except (ValueError, TypeError):
            product_data['commission_rate'] = 50
        
        return True
    
    def update_existing_product(self, existing: ClickBankProduct, product_data: dict, category: str):
        """Update existing product with new data"""
        # Update basic fields
        existing.title = product_data.get('title', existing.title)
        existing.vendor = product_data.get('vendor', existing.vendor)
        existing.description = product_data.get('description', existing.description)
        existing.gravity = product_data.get('gravity', existing.gravity)
        existing.commission_rate = product_data.get('commission_rate', existing.commission_rate)
        
        # Update tracking fields
        existing.last_seen_at = datetime.utcnow()
        existing.is_active = True
        existing.updated_at = datetime.utcnow()
        
        # Calculate performance score
        existing.performance_score = self.calculate_performance_score(product_data)
    
    def create_new_product(self, product_data: dict, category: str) -> ClickBankProduct:
        """Create new product with enhanced fields"""
        return ClickBankProduct(
            product_id=product_data.get('product_id', self.generate_product_id(product_data['title'])),
            title=product_data['title'],
            vendor=product_data['vendor'],
            description=product_data.get('description', ''),
            category=category,
            gravity=product_data.get('gravity', 0),
            commission_rate=product_data.get('commission_rate', 50),
            salespage_url=product_data['salespage_url'],
            product_page_url=product_data.get('product_page_url'),
            vendor_id=product_data.get('vendor_id', self.generate_vendor_id(product_data['vendor'])),
            product_type=product_data.get('product_type', 'digital'),
            rebill_percentage=product_data.get('rebill_percentage', 0),
            refund_rate=product_data.get('refund_rate', 0),
            activation_date=product_data.get('activation_date'),
            is_active=True,
            last_seen_at=datetime.utcnow(),
            performance_score=self.calculate_performance_score(product_data),
            affiliate_tools_available=product_data.get('affiliate_tools_available', False),
            target_keywords=product_data.get('target_keywords', []),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    def calculate_performance_score(self, product_data: dict) -> int:
        """Calculate a performance score (1-100) based on multiple factors"""
        score = 0
        
        # Gravity score contribution (40% of total)
        gravity = float(product_data.get('gravity', 0))
        if gravity > 100:
            score += 40
        elif gravity > 50:
            score += 30
        elif gravity > 20:
            score += 20
        elif gravity > 10:
            score += 10
        
        # Commission rate contribution (30% of total)
        commission = float(product_data.get('commission_rate', 50))
        if commission >= 70:
            score += 30
        elif commission >= 60:
            score += 25
        elif commission >= 50:
            score += 20
        elif commission >= 40:
            score += 15
        else:
            score += 10
        
        # Data quality contribution (30% of total)
        if product_data.get('description') and len(product_data['description']) > 50:
            score += 10
        if product_data.get('vendor') and len(product_data['vendor']) > 3:
            score += 10
        if product_data.get('salespage_url') and 'http' in product_data['salespage_url']:
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    def calculate_data_quality_score(self, products: List[dict]) -> int:
        """Calculate overall data quality score for a scraping session"""
        if not products:
            return 0
        
        total_score = 0
        for product in products:
            # Check for completeness
            completeness = 0
            if product.get('title'): completeness += 25
            if product.get('vendor'): completeness += 25
            if product.get('description'): completeness += 25
            if product.get('salespage_url'): completeness += 25
            
            total_score += completeness
        
        return int(total_score / len(products))
    
    def generate_product_id(self, title: str) -> str:
        """Generate a product ID from title"""
        clean_title = re.sub(r'[^a-zA-Z0-9]', '', title.upper())
        return clean_title[:10] + str(hash(title))[-4:]
    
    def generate_vendor_id(self, vendor: str) -> str:
        """Generate a vendor ID from vendor name"""
        clean_vendor = re.sub(r'[^a-zA-Z0-9]', '', vendor.lower())
        return clean_vendor[:15]
    
    async def mark_unseen_products_inactive(self, category: str, current_products: List[dict]) -> int:
        """Mark products as inactive if they weren't seen in the latest scrape"""
        if not current_products:
            return 0
        
        # Get URLs of products that were just scraped
        current_urls = {p.get('salespage_url') for p in current_products if p.get('salespage_url')}
        
        # Find products in this category that weren't seen
        unseen_products = self.db.query(ClickBankProduct).filter(
            and_(
                ClickBankProduct.category == category,
                ClickBankProduct.is_active == True,
                ~ClickBankProduct.salespage_url.in_(current_urls)
            )
        ).all()
        
        # Mark as inactive if they haven't been seen for more than 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        inactive_count = 0
        
        for product in unseen_products:
            if product.last_seen_at < cutoff_date:
                product.is_active = False
                product.updated_at = datetime.utcnow()
                inactive_count += 1
        
        return inactive_count
    
    async def update_product_performance_scores(self, category: str, products: List[dict]):
        """Update performance tracking for products"""
        today = datetime.utcnow().date()
        
        for product_data in products:
            if not product_data.get('salespage_url'):
                continue
                
            # Find the product in our database
            product = self.db.query(ClickBankProduct).filter(
                ClickBankProduct.salespage_url == product_data['salespage_url']
            ).first()
            
            if not product:
                continue
            
            # Create or update performance record
            performance = self.db.query(ProductPerformance).filter(
                and_(
                    ProductPerformance.product_id == product.product_id,
                    ProductPerformance.date_tracked == today
                )
            ).first()
            
            if not performance:
                performance = ProductPerformance(
                    product_id=product.product_id,
                    category=category,
                    date_tracked=today,
                    gravity_score=product_data.get('gravity', 0),
                    commission_rate=product_data.get('commission_rate', 0),
                    estimated_earnings=self.calculate_estimated_earnings(product_data),
                    rank_in_category=0,  # Will be calculated later
                    trending_direction='stable'
                )
                self.db.add(performance)
    
    def calculate_estimated_earnings(self, product_data: dict) -> float:
        """Estimate potential earnings based on gravity and commission"""
        gravity = float(product_data.get('gravity', 0))
        commission_rate = float(product_data.get('commission_rate', 50))
        
        # Simple estimation: gravity * commission_rate * estimated_price_factor
        estimated_price = 50  # Assume $50 average product price
        estimated_monthly_sales = gravity * 2  # Rough estimate
        
        return (estimated_monthly_sales * estimated_price * commission_rate) / 100
    
    def calculate_next_scrape_time(self, schedule: ScrapingSchedule) -> datetime:
        """Calculate next scrape time with dynamic adjustment based on priority"""
        now = datetime.utcnow()
        
        # High-priority categories get more frequent scraping
        if schedule.category in self.high_priority_categories:
            hours = min(schedule.scrape_frequency_hours, 12)  # Max every 12 hours
        elif schedule.category in self.medium_priority_categories:
            hours = min(schedule.scrape_frequency_hours, 24)  # Max every 24 hours
        else:
            hours = schedule.scrape_frequency_hours  # Use configured frequency
        
        return now + timedelta(hours=hours)
    
    async def perform_health_check(self):
        """Perform system health check and maintenance"""
        logger.info("🔍 Performing system health check...")
        
        # Check for categories that haven't been scraped recently
        overdue_threshold = datetime.utcnow() - timedelta(hours=48)
        overdue_categories = self.db.query(ScrapingSchedule).filter(
            and_(
                ScrapingSchedule.is_enabled == True,
                ScrapingSchedule.last_scraped_at < overdue_threshold
            )
        ).all()
        
        if overdue_categories:
            logger.warning(f"⚠️ Found {len(overdue_categories)} overdue categories: {[c.category for c in overdue_categories]}")
        
        # Check success rates
        low_success_categories = self.db.query(ScrapingSchedule).filter(
            and_(
                ScrapingSchedule.is_enabled == True,
                ScrapingSchedule.success_rate < 50
            )
        ).all()
        
        if low_success_categories:
            logger.warning(f"⚠️ Found {len(low_success_categories)} categories with low success rates: {[c.category for c in low_success_categories]}")
        
        # Update category rankings
        await self.update_category_rankings()
        
        logger.info("✅ Health check completed")
    
    async def update_category_rankings(self):
        """Update product rankings within each category"""
        categories = self.db.query(ScrapingSchedule.category).distinct().all()
        
        for (category,) in categories:
            # Get all active products in this category, ordered by gravity
            products = self.db.query(ClickBankProduct).filter(
                and_(
                    ClickBankProduct.category == category,
                    ClickBankProduct.is_active == True
                )
            ).order_by(ClickBankProduct.gravity.desc()).all()
            
            # Update performance records with rankings
            today = datetime.utcnow().date()
            for rank, product in enumerate(products, 1):
                performance = self.db.query(ProductPerformance).filter(
                    and_(
                        ProductPerformance.product_id == product.product_id,
                        ProductPerformance.date_tracked == today
                    )
                ).first()
                
                if performance:
                    performance.rank_in_category = rank
        
        self.db.commit()
    
    async def log_scraping_failure(self, category: str, error_message: str):
        """Log scraping failure for monitoring"""
        log = ScrapingLog(
            category=category,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            status='failed',
            error_message=error_message,
            scraping_duration_seconds=0
        )
        self.db.add(log)
        self.db.commit()


class EnhancedClickBankScraper:
    """
    Enhanced scraper with better product extraction for high-converting categories
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        }
    
    async def scrape_url_products(self, url: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape products from a ClickBank URL with enhanced extraction
        Note: This is a placeholder - you'll need to implement actual scraping
        based on ClickBank's current HTML structure or use Selenium for JavaScript pages
        """
        try:
            async with httpx.AsyncClient(timeout=30.0, headers=self.headers) as client:
                response = await client.get(url)
                
                if response.status_code != 200:
                    logger.error(f"Failed to fetch URL {url}: {response.status_code}")
                    return []
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # TODO: Implement actual product extraction based on ClickBank's HTML structure
                # Since ClickBank uses JavaScript, you may need to use Selenium here
                
                products = []
                # This is a placeholder - replace with actual extraction logic
                logger.warning(f"⚠️ Placeholder scraper used for {url} - implement actual extraction")
                
                return products
                
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {e}")
            return []


# ============================================================================
# Admin API Endpoints for Managing High-Converting Categories
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class CategoryStatsResponse(BaseModel):
    category: str
    category_name: str
    priority_level: int
    total_products: int
    active_products: int
    avg_gravity: float
    avg_commission_rate: float
    last_scraped: str
    success_rate: float

class ScrapingHealthResponse(BaseModel):
    total_categories: int
    active_schedules: int
    overdue_categories: int
    low_performance_categories: int
    avg_success_rate: float
    last_health_check: str

@router.get("/admin/category-performance", response_model=List[CategoryStatsResponse])
async def get_category_performance(db: Session = Depends(get_db)):
    """Get performance stats for all categories"""
    
    query = """
    SELECT 
        c.category,
        c.category_name,
        c.priority_level,
        COUNT(p.id) as total_products,
        COUNT(CASE WHEN p.is_active THEN 1 END) as active_products,
        AVG(p.gravity) as avg_gravity,
        AVG(p.commission_rate) as avg_commission_rate,
        s.last_scraped_at,
        s.success_rate
    FROM clickbank_category_urls c
    LEFT JOIN clickbank_products p ON c.category = p.category
    LEFT JOIN scraping_schedule s ON c.category = s.category
    GROUP BY c.category, c.category_name, c.priority_level, s.last_scraped_at, s.success_rate
    ORDER BY c.priority_level DESC
    """
    
    result = db.execute(query).fetchall()
    
    return [
        CategoryStatsResponse(
            category=row.category,
            category_name=row.category_name,
            priority_level=row.priority_level,
            total_products=row.total_products or 0,
            active_products=row.active_products or 0,
            avg_gravity=round(row.avg_gravity or 0, 2),
            avg_commission_rate=round(row.avg_commission_rate or 0, 2),
            last_scraped=row.last_scraped_at.isoformat() if row.last_scraped_at else "",
            success_rate=round(row.success_rate or 0, 2)
        )
        for row in result
    ]

@router.get("/admin/scraping-health", response_model=ScrapingHealthResponse)
async def get_scraping_health(db: Session = Depends(get_db)):
    """Get overall scraping system health"""
    
    total_categories = db.query(ScrapingSchedule).count()
    active_schedules = db.query(ScrapingSchedule).filter(ScrapingSchedule.is_enabled == True).count()
    
    # Overdue categories (not scraped in 48 hours)
    overdue_threshold = datetime.utcnow() - timedelta(hours=48)
    overdue_count = db.query(ScrapingSchedule).filter(
        and_(
            ScrapingSchedule.is_enabled == True,
            ScrapingSchedule.last_scraped_at < overdue_threshold
        )
    ).count()
    
    # Low performance categories (success rate < 50%)
    low_performance_count = db.query(ScrapingSchedule).filter(
        and_(
            ScrapingSchedule.is_enabled == True,
            ScrapingSchedule.success_rate < 50
        )
    ).count()
    
    # Average success rate
    avg_success_rate = db.query(func.avg(ScrapingSchedule.success_rate)).scalar() or 0
    
    return ScrapingHealthResponse(
        total_categories=total_categories,
        active_schedules=active_schedules,
        overdue_categories=overdue_count,
        low_performance_categories=low_performance_count,
        avg_success_rate=round(avg_success_rate, 2),
        last_health_check=datetime.utcnow().isoformat()
    )

@router.post("/admin/trigger-priority-scrape")
async def trigger_priority_scrape(db: Session = Depends(get_db)):
    """Trigger immediate scraping for high-priority categories"""
    
    high_priority_categories = ['mmo', 'weightloss', 'relationships']
    
    scheduler = EnhancedClickBankScheduler(db)
    results = []
    
    for category in high_priority_categories:
        schedule = db.query(ScrapingSchedule).filter(
            ScrapingSchedule.category == category
        ).first()
        
        if schedule:
            try:
                await scheduler.scrape_category_enhanced(schedule)
                results.append({"category": category, "status": "success"})
            except Exception as e:
                results.append({"category": category, "status": "failed", "error": str(e)})
    
    return {
        "message": "Priority scraping triggered",
        "categories": high_priority_categories,
        "results": results
    }