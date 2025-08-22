"""
Configuração unificada de banco de dados
Suporta SQLite (desenvolvimento), PostgreSQL (Vercel) e PostgreSQL (Hostinger)
"""

import os
from sqlalchemy import create_engine, text
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

def clean_database_url(database_url: str) -> str:
    """
    Limpa o DATABASE_URL removendo parâmetros incompatíveis
    como pgbouncer que causam erros no SQLAlchemy
    """
    if not database_url or "postgresql" not in database_url:
        return database_url
    
    # Remove parâmetros problemáticos
    problematic_params = [
        "pgbouncer",
        "pooling",
        "connection_limit",
        "connect_timeout"
    ]
    
    # Divide a URL em partes
    if "?" in database_url:
        base_url, params = database_url.split("?", 1)
        param_pairs = params.split("&")
        
        # Filtra parâmetros problemáticos
        clean_params = []
        for param in param_pairs:
            param_name = param.split("=")[0]
            if param_name not in problematic_params:
                clean_params.append(param)
        
        # Reconstrói a URL
        if clean_params:
            return f"{base_url}?{'&'.join(clean_params)}"
        else:
            return base_url
    else:
        return database_url

def get_database_url() -> str:
    """Retorna a URL do banco de dados baseada no ambiente"""
    if settings.IS_VERCEL or settings.IS_HOSTINGER:
        database_url = settings.DATABASE_URL
        if database_url:
            # Limpa a URL removendo parâmetros incompatíveis
            return clean_database_url(database_url)
        return "postgresql://localhost/postgres"
    else:
        return "sqlite:///./usina_cliente.db"

def create_database_engine():
    """Cria o engine do banco baseado na configuração"""
    try:
        database_url = get_database_url()
        config = settings.get_database_config()
        
        print(f"🔧 Criando engine para: {config['type']}")
        print(f"📡 URL: {database_url.replace(database_url.split('@')[0].split(':')[-1], '***') if '@' in database_url else database_url}")
        
        if config["type"] == "postgresql":
            # PostgreSQL (Vercel ou Hostinger)
            if config["pool_class"] == "NullPool":
                engine = create_engine(
                    database_url,
                    poolclass=NullPool,
                    echo=settings.DEBUG,
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
                echo=settings.DEBUG
                # SQLite não suporta connect_args complexos
            )
        
        print(f"✅ Engine criado com sucesso para {config['type']}")
        return engine
        
    except Exception as e:
        print(f"❌ Erro ao criar engine do banco: {e}")
        print(f"🔧 Configuração: {config}")
        raise

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