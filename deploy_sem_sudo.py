#!/usr/bin/env python3
"""
🚀 DEPLOY SEM SUDO - HOSTINGER
Sistema de Gestão de Faturas - Moara Energia

Este script faz deploy na Hostinger para usuários sem acesso sudo
"""

import os
import sys
import subprocess
import time

def print_banner():
    print("🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭")
    print("🏭 DEPLOY SEM SUDO - HOSTINGER 🏭")
    print("🏭 SISTEMA DE GESTÃO DE FATURAS 🏭")
    print("🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭")
    print("🚀 Deploy para usuários sem privilégios sudo")
    print()

def get_credentials():
    print("🔧 Configuração Rápida")
    print("=" * 30)
    
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

def deploy_sem_sudo():
    print_banner()
    
    # Obter credenciais
    host, user, port = get_credentials()
    
    print(f"\n🚀 Iniciando deploy para {host}...")
    print("⏱️  Tempo estimado: 3-5 minutos")
    print()
    
    # Etapa 1: Testar SSH
    if not run_command(f"ssh -p {port} {user}@{host} 'echo ✅ SSH OK'", "Testando conexão SSH"):
        print("❌ Falha na conexão SSH. Verifique suas credenciais.")
        return False
    
    # Etapa 2: Verificar Python disponível
    print("🐍 Verificando Python disponível...")
    python_versions = ["python3.11", "python3.10", "python3.9", "python3", "python"]
    python_cmd = None
    
    for version in python_versions:
        test_cmd = f"ssh -p {port} {user}@{host} '{version} --version'"
        if run_command(test_cmd, f"Testando {version}"):
            python_cmd = version
            break
    
    if not python_cmd:
        print("❌ Nenhuma versão do Python encontrada!")
        print("💡 Contate o suporte da Hostinger para instalar Python")
        return False
    
    print(f"✅ Python encontrado: {python_cmd}")
    
    # Etapa 3: Criar diretórios
    commands = [
        f"ssh -p {port} {user}@{host} 'mkdir -p ~/moara-faturas'",
        f"ssh -p {port} {user}@{host} 'mkdir -p ~/public_html'",
        f"ssh -p {port} {user}@{host} 'mkdir -p ~/moara-faturas/logs'"
    ]
    
    for cmd in commands:
        run_command(cmd, "Criando diretórios")
    
    # Etapa 4: Upload dos arquivos
    print("📤 Fazendo upload dos arquivos...")
    upload_cmd = f"scp -P {port} -r backend/ frontend/ *.py {user}@{host}:~/moara-faturas/"
    if not run_command(upload_cmd, "Upload dos arquivos"):
        print("❌ Falha no upload. Verifique a conexão.")
        return False
    
    # Etapa 5: Verificar se Python tem venv
    print("🔍 Verificando se Python suporta venv...")
    venv_test = f"ssh -p {port} {user}@{host} '{python_cmd} -m venv --help'"
    if run_command(venv_test, "Testando suporte a venv"):
        # Criar ambiente virtual
        venv_cmd = f"ssh -p {port} {user}@{host} 'cd ~/moara-faturas && {python_cmd} -m venv venv'"
        run_command(venv_cmd, "Criando ambiente virtual")
        
        # Instalar dependências
        pip_cmd = f"ssh -p {port} {user}@{host} 'cd ~/moara-faturas && source venv/bin/activate && pip install --user fastapi uvicorn sqlalchemy PyPDF2 python-dotenv stripe psycopg2-binary pydantic'"
        run_command(pip_cmd, "Instalando dependências")
    else:
        print("⚠️  Python não suporta venv, tentando instalar globalmente...")
        pip_cmd = f"ssh -p {port} {user}@{host} '{python_cmd} -m pip install --user fastapi uvicorn sqlalchemy PyPDF2 python-dotenv stripe psycopg2-binary pydantic'"
        run_command(pip_cmd, "Instalando dependências globalmente")
    
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
    
    # Etapa 7: Copiar frontend
    copy_cmd = f"ssh -p {port} {user}@{host} 'cp -r ~/moara-faturas/frontend/* ~/public_html/'"
    run_command(copy_cmd, "Copiando frontend")
    
    # Etapa 8: Criar script de inicialização
    start_script = f"""#!/bin/bash
cd ~/moara-faturas
export PYTHONPATH=$PYTHONPATH:~/moara-faturas
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
else
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
fi"""
    
    script_cmd = f"ssh -p {port} {user}@{host} 'echo \"{start_script}\" > ~/moara-faturas/start.sh && chmod +x ~/moara-faturas/start.sh'"
    run_command(script_cmd, "Criando script de inicialização")
    
    # Etapa 9: Testar se consegue iniciar
    print("🧪 Testando se o sistema inicia...")
    test_start = f"ssh -p {port} {user}@{host} 'cd ~/moara-faturas && timeout 10s python -c \"from backend.main import app; print(\\\"✅ Sistema importado com sucesso\\\")\"'"
    run_command(test_start, "Testando importação do sistema")
    
    # Sucesso!
    print("\n" + "="*60)
    print("🎉 DEPLOY SEM SUDO CONCLUÍDO!")
    print("="*60)
    
    print(f"\n🌐 Seu sistema está configurado em:")
    print(f"   Projeto: ~/moara-faturas")
    print(f"   Frontend: ~/public_html")
    
    print(f"\n🔧 Para iniciar o sistema:")
    print(f"   ssh -p {port} {user}@{host}")
    print(f"   cd ~/moara-faturas")
    print(f"   ./start.sh")
    
    print(f"\n⚠️  IMPORTANTE:")
    print(f"   1. Configure as variáveis reais no arquivo .env")
    print(f"   2. Configure o banco PostgreSQL (contate suporte)")
    print(f"   3. Configure o Stripe e Gmail")
    print(f"   4. Para produção, use nohup ou screen")
    
    print(f"\n📱 Para testar:")
    print(f"   curl http://{host}:8000/health")
    print(f"   curl http://{host}/")
    
    print(f"\n🚀 Sistema configurado! Inicie manualmente com ./start.sh")
    return True

if __name__ == "__main__":
    try:
        deploy_sem_sudo()
    except KeyboardInterrupt:
        print("\n⚠️  Deploy interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1) 