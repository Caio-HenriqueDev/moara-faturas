# Arquivo para Vercel - redireciona para o backend
import sys
import os

# Adiciona o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Importa e executa a aplicação FastAPI
from main import app

# Para Vercel, exporta a aplicação
handler = app 