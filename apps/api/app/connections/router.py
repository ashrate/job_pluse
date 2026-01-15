"""
Connections Router - OAuth 연동 관리
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.db.database import get_db
from app.db.models import Connection
from app.core.config import settings
from app.core.security import get_current_user_id

router = APIRouter()


class ConnectionResponse(BaseModel):
    """Connection response"""
    id: str
    provider: str
    status: str
    scopes: Optional[List[str]]
    last_sync_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConnectionCreate(BaseModel):
    """Create connection request"""
    provider: str
    code: str
    redirect_uri: Optional[str] = None


@router.get("", response_model=List[ConnectionResponse])
async def get_connections(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all connections for current user"""
    result = await db.execute(
        select(Connection)
        .where(Connection.user_id == UUID(user_id))
        .order_by(Connection.created_at.desc())
    )
    connections = result.scalars().all()
    
    return [
        ConnectionResponse(
            id=str(c.id),
            provider=c.provider,
            status=c.status,
            scopes=c.scopes,
            last_sync_at=c.last_sync_at,
            created_at=c.created_at
        )
        for c in connections
    ]


@router.post("/google/gmail", response_model=ConnectionResponse)
async def connect_gmail(
    request: ConnectionCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Connect Gmail for email parsing"""
    # TODO: Exchange code for tokens and store encrypted
    
    # Check if already connected
    result = await db.execute(
        select(Connection).where(
            (Connection.user_id == UUID(user_id)) &
            (Connection.provider == "google_gmail")
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gmail is already connected"
        )
    
    connection = Connection(
        user_id=UUID(user_id),
        provider="google_gmail",
        token_encrypted="encrypted_token_placeholder",
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
        status="active"
    )
    
    db.add(connection)
    await db.commit()
    await db.refresh(connection)
    
    return ConnectionResponse(
        id=str(connection.id),
        provider=connection.provider,
        status=connection.status,
        scopes=connection.scopes,
        last_sync_at=connection.last_sync_at,
        created_at=connection.created_at
    )


@router.post("/google/calendar", response_model=ConnectionResponse)
async def connect_calendar(
    request: ConnectionCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Connect Google Calendar for interview sync"""
    # TODO: Exchange code for tokens and store encrypted
    
    # Check if already connected
    result = await db.execute(
        select(Connection).where(
            (Connection.user_id == UUID(user_id)) &
            (Connection.provider == "google_calendar")
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Calendar is already connected"
        )
    
    connection = Connection(
        user_id=UUID(user_id),
        provider="google_calendar",
        token_encrypted="encrypted_token_placeholder",
        scopes=["https://www.googleapis.com/auth/calendar.readonly"],
        status="active"
    )
    
    db.add(connection)
    await db.commit()
    await db.refresh(connection)
    
    return ConnectionResponse(
        id=str(connection.id),
        provider=connection.provider,
        status=connection.status,
        scopes=connection.scopes,
        last_sync_at=connection.last_sync_at,
        created_at=connection.created_at
    )


@router.delete("/{connection_id}")
async def disconnect(
    connection_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Remove a connection"""
    result = await db.execute(
        select(Connection).where(
            (Connection.id == UUID(connection_id)) &
            (Connection.user_id == UUID(user_id))
        )
    )
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    await db.delete(connection)
    await db.commit()
    
    return {"message": "Connection removed successfully"}


@router.post("/{connection_id}/sync")
async def sync_connection(
    connection_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Trigger manual sync for a connection"""
    result = await db.execute(
        select(Connection).where(
            (Connection.id == UUID(connection_id)) &
            (Connection.user_id == UUID(user_id))
        )
    )
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    # TODO: Implement actual sync logic
    connection.last_sync_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Sync completed", "synced_at": connection.last_sync_at}
