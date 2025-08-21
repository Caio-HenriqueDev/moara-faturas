# Configuração de banco de dados para Vercel (PostgreSQL)
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Para Vercel, use variáveis de ambiente
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost/dbname"  # Fallback local
)

# Se estiver na Vercel, ajusta a URL para o formato correto
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configuração do engine com parâmetros otimizados para serverless
engine = None
if DATABASE_URL and DATABASE_URL != "postgresql://user:password@localhost/dbname":
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=1,
        max_overflow=0,
        echo=False
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # Fallback para desenvolvimento local
    SessionLocal = None

Base = declarative_base()

def create_tables():
    """Cria todas as tabelas no banco de dados"""
    if engine:
        Base.metadata.create_all(bind=engine)

def get_db():
    """Dependência para obter sessão do banco"""
    if not SessionLocal:
        # Fallback para desenvolvimento local
        from db import get_db as local_get_db
        return local_get_db()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 