from database import SessionLocal, engine
from models import Base, User
from sqlalchemy.orm import Session

# Test database connection
try:
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    
    # Test database session
    db = SessionLocal()
    try:
        # Try to query users
        users = db.query(User).all()
        print(f"✅ Database connection successful. Found {len(users)} users")
        
        # Try to create a test user
        test_user = User(
            email="test@test.com",
            username="testuser",
            full_name="Test User",
            hashed_password="test_hash"
        )
        db.add(test_user)
        db.commit()
        print("✅ User creation successful")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        db.rollback()
    finally:
        db.close()
        
except Exception as e:
    print(f"❌ Database setup error: {e}")
