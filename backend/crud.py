"""
Operações CRUD para o Sistema de Gestão de Faturas
Implementa todas as operações de banco de dados para faturas
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any

# Importações com fallback para Vercel
try:
    from .models import Fatura
    from .schemas import FaturaCreate, FaturaUpdate
except ImportError:
    from models import Fatura
    from schemas import FaturaCreate, FaturaUpdate

class FaturaCRUD:
    """Classe para operações CRUD de faturas"""
    
    @staticmethod
    def get_fatura_by_instalacao(db: Session, numero_instalacao: str) -> Optional[Fatura]:
        """
        Busca uma fatura pelo número de instalação.
        
        Args:
            db: Sessão do banco de dados
            numero_instalacao: Número da instalação
            
        Returns:
            Fatura encontrada ou None
        """
        return db.query(Fatura).filter(
            Fatura.numero_instalacao == numero_instalacao
        ).first()
    
    @staticmethod
    def get_fatura_by_id(db: Session, fatura_id: int) -> Optional[Fatura]:
        """
        Busca uma fatura pelo seu ID primário.
        
        Args:
            db: Sessão do banco de dados
            fatura_id: ID da fatura
            
        Returns:
            Fatura encontrada ou None
        """
        return db.query(Fatura).filter(Fatura.id == fatura_id).first()
    
    @staticmethod
    def get_faturas(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        ja_pago: Optional[bool] = None
    ) -> List[Fatura]:
        """
        Retorna uma lista de faturas com paginação e filtros opcionais.
        
        Args:
            db: Sessão do banco de dados
            skip: Número de registros para pular
            limit: Número máximo de registros
            ja_pago: Filtro por status de pagamento
            
        Returns:
            Lista de faturas
        """
        query = db.query(Fatura)
        
        if ja_pago is not None:
            query = query.filter(Fatura.ja_pago == ja_pago)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_fatura(db: Session, fatura_data: Dict[str, Any]) -> Fatura:
        """
        Cria uma nova fatura no banco de dados.
        
        Args:
            db: Sessão do banco de dados
            fatura_data: Dados da fatura
            
        Returns:
            Fatura criada
            
        Raises:
            IntegrityError: Se houver violação de constraint único
        """
        try:
            db_fatura = Fatura(**fatura_data)
            db.add(db_fatura)
            db.commit()
            db.refresh(db_fatura)
            return db_fatura
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Erro de integridade: {str(e)}")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Erro ao criar fatura: {str(e)}")
    
    @staticmethod
    def update_fatura(
        db: Session, 
        db_fatura: Fatura, 
        fatura_data: Dict[str, Any]
    ) -> Fatura:
        """
        Atualiza uma fatura existente com novos dados.
        
        Args:
            db: Sessão do banco de dados
            db_fatura: Fatura existente
            fatura_data: Novos dados para atualizar
            
        Returns:
            Fatura atualizada
        """
        try:
            for key, value in fatura_data.items():
                if hasattr(db_fatura, key):
                    setattr(db_fatura, key, value)
            
            db.commit()
            db.refresh(db_fatura)
            return db_fatura
        except Exception as e:
            db.rollback()
            raise ValueError(f"Erro ao atualizar fatura: {str(e)}")
    
    @staticmethod
    def update_fatura_ja_pago(db: Session, fatura_id: int) -> Optional[Fatura]:
        """
        Atualiza o status 'ja_pago' de uma fatura para True.
        
        Args:
            db: Sessão do banco de dados
            fatura_id: ID da fatura
            
        Returns:
            Fatura atualizada ou None se não encontrada
        """
        try:
            db_fatura = FaturaCRUD.get_fatura_by_id(db, fatura_id)
            if db_fatura:
                db_fatura.ja_pago = True
                db.commit()
                db.refresh(db_fatura)
                return db_fatura
            return None
        except Exception as e:
            db.rollback()
            raise ValueError(f"Erro ao atualizar status de pagamento: {str(e)}")
    
    @staticmethod
    def delete_fatura(db: Session, fatura_id: int) -> bool:
        """
        Remove uma fatura do banco de dados.
        
        Args:
            db: Sessão do banco de dados
            fatura_id: ID da fatura
            
        Returns:
            True se removida com sucesso, False caso contrário
        """
        try:
            db_fatura = FaturaCRUD.get_fatura_by_id(db, fatura_id)
            if db_fatura:
                db.delete(db_fatura)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise ValueError(f"Erro ao remover fatura: {str(e)}")
    
    @staticmethod
    def get_faturas_by_cliente(
        db: Session, 
        documento_cliente: str
    ) -> List[Fatura]:
        """
        Busca todas as faturas de um cliente específico.
        
        Args:
            db: Sessão do banco de dados
            documento_cliente: CPF/CNPJ do cliente
            
        Returns:
            Lista de faturas do cliente
        """
        return db.query(Fatura).filter(
            Fatura.documento_cliente == documento_cliente
        ).all()
    
    @staticmethod
    def get_faturas_pendentes(db: Session) -> List[Fatura]:
        """
        Retorna todas as faturas pendentes de pagamento.
        
        Args:
            db: Sessão do banco de dados
            
        Returns:
            Lista de faturas pendentes
        """
        return db.query(Fatura).filter(Fatura.ja_pago == False).all()
    
    @staticmethod
    def get_faturas_pagas(db: Session) -> List[Fatura]:
        """
        Retorna todas as faturas já pagas.
        
        Args:
            db: Sessão do banco de dados
            
        Returns:
            Lista de faturas pagas
        """
        return db.query(Fatura).filter(Fatura.ja_pago == True).all()

# Funções de conveniência para compatibilidade com código existente
def get_fatura_by_instalacao(db: Session, numero_instalacao: str) -> Optional[Fatura]:
    return FaturaCRUD.get_fatura_by_instalacao(db, numero_instalacao)

def get_fatura_by_id(db: Session, fatura_id: int) -> Optional[Fatura]:
    return FaturaCRUD.get_fatura_by_id(db, fatura_id)

def get_faturas(db: Session, skip: int = 0, limit: int = 100) -> List[Fatura]:
    return FaturaCRUD.get_faturas(db, skip, limit)

def create_fatura(db: Session, fatura_data: Dict[str, Any]) -> Fatura:
    return FaturaCRUD.create_fatura(db, fatura_data)

def update_fatura(db: Session, db_fatura: Fatura, fatura_data: Dict[str, Any]) -> Fatura:
    return FaturaCRUD.update_fatura(db, db_fatura, fatura_data)

def update_fatura_ja_pago(db: Session, fatura_id: int) -> Optional[Fatura]:
    return FaturaCRUD.update_fatura_ja_pago(db, fatura_id)