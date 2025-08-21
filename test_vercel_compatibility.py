#!/usr/bin/env python3
"""
Script de teste para verificar compatibilidade com Vercel
Executa verificações que simulam o ambiente da Vercel
"""

import os
import sys
import importlib
from pathlib import Path

def print_step(message):
    """Imprime uma mensagem de passo formatada"""
    print(f"\n{'='*50}")
    print(f"🔍 {message}")
    print(f"{'='*50}")

def print_success(message):
    """Imprime uma mensagem de sucesso"""
    print(f"✅ {message}")

def print_error(message):
    """Imprime uma mensagem de erro"""
    print(f"❌ {message}")

def print_warning(message):
    """Imprime uma mensagem de aviso"""
    print(f"⚠️ {message}")

def test_imports():
    """Testa se todos os imports funcionam corretamente"""
    print_step("Testando imports")
    
    # Simula ambiente Vercel
    os.environ["VERCEL_ENV"] = "production"
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
    
    try:
        # Testa imports principais
        import backend.config
        print_success("Config importado com sucesso")
        
        import backend.database
        print_success("Database importado com sucesso")
        
        import backend.crud
        print_success("CRUD importado com sucesso")
        
        import backend.schemas
        print_success("Schemas importado com sucesso")
        
        import backend.models
        print_success("Models importado com sucesso")
        
        import backend.utils.bot_mail
        print_success("Bot mail importado com sucesso")
        
        import backend.utils.pdf_parser
        print_success("PDF parser importado com sucesso")
        
        return True
        
    except ImportError as e:
        print_error(f"Erro de import: {e}")
        return False
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        return False

def test_configuration():
    """Testa se a configuração está funcionando corretamente"""
    print_step("Testando configuração")
    
    try:
        from backend.config import settings
        
        print_success(f"Ambiente detectado: {settings.ENVIRONMENT}")
        print_success(f"É Vercel: {settings.IS_VERCEL}")
        print_success(f"É produção: {settings.IS_PRODUCTION}")
        print_success(f"Debug: {settings.DEBUG}")
        
        # Testa configuração de banco
        db_config = settings.get_database_config()
        print_success(f"Config banco: {db_config['type']}")
        
        # Valida configurações
        issues = settings.validate_config()
        if issues:
            print_warning("Problemas de configuração detectados:")
            for issue in issues:
                print_warning(f"   - {issue}")
        else:
            print_success("Configuração validada com sucesso")
        
        return True
        
    except Exception as e:
        print_error(f"Erro na configuração: {e}")
        return False

def test_database_connection():
    """Testa se a conexão com banco está funcionando"""
    print_step("Testando conexão com banco")
    
    try:
        from backend.database import get_database_url, create_database_engine
        
        url = get_database_url()
        print_success(f"URL do banco: {url}")
        
        # Testa criação do engine (sem conectar)
        engine = create_database_engine()
        print_success("Engine do banco criado com sucesso")
        
        return True
        
    except Exception as e:
        print_error(f"Erro na conexão com banco: {e}")
        return False

def test_schemas():
    """Testa se os schemas estão funcionando corretamente"""
    print_step("Testando schemas")
    
    try:
        from backend.schemas import FaturaCreate, FaturaSchema
        
        # Testa criação de schema
        fatura_data = {
            "nome_cliente": "Teste Cliente",
            "documento_cliente": "12345678901",
            "email_cliente": "teste@email.com",
            "numero_instalacao": "123456",
            "valor_total": 100.50,
            "mes_referencia": "Janeiro/2024",
            "data_vencimento": "15/01/2024"
        }
        
        fatura_create = FaturaCreate(**fatura_data)
        print_success("Schema FaturaCreate criado com sucesso")
        
        return True
        
    except Exception as e:
        print_error(f"Erro nos schemas: {e}")
        return False

def test_utils():
    """Testa se os utilitários estão funcionando"""
    print_step("Testando utilitários")
    
    try:
        from backend.utils.pdf_parser import validar_dados_fatura
        
        # Testa validação de dados
        dados_teste = {
            "nome_cliente": "Teste",
            "documento_cliente": "12345678901",
            "numero_instalacao": "123456",
            "valor_total": 100.0,
            "mes_referencia": "Janeiro/2024",
            "data_vencimento": "15/01/2024"
        }
        
        resultado = validar_dados_fatura(dados_teste)
        if resultado:
            print_success("Validação de dados funcionando")
        else:
            print_warning("Validação de dados falhou")
        
        return True
        
    except Exception as e:
        print_error(f"Erro nos utilitários: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 TESTE DE COMPATIBILIDADE COM VERCEL")
    print("=" * 50)
    
    # Lista de testes
    testes = [
        ("Imports", test_imports),
        ("Configuração", test_configuration),
        ("Conexão com banco", test_database_connection),
        ("Schemas", test_schemas),
        ("Utilitários", test_utils)
    ]
    
    resultados = []
    
    for nome_teste, funcao_teste in testes:
        try:
            resultado = funcao_teste()
            resultados.append((nome_teste, resultado))
        except Exception as e:
            print_error(f"Erro no teste {nome_teste}: {e}")
            resultados.append((nome_teste, False))
    
    # Resumo dos resultados
    print_step("RESUMO DOS TESTES")
    
    sucessos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nome_teste, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{nome_teste}: {status}")
    
    print(f"\n📊 Resultado: {sucessos}/{total} testes passaram")
    
    if sucessos == total:
        print_success("🎉 Todos os testes passaram! Sistema compatível com Vercel.")
        return 0
    else:
        print_error("⚠️ Alguns testes falharam. Verifique os problemas acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 