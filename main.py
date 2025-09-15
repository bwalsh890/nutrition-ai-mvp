from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from database import get_db, engine
from models import Base
from schemas import (UserCreate, UserResponse, UserUpdate, ChatRequest, ChatResponse, ChatMessage, MessageTrackingResponse, 
                    HealthProfileCreate, HealthProfileUpdate, HealthProfileResponse, QuestionnaireCreate, QuestionnaireUpdate, 
                    QuestionnaireResponse, HabitTargetCreate, HabitTargetUpdate, HabitTargetResponse, HabitLogCreate, 
                    HabitLogUpdate, HabitLogResponse, DailyProgressResponse, WeeklyProgressResponse, MonthlyProgressResponse, 
                    FeedbackResponse)
from crud import (create_user, get_user, get_users, update_user, delete_user, check_message_limit, increment_message_count, 
                 get_current_month_year, get_user_health_profile, create_user_health_profile, update_user_health_profile, 
                 delete_user_health_profile, get_health_profile_for_ai, get_user_questionnaire, create_user_questionnaire, 
                 update_user_questionnaire, delete_user_questionnaire, get_user_habit_targets, get_habit_target, 
                 create_habit_target, update_habit_target, delete_habit_target, get_habit_logs, get_habit_log, 
                 create_habit_log, update_habit_log, delete_habit_log, calculate_daily_progress, calculate_weekly_progress, 
                 calculate_monthly_progress, generate_feedback)
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

# Questionnaire endpoints
@app.post("/users/{user_id}/questionnaire", response_model=QuestionnaireResponse)
async def create_questionnaire(user_id: int, questionnaire: QuestionnaireCreate, db: Session = Depends(get_db)):
    """Create a new questionnaire for a user."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if questionnaire already exists
    existing_questionnaire = get_user_questionnaire(db, user_id)
    if existing_questionnaire:
        raise HTTPException(status_code=400, detail="Questionnaire already exists. Use PUT to update.")
    
    # Create questionnaire
    questionnaire_data = questionnaire.dict(exclude_unset=True)
    db_questionnaire = create_user_questionnaire(db, user_id, questionnaire_data)
    
    return db_questionnaire

@app.get("/users/{user_id}/questionnaire", response_model=QuestionnaireResponse)
async def get_questionnaire(user_id: int, db: Session = Depends(get_db)):
    """Get user's questionnaire."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_questionnaire = get_user_questionnaire(db, user_id)
    if not db_questionnaire:
        raise HTTPException(status_code=404, detail="Questionnaire not found")
    
    return db_questionnaire

@app.put("/users/{user_id}/questionnaire", response_model=QuestionnaireResponse)
async def update_questionnaire(user_id: int, questionnaire: QuestionnaireUpdate, db: Session = Depends(get_db)):
    """Update user's questionnaire."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update questionnaire
    questionnaire_data = questionnaire.dict(exclude_unset=True)
    db_questionnaire = update_user_questionnaire(db, user_id, questionnaire_data)
    
    if not db_questionnaire:
        raise HTTPException(status_code=404, detail="Questionnaire not found")
    
    return db_questionnaire

@app.delete("/users/{user_id}/questionnaire")
async def delete_questionnaire(user_id: int, db: Session = Depends(get_db)):
    """Delete user's questionnaire."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = delete_user_questionnaire(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Questionnaire not found")
    
    return {"message": "Questionnaire deleted successfully"}

# Habit Target endpoints
@app.post("/users/{user_id}/habit-targets", response_model=HabitTargetResponse)
async def create_habit_target(user_id: int, habit_target: HabitTargetCreate, db: Session = Depends(get_db)):
    """Create a new habit target for a user."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if target already exists for this habit type
    existing_target = get_habit_target(db, user_id, habit_target.habit_type)
    if existing_target:
        raise HTTPException(status_code=400, detail=f"Target already exists for habit type '{habit_target.habit_type}'. Use PUT to update.")
    
    # Create habit target
    habit_target_data = habit_target.dict()
    db_habit_target = create_habit_target(db, user_id, habit_target_data)
    
    return db_habit_target

@app.get("/users/{user_id}/habit-targets", response_model=List[HabitTargetResponse])
async def get_habit_targets(user_id: int, habit_type: str = None, db: Session = Depends(get_db)):
    """Get user's habit targets."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    targets = get_user_habit_targets(db, user_id, habit_type)
    return targets

@app.get("/users/{user_id}/habit-targets/{habit_type}", response_model=HabitTargetResponse)
async def get_habit_target_endpoint(user_id: int, habit_type: str, db: Session = Depends(get_db)):
    """Get a specific habit target for a user."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    target = get_habit_target(db, user_id, habit_type)
    if not target:
        raise HTTPException(status_code=404, detail=f"Habit target not found for type '{habit_type}'")
    
    return target

@app.put("/users/{user_id}/habit-targets/{habit_type}", response_model=HabitTargetResponse)
async def update_habit_target_endpoint(user_id: int, habit_type: str, habit_target: HabitTargetUpdate, db: Session = Depends(get_db)):
    """Update a habit target for a user."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update habit target
    habit_target_data = habit_target.dict(exclude_unset=True)
    db_habit_target = update_habit_target(db, user_id, habit_type, habit_target_data)
    
    if not db_habit_target:
        raise HTTPException(status_code=404, detail=f"Habit target not found for type '{habit_type}'")
    
    return db_habit_target

@app.delete("/users/{user_id}/habit-targets/{habit_type}")
async def delete_habit_target_endpoint(user_id: int, habit_type: str, db: Session = Depends(get_db)):
    """Delete a habit target for a user."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = delete_habit_target(db, user_id, habit_type)
    if not success:
        raise HTTPException(status_code=404, detail=f"Habit target not found for type '{habit_type}'")
    
    return {"message": f"Habit target for '{habit_type}' deleted successfully"}

# Habit Log endpoints
@app.post("/users/{user_id}/habit-logs", response_model=HabitLogResponse)
async def create_habit_log(user_id: int, habit_log: HabitLogCreate, db: Session = Depends(get_db)):
    """Create a new habit log for a user."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if log already exists for this date and habit type
    existing_log = get_habit_log(db, user_id, habit_log.log_date, habit_log.habit_type)
    if existing_log:
        raise HTTPException(status_code=400, detail=f"Log already exists for {habit_log.habit_type} on {habit_log.log_date}. Use PUT to update.")
    
    # Create habit log
    habit_log_data = habit_log.dict()
    db_habit_log = create_habit_log(db, user_id, habit_log_data)
    
    return db_habit_log

@app.get("/users/{user_id}/habit-logs", response_model=List[HabitLogResponse])
async def get_habit_logs_endpoint(user_id: int, habit_type: str = None, start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    """Get user's habit logs with optional filters."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Parse dates if provided
    from datetime import date
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = date.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    
    if end_date:
        try:
            end_date_obj = date.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    logs = get_habit_logs(db, user_id, habit_type, start_date_obj, end_date_obj)
    return logs

@app.get("/users/{user_id}/habit-logs/{log_date}/{habit_type}", response_model=HabitLogResponse)
async def get_habit_log_endpoint(user_id: int, log_date: str, habit_type: str, db: Session = Depends(get_db)):
    """Get a specific habit log for a user."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Parse date
    from datetime import date
    try:
        log_date_obj = date.fromisoformat(log_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid log_date format. Use YYYY-MM-DD")
    
    log = get_habit_log(db, user_id, log_date_obj, habit_type)
    if not log:
        raise HTTPException(status_code=404, detail=f"Habit log not found for {habit_type} on {log_date}")
    
    return log

@app.put("/users/{user_id}/habit-logs/{log_date}/{habit_type}", response_model=HabitLogResponse)
async def update_habit_log_endpoint(user_id: int, log_date: str, habit_type: str, habit_log: HabitLogUpdate, db: Session = Depends(get_db)):
    """Update a habit log for a user."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Parse date
    from datetime import date
    try:
        log_date_obj = date.fromisoformat(log_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid log_date format. Use YYYY-MM-DD")
    
    # Update habit log
    habit_log_data = habit_log.dict(exclude_unset=True)
    db_habit_log = update_habit_log(db, user_id, log_date_obj, habit_type, habit_log_data)
    
    if not db_habit_log:
        raise HTTPException(status_code=404, detail=f"Habit log not found for {habit_type} on {log_date}")
    
    return db_habit_log

@app.delete("/users/{user_id}/habit-logs/{log_date}/{habit_type}")
async def delete_habit_log_endpoint(user_id: int, log_date: str, habit_type: str, db: Session = Depends(get_db)):
    """Delete a habit log for a user."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Parse date
    from datetime import date
    try:
        log_date_obj = date.fromisoformat(log_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid log_date format. Use YYYY-MM-DD")
    
    success = delete_habit_log(db, user_id, log_date_obj, habit_type)
    if not success:
        raise HTTPException(status_code=404, detail=f"Habit log not found for {habit_type} on {log_date}")
    
    return {"message": f"Habit log for {habit_type} on {log_date} deleted successfully"}

# Progress endpoints
@app.get("/users/{user_id}/progress/daily/{target_date}/{habit_type}", response_model=DailyProgressResponse)
async def get_daily_progress(user_id: int, target_date: str, habit_type: str, db: Session = Depends(get_db)):
    """Get daily progress for a specific habit."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Parse date
    from datetime import date
    try:
        target_date_obj = date.fromisoformat(target_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid target_date format. Use YYYY-MM-DD")
    
    progress = calculate_daily_progress(db, user_id, target_date_obj, habit_type)
    
    if "error" in progress:
        raise HTTPException(status_code=404, detail=progress["error"])
    
    return DailyProgressResponse(**progress)

@app.get("/users/{user_id}/progress/weekly/{week_start}/{habit_type}", response_model=WeeklyProgressResponse)
async def get_weekly_progress(user_id: int, week_start: str, habit_type: str, db: Session = Depends(get_db)):
    """Get weekly progress for a specific habit."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Parse date
    from datetime import date
    try:
        week_start_obj = date.fromisoformat(week_start)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid week_start format. Use YYYY-MM-DD")
    
    progress = calculate_weekly_progress(db, user_id, week_start_obj, habit_type)
    
    if "error" in progress:
        raise HTTPException(status_code=404, detail=progress["error"])
    
    return WeeklyProgressResponse(**progress)

@app.get("/users/{user_id}/progress/monthly/{year}/{month}/{habit_type}", response_model=MonthlyProgressResponse)
async def get_monthly_progress(user_id: int, year: int, month: int, habit_type: str, db: Session = Depends(get_db)):
    """Get monthly progress for a specific habit."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate month
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    progress = calculate_monthly_progress(db, user_id, year, month, habit_type)
    
    if "error" in progress:
        raise HTTPException(status_code=404, detail=progress["error"])
    
    return MonthlyProgressResponse(**progress)

# Feedback endpoint
@app.get("/users/{user_id}/feedback/{habit_type}", response_model=FeedbackResponse)
async def get_feedback(user_id: int, habit_type: str, days: int = 7, db: Session = Depends(get_db)):
    """Get feedback for a specific habit based on recent performance."""
    # Check if user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate days parameter
    if days < 1 or days > 30:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 30")
    
    feedback = generate_feedback(db, user_id, habit_type, days)
    
    if "error" in feedback:
        raise HTTPException(status_code=404, detail=feedback["error"])
    
    return FeedbackResponse(**feedback)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
