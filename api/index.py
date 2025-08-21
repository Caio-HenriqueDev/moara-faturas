# Arquivo para Vercel - Sistema de Gestão de Faturas Completo
import sys
import os

# Adiciona o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Importa e executa a aplicação FastAPI principal
from main import app

# Para Vercel, exporta a aplicação
handler = app 