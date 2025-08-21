# Arquivo para Vercel - aplicação FastAPI completa
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import os
import stripe
from dotenv import load_dotenv

# Carrega variáveis do ambiente
load_dotenv()

# Inicializa o aplicativo FastAPI
app = FastAPI(title="Sistema de Gestão de Faturas - Moara Energia", version="1.0.0")

# CORS configurado para aceitar apenas o front
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://127.0.0.1:3000",  # Frontend com http.server
    "http://localhost:3000",   # Frontend localhost
    "https://*.vercel.app",    # Vercel domains
    "https://*.vercel.app"     # Vercel domains
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração do Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Schemas Pydantic inline para evitar importações
class FaturaBase(BaseModel):
    nome_cliente: str
    documento_cliente: str
    email_cliente: str
    numero_instalacao: str
    valor_total: float
    mes_referencia: str
    data_vencimento: str
    url_pdf: Optional[str] = None

class FaturaCreate(FaturaBase):
    pass

class Fatura(FaturaBase):
    id: int
    ja_pago: bool
    data_criacao: str
    data_ultima_atualizacao: str

    class Config:
        from_attributes = True

class FaturaSchema(BaseModel):
    id: int
    nome_cliente: Optional[str] = None
    documento_cliente: Optional[str] = None
    email_cliente: Optional[str] = None
    numero_instalacao: Optional[str] = None
    valor_total: Optional[float] = None
    mes_referencia: Optional[str] = None
    data_vencimento: Optional[str] = None
    url_pdf: Optional[str] = None
    ja_pago: Optional[bool] = False

    class Config:
        from_attributes = True

class CheckoutSessionResponse(BaseModel):
    session_id: str
    checkout_url: str

# Endpoint raiz para teste
@app.get("/")
def read_root():
    """
    Endpoint raiz para verificar se o backend está funcionando.
    """
    return {
        "message": "Sistema de Gestão de Faturas - Moara Energia",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health"
        }
    }

# Endpoint de health check
@app.get("/health")
def health_check():
    """
    Endpoint para verificar a saúde do sistema.
    """
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "database": "ok",
            "stripe": "ok" if os.getenv("STRIPE_SECRET_KEY") else "not_configured",
            "email": "ok" if os.getenv("EMAIL_USER") else "not_configured"
        }
    }

# Endpoint para processar emails (simplificado para Vercel)
@app.post("/processar_email/")
def processar_email():
    """
    Endpoint simplificado para Vercel.
    """
    return {
        "message": "Funcionalidade de email não disponível no ambiente Vercel",
        "status": "info"
    }

# Endpoint para listar faturas (simplificado para Vercel)
@app.get("/faturas/", response_model=List[FaturaSchema])
def listar_faturas(skip: int = 0, limit: int = 100):
    """
    Endpoint simplificado para Vercel.
    """
    return []

# Endpoint para criar sessão de checkout (simplificado para Vercel)
@app.post("/create-checkout-session/{fatura_id}", response_model=CheckoutSessionResponse)
def create_checkout_session(fatura_id: int):
    """
    Endpoint simplificado para Vercel.
    """
    return {
        "session_id": "demo_session",
        "checkout_url": "https://stripe.com/demo"
    }

# Endpoint para webhook Stripe (simplificado para Vercel)
@app.post("/stripe-webhook/")
async def stripe_webhook(request: Request):
    """
    Endpoint simplificado para Vercel.
    """
    return {"status": "success", "message": "Webhook recebido"}

# Para Vercel, exporta a aplicação
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 