from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.context import CryptContext
from datetime import datetime, date
from models import User, MessageTracking, UserHealthProfile, UserQuestionnaire, DailyHabitLog, HabitTarget, ProgressStats
from schemas import UserCreate, UserUpdate

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username."""
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get multiple users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    """Update a user."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    update_data = user.dict(exclude_unset=True)
    
    # Hash password if it's being updated
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True

# Message tracking CRUD operations
def get_current_month_year() -> str:
    """Get current month-year string in format 'YYYY-MM'."""
    now = datetime.now()
    return f"{now.year}-{now.month:02d}"

def get_user_message_tracking(db: Session, user_id: int, month_year: str = None) -> Optional[MessageTracking]:
    """Get user's message tracking for a specific month."""
    if month_year is None:
        month_year = get_current_month_year()
    
    return db.query(MessageTracking).filter(
        MessageTracking.user_id == user_id,
        MessageTracking.month_year == month_year
    ).first()

def create_message_tracking(db: Session, user_id: int, month_year: str = None) -> MessageTracking:
    """Create new message tracking record for a user."""
    if month_year is None:
        month_year = get_current_month_year()
    
    db_tracking = MessageTracking(
        user_id=user_id,
        month_year=month_year,
        message_count=0
    )
    db.add(db_tracking)
    db.commit()
    db.refresh(db_tracking)
    return db_tracking

def increment_message_count(db: Session, user_id: int, month_year: str = None) -> MessageTracking:
    """Increment message count for a user in a specific month."""
    if month_year is None:
        month_year = get_current_month_year()
    
    # Get or create tracking record
    tracking = get_user_message_tracking(db, user_id, month_year)
    if not tracking:
        tracking = create_message_tracking(db, user_id, month_year)
    
    # Increment count
    tracking.message_count += 1
    db.commit()
    db.refresh(tracking)
    return tracking

def check_message_limit(db: Session, user_id: int, limit: int = 50, month_year: str = None) -> tuple[bool, int, int]:
    """
    Check if user has exceeded message limit.
    Returns: (is_within_limit, current_count, remaining_messages)
    """
    if month_year is None:
        month_year = get_current_month_year()
    
    tracking = get_user_message_tracking(db, user_id, month_year)
    current_count = tracking.message_count if tracking else 0
    remaining = max(0, limit - current_count)
    is_within_limit = current_count < limit
    
    return is_within_limit, current_count, remaining

# Health profile CRUD operations
def get_user_health_profile(db: Session, user_id: int) -> Optional[UserHealthProfile]:
    """Get user's health profile."""
    return db.query(UserHealthProfile).filter(UserHealthProfile.user_id == user_id).first()

def create_user_health_profile(db: Session, user_id: int, health_data: dict) -> UserHealthProfile:
    """Create a new health profile for a user."""
    # Convert lists to JSON strings for storage
    json_fields = ['dietary_restrictions', 'health_conditions', 'fitness_goals', 'allergies', 'medications']
    for field in json_fields:
        if field in health_data and health_data[field] is not None:
            import json
            health_data[field] = json.dumps(health_data[field])
    
    db_health_profile = UserHealthProfile(
        user_id=user_id,
        **health_data
    )
    db.add(db_health_profile)
    db.commit()
    db.refresh(db_health_profile)
    return db_health_profile

def update_user_health_profile(db: Session, user_id: int, health_data: dict) -> Optional[UserHealthProfile]:
    """Update user's health profile."""
    db_health_profile = get_user_health_profile(db, user_id)
    if not db_health_profile:
        return None
    
    # Convert lists to JSON strings for storage
    json_fields = ['dietary_restrictions', 'health_conditions', 'fitness_goals', 'allergies', 'medications']
    for field in json_fields:
        if field in health_data and health_data[field] is not None:
            import json
            health_data[field] = json.dumps(health_data[field])
    
    # Update only provided fields
    for field, value in health_data.items():
        if value is not None:
            setattr(db_health_profile, field, value)
    
    db.commit()
    db.refresh(db_health_profile)
    return db_health_profile

def delete_user_health_profile(db: Session, user_id: int) -> bool:
    """Delete user's health profile."""
    db_health_profile = get_user_health_profile(db, user_id)
    if not db_health_profile:
        return False
    
    db.delete(db_health_profile)
    db.commit()
    return True

def get_health_profile_for_ai(db: Session, user_id: int) -> dict:
    """Get health profile data formatted for AI context."""
    health_profile = get_user_health_profile(db, user_id)
    if not health_profile:
        return {}
    
    # Convert JSON strings back to lists
    import json
    result = {
        "age": health_profile.age,
        "gender": health_profile.gender,
        "height_cm": health_profile.height_cm,
        "weight_kg": health_profile.weight_kg,
        "activity_level": health_profile.activity_level,
    }
    
    # Parse JSON fields
    json_fields = ['dietary_restrictions', 'health_conditions', 'fitness_goals', 'allergies', 'medications']
    for field in json_fields:
        value = getattr(health_profile, field)
        if value:
            try:
                result[field] = json.loads(value)
            except json.JSONDecodeError:
                result[field] = []
        else:
            result[field] = []
    
    return result

# Questionnaire CRUD operations
def get_user_questionnaire(db: Session, user_id: int) -> Optional[UserQuestionnaire]:
    """Get user's questionnaire."""
    return db.query(UserQuestionnaire).filter(UserQuestionnaire.user_id == user_id).first()

def create_user_questionnaire(db: Session, user_id: int, questionnaire_data: dict) -> UserQuestionnaire:
    """Create a new questionnaire for a user."""
    db_questionnaire = UserQuestionnaire(
        user_id=user_id,
        **questionnaire_data
    )
    db.add(db_questionnaire)
    db.commit()
    db.refresh(db_questionnaire)
    return db_questionnaire

def update_user_questionnaire(db: Session, user_id: int, questionnaire_data: dict) -> Optional[UserQuestionnaire]:
    """Update user's questionnaire."""
    db_questionnaire = get_user_questionnaire(db, user_id)
    if not db_questionnaire:
        return None
    
    # Update only provided fields
    for field, value in questionnaire_data.items():
        if value is not None:
            setattr(db_questionnaire, field, value)
    
    db.commit()
    db.refresh(db_questionnaire)
    return db_questionnaire

def delete_user_questionnaire(db: Session, user_id: int) -> bool:
    """Delete user's questionnaire."""
    db_questionnaire = get_user_questionnaire(db, user_id)
    if not db_questionnaire:
        return False
    
    db.delete(db_questionnaire)
    db.commit()
    return True

# Habit Target CRUD operations
def get_user_habit_targets(db: Session, user_id: int, habit_type: str = None) -> List[HabitTarget]:
    """Get user's habit targets, optionally filtered by habit type."""
    query = db.query(HabitTarget).filter(HabitTarget.user_id == user_id)
    if habit_type:
        query = query.filter(HabitTarget.habit_type == habit_type)
    return query.all()

def get_habit_target(db: Session, user_id: int, habit_type: str) -> Optional[HabitTarget]:
    """Get a specific habit target for a user."""
    return db.query(HabitTarget).filter(
        HabitTarget.user_id == user_id,
        HabitTarget.habit_type == habit_type
    ).first()

def create_habit_target(db: Session, user_id: int, habit_target_data: dict) -> HabitTarget:
    """Create a new habit target for a user."""
    db_habit_target = HabitTarget(
        user_id=user_id,
        **habit_target_data
    )
    db.add(db_habit_target)
    db.commit()
    db.refresh(db_habit_target)
    return db_habit_target

def update_habit_target(db: Session, user_id: int, habit_type: str, habit_target_data: dict) -> Optional[HabitTarget]:
    """Update a habit target for a user."""
    db_habit_target = get_habit_target(db, user_id, habit_type)
    if not db_habit_target:
        return None
    
    # Update only provided fields
    for field, value in habit_target_data.items():
        if value is not None:
            setattr(db_habit_target, field, value)
    
    db.commit()
    db.refresh(db_habit_target)
    return db_habit_target

def delete_habit_target(db: Session, user_id: int, habit_type: str) -> bool:
    """Delete a habit target for a user."""
    db_habit_target = get_habit_target(db, user_id, habit_type)
    if not db_habit_target:
        return False
    
    db.delete(db_habit_target)
    db.commit()
    return True

# Daily Habit Log CRUD operations
def get_habit_logs(db: Session, user_id: int, habit_type: str = None, start_date: date = None, end_date: date = None) -> List[DailyHabitLog]:
    """Get user's habit logs with optional filters."""
    query = db.query(DailyHabitLog).filter(DailyHabitLog.user_id == user_id)
    
    if habit_type:
        query = query.filter(DailyHabitLog.habit_type == habit_type)
    if start_date:
        query = query.filter(DailyHabitLog.log_date >= start_date)
    if end_date:
        query = query.filter(DailyHabitLog.log_date <= end_date)
    
    return query.order_by(DailyHabitLog.log_date.desc()).all()

def get_habit_log(db: Session, user_id: int, log_date: date, habit_type: str) -> Optional[DailyHabitLog]:
    """Get a specific habit log for a user on a specific date."""
    return db.query(DailyHabitLog).filter(
        DailyHabitLog.user_id == user_id,
        DailyHabitLog.log_date == log_date,
        DailyHabitLog.habit_type == habit_type
    ).first()

def create_habit_log(db: Session, user_id: int, habit_log_data: dict) -> DailyHabitLog:
    """Create a new habit log for a user."""
    db_habit_log = DailyHabitLog(
        user_id=user_id,
        **habit_log_data
    )
    db.add(db_habit_log)
    db.commit()
    db.refresh(db_habit_log)
    return db_habit_log

def update_habit_log(db: Session, user_id: int, log_date: date, habit_type: str, habit_log_data: dict) -> Optional[DailyHabitLog]:
    """Update a habit log for a user."""
    db_habit_log = get_habit_log(db, user_id, log_date, habit_type)
    if not db_habit_log:
        return None
    
    # Update only provided fields
    for field, value in habit_log_data.items():
        if value is not None:
            setattr(db_habit_log, field, value)
    
    db.commit()
    db.refresh(db_habit_log)
    return db_habit_log

def delete_habit_log(db: Session, user_id: int, log_date: date, habit_type: str) -> bool:
    """Delete a habit log for a user."""
    db_habit_log = get_habit_log(db, user_id, log_date, habit_type)
    if not db_habit_log:
        return False
    
    db.delete(db_habit_log)
    db.commit()
    return True

# Progress Stats CRUD operations
def get_progress_stats(db: Session, user_id: int, habit_type: str = None, period_type: str = None, start_date: date = None, end_date: date = None) -> List[ProgressStats]:
    """Get user's progress stats with optional filters."""
    query = db.query(ProgressStats).filter(ProgressStats.user_id == user_id)
    
    if habit_type:
        query = query.filter(ProgressStats.habit_type == habit_type)
    if period_type:
        query = query.filter(ProgressStats.period_type == period_type)
    if start_date:
        query = query.filter(ProgressStats.stat_date >= start_date)
    if end_date:
        query = query.filter(ProgressStats.stat_date <= end_date)
    
    return query.order_by(ProgressStats.stat_date.desc()).all()

def create_progress_stat(db: Session, user_id: int, progress_data: dict) -> ProgressStats:
    """Create a new progress stat for a user."""
    db_progress_stat = ProgressStats(
        user_id=user_id,
        **progress_data
    )
    db.add(db_progress_stat)
    db.commit()
    db.refresh(db_progress_stat)
    return db_progress_stat

# Helper functions for progress calculations
def calculate_daily_progress(db: Session, user_id: int, target_date: date, habit_type: str) -> dict:
    """Calculate daily progress for a specific habit."""
    # Get target for the habit
    target = get_habit_target(db, user_id, habit_type)
    if not target:
        return {"error": "No target set for this habit"}
    
    # Get logs for the date
    logs = db.query(DailyHabitLog).filter(
        DailyHabitLog.user_id == user_id,
        DailyHabitLog.log_date == target_date,
        DailyHabitLog.habit_type == habit_type
    ).all()
    
    total_value = sum(log.logged_value for log in logs)
    completion_percentage = (total_value / target.target_value) * 100 if target.target_value > 0 else 0
    
    return {
        "date": target_date,
        "habit_type": habit_type,
        "logged_value": total_value,
        "target_value": target.target_value,
        "completion_percentage": completion_percentage,
        "is_goal_met": completion_percentage >= 100
    }

def calculate_weekly_progress(db: Session, user_id: int, week_start: date, habit_type: str) -> dict:
    """Calculate weekly progress for a specific habit."""
    from datetime import timedelta
    
    week_end = week_start + timedelta(days=6)
    
    # Get target for the habit
    target = get_habit_target(db, user_id, habit_type)
    if not target:
        return {"error": "No target set for this habit"}
    
    # Get logs for the week
    logs = db.query(DailyHabitLog).filter(
        DailyHabitLog.user_id == user_id,
        DailyHabitLog.log_date >= week_start,
        DailyHabitLog.log_date <= week_end,
        DailyHabitLog.habit_type == habit_type
    ).all()
    
    total_value = sum(log.logged_value for log in logs)
    weekly_target = target.target_value * 7  # Assuming daily target
    completion_percentage = (total_value / weekly_target) * 100 if weekly_target > 0 else 0
    
    # Count days with logs
    logged_dates = set(log.log_date for log in logs)
    days_met = len([d for d in logged_dates if d >= week_start and d <= week_end])
    
    return {
        "week_start": week_start,
        "week_end": week_end,
        "habit_type": habit_type,
        "total_value": total_value,
        "target_value": weekly_target,
        "completion_percentage": completion_percentage,
        "days_met": days_met,
        "total_days": 7
    }

def calculate_monthly_progress(db: Session, user_id: int, year: int, month: int, habit_type: str) -> dict:
    """Calculate monthly progress for a specific habit."""
    from datetime import date
    import calendar
    
    # Get first and last day of month
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    
    # Get target for the habit
    target = get_habit_target(db, user_id, habit_type)
    if not target:
        return {"error": "No target set for this habit"}
    
    # Get logs for the month
    logs = db.query(DailyHabitLog).filter(
        DailyHabitLog.user_id == user_id,
        DailyHabitLog.log_date >= first_day,
        DailyHabitLog.log_date <= last_day,
        DailyHabitLog.habit_type == habit_type
    ).all()
    
    total_value = sum(log.logged_value for log in logs)
    monthly_target = target.target_value * last_day.day  # Assuming daily target
    completion_percentage = (total_value / monthly_target) * 100 if monthly_target > 0 else 0
    
    # Count days with logs
    logged_dates = set(log.log_date for log in logs)
    days_met = len([d for d in logged_dates if d >= first_day and d <= last_day])
    
    return {
        "month": f"{year}-{month:02d}",
        "habit_type": habit_type,
        "total_value": total_value,
        "target_value": monthly_target,
        "completion_percentage": completion_percentage,
        "days_met": days_met,
        "total_days": last_day.day
    }

def generate_feedback(db: Session, user_id: int, habit_type: str, days: int = 7) -> dict:
    """Generate feedback based on recent habit performance."""
    from datetime import date, timedelta
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    # Get recent logs
    logs = db.query(DailyHabitLog).filter(
        DailyHabitLog.user_id == user_id,
        DailyHabitLog.log_date >= start_date,
        DailyHabitLog.log_date <= end_date,
        DailyHabitLog.habit_type == habit_type
    ).all()
    
    # Get target
    target = get_habit_target(db, user_id, habit_type)
    if not target:
        return {"error": "No target set for this habit"}
    
    # Calculate metrics
    total_value = sum(log.logged_value for log in logs)
    daily_average = total_value / days if days > 0 else 0
    completion_percentage = (daily_average / target.target_value) * 100 if target.target_value > 0 else 0
    
    # Calculate streak
    logged_dates = sorted(set(log.log_date for log in logs), reverse=True)
    streak_days = 0
    current_date = end_date
    
    for log_date in logged_dates:
        if log_date == current_date:
            streak_days += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    # Generate feedback
    if completion_percentage >= 100:
        feedback_message = f"Excellent! You've exceeded your {habit_type} goal by {completion_percentage - 100:.1f}%!"
        suggestions = ["Keep up the great work!", "Consider setting a higher goal if this feels too easy."]
        encouragement = "You're doing amazing! 🎉"
    elif completion_percentage >= 80:
        feedback_message = f"Great job! You're at {completion_percentage:.1f}% of your {habit_type} goal."
        suggestions = ["You're very close to your goal!", "Try to maintain this consistency."]
        encouragement = "You're almost there! 💪"
    elif completion_percentage >= 50:
        feedback_message = f"Good progress! You're at {completion_percentage:.1f}% of your {habit_type} goal."
        suggestions = ["Try to increase your daily amount slightly.", "Set smaller, achievable daily targets."]
        encouragement = "Keep pushing forward! 🌟"
    else:
        feedback_message = f"You're at {completion_percentage:.1f}% of your {habit_type} goal. Let's work on improving this!"
        suggestions = ["Start with smaller, more achievable goals.", "Try to log your habits daily.", "Consider what might be preventing you from reaching your goal."]
        encouragement = "Every small step counts! You've got this! 💪"
    
    return {
        "habit_type": habit_type,
        "feedback_message": feedback_message,
        "suggestions": suggestions,
        "encouragement": encouragement,
        "completion_percentage": completion_percentage,
        "streak_days": streak_days
    }
