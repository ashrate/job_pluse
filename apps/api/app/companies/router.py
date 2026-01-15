"""
Companies Router
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

from app.db.database import get_db
from app.db.models import Company, Job
from app.core.security import get_current_user_id

router = APIRouter()


class CompanyResponse(BaseModel):
    """Company response"""
    id: str
    name: str
    domain: Optional[str]
    logo_url: Optional[str]
    summary: Optional[dict]
    sources: Optional[dict]
    active_jobs_count: int = 0
    
    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    """Company list response"""
    items: List[CompanyResponse]
    total: int


class CompanyResolveRequest(BaseModel):
    """Company name resolve request"""
    name: str


@router.get("", response_model=CompanyListResponse)
async def search_companies(
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Search companies"""
    query = select(Company)
    
    if search:
        query = query.where(Company.name.ilike(f"%{search}%"))
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    companies = result.scalars().all()
    
    items = []
    for company in companies:
        # Count active jobs
        jobs_count_result = await db.execute(
            select(func.count()).where(
                (Job.company_id == company.id) &
                (Job.status == "open")
            )
        )
        jobs_count = jobs_count_result.scalar()
        
        items.append(CompanyResponse(
            id=str(company.id),
            name=company.name,
            domain=company.domain,
            logo_url=company.logo_url,
            summary=company.summary_json,
            sources=company.sources_json,
            active_jobs_count=jobs_count
        ))
    
    return CompanyListResponse(items=items, total=total)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get company by ID"""
    result = await db.execute(
        select(Company).where(Company.id == UUID(company_id))
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Count active jobs
    jobs_count_result = await db.execute(
        select(func.count()).where(
            (Job.company_id == company.id) &
            (Job.status == "open")
        )
    )
    jobs_count = jobs_count_result.scalar()
    
    return CompanyResponse(
        id=str(company.id),
        name=company.name,
        domain=company.domain,
        logo_url=company.logo_url,
        summary=company.summary_json,
        sources=company.sources_json,
        active_jobs_count=jobs_count
    )


@router.post("/resolve", response_model=CompanyResponse)
async def resolve_company_name(
    request: CompanyResolveRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Resolve company name to normalized company record.
    Creates a new company if not found.
    """
    # Normalize the name
    normalized_key = request.name.lower().strip().replace(" ", "_")
    
    # Try to find existing company
    result = await db.execute(
        select(Company).where(
            (Company.normalized_key == normalized_key) |
            (Company.name.ilike(f"%{request.name}%"))
        )
    )
    company = result.scalar_one_or_none()
    
    if not company:
        # Create new company
        company = Company(
            name=request.name,
            normalized_key=normalized_key
        )
        db.add(company)
        await db.commit()
        await db.refresh(company)
    
    return CompanyResponse(
        id=str(company.id),
        name=company.name,
        domain=company.domain,
        logo_url=company.logo_url,
        summary=company.summary_json,
        sources=company.sources_json,
        active_jobs_count=0
    )
