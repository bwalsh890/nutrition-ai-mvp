from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Base schema
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True

# Schema for creating a user
class UserCreate(UserBase):
    password: str

# Schema for updating a user
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

# Schema for user response
class UserResponse(UserBase):
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema for user in database
class UserInDB(UserResponse):
    hashed_password: str

# Chat schemas
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    user_id: int
    conversation_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    response: str
    conversation_history: List[ChatMessage]

# Message tracking schemas
class MessageTrackingResponse(BaseModel):
    user_id: int
    month_year: str
    message_count: int
    remaining_messages: int
    limit: int = 50
    
    class Config:
        from_attributes = True

# Health profile schemas
class HealthProfileCreate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    activity_level: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = []
    health_conditions: Optional[List[str]] = []
    fitness_goals: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    medications: Optional[List[str]] = []

class HealthProfileUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    activity_level: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    health_conditions: Optional[List[str]] = None
    fitness_goals: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    medications: Optional[List[str]] = None

class HealthProfileResponse(BaseModel):
    id: int
    user_id: int
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    activity_level: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = []
    health_conditions: Optional[List[str]] = []
    fitness_goals: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    medications: Optional[List[str]] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
