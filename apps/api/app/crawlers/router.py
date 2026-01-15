"""
Crawler API Router - 채용정보 크롤링 API
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.crawlers.manager import CrawlerManager
from app.crawlers.base import JobPosting

logger = logging.getLogger(__name__)
router = APIRouter()

# Global crawler manager instance
crawler_manager = CrawlerManager()


class JobSearchRequest(BaseModel):
    """Job search request body"""
    keyword: str
    location: Optional[str] = None
    experience_level: Optional[str] = None
    sources: Optional[List[str]] = None
    max_results: int = 100


class JobResponse(BaseModel):
    """Job response schema"""
    title: str
    company_name: str
    source: str
    source_url: str
    source_id: str
    location: Optional[str] = None
    salary: Optional[str] = None
    experience_level: Optional[str] = None
    employment_type: Optional[str] = None
    job_category: Optional[str] = None
    skills: List[str] = []
    description: Optional[str] = None
    company_logo_url: Optional[str] = None
    crawled_at: str


class SearchResponse(BaseModel):
    """Search response schema"""
    keyword: str
    total: int
    sources: List[str]
    jobs: List[JobResponse]
    crawled_at: str
    duration_seconds: float


class CrawlStatusResponse(BaseModel):
    """Crawl status for each source"""
    source: str
    success: bool
    job_count: int
    error: Optional[str] = None
    duration_seconds: float


class CrawlSummaryResponse(BaseModel):
    """Crawl summary response"""
    total_jobs: int
    successful_sources: int
    failed_sources: int
    sources: List[CrawlStatusResponse]
    crawled_at: str


# Store for background crawl results
_crawl_results: Dict[str, Any] = {}


@router.get("/sources")
async def get_available_sources():
    """Get list of available crawl sources"""
    return {
        "sources": [
            {"id": "wanted", "name": "원티드", "status": "active"},
            {"id": "jobkorea", "name": "잡코리아", "status": "active"},
            {"id": "jobplanet", "name": "잡플래닛", "status": "active"},
            {"id": "linkedin", "name": "링크드인", "status": "active"},
        ]
    }


@router.get("/search", response_model=SearchResponse)
async def search_jobs(
    keyword: str = Query(..., description="검색 키워드"),
    location: Optional[str] = Query(None, description="지역 (서울, 경기, 부산 등)"),
    experience_level: Optional[str] = Query(None, description="경력 (신입, 경력 등)"),
    sources: Optional[str] = Query(None, description="소스 목록 (쉼표 구분)"),
    max_results: int = Query(50, ge=1, le=200, description="최대 결과 수")
):
    """
    Search for jobs across multiple platforms.
    
    - **keyword**: Required search keyword (e.g., "프론트엔드", "백엔드", "React")
    - **location**: Optional location filter
    - **experience_level**: Optional experience level filter
    - **sources**: Optional comma-separated source list (wanted,jobkorea,jobplanet,linkedin)
    - **max_results**: Maximum number of results (default: 50)
    """
    start_time = datetime.utcnow()
    
    # Parse sources
    source_list = None
    if sources:
        source_list = [s.strip() for s in sources.split(',')]
    
    try:
        jobs = await crawler_manager.search(
            keyword=keyword,
            location=location,
            experience_level=experience_level,
            sources=source_list,
            max_results=max_results
        )
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Convert to response format
        job_responses = [
            JobResponse(
                title=job.title,
                company_name=job.company_name,
                source=job.source,
                source_url=job.source_url,
                source_id=job.source_id,
                location=job.location,
                salary=job.salary,
                experience_level=job.experience_level,
                employment_type=job.employment_type,
                job_category=job.job_category,
                skills=job.skills,
                description=job.description[:500] if job.description else None,
                company_logo_url=job.company_logo_url,
                crawled_at=job.crawled_at.isoformat()
            )
            for job in jobs
        ]
        
        return SearchResponse(
            keyword=keyword,
            total=len(job_responses),
            sources=source_list or list(crawler_manager.CRAWLERS.keys()),
            jobs=job_responses,
            crawled_at=datetime.utcnow().isoformat(),
            duration_seconds=round(duration, 2)
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crawl")
async def start_crawl(
    request: JobSearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a background crawl job.
    Use this for larger crawl operations.
    """
    import uuid
    
    crawl_id = str(uuid.uuid4())
    
    async def run_crawl():
        try:
            _crawl_results[crawl_id] = {"status": "running", "started_at": datetime.utcnow().isoformat()}
            
            results = await crawler_manager.crawl_all(
                keyword=request.keyword,
                location=request.location,
                experience_level=request.experience_level,
                sources=request.sources,
                max_pages=5,
                limit_per_page=20
            )
            
            jobs = crawler_manager.aggregate_jobs(results, deduplicate=True)
            
            _crawl_results[crawl_id] = {
                "status": "completed",
                "total_jobs": len(jobs),
                "sources": {
                    source: {
                        "success": result.success,
                        "job_count": len(result.jobs),
                        "error": result.error,
                        "duration": result.duration_seconds
                    }
                    for source, result in results.items()
                },
                "jobs": [job.to_dict() for job in jobs[:request.max_results]],
                "completed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            _crawl_results[crawl_id] = {
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat()
            }
    
    # Note: In production, use proper task queue like Celery
    background_tasks.add_task(run_crawl)
    
    return {
        "crawl_id": crawl_id,
        "status": "started",
        "message": "Crawl job started. Use /crawl/{crawl_id}/status to check progress."
    }


@router.get("/crawl/{crawl_id}/status")
async def get_crawl_status(crawl_id: str):
    """Get status of a background crawl job"""
    if crawl_id not in _crawl_results:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    
    return _crawl_results[crawl_id]


@router.get("/crawl/{crawl_id}/results")
async def get_crawl_results(
    crawl_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Get results of a completed crawl job"""
    if crawl_id not in _crawl_results:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    
    result = _crawl_results[crawl_id]
    
    if result.get("status") != "completed":
        return {
            "status": result.get("status"),
            "message": "Crawl not yet completed"
        }
    
    jobs = result.get("jobs", [])
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        "total": len(jobs),
        "page": page,
        "page_size": page_size,
        "jobs": jobs[start:end]
    }


@router.get("/job/{source}/{job_id}")
async def get_job_detail(source: str, job_id: str):
    """Get detailed information for a specific job"""
    crawler = crawler_manager.get_crawler(source)
    
    if not crawler:
        raise HTTPException(status_code=400, detail=f"Unknown source: {source}")
    
    try:
        await crawler.init_session()
        job = await crawler.get_job_detail(job_id)
        await crawler.close_session()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job detail error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
