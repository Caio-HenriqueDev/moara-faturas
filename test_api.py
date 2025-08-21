#!/usr/bin/env python3
"""
Teste local da API para verificar funcionamento antes do deploy no Vercel
"""

import uvicorn
from api.index import app

if __name__ == "__main__":
    print("🚀 Iniciando teste local da API...")
    print("📱 Acesse: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🏥 Health: http://localhost:8000/health")
    print("🧪 Test: http://localhost:8000/test")
    print("📄 Faturas: http://localhost:8000/faturas")
    print("\n⏹️  Pressione Ctrl+C para parar\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 