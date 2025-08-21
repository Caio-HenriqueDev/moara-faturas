#!/usr/bin/env python3
"""
Teste local da API para verificar funcionamento antes do deploy no Vercel
Sistema Completo de Gestão de Faturas - Moara Energia
"""

import uvicorn
from api.index import app

if __name__ == "__main__":
    print("🚀 Iniciando teste local da API COMPLETA...")
    print("📱 Acesse: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("🏥 Health: http://localhost:8000/health")
    print("🧪 Test: http://localhost:8000/test")
    print("📄 Faturas: http://localhost:8000/faturas")
    print("🔍 Fatura por ID: http://localhost:8000/faturas/1")
    print("📊 Stats: http://localhost:8000/stats")
    print("📧 Processar Email: http://localhost:8000/processar_email")
    print("💳 Checkout: http://localhost:8000/create-checkout-session/1")
    print("🔔 Webhook: http://localhost:8000/stripe-webhook")
    print("\n⏹️  Pressione Ctrl+C para parar\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 