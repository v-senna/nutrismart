import os
import shutil
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

# Detectar se estamos na Vercel
IS_VERCEL = os.getenv("VERCEL") == "1"

# DATABASE_URL pode ser PostgreSQL (Neon, Supabase, etc) ou SQLite local
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nutrismart_v2.db")

# ---------------------------------------------------------
# Compatibilidade: Neon/Supabase usam "postgres://"
# SQLAlchemy 2.x exige "postgresql://"
# ---------------------------------------------------------
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ---------------------------------------------------------
# Se for SQLite na Vercel, mover para /tmp (único dir com write)
# AVISO: /tmp é efêmero — dados podem ser perdidos entre cold starts.
# Para persistência real, configure DATABASE_URL com PostgreSQL.
# ---------------------------------------------------------
if IS_VERCEL and SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    db_name = "nutrismart_v2.db"
    tmp_db_path = f"/tmp/{db_name}"
    local_db_path = os.path.join(os.path.dirname(__file__), db_name)

    if not os.path.exists(tmp_db_path) and os.path.exists(local_db_path):
        shutil.copy2(local_db_path, tmp_db_path)

    SQLALCHEMY_DATABASE_URL = f"sqlite:///{tmp_db_path}"

# ---------------------------------------------------------
# Criar engine com opções corretas por banco
# ---------------------------------------------------------
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,   # Reconecta se a conexão caiu (importante em serverless)
        pool_size=1,          # Serverless não precisa de pool grande
        max_overflow=0,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
