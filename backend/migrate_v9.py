import sqlite3
import os

db_path = r"c:\Users\vinic\OneDrive\Desktop\pandas\nutrismart\backend\nutrismart_v2.db"

def migrate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Adicionar coluna para armazenar os dados das dicas importadas
        cursor.execute("ALTER TABLE health_profiles ADD COLUMN imported_tips TEXT")
        print("Coluna imported_tips adicionada com sucesso!")
    except sqlite3.OperationalError as e:
        print(f"Aviso: {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
