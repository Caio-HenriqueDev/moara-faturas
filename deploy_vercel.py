#!/usr/bin/env python3
"""
Script de Deploy para Vercel - Sistema de Gestão de Faturas
Moara Energia

Este script automatiza o processo de preparação para deploy na Vercel.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def print_step(message):
    """Imprime uma mensagem de passo formatada"""
    print(f"\n{'='*50}")
    print(f"🔄 {message}")
    print(f"{'='*50}")

def print_success(message):
    """Imprime uma mensagem de sucesso"""
    print(f"✅ {message}")

def print_error(message):
    """Imprime uma mensagem de erro"""
    print(f"❌ {message}")

def print_info(message):
    """Imprime uma mensagem informativa"""
    print(f"ℹ️  {message}")

def check_requirements():
    """Verifica se os requisitos estão instalados"""
    print_step("Verificando requisitos")
    
    # Verificar se git está instalado
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        print_success("Git está instalado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Git não está instalado")
        return False
    
    # Verificar se vercel CLI está instalado
    try:
        subprocess.run(["vercel", "--version"], check=True, capture_output=True)
        print_success("Vercel CLI está instalado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_info("Vercel CLI não está instalado. Instalando...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "vercel"], check=True)
            print_success("Vercel CLI instalado com sucesso")
        except subprocess.CalledProcessError:
            print_error("Falha ao instalar Vercel CLI")
            return False
    
    return True

def validate_project_structure():
    """Valida a estrutura do projeto"""
    print_step("Validando estrutura do projeto")
    
    required_files = [
        "backend/main.py",
        "backend/requirements.txt",
        "backend/runtime.txt",
        "vercel.json",
        "package.json",
        "frontend/index.html",
        "frontend/config.js"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print_error(f"Arquivos obrigatórios não encontrados: {missing_files}")
        return False
    
    print_success("Estrutura do projeto validada")
    return True

def check_environment_variables():
    """Verifica se as variáveis de ambiente estão configuradas"""
    print_step("Verificando variáveis de ambiente")
    
    required_vars = [
        "DATABASE_URL",
        "STRIPE_SECRET_KEY",
        "STRIPE_PUBLIC_KEY",
        "EMAIL_USER",
        "EMAIL_PASS"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print_info(f"Variáveis de ambiente não configuradas: {missing_vars}")
        print_info("Configure-as na Vercel Dashboard após o deploy")
    else:
        print_success("Todas as variáveis de ambiente estão configuradas")
    
    return True

def prepare_deploy():
    """Prepara o projeto para deploy"""
    print_step("Preparando projeto para deploy")
    
    # Verificar se há arquivos temporários ou de desenvolvimento
    dev_files = [
        "__pycache__",
        "*.pyc",
        ".env",
        "venv",
        ".pytest_cache",
        ".vercel"
    ]
    
    for pattern in dev_files:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print_info(f"Removido diretório: {path}")
            elif path.is_file():
                path.unlink()
                print_info(f"Removido arquivo: {path}")
    
    # Limpar arquivos de cache Python
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                cache_path = os.path.join(root, dir_name)
                shutil.rmtree(cache_path)
                print_info(f"Removido cache Python: {cache_path}")
    
    print_success("Projeto preparado para deploy")
    return True

def deploy_to_vercel():
    """Faz o deploy para a Vercel"""
    print_step("Iniciando deploy para Vercel")
    
    try:
        # Verificar se já está logado na Vercel
        result = subprocess.run(["vercel", "whoami"], capture_output=True, text=True)
        if result.returncode != 0:
            print_info("Faça login na Vercel primeiro:")
            print("vercel login")
            return False
        
        print_success(f"Logado como: {result.stdout.strip()}")
        
        # Fazer deploy
        print_info("Iniciando deploy...")
        subprocess.run(["vercel", "--prod"], check=True)
        
        print_success("Deploy concluído com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Erro durante deploy: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Script de Deploy para Vercel - Sistema de Gestão de Faturas")
    print("Moara Energia")
    
    # Verificar requisitos
    if not check_requirements():
        print_error("Requisitos não atendidos. Abortando...")
        sys.exit(1)
    
    # Validar estrutura
    if not validate_project_structure():
        print_error("Estrutura do projeto inválida. Abortando...")
        sys.exit(1)
    
    # Verificar variáveis de ambiente
    check_environment_variables()
    
    # Preparar projeto
    if not prepare_deploy():
        print_error("Falha ao preparar projeto. Abortando...")
        sys.exit(1)
    
    # Fazer deploy
    if not deploy_to_vercel():
        print_error("Falha no deploy. Verifique os logs acima.")
        sys.exit(1)
    
    print_success("🎉 Deploy concluído com sucesso!")
    print_info("Acesse seu projeto na Vercel Dashboard")
    print_info("Configure as variáveis de ambiente se necessário")

if __name__ == "__main__":
    main() 