"""
Configuração unificada de banco de dados
Suporta SQLite (desenvolvimento), PostgreSQL (Vercel) e PostgreSQL (Hostinger)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from typing import Generator

# Importações com fallback para Vercel
try:
    from .config import settings
    from .models import Base
except ImportError:
    from config import settings
    from models import Base

def get_database_url() -> str:
    """Retorna a URL do banco baseada no ambiente"""
    if settings.DATABASE_URL:
        # Ajusta formato para PostgreSQL se necessário
        if settings.DATABASE_URL.startswith("postgres://"):
            return settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return settings.DATABASE_URL
    
    # Fallback para desenvolvimento local
    return "sqlite:///./usina_cliente.db"

def create_database_engine():
    """Cria o engine do banco baseado na configuração"""
    database_url = get_database_url()
    config = settings.get_database_config()
    
    if config["type"] == "postgresql":
        # PostgreSQL (Vercel ou Hostinger)
        if config["pool_class"] == "NullPool":
            engine = create_engine(
                database_url,
                poolclass=NullPool,
                echo=settings.DEBUG
                # NullPool não suporta connect_args
            )
        else:
            engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=config.get("pool_size", 5),
                max_overflow=config.get("max_overflow", 10),
                pool_pre_ping=config.get("pool_pre_ping", True),
                pool_recycle=config.get("pool_recycle", 3600),
                echo=settings.DEBUG,
                **config.get("connect_args", {})
            )
    else:
        # SQLite (desenvolvimento local)
        engine = create_engine(
            database_url,
            echo=settings.DEBUG,
            **config.get("connect_args", {})
        )
    
    return engine

# Cria o engine global
engine = create_database_engine()

# Cria a sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Cria todas as tabelas no banco de dados"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def get_db() -> Generator:
    """Dependência para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection() -> bool:
    """Testa a conexão com o banco de dados"""
    try:
        with engine.connect() as connection:
            if settings.IS_VERCEL or settings.IS_HOSTINGER:
                connection.execute("SELECT 1")
            else:
                connection.execute("SELECT 1")
            print("✅ Conexão com banco de dados estabelecida")
            return True
    except Exception as e:
        print(f"❌ Erro de conexão com banco: {e}")
        return False

def get_database_info() -> dict:
    """Retorna informações sobre o banco de dados"""
    try:
        with engine.connect() as connection:
            if settings.IS_VERCEL or settings.IS_HOSTINGER:
                # PostgreSQL
                version_result = connection.execute("SELECT version()")
                version = version_result.fetchone()[0]
                
                tables_result = connection.execute("""
                    SELECT table_name, table_type 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                tables = [row[0] for row in tables_result.fetchall()]
                
                pool_info = {
                    "pool_size": engine.pool.size() if hasattr(engine, 'pool') else "N/A",
                    "pool_overflow": engine.pool.overflow() if hasattr(engine, 'pool') else "N/A"
                }
            else:
                # SQLite
                version = "SQLite"
                tables_result = connection.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table'
                    ORDER BY name
                """)
                tables = [row[0] for row in tables_result.fetchall()]
                pool_info = {"type": "SQLite"}
            
            return {
                "version": version,
                "tables": tables,
                "environment": settings.ENVIRONMENT,
                "database_url": get_database_url().replace(
                    get_database_url().split('@')[0].split(':')[-1], 
                    '***'
                ) if '@' in get_database_url() else "SQLite local",
                **pool_info
            }
    except Exception as e:
        return {"error": str(e)} 