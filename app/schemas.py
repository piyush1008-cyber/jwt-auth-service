from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    """Payload for registering a new user."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, description="Password with minimum 8 characters")
    full_name: Optional[str] = None
    role: Optional[str] = Field("user", pattern="^(user|moderator|admin)$")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip().lower()
        if not v.isalnum() and not all(c in "_-" or c.isalnum() for c in v):
            raise ValueError("Username may only contain letters, numbers, hyphens, and underscores")
        return v


class UserLogin(BaseModel):
    """Payload for user authentication."""
    username_or_email: str
    password: str


class UserResponse(BaseModel):
    """Public user profile response."""
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """JWT Token exchange response payload."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class RefreshTokenRequest(BaseModel):
    """Payload for rotating an expired access token."""
    refresh_token: str


class MessageResponse(BaseModel):
    """Generic status notification message."""
    message: str
    status: str = "success"
