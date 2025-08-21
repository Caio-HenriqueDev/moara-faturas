# USINA_CLIENTE/backend/crud.py
from sqlalchemy.orm import Session
try:
    from models import Fatura
except ImportError:
    try:
        from .models import Fatura
    except ImportError:
        from backend.models import Fatura

def get_fatura_by_instalacao(db: Session, numero_instalacao: str):
    """
    Busca uma fatura pelo número de instalação.
    """
    return db.query(Fatura).filter(Fatura.numero_instalacao == numero_instalacao).first()

def get_faturas(db: Session, skip: int = 0, limit: int = 100):
    """
    Retorna uma lista de faturas com paginação.
    """
    return db.query(Fatura).offset(skip).limit(limit).all()

def create_fatura(db: Session, fatura_data: dict):
    """
    Cria uma nova fatura no banco de dados.
    """
    # Cria uma nova instância da classe Fatura com os dados do dicionário
    db_fatura = Fatura(**fatura_data)
    
    # Adiciona a fatura à sessão
    db.add(db_fatura)
    
    # Salva as mudanças no banco de dados
    db.commit()
    
    # Atualiza a instância com os dados do banco de dados (ex: id, datas)
    db.refresh(db_fatura)
    
    return db_fatura

def update_fatura(db: Session, db_fatura: Fatura, fatura_data: dict):
    """
    Atualiza uma fatura existente com novos dados.
    """
    for key, value in fatura_data.items():
        setattr(db_fatura, key, value)
    
    db.commit()
    db.refresh(db_fatura)
    
    return db_fatura

# Função para buscar fatura por ID
def get_fatura_by_id(db: Session, fatura_id: int):
    """
    Busca uma fatura pelo seu ID primário.
    """
    return db.query(Fatura).filter(Fatura.id == fatura_id).first()

def update_fatura_ja_pago(db: Session, fatura_id: int):
    """
    Atualiza o status 'ja_pago' de uma fatura para True.
    """
    db_fatura = get_fatura_by_id(db, fatura_id)
    if db_fatura:
        db_fatura.ja_pago = True
        db.commit()
        db.refresh(db_fatura)
        return db_fatura
    return None