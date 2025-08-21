#!/usr/bin/env python3
"""
Script de inicialização para o Sistema de Gestão de Faturas
Funciona independente do diretório de execução
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def print_banner():
    """Imprime o banner do sistema"""
    print("🏭" * 50)
    print("🏭 SISTEMA DE GESTÃO DE FATURAS - USINA CLIENTE 🏭")
    print("🏭" * 50)
    print("🚀 Iniciando sistema...")
    print()

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    print("📋 Verificando dependências...")
    
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import stripe
        print("✅ Todas as dependências Python estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("💡 Execute: source venv/bin/activate && pip install -r backend/requirements.txt")
        return False

def check_environment():
    """Verifica e configura o ambiente"""
    print("🌍 Verificando ambiente...")
    
    # Verifica se existe arquivo .env
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ Arquivo .env não encontrado")
        print("💡 Copie env_template.txt para .env e configure as variáveis")
        return False
    
    # Verifica variáveis essenciais
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["EMAIL_USER", "EMAIL_PASS", "STRIPE_SECRET_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️ Variáveis de ambiente faltando: {', '.join(missing_vars)}")
        return False
    
    print("✅ Ambiente configurado corretamente")
    return True

def start_backend():
    """Inicia o backend na porta 8000"""
    print("🔧 Iniciando backend na porta 8000...")
    
    # Navega para o diretório backend
    backend_dir = Path(__file__).parent / 'backend'
    os.chdir(backend_dir)
    
    # Ativa o ambiente virtual e inicia uvicorn
    venv_python = Path(__file__).parent / 'venv' / 'bin' / 'python'
    venv_uvicorn = Path(__file__).parent / 'venv' / 'bin' / 'uvicorn'
    
    try:
        # Tenta usar uvicorn diretamente
        cmd = [str(venv_uvicorn), 'main:app', '--reload', '--port', '8000']
        print(f"🚀 Executando: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguarda um pouco para ver se iniciou
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Backend iniciado com sucesso na porta 8000")
            return process
        else:
            print("❌ Falha ao iniciar backend")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
        return None

def start_frontend():
    """Inicia o frontend na porta 3000"""
    print("🌐 Iniciando frontend na porta 3000...")
    
    # Navega para o diretório frontend
    frontend_dir = Path(__file__).parent / 'frontend'
    os.chdir(frontend_dir)
    
    try:
        # Inicia servidor HTTP simples
        cmd = ['python3', '-m', 'http.server', '3000']
        print(f"🚀 Executando: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguarda um pouco para ver se iniciou
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Frontend iniciado com sucesso na porta 3000")
            return process
        else:
            print("❌ Falha ao iniciar frontend")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar frontend: {e}")
        return None

def test_system():
    """Testa se o sistema está funcionando"""
    print("🧪 Testando sistema...")
    
    import requests
    import time
    
    # Aguarda um pouco para o backend inicializar
    time.sleep(5)
    
    try:
        # Testa backend
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend respondendo corretamente")
        else:
            print(f"⚠️ Backend retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar backend: {e}")
    
    try:
        # Testa frontend
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend respondendo corretamente")
        else:
            print(f"⚠️ Frontend retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar frontend: {e}")

def setup_signal_handlers(backend_process, frontend_process):
    """Configura handlers para sinais do sistema"""
    def signal_handler(signum, frame):
        print(f"\n🛑 Recebido sinal {signum}, encerrando sistema...")
        
        if backend_process:
            backend_process.terminate()
            print("🔧 Backend encerrado")
        
        if frontend_process:
            frontend_process.terminate()
            print("🌐 Frontend encerrado")
        
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Função principal"""
    print_banner()
    
    # Verifica dependências
    if not check_dependencies():
        print("❌ Dependências não atendidas. Encerrando...")
        sys.exit(1)
    
    # Verifica ambiente
    if not check_environment():
        print("❌ Ambiente não configurado. Encerrando...")
        sys.exit(1)
    
    # Inicia processos
    backend_process = start_backend()
    if not backend_process:
        print("❌ Falha ao iniciar backend. Encerrando...")
        sys.exit(1)
    
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Falha ao iniciar frontend. Encerrando...")
        backend_process.terminate()
        sys.exit(1)
    
    # Configura handlers de sinal
    setup_signal_handlers(backend_process, frontend_process)
    
    print("\n🎉 Sistema iniciado com sucesso!")
    print("📱 Frontend: http://localhost:3000")
    print("🔧 Backend: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n💡 Pressione Ctrl+C para encerrar")
    
    # Testa o sistema
    test_system()
    
    try:
        # Mantém os processos rodando
        while True:
            time.sleep(1)
            
            # Verifica se os processos ainda estão rodando
            if backend_process.poll() is not None:
                print("❌ Backend parou inesperadamente")
                break
                
            if frontend_process.poll() is not None:
                print("❌ Frontend parou inesperadamente")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Encerrando sistema...")
    finally:
        # Encerra processos
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        print("✅ Sistema encerrado")

if __name__ == "__main__":
    main() 