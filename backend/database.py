import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Detectar se estamos na Vercel
IS_VERCEL = os.getenv("VERCEL") == "1"

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./nutrismart_v2.db"
)

# Se estiver na Vercel e for SQLite, precisamos mover o arquivo para /tmp para permitir escrita
if IS_VERCEL and SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    db_name = "nutrismart_v2.db"
    tmp_db_path = f"/tmp/{db_name}"
    local_db_path = os.path.join(os.path.dirname(__file__), db_name)
    
    # Se o arquivo não existir em /tmp, copia do local (que é read-only na Vercel)
    if not os.path.exists(tmp_db_path):
        if os.path.exists(local_db_path):
            shutil.copy2(local_db_path, tmp_db_path)
            print(f"Database copied to {tmp_db_path}")
        else:
            print(f"Warning: local database {local_db_path} not found.")
    
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{tmp_db_path}"

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
