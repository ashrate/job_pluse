"""
Jobs Router
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.db.database import get_db
from app.db.models import Job, Company
from app.core.security import get_current_user_id

router = APIRouter()


class JobResponse(BaseModel):
    """Job response"""
    id: str
    title: str
    company_id: Optional[str]
    company_name: Optional[str]
    location: Optional[str]
    level: Optional[str]
    url: Optional[str]
    source: Optional[str]
    status: Optional[str]
    jd_summary: Optional[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Job list response"""
    items: List[JobResponse]
    total: int


class JobCreate(BaseModel):
    """Create job request"""
    title: str
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    level: Optional[str] = None
    jd_text: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None


@router.get("", response_model=JobListResponse)
async def search_jobs(
    search: Optional[str] = None,
    company_id: Optional[str] = None,
    location: Optional[str] = None,
    level: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Search jobs"""
    query = select(Job).where(Job.status != "closed")
    
    if search:
        query = query.where(Job.title.ilike(f"%{search}%"))
    
    if company_id:
        query = query.where(Job.company_id == UUID(company_id))
    
    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))
    
    if level:
        query = query.where(Job.level == level)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Job.created_at.desc())
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    items = []
    for job in jobs:
        company_name = None
        if job.company_id:
            company_result = await db.execute(
                select(Company.name).where(Company.id == job.company_id)
            )
            company_name = company_result.scalar()
        
        items.append(JobResponse(
            id=str(job.id),
            title=job.title,
            company_id=str(job.company_id) if job.company_id else None,
            company_name=company_name,
            location=job.location,
            level=job.level,
            url=job.url,
            source=job.source,
            status=job.status,
            jd_summary=job.jd_summary_json,
            created_at=job.created_at
        ))
    
    return JobListResponse(items=items, total=total)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get job by ID"""
    result = await db.execute(
        select(Job).where(Job.id == UUID(job_id))
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    company_name = None
    if job.company_id:
        company_result = await db.execute(
            select(Company.name).where(Company.id == job.company_id)
        )
        company_name = company_result.scalar()
    
    return JobResponse(
        id=str(job.id),
        title=job.title,
        company_id=str(job.company_id) if job.company_id else None,
        company_name=company_name,
        location=job.location,
        level=job.level,
        url=job.url,
        source=job.source,
        status=job.status,
        jd_summary=job.jd_summary_json,
        created_at=job.created_at
    )


@router.post("", response_model=JobResponse)
async def create_job(
    request: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new job posting"""
    job = Job(
        title=request.title,
        company_id=UUID(request.company_id) if request.company_id else None,
        location=request.location,
        level=request.level,
        jd_text=request.jd_text,
        url=request.url,
        source=request.source,
        status="open"
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    return JobResponse(
        id=str(job.id),
        title=job.title,
        company_id=str(job.company_id) if job.company_id else None,
        company_name=request.company_name,
        location=job.location,
        level=job.level,
        url=job.url,
        source=job.source,
        status=job.status,
        jd_summary=job.jd_summary_json,
        created_at=job.created_at
    )
