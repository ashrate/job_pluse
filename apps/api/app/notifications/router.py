"""
Notifications Router
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.security import get_current_user_id

router = APIRouter()


class NotificationResponse(BaseModel):
    """Notification response"""
    id: str
    type: str
    title: str
    message: str
    link: Optional[str]
    read: bool
    created_at: datetime


class NotificationSettings(BaseModel):
    """Notification settings"""
    email_enabled: bool = True
    deadline_reminder_days: int = 3
    interview_reminder_hours: int = 24
    followup_days: int = 7


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    user_id: str = Depends(get_current_user_id)
):
    """Get notifications for current user"""
    # TODO: Implement database storage for notifications
    # For now, return empty list
    return []


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Mark notification as read"""
    return {"message": "Notification marked as read"}


@router.post("/read-all")
async def mark_all_as_read(
    user_id: str = Depends(get_current_user_id)
):
    """Mark all notifications as read"""
    return {"message": "All notifications marked as read"}


@router.get("/settings", response_model=NotificationSettings)
async def get_notification_settings(
    user_id: str = Depends(get_current_user_id)
):
    """Get notification settings"""
    # TODO: Load from database
    return NotificationSettings()


@router.put("/settings", response_model=NotificationSettings)
async def update_notification_settings(
    settings: NotificationSettings,
    user_id: str = Depends(get_current_user_id)
):
    """Update notification settings"""
    # TODO: Save to database
    return settings
