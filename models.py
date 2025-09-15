from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
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
