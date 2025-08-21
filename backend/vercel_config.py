"""
Configuração específica para Vercel
Este arquivo é usado apenas quando o sistema está rodando na Vercel
"""

import os
from typing import Optional

class VercelSettings:
    """Configurações específicas para Vercel"""
    
    # Ambiente Vercel
    ENVIRONMENT: str = "production"
    IS_VERCEL: bool = True
    IS_PRODUCTION: bool = True
    DEBUG: bool = False
    
    # Configurações de banco de dados
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Configurações de email
    EMAIL_USER: Optional[str] = os.getenv("EMAIL_USER")
    EMAIL_PASS: Optional[str] = os.getenv("EMAIL_PASS")
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "imap.gmail.com")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "993"))
    
    # Configurações do Stripe
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLIC_KEY: Optional[str] = os.getenv("STRIPE_PUBLIC_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # URLs do frontend
    FRONTEND_SUCCESS_URL: str = os.getenv(
        "FRONTEND_SUCCESS_URL", 
        "https://moara.vercel.app/success"
    )
    FRONTEND_CANCEL_URL: str = os.getenv(
        "FRONTEND_CANCEL_URL", 
        "https://moara.vercel.app/cancel"
    )
    
    # Configurações de CORS
    CORS_ORIGINS: list = [
        "https://*.vercel.app",
        "https://moara.vercel.app",
        "https://moaraenergiasolar.vercel.app"
    ]
    
    # Configurações de arquivos (Vercel usa /tmp)
    PDF_STORAGE_PATH: str = "/tmp/sample_emails"
    
    @classmethod
    def get_database_config(cls) -> dict:
        """Retorna configuração específica do banco para Vercel"""
        return {
            "type": "postgresql",
            "pool_class": "NullPool",
            "connect_args": {
                "connect_timeout": 10,
                "application_name": "moara_faturas"
            }
        }
    
    @classmethod
    def validate_config(cls) -> list:
        """Valida as configurações para Vercel"""
        issues = []
        
        if not cls.DATABASE_URL:
            issues.append("DATABASE_URL não configurado para Vercel")
        if not cls.EMAIL_USER:
            issues.append("EMAIL_USER não configurado")
        if not cls.EMAIL_PASS:
            issues.append("EMAIL_PASS não configurado")
        if not cls.STRIPE_SECRET_KEY:
            issues.append("STRIPE_SECRET_KEY não configurado")
        if not cls.STRIPE_PUBLIC_KEY:
            issues.append("STRIPE_PUBLIC_KEY não configurado")
            
        return issues

# Instância global das configurações Vercel
vercel_settings = VercelSettings() 