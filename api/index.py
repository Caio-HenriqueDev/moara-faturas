from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Criação da aplicação FastAPI
app = FastAPI(
    title="Sistema de Gestão de Faturas - Moara Energia",
    description="API simplificada para Vercel",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint raiz
@app.get("/")
async def root():
    return {"message": "API funcionando no Vercel!", "status": "success"}

# Endpoint de health
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "moara-api"}

# Endpoint de teste
@app.get("/test")
async def test():
    return {"test": "ok", "message": "Sistema operacional"}

# Endpoint de faturas (simulado)
@app.get("/faturas")
async def faturas():
    return [
        {
            "id": 1,
            "nome_cliente": "Cliente Teste",
            "valor_total": 150.00,
            "status": "pendente"
        }
    ]

# Endpoint de processamento (simulado)
@app.post("/processar_email")
async def processar_email():
    return {"message": "Email processado com sucesso", "status": "success"}

# Endpoint de checkout (simulado)
@app.post("/checkout/{fatura_id}")
async def checkout(fatura_id: int):
    return {
        "session_id": f"session_{fatura_id}",
        "checkout_url": "https://stripe.com/demo",
        "status": "created"
    }

# Endpoint de webhook (simulado)
@app.post("/webhook")
async def webhook():
    return {"status": "webhook_received", "message": "Evento processado"}

# Para Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 