# USINA_CLIENTE/backend/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Fatura(Base):
    __tablename__ = 'faturas'

    id = Column(Integer, primary_key=True, index=True)
    nome_cliente = Column(String, index=True)
    documento_cliente = Column(String, unique=True, index=True)
    email_cliente = Column(String, index=True)
    numero_instalacao = Column(String, unique=True, index=True)
    valor_total = Column(Float)
    mes_referencia = Column(String)
    data_vencimento = Column(String)
    url_pdf = Column(String) # Opcional: Se quisermos guardar o link do pdf original
    ja_pago = Column(Boolean, default=False)
    data_criacao = Column(DateTime, server_default=func.now())
    data_ultima_atualizacao = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<Fatura(id={self.id}, nome='{self.nome_cliente}', valor={self.valor_total})>"