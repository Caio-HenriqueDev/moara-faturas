# Configuração Gunicorn para Hostinger
# Sistema de Gestão de Faturas - Moara Energia

# Configurações de binding
bind = "0.0.0.0:8000"  # Escutar em todas as interfaces na porta 8000
backlog = 2048  # Tamanho da fila de conexões pendentes

# Configurações de workers
workers = 2  # Número de workers (recomendado: 2-4 para VPS)
worker_class = "uvicorn.workers.UvicornWorker"  # Usar workers do Uvicorn
worker_connections = 1000  # Máximo de conexões por worker
max_requests = 1000  # Reiniciar worker após N requests
max_requests_jitter = 100  # Variação para evitar reinicialização simultânea

# Configurações de timeout
timeout = 30  # Timeout para requests
keepalive = 2  # Tempo de keep-alive
graceful_timeout = 30  # Tempo para worker finalizar

# Configurações de performance
preload_app = True  # Pré-carregar aplicação
sendfile = True  # Otimização para arquivos estáticos
max_requests_jitter = 100  # Variação para evitar reinicialização simultânea

# Configurações de logging
accesslog = "-"  # Log de acesso no stdout
errorlog = "-"   # Log de erro no stdout
loglevel = "info"  # Nível de log
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de segurança
limit_request_line = 4094  # Tamanho máximo da linha de request
limit_request_fields = 100  # Número máximo de campos no header
limit_request_field_size = 8190  # Tamanho máximo de cada campo

# Configurações de processo
user = None  # Usuário para rodar (será definido pelo systemd)
group = None  # Grupo para rodar (será definido pelo systemd)
tmp_upload_dir = None  # Diretório temporário para uploads

# Configurações de reload (apenas para desenvolvimento)
reload = False  # Não recarregar automaticamente em produção
reload_engine = "auto"  # Engine de reload automático

# Configurações de stats
statsd_host = None  # Host para métricas StatsD
statsd_prefix = "gunicorn"  # Prefixo para métricas

# Configurações de check
check_config = False  # Verificar configuração ao iniciar

# Configurações de SSL (se necessário)
keyfile = None  # Arquivo de chave privada SSL
certfile = None  # Arquivo de certificado SSL

# Configurações de proxy
forwarded_allow_ips = "127.0.0.1,::1"  # IPs confiáveis para headers X-Forwarded-*
proxy_protocol = False  # Usar protocolo de proxy

# Configurações de worker
worker_tmp_dir = None  # Diretório temporário para workers
worker_exit_on_app_exit = False  # Não sair quando app sair

# Configurações de signal
worker_int = "INT"  # Sinal para interromper worker
worker_abort = "ABRT"  # Sinal para abortar worker

# Configurações de hook
def on_starting(server):
    """Hook executado quando o servidor inicia"""
    server.log.info("🚀 Iniciando Gunicorn para Moara Faturas")

def on_reload(server):
    """Hook executado quando o servidor recarrega"""
    server.log.info("🔄 Recarregando Gunicorn")

def when_ready(server):
    """Hook executado quando o servidor está pronto"""
    server.log.info("✅ Gunicorn pronto para receber conexões")

def worker_int(worker):
    """Hook executado quando um worker é interrompido"""
    worker.log.info("⚠️  Worker interrompido")

def worker_abort(worker):
    """Hook executado quando um worker é abortado"""
    worker.log.info("❌ Worker abortado")

def pre_fork(server, worker):
    """Hook executado antes de criar um worker"""
    server.log.info(f"🔄 Criando worker {worker.pid}")

def post_fork(server, worker):
    """Hook executado após criar um worker"""
    server.log.info(f"✅ Worker {worker.pid} criado")

def post_worker_init(worker):
    """Hook executado após inicializar um worker"""
    worker.log.info(f"🚀 Worker {worker.pid} inicializado")

def worker_connect(worker):
    """Hook executado quando um worker se conecta"""
    worker.log.info(f"🔗 Worker {worker.pid} conectado")

def worker_disconnect(worker):
    """Hook executado quando um worker se desconecta"""
    worker.log.info(f"🔌 Worker {worker.pid} desconectado")

def post_request(worker, req, environ, resp):
    """Hook executado após processar um request"""
    worker.log.info(f"📝 Request processado: {req.method} {req.path}")

def on_exit(server):
    """Hook executado quando o servidor sai"""
    server.log.info("👋 Gunicorn finalizado")

# Configurações específicas para FastAPI
def worker_exit(server, worker):
    """Hook executado quando um worker sai"""
    server.log.info(f"👋 Worker {worker.pid} finalizado")

def pre_exec(server):
    """Hook executado antes de executar o servidor"""
    server.log.info("🚀 Preparando execução do Gunicorn")

def post_exec(server):
    """Hook executado após executar o servidor"""
    server.log.info("✅ Execução do Gunicorn iniciada")

# Configurações de health check
def health_check(worker):
    """Verificação de saúde do worker"""
    try:
        # Aqui você pode adicionar verificações específicas
        # Por exemplo, verificar conexão com banco, etc.
        return True
    except Exception as e:
        worker.log.error(f"❌ Health check falhou: {e}")
        return False

# Configurações de métricas
def worker_metrics(worker):
    """Métricas do worker"""
    return {
        "pid": worker.pid,
        "age": worker.age,
        "requests": worker.requests,
        "status": "running" if worker.alive else "stopped"
    }

# Configurações de debug
def debug_info(server):
    """Informações de debug do servidor"""
    return {
        "bind": server.cfg.bind,
        "workers": server.cfg.workers,
        "worker_class": server.cfg.worker_class,
        "timeout": server.cfg.timeout,
        "max_requests": server.cfg.max_requests
    } 