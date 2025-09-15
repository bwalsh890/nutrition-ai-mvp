from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from database import get_db, engine
from models import Base
from schemas import UserCreate, UserResponse, UserUpdate, ChatRequest, ChatResponse, ChatMessage, MessageTrackingResponse, HealthProfileCreate, HealthProfileUpdate, HealthProfileResponse
from crud import create_user, get_user, get_users, update_user, delete_user, check_message_limit, increment_message_count, get_current_month_year, get_user_health_profile, create_user_health_profile, update_user_health_profile, delete_user_health_profile, get_health_profile_for_ai
from openai_service import get_openai_service

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Nutrition AI MVP",
    description="A FastAPI application with PostgreSQL",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Nutrition AI MVP API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# User endpoints
@app.post("/users/", response_model=UserResponse)
async def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)

@app.get("/users/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user_endpoint(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}")
async def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    success = delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # Check message limit for user
        is_within_limit, current_count, remaining = check_message_limit(db, chat_request.user_id, limit=50)
        
        if not is_within_limit:
            raise HTTPException(
                status_code=429, 
                detail=f"Message limit exceeded. You have used {current_count}/50 messages this month. Please try again next month."
            )
        
        # Get user's health profile for personalized advice
        health_profile = get_health_profile_for_ai(db, chat_request.user_id)
        
        # Get OpenAI service
        openai_service = get_openai_service()
        
        # Get response from OpenAI with health context
        response = await openai_service.chat_completion(
            message=chat_request.message,
            conversation_history=chat_request.conversation_history,
            health_profile=health_profile
        )
        
        # Increment message count after successful API call
        increment_message_count(db, chat_request.user_id)
        
        # Update conversation history
        updated_history = chat_request.conversation_history.copy()
        updated_history.append(ChatMessage(role="user", content=chat_request.message))
        updated_history.append(ChatMessage(role="assistant", content=response))
        
        return ChatResponse(
            response=response,
            conversation_history=updated_history
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

# Message usage endpoint
@app.get("/users/{user_id}/message-usage", response_model=MessageTrackingResponse)
async def get_message_usage(user_id: int, db: Session = Depends(get_db)):
    """Get user's current message usage for this month."""
    is_within_limit, current_count, remaining = check_message_limit(db, user_id, limit=50)
    month_year = get_current_month_year()
    
    return MessageTrackingResponse(
        user_id=user_id,
        month_year=month_year,
        message_count=current_count,
        remaining_messages=remaining,
        limit=50
    )

# Health profile endpoints
@app.post("/users/{user_id}/health-profile", response_model=HealthProfileResponse)
async def create_health_profile(user_id: int, health_profile: HealthProfileCreate, db: Session = Depends(get_db)):
    """Create a new health profile for a user."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if health profile already exists
    existing_profile = get_user_health_profile(db, user_id)
    if existing_profile:
        raise HTTPException(status_code=400, detail="Health profile already exists. Use PUT to update.")
    
    # Create health profile
    health_data = health_profile.dict(exclude_unset=True)
    db_health_profile = create_user_health_profile(db, user_id, health_data)
    
    # Convert JSON strings back to lists for response
    import json
    response_data = {
        "id": db_health_profile.id,
        "user_id": db_health_profile.user_id,
        "age": db_health_profile.age,
        "gender": db_health_profile.gender,
        "height_cm": db_health_profile.height_cm,
        "weight_kg": db_health_profile.weight_kg,
        "activity_level": db_health_profile.activity_level,
        "created_at": db_health_profile.created_at,
        "updated_at": db_health_profile.updated_at,
    }
    
    # Parse JSON fields
    json_fields = ['dietary_restrictions', 'health_conditions', 'fitness_goals', 'allergies', 'medications']
    for field in json_fields:
        value = getattr(db_health_profile, field)
        if value:
            try:
                response_data[field] = json.loads(value)
            except json.JSONDecodeError:
                response_data[field] = []
        else:
            response_data[field] = []
    
    return HealthProfileResponse(**response_data)

@app.get("/users/{user_id}/health-profile", response_model=HealthProfileResponse)
async def get_health_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user's health profile."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_health_profile = get_user_health_profile(db, user_id)
    if not db_health_profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    
    # Convert JSON strings back to lists for response
    import json
    response_data = {
        "id": db_health_profile.id,
        "user_id": db_health_profile.user_id,
        "age": db_health_profile.age,
        "gender": db_health_profile.gender,
        "height_cm": db_health_profile.height_cm,
        "weight_kg": db_health_profile.weight_kg,
        "activity_level": db_health_profile.activity_level,
        "created_at": db_health_profile.created_at,
        "updated_at": db_health_profile.updated_at,
    }
    
    # Parse JSON fields
    json_fields = ['dietary_restrictions', 'health_conditions', 'fitness_goals', 'allergies', 'medications']
    for field in json_fields:
        value = getattr(db_health_profile, field)
        if value:
            try:
                response_data[field] = json.loads(value)
            except json.JSONDecodeError:
                response_data[field] = []
        else:
            response_data[field] = []
    
    return HealthProfileResponse(**response_data)

@app.put("/users/{user_id}/health-profile", response_model=HealthProfileResponse)
async def update_health_profile(user_id: int, health_profile: HealthProfileUpdate, db: Session = Depends(get_db)):
    """Update user's health profile."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update health profile
    health_data = health_profile.dict(exclude_unset=True)
    db_health_profile = update_user_health_profile(db, user_id, health_data)
    
    if not db_health_profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    
    # Convert JSON strings back to lists for response
    import json
    response_data = {
        "id": db_health_profile.id,
        "user_id": db_health_profile.user_id,
        "age": db_health_profile.age,
        "gender": db_health_profile.gender,
        "height_cm": db_health_profile.height_cm,
        "weight_kg": db_health_profile.weight_kg,
        "activity_level": db_health_profile.activity_level,
        "created_at": db_health_profile.created_at,
        "updated_at": db_health_profile.updated_at,
    }
    
    # Parse JSON fields
    json_fields = ['dietary_restrictions', 'health_conditions', 'fitness_goals', 'allergies', 'medications']
    for field in json_fields:
        value = getattr(db_health_profile, field)
        if value:
            try:
                response_data[field] = json.loads(value)
            except json.JSONDecodeError:
                response_data[field] = []
        else:
            response_data[field] = []
    
    return HealthProfileResponse(**response_data)

@app.delete("/users/{user_id}/health-profile")
async def delete_health_profile(user_id: int, db: Session = Depends(get_db)):
    """Delete user's health profile."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = delete_user_health_profile(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Health profile not found")
    
    return {"message": "Health profile deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
