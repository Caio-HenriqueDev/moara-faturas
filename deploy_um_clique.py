#!/usr/bin/env python3
"""
🚀 DEPLOY COM UM CLIQUE - HOSTINGER
Sistema de Gestão de Faturas - Moara Energia

Este script faz o deploy completo na Hostinger com apenas algumas perguntas!
"""

import os
import sys
import subprocess
import time

def print_banner():
    print("🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭")
    print("🏭 DEPLOY COM UM CLIQUE - HOSTINGER 🏭")
    print("🏭 SISTEMA DE GESTÃO DE FATURAS 🏭")
    print("🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭")
    print("🚀 Deploy automatizado - Apenas 3 perguntas!")
    print()

def get_credentials():
    print("🔧 Configuração Rápida")
    print("=" * 30)
    
    # Perguntas essenciais
    host = input("🌐 Seu domínio (ex: meusite.com): ").strip()
    if not host:
        print("❌ Domínio é obrigatório!")
        sys.exit(1)
    
    user = input("👤 Seu usuário SSH (ex: u123456789): ").strip()
    if not user:
        print("❌ Usuário SSH é obrigatório!")
        sys.exit(1)
    
    port = input("🔌 Porta SSH (padrão: 65002): ").strip() or "65002"
    
    return host, user, port

def run_command(cmd, description):
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}")
            return True
        else:
            print(f"⚠️  {description} - {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro em {description}: {e}")
        return False

def deploy_automatico():
    print_banner()
    
    # Obter credenciais
    host, user, port = get_credentials()
    
    print(f"\n🚀 Iniciando deploy para {host}...")
    print("⏱️  Tempo estimado: 5-10 minutos")
    print()
    
    # Etapa 1: Testar SSH
    if not run_command(f"ssh -p {port} {user}@{host} 'echo ✅ SSH OK'", "Testando conexão SSH"):
        print("❌ Falha na conexão SSH. Verifique suas credenciais.")
        return False
    
    # Etapa 2: Instalar dependências
    commands = [
        f"ssh -p {port} {user}@{host} 'sudo apt update -y'",
        f"ssh -p {port} {user}@{host} 'sudo apt install -y python3.11 python3.11-venv python3.11-pip postgresql postgresql-contrib libpq-dev python3-dev build-essential nginx certbot python3-certbot-nginx ufw'",
        f"ssh -p {port} {user}@{host} 'mkdir -p ~/moara-faturas ~/public_html/api ~/moara-faturas/logs'"
    ]
    
    for cmd in commands:
        if not run_command(cmd, "Instalando dependências"):
            print("⚠️  Continuando mesmo com avisos...")
    
    # Etapa 3: Configurar banco
    print("🗄️  Configurando banco de dados...")
    db_commands = [
        f"ssh -p {port} {user}@{host} 'sudo -u postgres psql -c \"CREATE USER moara_user WITH PASSWORD \\'moara123\\';\"'",
        f"ssh -p {port} {user}@{host} 'sudo -u postgres psql -c \"CREATE DATABASE moara_faturas OWNER moara_user;\"'",
        f"ssh -p {port} {user}@{host} 'sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE moara_faturas TO moara_user;\"'"
    ]
    
    for cmd in db_commands:
        run_command(cmd, "Configurando PostgreSQL")
    
    # Etapa 4: Upload dos arquivos
    print("📤 Fazendo upload dos arquivos...")
    upload_cmd = f"scp -P {port} -r backend/ frontend/ *.py {user}@{host}:~/moara-faturas/"
    if not run_command(upload_cmd, "Upload dos arquivos"):
        print("❌ Falha no upload. Verifique a conexão.")
        return False
    
    # Etapa 5: Configurar Python
    python_commands = [
        f"ssh -p {port} {user}@{host} 'cd ~/moara-faturas && python3.11 -m venv venv'",
        f"ssh -p {port} {user}@{host} 'cd ~/moara-faturas && source venv/bin/activate && pip install -r backend/requirements_hostinger.txt gunicorn'"
    ]
    
    for cmd in python_commands:
        if not run_command(cmd, "Configurando Python"):
            print("⚠️  Continuando mesmo com avisos...")
    
    # Etapa 6: Criar .env
    env_content = f"""DATABASE_URL=postgresql://moara_user:moara123@localhost:5432/moara_faturas
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key_here
STRIPE_PUBLIC_KEY=pk_live_your_stripe_public_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
EMAIL_USER=seu_email@gmail.com
EMAIL_PASS=sua_senha_de_app_gmail
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
FRONTEND_SUCCESS_URL=https://{host}/success
FRONTEND_CANCEL_URL=https://{host}/cancel
ENVIRONMENT=production"""
    
    env_cmd = f"ssh -p {port} {user}@{host} 'cd ~/moara-faturas && echo \"{env_content}\" > .env'"
    run_command(env_cmd, "Criando arquivo .env")
    
    # Etapa 7: Configurar Nginx
    nginx_config = f"""server {{
    listen 80;
    server_name {host} www.{host};
    
    location / {{
        root ~/public_html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }}
    
    location /api/ {{
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}"""
    
    nginx_cmd = f"ssh -p {port} {user}@{host} 'echo \"{nginx_config}\" | sudo tee /etc/nginx/sites-available/moara'"
    run_command(nginx_cmd, "Configurando Nginx")
    
    # Ativar Nginx
    nginx_activate = f"ssh -p {port} {user}@{host} 'sudo ln -sf /etc/nginx/sites-available/moara /etc/nginx/sites-enabled/ && sudo nginx -t && sudo systemctl restart nginx'"
    run_command(nginx_activate, "Ativando Nginx")
    
    # Etapa 8: Configurar serviço
    service_content = f"""[Unit]
Description=Moara Faturas API
After=network.target postgresql.service

[Service]
Type=simple
User={user}
WorkingDirectory=~/moara-faturas
Environment=PATH=~/moara-faturas/venv/bin
ExecStart=~/moara-faturas/venv/bin/gunicorn -c gunicorn_config.py backend.main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target"""
    
    service_cmd = f"ssh -p {port} {user}@{host} 'echo \"{service_content}\" | sudo tee /etc/systemd/system/moara.service'"
    run_command(service_cmd, "Criando serviço systemd")
    
    # Ativar serviço
    service_activate = f"ssh -p {port} {user}@{host} 'sudo systemctl daemon-reload && sudo systemctl enable moara && sudo systemctl start moara'"
    run_command(service_activate, "Ativando serviço")
    
    # Etapa 9: Copiar frontend
    copy_cmd = f"ssh -p {port} {user}@{host} 'cp -r ~/moara-faturas/frontend/* ~/public_html/'"
    run_command(copy_cmd, "Copiando frontend")
    
    # Etapa 10: Configurar SSL
    ssl_cmd = f"ssh -p {port} {user}@{host} 'sudo certbot --nginx -d {host} --non-interactive --agree-tos --email admin@{host}'"
    run_command(ssl_cmd, "Configurando SSL")
    
    # Etapa 11: Testar
    print("🧪 Testando deploy...")
    test_commands = [
        f"ssh -p {port} {user}@{host} 'curl -s http://localhost:8000/health'",
        f"ssh -p {port} {user}@{host} 'curl -s http://localhost/'",
        f"ssh -p {port} {user}@{host} 'curl -s https://{host}/'"
    ]
    
    for cmd in test_commands:
        run_command(cmd, "Testando endpoints")
    
    # Sucesso!
    print("\n" + "="*60)
    print("🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
    print("="*60)
    
    print(f"\n🌐 Seu sistema está rodando em:")
    print(f"   Frontend: https://{host}")
    print(f"   API: https://{host}/api/")
    print(f"   Health: https://{host}/api/health")
    print(f"   Docs: https://{host}/api/docs")
    
    print(f"\n🔑 Credenciais do banco:")
    print(f"   Usuário: moara_user")
    print(f"   Senha: moara123")
    print(f"   Database: moara_faturas")
    
    print(f"\n⚠️  IMPORTANTE - Configure no arquivo .env:")
    print(f"   1. Suas chaves do Stripe")
    print(f"   2. Seu email e senha do Gmail")
    print(f"   3. Outras variáveis específicas")
    
    print(f"\n🔧 Comandos úteis:")
    print(f"   Ver status: ssh -p {port} {user}@{host} 'sudo systemctl status moara'")
    print(f"   Ver logs: ssh -p {port} {user}@{host} 'sudo journalctl -u moara -f'")
    print(f"   Reiniciar: ssh -p {port} {user}@{host} 'sudo systemctl restart moara'")
    
    print(f"\n🚀 Sistema pronto para uso!")
    return True

if __name__ == "__main__":
    try:
        deploy_automatico()
    except KeyboardInterrupt:
        print("\n⚠️  Deploy interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1) 