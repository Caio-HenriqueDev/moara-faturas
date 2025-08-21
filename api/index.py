from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import json

# Criação da aplicação FastAPI
app = FastAPI(
    title="Sistema de Gestão de Faturas - Moara Energia",
    description="API completa para gestão de faturas de energia",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas Pydantic
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

# Dados simulados para demonstração
FATURAS_SIMULADAS = [
    {
        "id": 1,
        "nome_cliente": "João Silva",
        "documento_cliente": "123.456.789-00",
        "email_cliente": "joao@email.com",
        "numero_instalacao": "123456789",
        "valor_total": 150.00,
        "mes_referencia": "Janeiro 2024",
        "data_vencimento": "2024-02-15",
        "status": "pendente",
        "ja_pago": False,
        "data_criacao": "2024-01-15T10:00:00Z",
        "data_ultima_atualizacao": "2024-01-15T10:00:00Z"
    },
    {
        "id": 2,
        "nome_cliente": "Maria Santos",
        "documento_cliente": "987.654.321-00",
        "email_cliente": "maria@email.com",
        "numero_instalacao": "987654321",
        "valor_total": 89.50,
        "mes_referencia": "Janeiro 2024",
        "data_vencimento": "2024-02-20",
        "status": "pago",
        "ja_pago": True,
        "data_criacao": "2024-01-16T14:30:00Z",
        "data_ultima_atualizacao": "2024-01-16T14:30:00Z"
    }
]

# Endpoint raiz
@app.get("/")
async def root():
    return {
        "message": "Sistema de Gestão de Faturas - Moara Energia",
        "status": "online",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "test": "/test",
            "faturas": "/faturas",
            "fatura_by_id": "/faturas/{id}",
            "processar_email": "/processar_email",
            "create_checkout": "/create-checkout-session/{fatura_id}",
            "webhook": "/stripe-webhook",
            "stats": "/stats"
        }
    }

# Endpoint de health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "moara-api",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "version": "2.0.0",
        "services": {
            "database": "simulated",
            "stripe": "simulated",
            "email": "simulated"
        }
    }

# Endpoint de teste
@app.get("/test")
async def test():
    return {
        "test": "ok",
        "message": "Sistema operacional",
        "timestamp": datetime.now().isoformat(),
        "performance": "excellent"
    }

# Endpoint de faturas
@app.get("/faturas", response_model=List[FaturaSchema])
async def faturas():
    return FATURAS_SIMULADAS

# Endpoint de fatura por ID
@app.get("/faturas/{fatura_id}", response_model=FaturaSchema)
async def fatura_by_id(fatura_id: int):
    if fatura_id < 1 or fatura_id > len(FATURAS_SIMULADAS):
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    
    fatura = FATURAS_SIMULADAS[fatura_id - 1]
    return fatura

# Endpoint para processar emails (simulado)
@app.post("/processar_email")
async def processar_email():
    return {
        "message": "Emails processados com sucesso",
        "status": "success",
        "emails_processados": 5,
        "faturas_extraidas": 2,
        "timestamp": datetime.now().isoformat()
    }

# Endpoint para criar sessão de checkout (simulado)
@app.post("/create-checkout-session/{fatura_id}", response_model=CheckoutSessionResponse)
async def create_checkout_session(fatura_id: int):
    if fatura_id < 1 or fatura_id > len(FATURAS_SIMULADAS):
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    
    return {
        "session_id": f"session_{fatura_id}_{datetime.now().timestamp()}",
        "checkout_url": "https://stripe.com/demo",
        "status": "created",
        "fatura_id": fatura_id,
        "timestamp": datetime.now().isoformat()
    }

# Endpoint para webhook Stripe (simulado)
@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    return {
        "status": "webhook_received",
        "message": "Evento processado com sucesso",
        "event_type": "payment.succeeded",
        "timestamp": datetime.now().isoformat()
    }

# Endpoint de estatísticas
@app.get("/stats")
async def stats():
    total_faturas = len(FATURAS_SIMULADAS)
    faturas_pendentes = len([f for f in FATURAS_SIMULADAS if not f["ja_pago"]])
    faturas_pagas = len([f for f in FATURAS_SIMULADAS if f["ja_pago"]])
    valor_total = sum(f["valor_total"] for f in FATURAS_SIMULADAS)
    
    return {
        "total_faturas": total_faturas,
        "faturas_pendentes": faturas_pendentes,
        "faturas_pagas": faturas_pagas,
        "valor_total": valor_total,
        "timestamp": datetime.now().isoformat()
    }

# Para Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 