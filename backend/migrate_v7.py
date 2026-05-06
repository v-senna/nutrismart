import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "nutrismart_v2.db")

def migrate():
    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    columns_to_add = [
        ("imported_protein", "FLOAT"),
        ("imported_carbs", "FLOAT"),
        ("imported_fats", "FLOAT")
    ]

    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE health_profiles ADD COLUMN {col_name} {col_type}")
            print(f"Successfully added {col_name} column to health_profiles.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column {col_name} already exists.")
            else:
                print(f"Error adding {col_name}: {e}")

    conn.commit()
    conn.close()
    print("Migration v7 completed.")

if __name__ == "__main__":
    migrate()
