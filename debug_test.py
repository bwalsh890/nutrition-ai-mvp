#!/usr/bin/env python3
import sys
sys.path.append('.')

from database import get_db
from crud import create_habit_target
from models import HabitTarget

# Test the habit target creation directly
db = next(get_db())

try:
    print("Testing habit target creation...")
    
    habit_target_data = {
        "habit_type": "water",
        "target_value": 2000.0,
        "target_unit": "ml",
        "is_active": True
    }
    
    print(f"Creating habit target with data: {habit_target_data}")
    
    result = create_habit_target(db, 2, habit_target_data)
    print(f"Success! Created habit target: {result}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
