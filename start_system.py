#!/usr/bin/env python3
"""
Script de inicialização definitivo para o Sistema de Gestão de Faturas
Funciona independente do diretório de execução
"""

import os
import sys
import subprocess
import time
import signal
import threading

def print_banner():
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
        print("💡 Execute: source venv/bin/activate && pip install -r requirements.txt")
        return False

def start_backend():
    """Inicia o backend na porta 8000"""
    print("🔧 Iniciando backend na porta 8000...")
    
    # Navega para o diretório backend
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    # Ativa o ambiente virtual e inicia uvicorn
    venv_python = os.path.join(os.path.dirname(backend_dir), 'venv', 'bin', 'python')
    venv_uvicorn = os.path.join(os.path.dirname(backend_dir), 'venv', 'bin', 'uvicorn')
    
    try:
        # Tenta usar uvicorn diretamente
        cmd = [venv_uvicorn, 'main:app', '--reload', '--port', '8000']
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
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
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
    print("\n🧪 Testando sistema...")
    
    import requests
    
    try:
        # Testa backend
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend respondendo na porta 8000")
        else:
            print(f"⚠️ Backend respondeu com status: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend não responde: {e}")
    
    try:
        # Testa frontend
        response = requests.get("http://localhost:3000/", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend respondendo na porta 3000")
        else:
            print(f"⚠️ Frontend respondeu com status: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend não responde: {e}")

def main():
    """Função principal"""
    print_banner()
    
    # Verifica dependências
    if not check_dependencies():
        print("❌ Sistema não pode ser iniciado. Corrija as dependências primeiro.")
        return
    
    print()
    
    # Inicia backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Falha ao iniciar backend. Sistema não pode continuar.")
        return
    
    print()
    
    # Inicia frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Falha ao iniciar frontend.")
        print("💡 Backend continua rodando na porta 8000")
    
    print()
    
    # Testa sistema
    test_system()
    
    print("\n🎯 SISTEMA INICIADO COM SUCESSO!")
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n⏹️  Pressione Ctrl+C para parar o sistema")
    
    try:
        # Mantém o sistema rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Parando sistema...")
        
        if backend_process:
            backend_process.terminate()
            print("✅ Backend parado")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend parado")
        
        print("👋 Sistema parado com sucesso!")

if __name__ == "__main__":
    main() 