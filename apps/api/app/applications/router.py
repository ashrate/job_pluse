"""
Applications Router - 지원현황 관리 (핵심)
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

from app.db.database import get_db
from app.db.models import Application, Interview
from app.core.security import get_current_user_id

router = APIRouter()


class ApplicationStage(str, Enum):
    """Application stages"""
    INTERESTED = "interested"
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW_1 = "interview_1"
    INTERVIEW_2 = "interview_2"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ApplicationCreate(BaseModel):
    """Create application request"""
    company_name: str
    position_title: Optional[str] = None
    stage: ApplicationStage = ApplicationStage.INTERESTED
    applied_at: Optional[datetime] = None
    channel: Optional[str] = None
    job_url: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class ApplicationUpdate(BaseModel):
    """Update application request"""
    company_name: Optional[str] = None
    position_title: Optional[str] = None
    stage: Optional[ApplicationStage] = None
    applied_at: Optional[datetime] = None
    channel: Optional[str] = None
    job_url: Optional[str] = None
    notes: Optional[str] = None
    next_action_at: Optional[datetime] = None
    next_action_memo: Optional[str] = None
    tags: Optional[List[str]] = None


class InterviewCreate(BaseModel):
    """Create interview request"""
    datetime: datetime
    type: Optional[str] = None
    location_or_link: Optional[str] = None
    memo: Optional[str] = None


class InterviewResponse(BaseModel):
    """Interview response"""
    id: str
    datetime: datetime
    type: Optional[str]
    location_or_link: Optional[str]
    memo: Optional[str]
    
    class Config:
        from_attributes = True


class ApplicationResponse(BaseModel):
    """Application response"""
    id: str
    company_name: str
    position_title: Optional[str]
    stage: str
    applied_at: Optional[datetime]
    channel: Optional[str]
    job_url: Optional[str]
    notes: Optional[str]
    next_action_at: Optional[datetime]
    next_action_memo: Optional[str]
    tags: Optional[List[str]]
    source: Optional[str]
    created_at: datetime
    updated_at: datetime
    interviews: List[InterviewResponse] = []
    
    class Config:
        from_attributes = True


class ApplicationsListResponse(BaseModel):
    """Applications list response"""
    items: List[ApplicationResponse]
    total: int
    page: int
    page_size: int


class PipelineStats(BaseModel):
    """Pipeline statistics"""
    interested: int = 0
    applied: int = 0
    screening: int = 0
    interview_1: int = 0
    interview_2: int = 0
    offer: int = 0
    accepted: int = 0
    rejected: int = 0
    total: int = 0


@router.get("", response_model=ApplicationsListResponse)
async def get_applications(
    stage: Optional[ApplicationStage] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all applications with filtering and pagination"""
    query = select(Application).where(Application.user_id == UUID(user_id))
    
    if stage:
        query = query.where(Application.stage == stage.value)
    
    if search:
        query = query.where(
            (Application.company_name.ilike(f"%{search}%")) |
            (Application.position_title.ilike(f"%{search}%"))
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Application.updated_at.desc())
    
    result = await db.execute(query)
    applications = result.scalars().all()
    
    items = []
    for app in applications:
        # Load interviews
        interviews_result = await db.execute(
            select(Interview).where(Interview.application_id == app.id)
        )
        interviews = interviews_result.scalars().all()
        
        items.append(ApplicationResponse(
            id=str(app.id),
            company_name=app.company_name,
            position_title=app.position_title,
            stage=app.stage,
            applied_at=app.applied_at,
            channel=app.channel,
            job_url=app.job_url,
            notes=app.notes,
            next_action_at=app.next_action_at,
            next_action_memo=app.next_action_memo,
            tags=app.tags,
            source=app.source,
            created_at=app.created_at,
            updated_at=app.updated_at,
            interviews=[
                InterviewResponse(
                    id=str(iv.id),
                    datetime=iv.datetime,
                    type=iv.type,
                    location_or_link=iv.location_or_link,
                    memo=iv.memo
                ) for iv in interviews
            ]
        ))
    
    return ApplicationsListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/stats", response_model=PipelineStats)
async def get_pipeline_stats(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get pipeline statistics by stage"""
    result = await db.execute(
        select(Application.stage, func.count(Application.id))
        .where(Application.user_id == UUID(user_id))
        .group_by(Application.stage)
    )
    
    stats = {row[0]: row[1] for row in result.all()}
    total = sum(stats.values())
    
    return PipelineStats(
        interested=stats.get("interested", 0),
        applied=stats.get("applied", 0),
        screening=stats.get("screening", 0),
        interview_1=stats.get("interview_1", 0),
        interview_2=stats.get("interview_2", 0),
        offer=stats.get("offer", 0),
        accepted=stats.get("accepted", 0),
        rejected=stats.get("rejected", 0),
        total=total
    )


@router.post("", response_model=ApplicationResponse)
async def create_application(
    request: ApplicationCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new application"""
    application = Application(
        user_id=UUID(user_id),
        company_name=request.company_name,
        position_title=request.position_title,
        stage=request.stage.value,
        applied_at=request.applied_at,
        channel=request.channel,
        job_url=request.job_url,
        notes=request.notes,
        tags=request.tags,
        source="manual"
    )
    
    db.add(application)
    await db.commit()
    await db.refresh(application)
    
    return ApplicationResponse(
        id=str(application.id),
        company_name=application.company_name,
        position_title=application.position_title,
        stage=application.stage,
        applied_at=application.applied_at,
        channel=application.channel,
        job_url=application.job_url,
        notes=application.notes,
        next_action_at=application.next_action_at,
        next_action_memo=application.next_action_memo,
        tags=application.tags,
        source=application.source,
        created_at=application.created_at,
        updated_at=application.updated_at,
        interviews=[]
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get application by ID"""
    result = await db.execute(
        select(Application).where(
            (Application.id == UUID(application_id)) &
            (Application.user_id == UUID(user_id))
        )
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Load interviews
    interviews_result = await db.execute(
        select(Interview).where(Interview.application_id == application.id)
    )
    interviews = interviews_result.scalars().all()
    
    return ApplicationResponse(
        id=str(application.id),
        company_name=application.company_name,
        position_title=application.position_title,
        stage=application.stage,
        applied_at=application.applied_at,
        channel=application.channel,
        job_url=application.job_url,
        notes=application.notes,
        next_action_at=application.next_action_at,
        next_action_memo=application.next_action_memo,
        tags=application.tags,
        source=application.source,
        created_at=application.created_at,
        updated_at=application.updated_at,
        interviews=[
            InterviewResponse(
                id=str(iv.id),
                datetime=iv.datetime,
                type=iv.type,
                location_or_link=iv.location_or_link,
                memo=iv.memo
            ) for iv in interviews
        ]
    )


@router.patch("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: str,
    request: ApplicationUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update application"""
    result = await db.execute(
        select(Application).where(
            (Application.id == UUID(application_id)) &
            (Application.user_id == UUID(user_id))
        )
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Update fields
    if request.company_name is not None:
        application.company_name = request.company_name
    if request.position_title is not None:
        application.position_title = request.position_title
    if request.stage is not None:
        application.stage = request.stage.value
    if request.applied_at is not None:
        application.applied_at = request.applied_at
    if request.channel is not None:
        application.channel = request.channel
    if request.job_url is not None:
        application.job_url = request.job_url
    if request.notes is not None:
        application.notes = request.notes
    if request.next_action_at is not None:
        application.next_action_at = request.next_action_at
    if request.next_action_memo is not None:
        application.next_action_memo = request.next_action_memo
    if request.tags is not None:
        application.tags = request.tags
    
    await db.commit()
    await db.refresh(application)
    
    # Load interviews
    interviews_result = await db.execute(
        select(Interview).where(Interview.application_id == application.id)
    )
    interviews = interviews_result.scalars().all()
    
    return ApplicationResponse(
        id=str(application.id),
        company_name=application.company_name,
        position_title=application.position_title,
        stage=application.stage,
        applied_at=application.applied_at,
        channel=application.channel,
        job_url=application.job_url,
        notes=application.notes,
        next_action_at=application.next_action_at,
        next_action_memo=application.next_action_memo,
        tags=application.tags,
        source=application.source,
        created_at=application.created_at,
        updated_at=application.updated_at,
        interviews=[
            InterviewResponse(
                id=str(iv.id),
                datetime=iv.datetime,
                type=iv.type,
                location_or_link=iv.location_or_link,
                memo=iv.memo
            ) for iv in interviews
        ]
    )


@router.delete("/{application_id}")
async def delete_application(
    application_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete application"""
    result = await db.execute(
        select(Application).where(
            (Application.id == UUID(application_id)) &
            (Application.user_id == UUID(user_id))
        )
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    await db.delete(application)
    await db.commit()
    
    return {"message": "Application deleted successfully"}


@router.post("/{application_id}/interviews", response_model=InterviewResponse)
async def add_interview(
    application_id: str,
    request: InterviewCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Add interview to application"""
    # Verify application ownership
    result = await db.execute(
        select(Application).where(
            (Application.id == UUID(application_id)) &
            (Application.user_id == UUID(user_id))
        )
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    interview = Interview(
        application_id=UUID(application_id),
        datetime=request.datetime,
        type=request.type,
        location_or_link=request.location_or_link,
        memo=request.memo
    )
    
    db.add(interview)
    await db.commit()
    await db.refresh(interview)
    
    return InterviewResponse(
        id=str(interview.id),
        datetime=interview.datetime,
        type=interview.type,
        location_or_link=interview.location_or_link,
        memo=interview.memo
    )
