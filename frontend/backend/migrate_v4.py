import sqlite3

def migrate():
    db_path = 'c:/Users/vinic/OneDrive/Desktop/pandas/nutrismart/backend/nutrismart_v2.db'
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Adding column 'imc_classification' to 'nutritional_plans'...")
        cursor.execute("ALTER TABLE nutritional_plans ADD COLUMN imc_classification VARCHAR")
        
        conn.commit()
        conn.close()
        print("Migration successful!")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
