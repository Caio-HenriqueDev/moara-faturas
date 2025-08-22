"""
API principal do Sistema de Gestão de Faturas - Moara Energia
Implementa todos os endpoints da API usando FastAPI
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import stripe
from datetime import datetime

# Importações locais com fallback para Vercel
try:
    # Desenvolvimento local
    from .config import settings
    from .database import get_db, create_tables
    from . import crud
    from .schemas import (
        FaturaSchema, 
        FaturaCreate, 
        FaturaUpdate,
        CheckoutSessionResponse,
        ProcessamentoEmailResponse,
        HealthCheckResponse
    )
    from .utils import bot_mail
except ImportError:
    # Vercel - imports absolutos
    from config import settings
    from database import get_db, create_tables
    import crud
    from schemas import (
        FaturaSchema, 
        FaturaCreate, 
        FaturaUpdate,
        CheckoutSessionResponse,
        ProcessamentoEmailResponse,
        HealthCheckResponse
    )
    from utils import bot_mail

# Inicializa o aplicativo FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.DEBUG
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração do Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Criação das tabelas (apenas se estiver na Vercel)
if settings.IS_VERCEL:
    try:
        create_tables()
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível criar tabelas: {e}")

# Eventos da aplicação
@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização da aplicação"""
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} iniciando...")
    print(f"🌍 Ambiente: {settings.ENVIRONMENT}")
    
    # Valida configurações
    issues = settings.validate_config()
    if issues:
        print("⚠️ Problemas de configuração detectados:")
        for issue in issues:
            print(f"   - {issue}")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado no encerramento da aplicação"""
    print(f"🛑 {settings.APP_NAME} encerrando...")

# Endpoints da API

@app.get("/", response_model=dict)
def read_root():
    """
    Endpoint raiz para verificar se o backend está funcionando.
    """
    return {
        "message": settings.APP_NAME,
        "status": "online",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "faturas": "/faturas/",
            "processar_email": "/processar_email/",
            "checkout": "/create-checkout-session/{fatura_id}",
            "webhook": "/stripe-webhook/"
        }
    }

@app.get("/health", response_model=HealthCheckResponse)
def health_check():
    """
    Endpoint para verificar a saúde do sistema.
    """
    try:
        # Testa conexão com banco
        db_status = "ok"
        if settings.IS_VERCEL:
            try:
                from database import test_connection
                if not test_connection():
                    db_status = "error: connection failed"
            except Exception as e:
                db_status = f"error: {str(e)}"
        
        return HealthCheckResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            environment=settings.ENVIRONMENT,
            services={
                "database": db_status,
                "stripe": "ok" if stripe.api_key else "not_configured",
                "email": "ok" if settings.EMAIL_USER and settings.EMAIL_PASS else "not_configured"
            }
        )
    except Exception as e:
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            environment=settings.ENVIRONMENT,
            services={"error": str(e)}
        )

@app.post("/processar_email/", response_model=ProcessamentoEmailResponse)
def processar_email(db_session: Session = Depends(get_db)):
    """
    Busca novos e-mails com anexos PDF, extrai os dados e salva/atualiza no banco.
    """
    if not db_session:
        raise HTTPException(status_code=500, detail="Banco de dados não disponível")
    
    try:
        print("Iniciando busca e processamento de e-mails...")
        dados_emails = bot_mail.buscar_e_processar_emails()

        if not dados_emails:
            return ProcessamentoEmailResponse(
                message="Nenhum novo email com fatura encontrado.",
                faturas_processadas=0
            )

        faturas_processadas = 0
        for fatura_data in dados_emails:
            try:
                fatura_existente = crud.get_fatura_by_instalacao(
                    db_session, 
                    fatura_data["numero_instalacao"]
                )
                
                if fatura_existente:
                    crud.update_fatura(db_session, fatura_existente, fatura_data)
                    print(f"✅ Fatura atualizada: {fatura_data['nome_cliente']} (Instalação: {fatura_data['numero_instalacao']})")
                else:
                    crud.create_fatura(db_session, fatura_data)
                    print(f"✅ Nova fatura criada: {fatura_data['nome_cliente']} (Instalação: {fatura_data['numero_instalacao']})")
                
                faturas_processadas += 1
            except Exception as e:
                print(f"❌ Erro ao processar fatura {fatura_data.get('numero_instalacao', 'N/A')}: {e}")
                continue

        return ProcessamentoEmailResponse(
            message="Processamento de e-mails concluído com sucesso.",
            faturas_processadas=faturas_processadas
        )

    except Exception as e:
        print(f"❌ Erro no processamento: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

@app.get("/testar_gmail/")
def testar_gmail():
    """
    Testa a conexão com o Gmail para debug.
    """
    try:
        print("🧪 Testando conexão com Gmail...")
        
        # Testa conexão
        mail = bot_mail.conectar_email()
        if not mail:
            return {
                "status": "error",
                "message": "Falha na conexão com Gmail",
                "details": "Verifique as credenciais e configurações"
            }
        
        # Testa busca de emails
        try:
            status, messages = mail.search(None, "ALL")
            if status == "OK":
                email_count = len(messages[0].split()) if messages[0] else 0
                result = {
                    "status": "success",
                    "message": "Conexão com Gmail estabelecida com sucesso",
                    "details": {
                        "email_count": email_count,
                        "connection": "IMAP SSL",
                        "host": settings.EMAIL_HOST,
                        "port": settings.EMAIL_PORT,
                        "user": settings.EMAIL_USER
                    }
                }
            else:
                result = {
                    "status": "warning",
                    "message": "Conectado mas erro ao buscar emails",
                    "details": f"Status: {status}"
                }
        except Exception as e:
            result = {
                "status": "warning",
                "message": "Conectado mas erro ao buscar emails",
                "details": str(e)
            }
        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass
        
        return result
        
    except Exception as e:
        print(f"❌ Erro no teste do Gmail: {e}")
        return {
            "status": "error",
            "message": "Erro ao testar Gmail",
            "details": str(e)
        }

@app.get("/faturas/", response_model=List[FaturaSchema])
def listar_faturas(
    skip: int = 0, 
    limit: int = 100, 
    db_session: Session = Depends(get_db)
):
    """
    Retorna uma lista de todas as faturas cadastradas.
    """
    if not db_session:
        raise HTTPException(status_code=500, detail="Banco de dados não disponível")
    
    try:
        faturas = crud.get_faturas(db_session, skip=skip, limit=limit)
        return faturas
    except Exception as e:
        print(f"❌ Erro ao listar faturas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar faturas: {str(e)}")

@app.get("/faturas/pendentes", response_model=List[FaturaSchema])
def listar_faturas_pendentes(db_session: Session = Depends(get_db)):
    """
    Retorna uma lista de faturas pendentes de pagamento.
    """
    if not db_session:
        raise HTTPException(status_code=500, detail="Banco de dados não disponível")
    
    try:
        faturas = crud.FaturaCRUD.get_faturas_pendentes(db_session)
        return faturas
    except Exception as e:
        print(f"❌ Erro ao listar faturas pendentes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar faturas pendentes: {str(e)}")

@app.get("/faturas/pagas", response_model=List[FaturaSchema])
def listar_faturas_pagas(db_session: Session = Depends(get_db)):
    """
    Retorna uma lista de faturas já pagas.
    """
    if not db_session:
        raise HTTPException(status_code=500, detail="Banco de dados não disponível")
    
    try:
        faturas = crud.FaturaCRUD.get_faturas_pagas(db_session)
        return faturas
    except Exception as e:
        print(f"❌ Erro ao listar faturas pagas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar faturas pagas: {str(e)}")

@app.get("/faturas/{fatura_id}", response_model=FaturaSchema)
def obter_fatura(fatura_id: int, db_session: Session = Depends(get_db)):
    """
    Retorna uma fatura específica pelo ID.
    """
    if not db_session:
        raise HTTPException(status_code=500, detail="Banco de dados não disponível")
    
    try:
        fatura = crud.get_fatura_by_id(db_session, fatura_id)
        if not fatura:
            raise HTTPException(status_code=404, detail="Fatura não encontrada")
        return fatura
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao obter fatura: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter fatura: {str(e)}")

@app.post("/create-checkout-session/{fatura_id}", response_model=CheckoutSessionResponse)
def create_checkout_session(fatura_id: int, db_session: Session = Depends(get_db)):
    """
    Cria uma sessão de checkout do Stripe para pagamento de uma fatura.
    """
    if not db_session:
        raise HTTPException(status_code=500, detail="Banco de dados não disponível")
    
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe não configurado")
    
    try:
        fatura = crud.get_fatura_by_id(db_session, fatura_id)
        if not fatura:
            raise HTTPException(status_code=404, detail="Fatura não encontrada")

        valor_em_centavos = int(fatura.valor_total * 100)

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
            success_url=f"{settings.FRONTEND_SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=settings.FRONTEND_CANCEL_URL,
            metadata={"fatura_id": str(fatura.id)}
        )
        
        return CheckoutSessionResponse(
            session_id=session.id, 
            checkout_url=session.url
        )
    except Exception as e:
        print(f"❌ Erro ao criar sessão de checkout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stripe-webhook/")
async def stripe_webhook(request: Request, db_session: Session = Depends(get_db)):
    """
    Recebe eventos do Stripe para atualizar status de pagamento.
    """
    if not db_session:
        raise HTTPException(status_code=500, detail="Banco de dados não disponível")
    
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe não configurado")
    
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    if not webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret não configurado")

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
            try:
                fatura_id = int(fatura_id_str)
                crud.update_fatura_ja_pago(db_session, fatura_id)
                print(f"✅ Pagamento concluído para a fatura ID: {fatura_id}")
            except Exception as e:
                print(f"❌ Erro ao atualizar fatura {fatura_id_str}: {e}")

    return {"status": "success"}
