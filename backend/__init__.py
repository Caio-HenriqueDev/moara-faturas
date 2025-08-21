"""
Sistema de Gestão de Faturas - Moara Energia
Backend FastAPI para processamento de faturas e integração com serviços externos.
"""

__version__ = "1.0.0"
__author__ = "Moara Energia"
__description__ = "Sistema de Gestão de Faturas - Backend API"

# Importações principais com fallback para Vercel
try:
    # Desenvolvimento local
    from . import models
    from . import crud
    from . import schemas
    from . import utils
    from . import config
    from . import database
except ImportError:
    # Vercel - importações absolutas
    import models
    import crud
    import schemas
    import utils
    import config
    import database

__all__ = [
    'models',
    'crud', 
    'schemas',
    'utils',
    'config',
    'database'
]
