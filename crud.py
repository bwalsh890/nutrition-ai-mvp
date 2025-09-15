from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.context import CryptContext
from datetime import datetime
from models import User, MessageTracking, UserHealthProfile
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
