#!/usr/bin/env python3
"""
Teste local da API para verificar funcionamento antes do deploy no Vercel
Versão 2.0 - Sistema completo de gestão de faturas
"""

import uvicorn
from api.index import app

if __name__ == "__main__":
    print("🚀 Iniciando teste local da API v2.0...")
    print("📱 Acesse: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("🏥 Health: http://localhost:8000/health")
    print("🧪 Test: http://localhost:8000/test")
    print("📄 Faturas: http://localhost:8000/faturas")
    print("📊 Stats: http://localhost:8000/stats")
    print("🔍 Fatura por ID: http://localhost:8000/faturas/1")
    print("\n⏹️  Pressione Ctrl+C para parar\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 