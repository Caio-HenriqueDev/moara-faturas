from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
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
        "data_criacao": "2024-01-15T10:00:00Z"
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
        "data_criacao": "2024-01-16T14:30:00Z"
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
            "checkout": "/checkout/{fatura_id}",
            "webhook": "/webhook"
        }
    }

# Endpoint de health
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "moara-api",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "version": "2.0.0"
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
@app.get("/faturas")
async def faturas():
    return {
        "total": len(FATURAS_SIMULADAS),
        "faturas": FATURAS_SIMULADAS,
        "timestamp": datetime.now().isoformat()
    }

# Endpoint de fatura por ID
@app.get("/faturas/{fatura_id}")
async def fatura_by_id(fatura_id: int):
    if fatura_id < 1 or fatura_id > len(FATURAS_SIMULADAS):
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    
    fatura = FATURAS_SIMULADAS[fatura_id - 1]
    return {
        "fatura": fatura,
        "timestamp": datetime.now().isoformat()
    }

# Endpoint de processamento (simulado)
@app.post("/processar_email")
async def processar_email():
    return {
        "message": "Emails processados com sucesso",
        "status": "success",
        "emails_processados": 5,
        "faturas_extraidas": 2,
        "timestamp": datetime.now().isoformat()
    }

# Endpoint de checkout (simulado)
@app.post("/checkout/{fatura_id}")
async def checkout(fatura_id: int):
    if fatura_id < 1 or fatura_id > len(FATURAS_SIMULADAS):
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    
    return {
        "session_id": f"session_{fatura_id}_{datetime.now().timestamp()}",
        "checkout_url": "https://stripe.com/demo",
        "status": "created",
        "fatura_id": fatura_id,
        "timestamp": datetime.now().isoformat()
    }

# Endpoint de webhook (simulado)
@app.post("/webhook")
async def webhook():
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
    faturas_pendentes = len([f for f in FATURAS_SIMULADAS if f["status"] == "pendente"])
    faturas_pagas = len([f for f in FATURAS_SIMULADAS if f["status"] == "pago"])
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