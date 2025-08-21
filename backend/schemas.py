"""
Schemas Pydantic para validação de dados da API
Define a estrutura dos dados de entrada e saída
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class FaturaBase(BaseModel):
    """Schema base para faturas"""
    nome_cliente: str = Field(..., min_length=1, max_length=255, description="Nome completo do cliente")
    documento_cliente: str = Field(..., min_length=11, max_length=20, description="CPF/CNPJ do cliente")
    email_cliente: str = Field(..., description="Email do cliente")
    numero_instalacao: str = Field(..., min_length=1, max_length=20, description="Número da instalação")
    valor_total: float = Field(..., gt=0, description="Valor total da fatura")
    mes_referencia: str = Field(..., min_length=1, max_length=50, description="Mês de referência")
    data_vencimento: str = Field(..., min_length=1, max_length=20, description="Data de vencimento")
    url_pdf: Optional[str] = Field(None, description="URL ou caminho do PDF da fatura")

class FaturaCreate(FaturaBase):
    """Schema para criação de faturas"""
    pass

class FaturaUpdate(BaseModel):
    """Schema para atualização de faturas"""
    nome_cliente: Optional[str] = Field(None, min_length=1, max_length=255)
    documento_cliente: Optional[str] = Field(None, min_length=11, max_length=20)
    email_cliente: Optional[str] = Field(None)
    numero_instalacao: Optional[str] = Field(None, min_length=1, max_length=20)
    valor_total: Optional[float] = Field(None, gt=0)
    mes_referencia: Optional[str] = Field(None, min_length=1, max_length=50)
    data_vencimento: Optional[str] = Field(None, min_length=1, max_length=20)
    url_pdf: Optional[str] = Field(None)
    ja_pago: Optional[bool] = Field(None)

class FaturaSchema(FaturaBase):
    """Schema completo para faturas (inclui campos do banco)"""
    id: int = Field(..., description="ID único da fatura")
    ja_pago: bool = Field(default=False, description="Status de pagamento")
    data_criacao: Optional[datetime] = Field(None, description="Data de criação")
    data_ultima_atualizacao: Optional[datetime] = Field(None, description="Data da última atualização")

    class Config:
        from_attributes = True  # Pydantic v2
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class CheckoutSessionResponse(BaseModel):
    """Schema para resposta de criação de sessão de checkout"""
    session_id: str = Field(..., description="ID da sessão do Stripe")
    checkout_url: str = Field(..., description="URL para checkout")

class ProcessamentoEmailResponse(BaseModel):
    """Schema para resposta de processamento de emails"""
    message: str = Field(..., description="Mensagem de resultado")
    faturas_processadas: int = Field(..., description="Número de faturas processadas")

class HealthCheckResponse(BaseModel):
    """Schema para resposta de health check"""
    status: str = Field(..., description="Status do sistema")
    timestamp: str = Field(..., description="Timestamp da verificação")
    environment: str = Field(..., description="Ambiente atual")
    services: dict = Field(..., description="Status dos serviços")
