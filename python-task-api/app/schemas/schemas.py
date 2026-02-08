"""
Pydantic schemas for request/response validation
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.models import UserRole, TaskStatus, TaskPriority


# ============ User Schemas ============


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation"""

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for user update"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserInDB(UserBase):
    """User schema with database fields"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserResponse(UserInDB):
    """User response schema"""

    pass


# ============ Task Schemas ============


class TaskBase(BaseModel):
    """Base task schema"""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Schema for task creation"""

    pass


class TaskUpdate(BaseModel):
    """Schema for task update"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskInDB(TaskBase):
    """Task schema with database fields"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TaskResponse(TaskInDB):
    """Task response schema"""

    pass


# ============ Authentication Schemas ============


class Token(BaseModel):
    """Token response schema"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""

    user_id: Optional[int] = None
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema"""

    username: str
    password: str


# ============ Generic Schemas ============


class PaginatedResponse(BaseModel):
    """Generic paginated response"""

    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


class HealthCheck(BaseModel):
    """Health check response"""

    status: str
    version: str
    timestamp: datetime


class MessageResponse(BaseModel):
    """Generic message response"""

    message: str
