"""
Resumes Router - 이력서 업로드 및 AI 분석
"""
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID
import aiofiles
import os

from app.db.database import get_db
from app.db.models import ResumeVersion
from app.core.config import settings
from app.core.security import get_current_user_id

router = APIRouter()


class ResumeResponse(BaseModel):
    """Resume response"""
    id: str
    original_filename: Optional[str]
    target_role: Optional[str]
    score: Optional[int]
    pii_masked: bool
    created_at: datetime
    has_analysis: bool
    
    class Config:
        from_attributes = True


class ResumeDetailResponse(ResumeResponse):
    """Resume detail response with analysis"""
    text_extract: Optional[str]
    analysis: Optional[dict]


class AnalysisReport(BaseModel):
    """Resume analysis report"""
    overall_score: int
    sections: dict
    suggestions: List[dict]
    keyword_analysis: Optional[dict]


@router.get("", response_model=List[ResumeResponse])
async def get_resumes(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all resumes for current user"""
    result = await db.execute(
        select(ResumeVersion)
        .where(ResumeVersion.user_id == UUID(user_id))
        .order_by(ResumeVersion.created_at.desc())
    )
    resumes = result.scalars().all()
    
    return [
        ResumeResponse(
            id=str(r.id),
            original_filename=r.original_filename,
            target_role=r.target_role,
            score=r.score,
            pii_masked=r.pii_masked,
            created_at=r.created_at,
            has_analysis=r.analysis_json is not None
        )
        for r in resumes
    ]


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    target_role: Optional[str] = Form(None),
    pii_mask: bool = Form(False),
    retention_days: int = Form(30),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Upload a new resume"""
    # Validate file type
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are allowed"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {settings.MAX_FILE_SIZE / 1024 / 1024}MB limit"
        )
    
    # Save file
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, user_id)
    os.makedirs(user_upload_dir, exist_ok=True)
    
    file_path = os.path.join(user_upload_dir, f"{UUID(user_id)}_{file.filename}")
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Create database record
    resume = ResumeVersion(
        user_id=UUID(user_id),
        file_url=file_path,
        original_filename=file.filename,
        target_role=target_role,
        pii_masked=pii_mask,
        retention_until=datetime.utcnow() + timedelta(days=retention_days)
    )
    
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    
    return ResumeResponse(
        id=str(resume.id),
        original_filename=resume.original_filename,
        target_role=resume.target_role,
        score=resume.score,
        pii_masked=resume.pii_masked,
        created_at=resume.created_at,
        has_analysis=False
    )


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(
    resume_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get resume by ID"""
    result = await db.execute(
        select(ResumeVersion).where(
            (ResumeVersion.id == UUID(resume_id)) &
            (ResumeVersion.user_id == UUID(user_id))
        )
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return ResumeDetailResponse(
        id=str(resume.id),
        original_filename=resume.original_filename,
        target_role=resume.target_role,
        score=resume.score,
        pii_masked=resume.pii_masked,
        created_at=resume.created_at,
        has_analysis=resume.analysis_json is not None,
        text_extract=resume.text_extract,
        analysis=resume.analysis_json
    )


@router.post("/{resume_id}/analyze", response_model=AnalysisReport)
async def analyze_resume(
    resume_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Request AI analysis for resume"""
    from app.resumes.analyzer import analyze_resume_with_ai, extract_text_from_file
    
    result = await db.execute(
        select(ResumeVersion).where(
            (ResumeVersion.id == UUID(resume_id)) &
            (ResumeVersion.user_id == UUID(user_id))
        )
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Extract text from resume file
    resume_text = ""
    if resume.file_url and os.path.exists(resume.file_url):
        try:
            resume_text = await extract_text_from_file(resume.file_url)
        except Exception as e:
            # If extraction fails, use stored text or empty string
            resume_text = resume.text_extract or ""
    elif resume.text_extract:
        resume_text = resume.text_extract
    
    # If no text available, return error
    if not resume_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from resume. Please upload a valid PDF or DOCX file."
        )
    
    # Store extracted text
    resume.text_extract = resume_text
    
    # Perform AI analysis
    analysis = await analyze_resume_with_ai(
        resume_text=resume_text,
        target_role=resume.target_role,
        filename=resume.original_filename
    )
    
    # Save analysis to database
    resume.analysis_json = analysis
    resume.score = analysis["overall_score"]
    await db.commit()
    
    return AnalysisReport(
        overall_score=analysis["overall_score"],
        sections=analysis["sections"],
        suggestions=analysis["suggestions"],
        keyword_analysis=analysis.get("keyword_analysis")
    )


@router.get("/{resume_id}/report", response_model=AnalysisReport)
async def get_analysis_report(
    resume_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get analysis report for resume"""
    result = await db.execute(
        select(ResumeVersion).where(
            (ResumeVersion.id == UUID(resume_id)) &
            (ResumeVersion.user_id == UUID(user_id))
        )
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if not resume.analysis_json:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found. Please run analyze first."
        )
    
    analysis = resume.analysis_json
    
    return AnalysisReport(
        overall_score=analysis.get("overall_score", 0),
        sections=analysis.get("sections", {}),
        suggestions=analysis.get("suggestions", []),
        keyword_analysis=analysis.get("keyword_analysis")
    )


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete resume"""
    result = await db.execute(
        select(ResumeVersion).where(
            (ResumeVersion.id == UUID(resume_id)) &
            (ResumeVersion.user_id == UUID(user_id))
        )
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Delete file if exists
    if resume.file_url and os.path.exists(resume.file_url):
        os.remove(resume.file_url)
    
    await db.delete(resume)
    await db.commit()
    
    return {"message": "Resume deleted successfully"}
