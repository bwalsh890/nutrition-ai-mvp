from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    message_tracking = relationship("MessageTracking", back_populates="user")
    health_profile = relationship("UserHealthProfile", back_populates="user", uselist=False)
    questionnaire = relationship("UserQuestionnaire", back_populates="user", uselist=False)
    habit_logs = relationship("DailyHabitLog", back_populates="user")
    habit_targets = relationship("HabitTarget", back_populates="user")
    progress_stats = relationship("ProgressStats", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

class MessageTracking(Base):
    __tablename__ = "message_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month_year = Column(String, nullable=False)  # Format: "2024-01"
    message_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="message_tracking")
    
    def __repr__(self):
        return f"<MessageTracking(user_id={self.user_id}, month_year='{self.month_year}', count={self.message_count})>"

class UserHealthProfile(Base):
    __tablename__ = "user_health_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)  # "male", "female", "other", "prefer_not_to_say"
    height_cm = Column(Integer, nullable=True)
    weight_kg = Column(Integer, nullable=True)
    activity_level = Column(String, nullable=True)  # "sedentary", "lightly_active", "moderately_active", "very_active", "extremely_active"
    dietary_restrictions = Column(Text, nullable=True)  # JSON string of restrictions
    health_conditions = Column(Text, nullable=True)  # JSON string of conditions
    fitness_goals = Column(Text, nullable=True)  # JSON string of goals
    allergies = Column(Text, nullable=True)  # JSON string of allergies
    medications = Column(Text, nullable=True)  # JSON string of medications
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="health_profile")
    
    def __repr__(self):
        return f"<UserHealthProfile(user_id={self.user_id}, age={self.age}, gender='{self.gender}')>"

class UserQuestionnaire(Base):
    __tablename__ = "user_questionnaires"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    sleep_hours = Column(Float, nullable=True)  # Average hours of sleep per night
    water_goal_ml = Column(Integer, nullable=True)  # Daily water intake goal in ml
    meal_frequency = Column(Integer, nullable=True)  # Number of meals per day
    exercise_frequency = Column(Integer, nullable=True)  # Days per week
    exercise_duration = Column(Integer, nullable=True)  # Minutes per session
    stress_level = Column(String, nullable=True)  # "low", "moderate", "high"
    energy_level = Column(String, nullable=True)  # "low", "moderate", "high"
    mood_tracking = Column(Boolean, default=False)  # Whether user wants mood tracking
    weight_goal = Column(String, nullable=True)  # "lose", "maintain", "gain"
    target_weight_kg = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="questionnaire")
    
    def __repr__(self):
        return f"<UserQuestionnaire(user_id={self.user_id}, sleep_hours={self.sleep_hours})>"

class HabitTarget(Base):
    __tablename__ = "habit_targets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    habit_type = Column(String, nullable=False)  # "water", "meals", "exercise", "sleep"
    target_value = Column(Float, nullable=False)  # Target value (ml, count, minutes, hours)
    target_unit = Column(String, nullable=False)  # "ml", "count", "minutes", "hours"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="habit_targets")
    
    def __repr__(self):
        return f"<HabitTarget(user_id={self.user_id}, habit_type='{self.habit_type}', target={self.target_value})>"

class DailyHabitLog(Base):
    __tablename__ = "daily_habit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    log_date = Column(Date, nullable=False)
    habit_type = Column(String, nullable=False)  # "water", "meals", "exercise", "sleep", "mood"
    logged_value = Column(Float, nullable=False)  # Actual logged value
    unit = Column(String, nullable=False)  # "ml", "count", "minutes", "hours", "rating"
    notes = Column(Text, nullable=True)  # Optional notes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="habit_logs")
    
    def __repr__(self):
        return f"<DailyHabitLog(user_id={self.user_id}, date={self.log_date}, habit='{self.habit_type}', value={self.logged_value})>"

class ProgressStats(Base):
    __tablename__ = "progress_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stat_date = Column(Date, nullable=False)
    period_type = Column(String, nullable=False)  # "daily", "weekly", "monthly"
    habit_type = Column(String, nullable=False)  # "water", "meals", "exercise", "sleep"
    total_value = Column(Float, nullable=False)  # Total value for the period
    target_value = Column(Float, nullable=False)  # Target value for the period
    completion_percentage = Column(Float, nullable=False)  # Percentage of target achieved
    streak_days = Column(Integer, default=0)  # Current streak
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="progress_stats")
    
    def __repr__(self):
        return f"<ProgressStats(user_id={self.user_id}, date={self.stat_date}, habit='{self.habit_type}', completion={self.completion_percentage}%)>"
