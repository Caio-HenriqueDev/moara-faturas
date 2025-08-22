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
import os

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

@app.get("/")
def root():
    """
    Endpoint raiz para teste básico.
    """
    return {
        "message": "Sistema de Gestão de Faturas - Moara Energia",
        "status": "online",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/test/")
def test_endpoint():
    """
    Endpoint de teste simples.
    """
    return {
        "status": "success",
        "message": "API funcionando corretamente",
        "environment": settings.ENVIRONMENT,
        "is_vercel": settings.IS_VERCEL
    }


@app.post("/testar_pdf/")
def testar_processamento_pdf():
    """
    Testa o processamento de um PDF específico para debug.
    """
    try:
        print("🧪 Testando processamento de PDF...")
        
        # Lista arquivos na pasta de amostras
        sample_path = settings.PDF_STORAGE_PATH
        if not os.path.exists(sample_path):
            return {
                "status": "error",
                "message": f"Pasta de amostras não encontrada: {sample_path}"
            }
        
        arquivos = [f for f in os.listdir(sample_path) if f.endswith('.pdf')]
        
        if not arquivos:
            return {
                "status": "warning",
                "message": "Nenhum PDF encontrado para teste",
                "pasta": sample_path
            }
        
        # Testa o primeiro PDF encontrado
        pdf_teste = os.path.join(sample_path, arquivos[0])
        print(f"📄 Testando PDF: {pdf_teste}")
        
        # Importa e testa o parser
        from backend.utils.pdf_parser import extrair_dados_fatura_pdf
        
        dados = extrair_dados_fatura_pdf(pdf_teste)
        
        if dados:
            return {
                "status": "success",
                "message": "PDF processado com sucesso",
                "pdf_teste": arquivos[0],
                "dados_extraidos": dados,
                "pasta": sample_path,
                "total_pdfs": len(arquivos)
            }
        else:
            return {
                "status": "error",
                "message": "Falha ao processar PDF",
                "pdf_teste": arquivos[0],
                "pasta": sample_path,
                "total_pdfs": len(arquivos)
            }
            
    except Exception as e:
        print(f"❌ Erro no teste de PDF: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Erro no teste: {str(e)}",
            "traceback": str(e.__class__.__name__)
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

@app.post("/processar_email/")
def processar_emails(db_session: Session = Depends(get_db)):
    """
    Processa emails para buscar novas faturas.
    BASEADO NO SISTEMA FUNCIONAL
    """
    try:
        print("🚀 Iniciando processamento de emails...")
        
        # Valida configurações básicas
        if not settings.EMAIL_USER or not settings.EMAIL_PASS:
            error_msg = "Credenciais de email não configuradas"
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "faturas_processadas": 0,
                "message": error_msg
            }
        
        print(f"🔧 Configurações válidas:")
        print(f"   - EMAIL_USER: {settings.EMAIL_USER}")
        print(f"   - EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"   - EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"   - EMAIL_PASS: {'***CONFIGURADO***' if settings.EMAIL_PASS else 'NÃO CONFIGURADO'}")
        
        # Processa os emails usando a lógica que funciona
        print("📧 Iniciando processamento de emails...")
        dados_emails = bot_mail.buscar_e_processar_emails()
        
        if not dados_emails:
            print("ℹ️ Nenhum novo email com fatura encontrado")
            return {
                "status": "success",
                "faturas_processadas": 0,
                "message": "Nenhum novo email com fatura encontrado"
            }
        
        print(f"📊 Processamento concluído: {len(dados_emails)} faturas encontradas")
        
        # Salva as faturas no banco (lógica que funciona)
        faturas_salvas = 0
        for fatura_data in dados_emails:
            try:
                print(f"💾 Salvando fatura: {fatura_data.get('nome_cliente', 'N/A')}")
                
                # Verifica se a fatura já existe
                fatura_existente = crud.get_fatura_by_instalacao(db_session, fatura_data["numero_instalacao"])
                
                if fatura_existente:
                    # Atualiza fatura existente
                    for key, value in fatura_data.items():
                        if hasattr(fatura_existente, key):
                            setattr(fatura_existente, key, value)
                    db_session.commit()
                    print(f"✅ Fatura atualizada: {fatura_data['nome_cliente']} (Instalação: {fatura_data['numero_instalacao']})")
                    faturas_salvas += 1
                else:
                    # Cria nova fatura
                    nova_fatura = crud.create_fatura(db_session, fatura_data)
                    db_session.commit()
                    print(f"✅ Nova fatura criada: {fatura_data['nome_cliente']} (Instalação: {fatura_data['numero_instalacao']})")
                    faturas_salvas += 1
                    
            except Exception as e:
                print(f"❌ Erro ao processar fatura {fatura_data.get('numero_instalacao', 'N/A')}: {e}")
                db_session.rollback()
                continue
        
        print("=" * 80)
        print(f"🎯 PROCESSAMENTO FINALIZADO")
        print(f"📊 Faturas encontradas: {len(dados_emails)}")
        print(f"💾 Faturas salvas: {faturas_salvas}")
        print("=" * 80)
        
        return {
            "status": "success",
            "faturas_processadas": len(dados_emails),
            "faturas_salvas": faturas_salvas,
            "message": f"Processamento concluído: {len(dados_emails)} faturas encontradas, {faturas_salvas} salvas"
        }
        
    except Exception as e:
        print(f"❌ Erro no processamento: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "faturas_processadas": 0,
            "message": f"Erro no processamento: {str(e)}"
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

@app.get("/debug/")
def debug_config():
    """
    Endpoint para debug das configurações e conexões.
    """
    try:
        debug_info = {
            "config": settings.debug_email_config(),
            "database": {
                "url": settings.DATABASE_URL[:20] + "..." if settings.DATABASE_URL else "NÃO CONFIGURADO",
                "type": "postgresql" if settings.IS_VERCEL else "sqlite"
            },
            "environment": {
                "vercel_env": os.getenv("VERCEL_ENV"),
                "environment": settings.ENVIRONMENT,
                "debug": settings.DEBUG
            },
            "validation": {
                "issues": settings.validate_config(),
                "email_configured": bool(settings.EMAIL_USER and settings.EMAIL_PASS),
                "stripe_configured": bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_PUBLIC_KEY),
                "database_configured": bool(settings.DATABASE_URL)
            }
        }
        
        return debug_info
        
    except Exception as e:
        return {
            "error": str(e),
            "traceback": str(e.__class__.__name__)
        }


@app.get("/logs/")
def get_logs():
    """
    Endpoint para obter logs do sistema.
    """
    try:
        # Simula logs do sistema (em produção, isso viria de um sistema de logging real)
        logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "info",
                "message": "Sistema funcionando normalmente",
                "service": "main"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "info", 
                "message": f"Configuração de email: {'OK' if settings.EMAIL_USER and settings.EMAIL_PASS else 'ERRO'}",
                "service": "email"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "info",
                "message": f"Banco de dados: {'OK' if settings.DATABASE_URL else 'ERRO'}",
                "service": "database"
            }
        ]
        
        return {
            "status": "success",
            "logs": logs,
            "total": len(logs)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/ping")
def ping():
    """Endpoint simples para testar se a API está funcionando"""
    return {"message": "pong", "status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/teste_email_real")
def teste_email_real():
    """
    Endpoint para testar o processamento completo de um email real
    Cria um PDF de teste e processa como se fosse um anexo de email
    """
    try:
        print("🧪 INICIANDO TESTE DE EMAIL REAL")
        
        # Importa módulos necessários
        from .utils.bot_mail import gerar_hash
        from .utils.pdf_parser import extrair_dados_fatura_pdf
        import tempfile
        import os
        
        # Cria PDF de teste
        try:
            from fpdf import FPDF
            
            # Cria PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Adiciona conteúdo da fatura
            pdf.cell(200, 10, txt="FATURA DE ENERGIA ELETRICA", ln=True, align='C')
            pdf.ln(10)
            
            pdf.cell(200, 10, txt="JOSE SILVA", ln=True, align='L')
            pdf.cell(200, 10, txt="MURIAE", ln=True, align='L')
            pdf.ln(5)
            
            pdf.cell(200, 10, txt="CNPJ/CPF/RANI: 123.456.789-00", ln=True, align='L')
            pdf.cell(200, 10, txt="Instalacao: 123456 Ponta", ln=True, align='L')
            pdf.cell(200, 10, txt="Mes Referencia: Agosto/2025", ln=True, align='L')
            pdf.cell(200, 10, txt="Data Vencimento: 15/09/2025", ln=True, align='L')
            pdf.ln(5)
            
            pdf.cell(200, 10, txt="Consumo em kWh:", ln=True, align='L')
            pdf.cell(200, 10, txt="250,00", ln=True, align='L')
            pdf.ln(5)
            
            pdf.cell(200, 10, txt="Preco Unitario: R$ 0,30", ln=True, align='L')
            pdf.cell(200, 10, txt="Valor Total: R$ 75,00", ln=True, align='L')
            pdf.ln(5)
            
            pdf.cell(200, 10, txt="Saldo Acumulado: 0,00", ln=True, align='L')
            
            # Salva em arquivo temporário
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            pdf.output(temp_file.name)
            temp_file.close()
            
            print(f"✅ PDF de teste criado: {temp_file.name}")
            
        except Exception as e:
            print(f"❌ Erro ao criar PDF: {e}")
            return {"status": "error", "message": f"Erro ao criar PDF: {str(e)}"}
        
        try:
            # Gera hash do arquivo
            with open(temp_file.name, 'rb') as f:
                conteudo = f.read()
            
            hash_arquivo = gerar_hash(conteudo)
            print(f"🔐 Hash gerado: {hash_arquivo}")
            
            # Cria diretório de armazenamento
            storage_path = settings.PDF_STORAGE_PATH
            os.makedirs(storage_path, exist_ok=True)
            print(f"📁 Diretório criado: {storage_path}")
            
            # Salva arquivo com hash
            path_final = os.path.join(storage_path, f"{hash_arquivo}.pdf")
            with open(path_final, 'wb') as f:
                f.write(conteudo)
            print(f"💾 Arquivo salvo: {path_final}")
            
            # Testa extração de dados
            print("🔍 TESTANDO EXTRAÇÃO DE DADOS...")
            dados_extraidos = extrair_dados_fatura_pdf(path_final)
            
            if dados_extraidos:
                print("✅ DADOS EXTRAÍDOS COM SUCESSO:")
                for campo, valor in dados_extraidos.items():
                    print(f"   - {campo}: {valor}")
                
                # Valida dados obrigatórios
                campos_obrigatorios = ["nome_cliente", "numero_instalacao"]
                campos_faltando = [campo for campo in campos_obrigatorios if not dados_extraidos.get(campo)]
                
                if not campos_faltando:
                    print("🎯 VALIDAÇÃO: Todos os campos obrigatórios encontrados!")
                    
                    # Limpa arquivos temporários
                    try:
                        os.unlink(temp_file.name)
                        os.unlink(path_final)
                    except:
                        pass
                    
                    return {
                        "status": "success",
                        "message": "Teste de email real concluído com sucesso!",
                        "dados_extraidos": dados_extraidos,
                        "hash_arquivo": hash_arquivo
                    }
                else:
                    print(f"❌ VALIDAÇÃO: Campos faltando: {campos_faltando}")
                    return {
                        "status": "error",
                        "message": f"Campos obrigatórios faltando: {campos_faltando}",
                        "dados_extraidos": dados_extraidos
                    }
            else:
                print("❌ Falha na extração de dados")
                return {"status": "error", "message": "Falha na extração de dados do PDF"}
                
        except Exception as e:
            print(f"❌ Erro durante o processamento: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": f"Erro durante o processamento: {str(e)}"}
        
        finally:
            # Limpa arquivos temporários
            try:
                if 'temp_file' in locals() and os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
                if 'path_final' in locals() and os.path.exists(path_final):
                    os.unlink(path_final)
            except:
                pass
                
    except Exception as e:
        print(f"❌ Erro geral no teste: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"Erro geral: {str(e)}"}
