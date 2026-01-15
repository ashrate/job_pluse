"""
Database Models - SQLAlchemy ORM
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    target_role: Mapped[Optional[str]] = mapped_column(String(100))
    target_level: Mapped[Optional[str]] = mapped_column(String(50))
    target_location: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    applications: Mapped[List["Application"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    connections: Mapped[List["Connection"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    resume_versions: Mapped[List["ResumeVersion"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Connection(Base):
    """OAuth Connection model"""
    __tablename__ = "connections"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # 'google_gmail', 'google_calendar'
    token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_encrypted: Mapped[Optional[str]] = mapped_column(Text)
    scopes: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    status: Mapped[str] = mapped_column(String(20), default="active")
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="connections")


class Company(Base):
    """Company model"""
    __tablename__ = "companies"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255))
    normalized_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    summary_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    sources_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    logo_url: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    jobs: Mapped[List["Job"]] = relationship(back_populates="company")


class Job(Base):
    """Job Posting model"""
    __tablename__ = "jobs"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    level: Mapped[Optional[str]] = mapped_column(String(50))
    jd_text: Mapped[Optional[str]] = mapped_column(Text)
    jd_summary_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    url: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String(50))  # 'company_site', 'linkedin', etc.
    status: Mapped[Optional[str]] = mapped_column(String(20))  # 'open', 'closed', 'unknown'
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company: Mapped[Optional["Company"]] = relationship(back_populates="jobs")
    applications: Mapped[List["Application"]] = relationship(back_populates="job")


class Application(Base):
    """Job Application model (핵심)"""
    __tablename__ = "applications"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    position_title: Mapped[Optional[str]] = mapped_column(String(500))
    stage: Mapped[str] = mapped_column(String(50), nullable=False, default="interested", index=True)
    # stages: interested, applied, screening, interview_1, interview_2, offer, accepted, rejected
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    channel: Mapped[Optional[str]] = mapped_column(String(100))
    job_url: Mapped[Optional[str]] = mapped_column(Text)
    resume_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    next_action_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    next_action_memo: Mapped[Optional[str]] = mapped_column(String(500))
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    source: Mapped[Optional[str]] = mapped_column(String(50))  # 'manual', 'gmail', 'extension'
    confidence: Mapped[Optional[str]] = mapped_column(String(20))  # 'confirmed', 'needs_review'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="applications")
    job: Mapped[Optional["Job"]] = relationship(back_populates="applications")
    interviews: Mapped[List["Interview"]] = relationship(back_populates="application", cascade="all, delete-orphan")


class Interview(Base):
    """Interview/Schedule model"""
    __tablename__ = "interviews"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"))
    datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(50))  # 'phone', 'video', 'onsite', 'task'
    location_or_link: Mapped[Optional[str]] = mapped_column(Text)
    memo: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    application: Mapped["Application"] = relationship(back_populates="interviews")


class ResumeVersion(Base):
    """Resume Version model"""
    __tablename__ = "resume_versions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    file_url: Mapped[Optional[str]] = mapped_column(Text)
    original_filename: Mapped[Optional[str]] = mapped_column(String(255))
    text_extract: Mapped[Optional[str]] = mapped_column(Text)
    target_role: Mapped[Optional[str]] = mapped_column(String(100))
    analysis_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    score: Mapped[Optional[int]] = mapped_column(Integer)
    pii_masked: Mapped[bool] = mapped_column(Boolean, default=False)
    retention_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="resume_versions")


class AuditLog(Base):
    """Audit Log model"""
    __tablename__ = "audit_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50))
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6 length
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
