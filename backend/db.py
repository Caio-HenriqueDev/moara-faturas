# USINA_CLIENTE/backend/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
try:
    from .models import Fatura, Base
except ImportError:
    from models import Fatura, Base 

# Define o nome do arquivo do banco de dados SQLite
DATABASE_URL = "sqlite:///./usina_cliente.db"

# Cria o engine do banco de dados
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Necessário para SQLite
)

# Cria a sessão do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Cria todas as tabelas no banco de dados"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependência para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
