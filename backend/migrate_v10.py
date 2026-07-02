import sqlite3

db_path = r"c:\Users\vinic\OneDrive\Desktop\pandas\nutrismart\backend\nutrismart_v2.db"

def migrate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Adicionar coluna role na tabela users
        cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'paciente'")
        print("Coluna role adicionada com sucesso na tabela users!")
    except sqlite3.OperationalError as e:
        print(f"Aviso: {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
