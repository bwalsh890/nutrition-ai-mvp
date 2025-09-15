from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date

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

# Habit tracking schemas
class QuestionnaireCreate(BaseModel):
    sleep_hours: Optional[float] = None
    water_goal_ml: Optional[int] = None
    meal_frequency: Optional[int] = None
    exercise_frequency: Optional[int] = None
    exercise_duration: Optional[int] = None
    stress_level: Optional[str] = None
    energy_level: Optional[str] = None
    mood_tracking: Optional[bool] = False
    weight_goal: Optional[str] = None
    target_weight_kg: Optional[float] = None

class QuestionnaireUpdate(BaseModel):
    sleep_hours: Optional[float] = None
    water_goal_ml: Optional[int] = None
    meal_frequency: Optional[int] = None
    exercise_frequency: Optional[int] = None
    exercise_duration: Optional[int] = None
    stress_level: Optional[str] = None
    energy_level: Optional[str] = None
    mood_tracking: Optional[bool] = None
    weight_goal: Optional[str] = None
    target_weight_kg: Optional[float] = None

class QuestionnaireResponse(BaseModel):
    id: int
    user_id: int
    sleep_hours: Optional[float] = None
    water_goal_ml: Optional[int] = None
    meal_frequency: Optional[int] = None
    exercise_frequency: Optional[int] = None
    exercise_duration: Optional[int] = None
    stress_level: Optional[str] = None
    energy_level: Optional[str] = None
    mood_tracking: bool = False
    weight_goal: Optional[str] = None
    target_weight_kg: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class HabitTargetCreate(BaseModel):
    habit_type: str  # "water", "meals", "exercise", "sleep"
    target_value: float
    target_unit: str  # "ml", "count", "minutes", "hours"

class HabitTargetUpdate(BaseModel):
    target_value: Optional[float] = None
    target_unit: Optional[str] = None
    is_active: Optional[bool] = None

class HabitTargetResponse(BaseModel):
    id: int
    user_id: int
    habit_type: str
    target_value: float
    target_unit: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class HabitLogCreate(BaseModel):
    log_date: date
    habit_type: str  # "water", "meals", "exercise", "sleep", "mood"
    logged_value: float
    unit: str  # "ml", "count", "minutes", "hours", "rating"
    notes: Optional[str] = None

class HabitLogUpdate(BaseModel):
    logged_value: Optional[float] = None
    unit: Optional[str] = None
    notes: Optional[str] = None

class HabitLogResponse(BaseModel):
    id: int
    user_id: int
    log_date: date
    habit_type: str
    logged_value: float
    unit: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProgressStatsResponse(BaseModel):
    id: int
    user_id: int
    stat_date: date
    period_type: str  # "daily", "weekly", "monthly"
    habit_type: str
    total_value: float
    target_value: float
    completion_percentage: float
    streak_days: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DailyProgressResponse(BaseModel):
    date: date
    habit_type: str
    logged_value: float
    target_value: float
    completion_percentage: float
    streak_days: int
    is_goal_met: bool

class WeeklyProgressResponse(BaseModel):
    week_start: date
    week_end: date
    habit_type: str
    total_value: float
    target_value: float
    completion_percentage: float
    days_met: int
    total_days: int

class MonthlyProgressResponse(BaseModel):
    month: str  # "2024-01"
    habit_type: str
    total_value: float
    target_value: float
    completion_percentage: float
    days_met: int
    total_days: int

class FeedbackResponse(BaseModel):
    habit_type: str
    feedback_message: str
    suggestions: List[str]
    encouragement: str
    completion_percentage: float
    streak_days: int
