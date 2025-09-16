from database import SessionLocal
from models import User

db = SessionLocal()
users = db.query(User).all()

print("Existing users in database:")
for u in users:
    print(f"ID: {u.id}, Username: {u.username}, Email: {u.email}, Name: {u.full_name}")

db.close()
