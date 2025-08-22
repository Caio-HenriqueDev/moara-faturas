"""
Configuração centralizada do Sistema de Gestão de Faturas
Gerencia variáveis de ambiente e configurações para diferentes ambientes
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Carrega variáveis do ambiente
load_dotenv()

class Settings:
    """Configurações centralizadas do sistema"""
    
    # Informações da aplicação
    APP_NAME: str = "Sistema de Gestão de Faturas - Moara Energia"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Ambiente
    ENVIRONMENT: str = os.getenv("VERCEL_ENV", "local")
    IS_PRODUCTION: bool = ENVIRONMENT == "production"
    IS_VERCEL: bool = bool(os.getenv("VERCEL_ENV"))
    IS_HOSTINGER: bool = bool(os.getenv("HOSTINGER_ENV"))
    
    # Configurações de banco de dados
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Configurações de email
    EMAIL_USER: Optional[str] = os.getenv("EMAIL_USER")
    EMAIL_PASS: Optional[str] = os.getenv("EMAIL_PASS")
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "imap.gmail.com")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "993"))
    
    # Fallback para compatibilidade com variáveis antigas
    if not EMAIL_USER:
        EMAIL_USER = os.getenv("GMAIL_USER")
    if not EMAIL_PASS:
        EMAIL_PASS = os.getenv("GMAIL_PASSWORD")
    if not EMAIL_HOST or EMAIL_HOST == "imap.gmail.com":
        EMAIL_HOST = os.getenv("GMAIL_HOST", "imap.gmail.com")
    if EMAIL_PORT == 993:
        EMAIL_PORT = int(os.getenv("GMAIL_PORT", "993"))
    
    # Configurações do Stripe
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLIC_KEY: Optional[str] = os.getenv("STRIPE_PUBLIC_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # URLs do frontend
    FRONTEND_SUCCESS_URL: str = os.getenv(
        "FRONTEND_SUCCESS_URL", 
        "http://localhost:3000/success"
    )
    FRONTEND_CANCEL_URL: str = os.getenv(
        "FRONTEND_CANCEL_URL", 
        "http://localhost:3000/cancel"
    )
    
    # Configurações de CORS
    CORS_ORIGINS: list = [
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://moara-solar-l7whuoy74-diretoriamoovestudio-5505s-projects.vercel.app",
        "https://moara-solar-48c8u9u4c-diretoriamoovestudio-5505s-projects.vercel.app",
        "https://moara-solar-re64ibgs1-diretoriamoovestudio-5505s-projects.vercel.app"
    ]
    
    # Configurações de arquivos
    PDF_STORAGE_PATH: str = (
        "/tmp/sample_emails" if IS_VERCEL 
        else "data/sample_emails"
    )
    
    @classmethod
    def get_database_config(cls) -> dict:
        """Retorna configuração específica do banco baseada no ambiente"""
        if cls.IS_VERCEL:
            return {
                "type": "postgresql",
                "pool_class": "NullPool",
                "connect_args": {
                    "connect_timeout": 10,
                    "application_name": "moara_faturas"
                }
            }
        elif cls.IS_HOSTINGER:
            return {
                "type": "postgresql",
                "pool_class": "QueuePool",
                "pool_size": 5,
                "max_overflow": 10,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
                "connect_args": {
                    "connect_timeout": 10,
                    "application_name": "moara_faturas_hostinger"
                }
            }
        else:
            return {
                "type": "sqlite",
                "connect_args": {"check_same_thread": False}
            }
    
    @classmethod
    def validate_config(cls) -> list:
        """Valida as configurações e retorna lista de problemas"""
        issues = []
        
        # Validação de email
        if not cls.EMAIL_USER:
            issues.append("EMAIL_USER não configurado")
        elif "@" not in cls.EMAIL_USER:
            issues.append("EMAIL_USER deve ser um email válido")
            
        if not cls.EMAIL_PASS:
            issues.append("EMAIL_PASS não configurado")
        elif len(cls.EMAIL_PASS) < 8:
            issues.append("EMAIL_PASS deve ter pelo menos 8 caracteres")
            
        if not cls.EMAIL_HOST:
            issues.append("EMAIL_HOST não configurado")
            
        if cls.EMAIL_PORT not in [993, 587, 465]:
            issues.append("EMAIL_PORT deve ser 993 (IMAP SSL), 587 (SMTP) ou 465 (SMTP SSL)")
        
        # Validação de Stripe
        if not cls.STRIPE_SECRET_KEY:
            issues.append("STRIPE_SECRET_KEY não configurado")
        if not cls.STRIPE_PUBLIC_KEY:
            issues.append("STRIPE_PUBLIC_KEY não configurado")
            
        # Validação de banco de dados
        if cls.IS_VERCEL and not cls.DATABASE_URL:
            issues.append("DATABASE_URL não configurado para Vercel")
        elif cls.IS_HOSTINGER and not cls.DATABASE_URL:
            issues.append("DATABASE_URL não configurado para Hostinger")
            
        return issues

    @classmethod
    def debug_email_config(cls) -> dict:
        """Retorna configurações de email para debug"""
        return {
            "EMAIL_USER": cls.EMAIL_USER,
            "EMAIL_PASS": "***" if cls.EMAIL_PASS else "NÃO CONFIGURADO",
            "EMAIL_HOST": cls.EMAIL_HOST,
            "EMAIL_PORT": cls.EMAIL_PORT,
            "IS_VERCEL": cls.IS_VERCEL,
            "ENVIRONMENT": cls.ENVIRONMENT
        }

# Instância global das configurações
settings = Settings()

# Se estiver na Vercel, sobrescreve com configurações específicas
if settings.IS_VERCEL:
    try:
        from .vercel_config import vercel_settings
        # Sobrescreve configurações com as específicas da Vercel
        settings.ENVIRONMENT = vercel_settings.ENVIRONMENT
        settings.IS_PRODUCTION = vercel_settings.IS_PRODUCTION
        settings.DEBUG = vercel_settings.DEBUG
        settings.FRONTEND_SUCCESS_URL = vercel_settings.FRONTEND_SUCCESS_URL
        settings.FRONTEND_CANCEL_URL = vercel_settings.FRONTEND_CANCEL_URL
        settings.CORS_ORIGINS = vercel_settings.CORS_ORIGINS
        settings.PDF_STORAGE_PATH = vercel_settings.PDF_STORAGE_PATH
    except ImportError:
        # Fallback se não conseguir importar configurações específicas da Vercel
        pass 