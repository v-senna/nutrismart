import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('c:/Users/vinic/OneDrive/Desktop/pandas/nutrismart/backend/nutrismart_v2.db')
        cursor = conn.cursor()
        
        print("Adding column 'project_duration_months' to 'health_profiles'...")
        cursor.execute("ALTER TABLE health_profiles ADD COLUMN project_duration_months INTEGER DEFAULT 12")
        
        conn.commit()
        conn.close()
        print("Migration successful!")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
