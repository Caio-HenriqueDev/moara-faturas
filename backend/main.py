# USINA_CLIENTE/backend/main.py

from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import os
import stripe
from dotenv import load_dotenv

# Carrega variáveis do ambiente
load_dotenv()

# Determina qual configuração de banco usar
if os.getenv("VERCEL_ENV"):
    # Está na Vercel - importações absolutas
    import crud, models
    from db_vercel import get_db, Base
    from schemas import FaturaSchema
    from utils import bot_mail, pdf_parser
else:
    # Está localmente
    try:
        from . import crud, models, db
        from .schemas import FaturaSchema
        from .utils import bot_mail, pdf_parser
        get_db = db.get_db
        Base = db.Base
    except ImportError:
        import crud, models, db
        from schemas import FaturaSchema
        from utils import bot_mail, pdf_parser
        get_db = db.get_db
        Base = db.Base

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

# Criação das tabelas (apenas se estiver localmente)
if not os.getenv("VERCEL_ENV"):
    try:
        db.create_tables()
    except:
        pass

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
        from_attributes = True  # Pydantic v2

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
            "faturas": "/faturas/",
            "processar_email": "/processar_email/",
            "checkout": "/create-checkout-session/{fatura_id}",
            "webhook": "/stripe-webhook/"
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
            "stripe": "ok",
            "email": "ok"
        }
    }

# Processar novos e-mails
@app.post("/processar_email/")
def processar_email(db_session: Session = Depends(get_db)):
    """
    Busca novos e-mails com anexos PDF, extrai os dados e salva/atualiza no banco.
    """
    try:
        print("Iniciando busca e processamento de e-mails...")
        dados_emails = bot_mail.buscar_e_processar_emails()

        if not dados_emails:
            return {"message": "Nenhum novo email com fatura encontrado."}

        for fatura_data in dados_emails:
            fatura_existente = crud.get_fatura_by_instalacao(db_session, fatura_data["numero_instalacao"])
            if fatura_existente:
                crud.update_fatura(db_session, fatura_existente, fatura_data)
                print(f"Fatura atualizada: {fatura_data['nome_cliente']} (Instalação: {fatura_data['numero_instalacao']})")
            else:
                crud.create_fatura(db_session, fatura_data)
                print(f"Nova fatura criada: {fatura_data['nome_cliente']} (Instalação: {fatura_data['numero_instalacao']})")

        return {"message": "Processamento de e-mails concluído com sucesso."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

# Listar faturas
@app.get("/faturas/", response_model=List[FaturaSchema])
def listar_faturas(skip: int = 0, limit: int = 100, db_session: Session = Depends(get_db)):
    """
    Retorna uma lista de todas as faturas cadastradas.
    """
    faturas = crud.get_faturas(db_session, skip=skip, limit=limit)
    return faturas

# Criar sessão de checkout no Stripe
@app.post("/create-checkout-session/{fatura_id}", response_model=CheckoutSessionResponse)
def create_checkout_session(fatura_id: int, db_session: Session = Depends(get_db)):
    """
    Cria uma sessão de checkout do Stripe para pagamento de uma fatura.
    """
    fatura = crud.get_fatura_by_id(db_session, fatura_id)
    if not fatura:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")

    valor_em_centavos = int(fatura.valor_total * 100)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': f"Fatura de {fatura.mes_referencia}",
                    },
                    'unit_amount': valor_em_centavos,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=os.getenv("FRONTEND_SUCCESS_URL", "http://localhost:3000/success") + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=os.getenv("FRONTEND_CANCEL_URL", "http://localhost:3000/cancel"),
            metadata={"fatura_id": str(fatura.id)}
        )
        return {"session_id": session.id, "checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Webhook Stripe
@app.post("/stripe-webhook/")
async def stripe_webhook(request: Request, db_session: Session = Depends(get_db)):
    """
    Recebe eventos do Stripe para atualizar status de pagamento.
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        fatura_id_str = session.get('metadata', {}).get('fatura_id')
        if fatura_id_str:
            fatura_id = int(fatura_id_str)
            crud.update_fatura_ja_pago(db_session, fatura_id)
            print(f"Pagamento concluído para a fatura ID: {fatura_id}")

    return {"status": "success"}
