from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import uvicorn
import logging
import time
import json
from datetime import datetime

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
from onboarding_service import OnboardingChatService
from ai_profiling_service import AIProfilingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize onboarding service
onboarding_service = OnboardingChatService()
ai_profiling_service = AIProfilingService()

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

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.3f}s")
    return response

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
@app.post("/chat")
async def chat_endpoint(request: dict, db: Session = Depends(get_db)):
    try:
        user_id = request.get("user_id")
        message = request.get("message")
        health_profile = request.get("health_profile", {})
        current_diet_plan = request.get("current_diet_plan", {})
        
        if not user_id or not message:
            raise HTTPException(status_code=400, detail="user_id and message are required")
        
        # Check message limit for user
        is_within_limit, current_count, remaining = check_message_limit(db, user_id, limit=50)
        
        if not is_within_limit:
            raise HTTPException(
                status_code=429, 
                detail=f"Message limit exceeded. You have used {current_count}/50 messages this month. Please try again next month."
            )
        
        # Get OpenAI service
        openai_service = get_openai_service()
        
        # Create enhanced context for diet plan modifications
        diet_context = f"""
        Current diet plan: {json.dumps(current_diet_plan, indent=2)}
        User health profile: {json.dumps(health_profile, indent=2)}
        
        The user can ask for diet modifications like:
        - "Make it paleo"
        - "Make it 2000 calories per day"
        - "Make it vegetarian"
        - "Add more protein"
        - "Reduce carbs"
        
        If the user requests diet modifications, respond with a JSON object containing:
        {{
            "response": "Your conversational response to the user",
            "diet_plan_modifications": {{
                "Monday": {{"Breakfast": "new meal", "Lunch": "new meal", ...}},
                "Tuesday": {{"Breakfast": "new meal", "Lunch": "new meal", ...}},
                ...
            }}
        }}
        
        If no diet modifications are needed, just respond normally without the diet_plan_modifications field.
        """
        
        # Get response from OpenAI with enhanced context
        response = await openai_service.chat_completion(
            message=f"{diet_context}\n\nUser message: {message}",
            conversation_history=[],
            health_profile=health_profile
        )
        
        # Increment message count after successful API call
        increment_message_count(db, user_id)
        
        # Try to parse JSON response for diet modifications
        try:
            # Look for JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed_response = json.loads(json_match.group())
                return {
                    "response": parsed_response.get("response", response),
                    "diet_plan_modifications": parsed_response.get("diet_plan_modifications")
                }
        except:
            pass
        
        # If no JSON found, return normal response
        return {
            "response": response,
            "diet_plan_modifications": None
        }
        
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

# Onboarding chat endpoints
@app.post("/onboarding-chat")
async def onboarding_chat(
    request: dict,
    db: Session = Depends(get_db)
):
    """Handle onboarding chat conversation"""
    try:
        # Extract parameters from request body
        user_id = request.get("user_id")
        message = request.get("message")
        session_data = request.get("session_data")
        
        # Initialize session data if not provided
        if session_data is None:
            session_data = {
                "current_question_id": 0,
                "waiting_for_follow_up": False,
                "collected_data": {},
                "started_at": datetime.now().isoformat()
            }
        
        # Process the user's response
        updated_session, ai_response = onboarding_service.process_response(
            session_data, message
        )
        
        # Check if onboarding is complete
        is_complete = (
            updated_session.get("current_question_id", 0) >= len(onboarding_service.questions)
        )
        
        if is_complete:
            # Build comprehensive user profile
            collected_data = updated_session.get("collected_data", {})
            user_profile = onboarding_service.build_user_profile(collected_data)
            profile_summary = onboarding_service.get_profile_summary(collected_data)
            diet_recommendations = onboarding_service.get_diet_recommendations(collected_data)
            
            # Log the profile for debugging
            logger.info(f"User Profile Built: {profile_summary}")
            logger.info(f"Diet Recommendations: {diet_recommendations}")
            
            # Save profile data to database (simplified for now)
            questionnaire_data = {
                "sleep_hours": 8,  # Default
                "water_goal_ml": 2000,  # Default
                "meal_frequency": 3,  # Default
                "exercise_frequency": 3,  # Default
                "exercise_duration": 30,  # Default
                "stress_level": "moderate",  # Default
                "energy_level": user_profile.get("current_energy_level", "medium"),
                "weight_goal": "maintain",  # Default
                "target_weight_kg": float(user_profile.get("weight_kg", 70))
            }
            
            # Save to database
            try:
                create_user_questionnaire(db, user_id, questionnaire_data)
                logger.info(f"Questionnaire saved for user {user_id}")
            except Exception as e:
                logger.error(f"Error saving questionnaire: {e}")
        
        return {
            "response": ai_response,
            "session_data": updated_session,
            "is_complete": is_complete,
            "progress": {
                "current_question": updated_session.get("current_question_id", 0) + 1,
                "total_questions": len(onboarding_service.questions),
                "percentage": ((updated_session.get("current_question_id", 0) + 1) / len(onboarding_service.questions)) * 100
            }
        }
        
    except Exception as e:
        logger.error(f"Error in onboarding chat: {e}")
        return {"error": "Sorry, I encountered an error. Please try again."}

@app.post("/start-onboarding/{user_id}")
async def start_onboarding(user_id: int):
    """Start the onboarding process"""
    first_question = onboarding_service.get_next_question({
        "current_question_id": 0,
        "waiting_for_follow_up": False,
        "collected_data": {}
    })
    
    return {
        "message": "Hi! I'm here to help you discover your personalized nutrition path. This conversation will help me understand what matters most to you and build a plan that truly fits your life.",
        "question": first_question["question"],
        "session_data": {
            "current_question_id": 0,
            "waiting_for_follow_up": False,
            "collected_data": {},
            "started_at": datetime.now().isoformat()
        }
    }

# AI Profiling endpoints
@app.post("/start-ai-profiling/{user_id}")
async def start_ai_profiling(user_id: int):
    """Start the AI-driven profiling process"""
    try:
        result = await ai_profiling_service.start_profiling(user_id)
        return result
    except Exception as e:
        logger.error(f"Error starting AI profiling: {e}")
        return {"error": "Sorry, I encountered an error starting the profiling process."}

@app.post("/ai-profiling-chat")
async def ai_profiling_chat(request: dict):
    """Handle AI profiling conversation"""
    try:
        user_id = request.get("user_id")
        message = request.get("message")
        session_data = request.get("session_data")
        
        if not user_id or not message or not session_data:
            raise HTTPException(status_code=400, detail="user_id, message, and session_data are required")
        
        result = await ai_profiling_service.process_user_response(session_data, message)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI profiling chat: {e}")
        return {"error": "Sorry, I encountered an error. Please try again."}

@app.post("/build-meal-plan/{user_id}")
async def build_meal_plan(user_id: int, request: dict):
    """Build personalized meal plan from completed profile"""
    try:
        profile_data = request.get("profile_data")
        if not profile_data:
            raise HTTPException(status_code=400, detail="profile_data is required")
        
        meal_plan = ai_profiling_service.build_meal_plan(profile_data)
        
        return {
            "meal_plan": meal_plan,
            "message": "Your personalized meal plan is ready! 🎯"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error building meal plan: {e}")
        return {"error": "Sorry, I encountered an error building your meal plan."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
