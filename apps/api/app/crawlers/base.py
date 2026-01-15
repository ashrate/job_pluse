"""
Base Crawler - Abstract base class for all job crawlers
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import logging
import httpx
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)


@dataclass
class JobPosting:
    """Standardized job posting data structure"""
    # Required fields
    title: str
    company_name: str
    source: str  # 'jobkorea', 'wanted', 'jobplanet', 'linkedin'
    source_url: str
    source_id: str  # Unique ID from source platform
    
    # Optional fields
    location: Optional[str] = None
    salary: Optional[str] = None
    experience_level: Optional[str] = None  # 신입, 경력, 무관
    employment_type: Optional[str] = None  # 정규직, 계약직, 인턴
    job_category: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    deadline: Optional[datetime] = None
    posted_at: Optional[datetime] = None
    company_logo_url: Optional[str] = None
    
    # Metadata
    crawled_at: datetime = field(default_factory=datetime.utcnow)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'company_name': self.company_name,
            'source': self.source,
            'source_url': self.source_url,
            'source_id': self.source_id,
            'location': self.location,
            'salary': self.salary,
            'experience_level': self.experience_level,
            'employment_type': self.employment_type,
            'job_category': self.job_category,
            'skills': self.skills,
            'description': self.description,
            'requirements': self.requirements,
            'benefits': self.benefits,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'company_logo_url': self.company_logo_url,
            'crawled_at': self.crawled_at.isoformat(),
        }


class BaseCrawler(ABC):
    """Abstract base class for job crawlers"""
    
    # Override in subclasses
    SOURCE_NAME: str = "base"
    BASE_URL: str = ""
    RATE_LIMIT_SECONDS: float = 2.0  # Delay between requests
    MAX_RETRIES: int = 3
    
    def __init__(self):
        self.ua = UserAgent()
        self.session: Optional[httpx.AsyncClient] = None
        self._last_request_time: float = 0
        
    def get_headers(self) -> Dict[str, str]:
        """Get randomized headers to avoid detection"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
    
    async def init_session(self):
        """Initialize HTTP session"""
        if self.session is None:
            self.session = httpx.AsyncClient(
                headers=self.get_headers(),
                timeout=30.0,
                follow_redirects=True
            )
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.aclose()
            self.session = None
    
    async def rate_limit(self):
        """Enforce rate limiting between requests"""
        import time
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        if elapsed < self.RATE_LIMIT_SECONDS:
            await asyncio.sleep(self.RATE_LIMIT_SECONDS - elapsed)
        self._last_request_time = time.time()
    
    async def fetch(self, url: str, **kwargs) -> Optional[httpx.Response]:
        """Fetch URL with rate limiting and retry logic"""
        await self.init_session()
        await self.rate_limit()
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.session.get(url, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error {e.response.status_code} for {url}")
                if e.response.status_code == 429:  # Rate limited
                    await asyncio.sleep(10 * (attempt + 1))
                elif e.response.status_code >= 500:
                    await asyncio.sleep(2 * (attempt + 1))
                else:
                    raise
            except httpx.RequestError as e:
                logger.warning(f"Request error for {url}: {e}")
                await asyncio.sleep(2 * (attempt + 1))
        
        return None
    
    async def fetch_json(self, url: str, **kwargs) -> Optional[Dict]:
        """Fetch JSON data"""
        response = await self.fetch(url, **kwargs)
        if response:
            return response.json()
        return None
    
    @abstractmethod
    async def search_jobs(
        self,
        keyword: str,
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[JobPosting]:
        """
        Search for jobs with given criteria.
        Must be implemented by each crawler.
        """
        pass
    
    @abstractmethod
    async def get_job_detail(self, job_id: str) -> Optional[JobPosting]:
        """
        Get detailed information for a specific job.
        Must be implemented by each crawler.
        """
        pass
    
    async def crawl(
        self,
        keyword: str,
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        max_pages: int = 5,
        limit_per_page: int = 20
    ) -> List[JobPosting]:
        """
        Crawl multiple pages of job listings.
        """
        all_jobs = []
        
        try:
            await self.init_session()
            
            for page in range(1, max_pages + 1):
                logger.info(f"[{self.SOURCE_NAME}] Crawling page {page}...")
                
                jobs = await self.search_jobs(
                    keyword=keyword,
                    location=location,
                    experience_level=experience_level,
                    page=page,
                    limit=limit_per_page
                )
                
                if not jobs:
                    logger.info(f"[{self.SOURCE_NAME}] No more jobs found at page {page}")
                    break
                
                all_jobs.extend(jobs)
                logger.info(f"[{self.SOURCE_NAME}] Found {len(jobs)} jobs on page {page}")
            
        except Exception as e:
            logger.error(f"[{self.SOURCE_NAME}] Crawl error: {e}")
            raise
        finally:
            await self.close_session()
        
        return all_jobs
