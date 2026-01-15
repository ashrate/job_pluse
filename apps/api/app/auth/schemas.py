"""
Authentication Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class GoogleAuthRequest(BaseModel):
    """Google OAuth authorization code request"""
    code: str
    redirect_uri: Optional[str] = None


class TokenResponse(BaseModel):
    """JWT Token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """Current user response"""
    id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    target_role: Optional[str] = None
    target_level: Optional[str] = None
    target_location: Optional[str] = None
    
    class Config:
        from_attributes = True
