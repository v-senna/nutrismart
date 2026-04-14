import sqlite3
import os

def migrate():
    db_path = 'c:/Users/vinic/OneDrive/Desktop/pandas/nutrismart/backend/nutrismart_v2.db'
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Adding column 'first_meal_time' to 'health_profiles'...")
        cursor.execute("ALTER TABLE health_profiles ADD COLUMN first_meal_time VARCHAR DEFAULT '08:00'")
        
        conn.commit()
        conn.close()
        print("Migration successful!")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
