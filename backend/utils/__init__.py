# USINA_CLIENTE/backend/utils/__init__.py
# Módulo de utilitários para o sistema de gestão de faturas

# Importações condicionais para compatibilidade com Vercel
try:
    from . import bot_mail
    from . import pdf_parser
    __all__ = ['bot_mail', 'pdf_parser']
except ImportError:
    # Para Vercel, importações absolutas
    import bot_mail
    import pdf_parser
    __all__ = ['bot_mail', 'pdf_parser']
