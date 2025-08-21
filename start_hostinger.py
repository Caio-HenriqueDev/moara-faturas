#!/usr/bin/env python3
"""
Script de Inicialização para Hostinger
Sistema de Gestão de Faturas - Moara Energia

Este script inicia o sistema na Hostinger usando Gunicorn
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def print_banner():
    """Imprime o banner do sistema"""
    print("🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭")
    print("🏭 SISTEMA DE GESTÃO DE FATURAS - MOARA ENERGIA 🏭")
    print("🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭")
    print("🚀 Iniciando sistema na Hostinger...")

def check_environment():
    """Verifica se o ambiente está configurado corretamente"""
    print("\n📋 Verificando ambiente...")
    
    # Verificar se estamos no diretório correto
    if not Path("backend/main.py").exists():
        print("❌ Erro: Execute este script na raiz do projeto")
        print("💡 Certifique-se de estar no diretório correto")
        return False
    
    # Verificar se o ambiente virtual existe
    if not Path("venv").exists():
        print("❌ Erro: Ambiente virtual não encontrado")
        print("💡 Execute: python3.11 -m venv venv")
        return False
    
    # Verificar se as dependências estão instaladas
    try:
        import fastapi
        print("✅ FastAPI instalado")
    except ImportError:
        print("❌ FastAPI não instalado")
        print("💡 Execute: source venv/bin/activate && pip install -r backend/requirements_hostinger.txt")
        return False
    
    print("✅ Ambiente verificado com sucesso")
    return True

def check_variables():
    """Verifica se as variáveis de ambiente estão configuradas"""
    print("\n🔧 Verificando variáveis de ambiente...")
    
    required_vars = [
        "DATABASE_URL",
        "STRIPE_SECRET_KEY", 
        "EMAIL_USER"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Variáveis não configuradas: {missing_vars}")
        print("💡 Configure-as no arquivo .env")
        print("📖 Veja HOSTINGER_DEPLOY.md para instruções")
        return False
    
    print("✅ Variáveis de ambiente configuradas")
    return True

def test_database():
    """Testa a conexão com o banco de dados"""
    print("\n🗄️  Testando conexão com banco de dados...")
    
    try:
        from backend.db_hostinger import test_connection
        if test_connection():
            print("✅ Conexão com banco estabelecida")
            return True
        else:
            print("❌ Falha na conexão com banco")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar banco: {e}")
        return False

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("\n🧪 Testando importações...")
    
    try:
        from backend.main import app
        print("✅ Backend importado com sucesso")
        
        from backend.utils import bot_mail, pdf_parser
        print("✅ Utilitários importados com sucesso")
        
        return True
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def start_gunicorn():
    """Inicia o servidor com Gunicorn"""
    print("\n🔥 Iniciando servidor com Gunicorn...")
    
    # Verificar se Gunicorn está instalado
    try:
        import gunicorn
        print("✅ Gunicorn instalado")
    except ImportError:
        print("❌ Gunicorn não instalado")
        print("💡 Instalando Gunicorn...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "gunicorn"
        ], check=True)
    
    # Comando para iniciar Gunicorn
    gunicorn_cmd = [
        "gunicorn",
        "-c", "gunicorn_config.py",
        "backend.main:app"
    ]
    
    print(f"🚀 Executando: {' '.join(gunicorn_cmd)}")
    
    try:
        # Iniciar Gunicorn
        subprocess.run(gunicorn_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar Gunicorn: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⚠️  Servidor interrompido pelo usuário")
        return True
    
    return True

def signal_handler(signum, frame):
    """Manipulador de sinais para graceful shutdown"""
    print(f"\n⚠️  Recebido sinal {signum}, finalizando...")
    sys.exit(0)

def main():
    """Função principal"""
    # Configurar manipulador de sinais
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Imprimir banner
    print_banner()
    
    # Verificar ambiente
    if not check_environment():
        sys.exit(1)
    
    # Verificar variáveis de ambiente
    if not check_variables():
        print("\n⚠️  Aviso: Algumas variáveis não estão configuradas")
        print("💡 O sistema pode não funcionar completamente")
        
        # Perguntar se deve continuar
        response = input("\n❓ Deseja continuar mesmo assim? (y/N): ")
        if response.lower() != 'y':
            print("👋 Finalizando...")
            sys.exit(0)
    
    # Testar banco de dados
    if not test_database():
        print("\n⚠️  Aviso: Problemas com banco de dados")
        print("💡 O sistema pode não funcionar completamente")
        
        # Perguntar se deve continuar
        response = input("\n❓ Deseja continuar mesmo assim? (y/N): ")
        if response.lower() != 'y':
            print("👋 Finalizando...")
            sys.exit(0)
    
    # Testar importações
    if not test_imports():
        print("❌ Erro: Falha nas importações")
        print("💡 Verifique se todas as dependências estão instaladas")
        sys.exit(1)
    
    # Iniciar servidor
    if start_gunicorn():
        print("✅ Servidor iniciado com sucesso")
    else:
        print("❌ Falha ao iniciar servidor")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Sistema finalizado pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print("💡 Verifique os logs para mais detalhes")
        sys.exit(1) 