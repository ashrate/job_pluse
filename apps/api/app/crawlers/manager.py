"""
Crawler Manager - 크롤러 통합 관리자
모든 크롤러를 통합 관리하고 병렬 크롤링을 지원합니다.
"""
import asyncio
from typing import List, Optional, Dict, Any, Type
from datetime import datetime
import logging
from dataclasses import dataclass

from app.crawlers.base import BaseCrawler, JobPosting
from app.crawlers.wanted import WantedCrawler
from app.crawlers.jobkorea import JobKoreaCrawler
from app.crawlers.jobplanet import JobPlanetCrawler
from app.crawlers.linkedin import LinkedInCrawler

logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    """Result of a crawl operation"""
    source: str
    jobs: List[JobPosting]
    success: bool
    error: Optional[str] = None
    duration_seconds: float = 0.0
    crawled_at: datetime = None
    
    def __post_init__(self):
        if self.crawled_at is None:
            self.crawled_at = datetime.utcnow()


class CrawlerManager:
    """
    Unified crawler manager for all job platforms.
    Supports parallel crawling and aggregation of results.
    """
    
    # Available crawlers
    CRAWLERS: Dict[str, Type[BaseCrawler]] = {
        'wanted': WantedCrawler,
        'jobkorea': JobKoreaCrawler,
        'jobplanet': JobPlanetCrawler,
        'linkedin': LinkedInCrawler,
    }
    
    def __init__(self, enabled_sources: Optional[List[str]] = None):
        """
        Initialize crawler manager.
        
        Args:
            enabled_sources: List of source names to enable. 
                           If None, all sources are enabled.
        """
        if enabled_sources:
            self.enabled_sources = [s for s in enabled_sources if s in self.CRAWLERS]
        else:
            self.enabled_sources = list(self.CRAWLERS.keys())
        
        logger.info(f"CrawlerManager initialized with sources: {self.enabled_sources}")
    
    def get_crawler(self, source: str) -> Optional[BaseCrawler]:
        """Get crawler instance for a source"""
        if source in self.CRAWLERS:
            return self.CRAWLERS[source]()
        return None
    
    async def crawl_source(
        self,
        source: str,
        keyword: str,
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        max_pages: int = 3,
        limit_per_page: int = 20
    ) -> CrawlResult:
        """
        Crawl a single source.
        
        Args:
            source: Source name (wanted, jobkorea, etc.)
            keyword: Search keyword
            location: Location filter
            experience_level: Experience level filter
            max_pages: Maximum pages to crawl
            limit_per_page: Jobs per page
            
        Returns:
            CrawlResult with jobs and status
        """
        start_time = datetime.utcnow()
        
        crawler = self.get_crawler(source)
        if not crawler:
            return CrawlResult(
                source=source,
                jobs=[],
                success=False,
                error=f"Unknown source: {source}"
            )
        
        try:
            jobs = await crawler.crawl(
                keyword=keyword,
                location=location,
                experience_level=experience_level,
                max_pages=max_pages,
                limit_per_page=limit_per_page
            )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"[{source}] Crawled {len(jobs)} jobs in {duration:.2f}s")
            
            return CrawlResult(
                source=source,
                jobs=jobs,
                success=True,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"[{source}] Crawl failed: {e}")
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            return CrawlResult(
                source=source,
                jobs=[],
                success=False,
                error=str(e),
                duration_seconds=duration
            )
    
    async def crawl_all(
        self,
        keyword: str,
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        sources: Optional[List[str]] = None,
        max_pages: int = 3,
        limit_per_page: int = 20,
        parallel: bool = True
    ) -> Dict[str, CrawlResult]:
        """
        Crawl multiple sources.
        
        Args:
            keyword: Search keyword
            location: Location filter
            experience_level: Experience level filter
            sources: Specific sources to crawl (uses enabled_sources if None)
            max_pages: Maximum pages per source
            limit_per_page: Jobs per page
            parallel: Whether to crawl in parallel
            
        Returns:
            Dictionary mapping source names to CrawlResults
        """
        target_sources = sources or self.enabled_sources
        target_sources = [s for s in target_sources if s in self.CRAWLERS]
        
        logger.info(f"Starting crawl for keyword='{keyword}' on sources: {target_sources}")
        
        crawl_tasks = [
            self.crawl_source(
                source=source,
                keyword=keyword,
                location=location,
                experience_level=experience_level,
                max_pages=max_pages,
                limit_per_page=limit_per_page
            )
            for source in target_sources
        ]
        
        if parallel:
            results = await asyncio.gather(*crawl_tasks, return_exceptions=True)
        else:
            results = []
            for task in crawl_tasks:
                try:
                    result = await task
                    results.append(result)
                except Exception as e:
                    results.append(e)
        
        # Map results to source names
        results_dict = {}
        for source, result in zip(target_sources, results):
            if isinstance(result, Exception):
                results_dict[source] = CrawlResult(
                    source=source,
                    jobs=[],
                    success=False,
                    error=str(result)
                )
            else:
                results_dict[source] = result
        
        # Log summary
        total_jobs = sum(len(r.jobs) for r in results_dict.values())
        successful = sum(1 for r in results_dict.values() if r.success)
        logger.info(f"Crawl complete: {total_jobs} total jobs from {successful}/{len(target_sources)} sources")
        
        return results_dict
    
    def aggregate_jobs(
        self,
        results: Dict[str, CrawlResult],
        deduplicate: bool = True,
        sort_by: str = 'crawled_at'
    ) -> List[JobPosting]:
        """
        Aggregate jobs from multiple crawl results.
        
        Args:
            results: Dictionary of CrawlResults
            deduplicate: Remove duplicate jobs (by title + company)
            sort_by: Field to sort by
            
        Returns:
            List of aggregated JobPostings
        """
        all_jobs = []
        
        for result in results.values():
            if result.success:
                all_jobs.extend(result.jobs)
        
        if deduplicate:
            seen = set()
            unique_jobs = []
            for job in all_jobs:
                key = (job.title.lower(), job.company_name.lower())
                if key not in seen:
                    seen.add(key)
                    unique_jobs.append(job)
            all_jobs = unique_jobs
        
        # Sort
        if sort_by == 'crawled_at':
            all_jobs.sort(key=lambda j: j.crawled_at, reverse=True)
        elif sort_by == 'posted_at':
            all_jobs.sort(key=lambda j: j.posted_at or datetime.min, reverse=True)
        elif sort_by == 'company':
            all_jobs.sort(key=lambda j: j.company_name)
        elif sort_by == 'title':
            all_jobs.sort(key=lambda j: j.title)
        
        return all_jobs
    
    async def search(
        self,
        keyword: str,
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        sources: Optional[List[str]] = None,
        max_results: int = 100
    ) -> List[JobPosting]:
        """
        High-level search across all enabled sources.
        
        Args:
            keyword: Search keyword
            location: Location filter
            experience_level: Experience level filter
            sources: Specific sources to search
            max_results: Maximum total results
            
        Returns:
            Aggregated and deduplicated list of JobPostings
        """
        # Calculate pages needed per source
        num_sources = len(sources or self.enabled_sources)
        results_per_source = max(20, max_results // max(1, num_sources))
        pages_per_source = (results_per_source // 20) + 1
        
        results = await self.crawl_all(
            keyword=keyword,
            location=location,
            experience_level=experience_level,
            sources=sources,
            max_pages=min(pages_per_source, 5),
            limit_per_page=20
        )
        
        jobs = self.aggregate_jobs(results, deduplicate=True)
        
        return jobs[:max_results]
