# USINA_CLIENTE/backend/models.py
"""
Modelos SQLAlchemy para o Sistema de Gestão de Faturas
Define a estrutura das tabelas do banco de dados
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Fatura(Base):
    """
    Modelo para armazenar faturas de energia elétrica
    """
    __tablename__ = 'faturas'

    # Campos de identificação
    id = Column(Integer, primary_key=True, index=True)
    
    # Dados do cliente
    nome_cliente = Column(String(255), nullable=False, index=True)
    documento_cliente = Column(String(20), unique=True, nullable=False, index=True)
    email_cliente = Column(String(255), nullable=False, index=True)
    
    # Dados da instalação
    numero_instalacao = Column(String(20), unique=True, nullable=False, index=True)
    
    # Dados financeiros
    valor_total = Column(Float, nullable=False)
    
    # Dados temporais
    mes_referencia = Column(String(50), nullable=False)
    data_vencimento = Column(String(20), nullable=False)
    
    # Arquivos e status
    url_pdf = Column(Text, nullable=True)  # Caminho ou URL do PDF
    ja_pago = Column(Boolean, default=False, index=True)
    
    # Timestamps
    data_criacao = Column(DateTime, server_default=func.now(), nullable=False)
    data_ultima_atualizacao = Column(DateTime, onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Fatura(id={self.id}, nome='{self.nome_cliente}', valor={self.valor_total})>"
    
    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
            'nome_cliente': self.nome_cliente,
            'documento_cliente': self.documento_cliente,
            'email_cliente': self.email_cliente,
            'numero_instalacao': self.numero_instalacao,
            'valor_total': self.valor_total,
            'mes_referencia': self.mes_referencia,
            'data_vencimento': self.data_vencimento,
            'url_pdf': self.url_pdf,
            'ja_pago': self.ja_pago,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_ultima_atualizacao': self.data_ultima_atualizacao.isoformat() if self.data_ultima_atualizacao else None
        }