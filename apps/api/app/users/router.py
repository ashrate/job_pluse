"""
Users Router
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.db.database import get_db
from app.db.models import User
from app.core.security import get_current_user_id

router = APIRouter()


class UserUpdateRequest(BaseModel):
    """User profile update request"""
    name: Optional[str] = None
    target_role: Optional[str] = None
    target_level: Optional[str] = None
    target_location: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    target_role: Optional[str] = None
    target_level: Optional[str] = None
    target_location: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get current user profile"""
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        target_role=user.target_role,
        target_level=user.target_level,
        target_location=user.target_location
    )


@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    request: UserUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile"""
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields if provided
    if request.name is not None:
        user.name = request.name
    if request.target_role is not None:
        user.target_role = request.target_role
    if request.target_level is not None:
        user.target_level = request.target_level
    if request.target_location is not None:
        user.target_location = request.target_location
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        target_role=user.target_role,
        target_level=user.target_level,
        target_location=user.target_location
    )


@router.delete("/account")
async def delete_account(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete user account and all associated data"""
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db.delete(user)
    await db.commit()
    
    return {"message": "Account deleted successfully"}
