import sqlite3
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import models

# 1. Configurações
SQLITE_PATH = 'nutrismart_v2.db'
# Pegue a URL do Neon (adicione aqui temporariamente ou use ENV)
NEON_URL = os.getenv("DATABASE_URL")

if not NEON_URL or "postgresql" not in NEON_URL:
    print("ERRO: Defina a variável de ambiente DATABASE_URL com o link do Neon antes de rodar.")
    print("Exemplo no Windows: set DATABASE_URL=postgresql://...")
    exit(1)

print(f"Iniciando sincronização: {SQLITE_PATH} -> Cloud (Neon)")

# 2. Conectar ao SQLite
sqlite_conn = sqlite3.connect(SQLITE_PATH)
sqlite_conn.row_factory = sqlite3.Row
sqlite_cursor = sqlite_conn.cursor()

# 3. Conectar ao Postgres (Neon)
engine = create_engine(NEON_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Criar tabelas no Neon se não existirem
models.Base.metadata.create_all(bind=engine)

def sync_table(table_name, model_class):
    print(f"Sincronizando tabela: {table_name}...")
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()
    
    # Limpar tabela no destino para evitar duplicatas (Opcional, cuidado!)
    # session.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
    
    count = 0
    for row in rows:
        data = dict(row)
        # Tentar inserir ou atualizar
        obj = model_class(**data)
        session.merge(obj)
        count += 1
    
    session.commit()
    print(f"  {count} registros sincronizados em {table_name}.")

try:
    sync_table("users", models.User)
    sync_table("health_profiles", models.HealthProfile)
    sync_table("dietary_preferences", models.DietaryPreferences)
    sync_table("nutritional_plans", models.NutritionalPlan)
    sync_table("weight_logs", models.WeightLog)
    print("\n✅ TUDO PRONTO! Seus dados locais agora estão no Neon.")
except Exception as e:
    session.rollback()
    print(f"\n❌ ERRO durante a sincronização: {e}")
finally:
    sqlite_conn.close()
    session.close()
