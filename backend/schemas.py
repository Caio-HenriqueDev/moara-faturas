from pydantic import BaseModel
from typing import Optional

class FaturaSchema(BaseModel):
    id: int
    nome_cliente: Optional[str]
    documento_cliente: Optional[str]
    email_cliente: Optional[str]
    numero_instalacao: Optional[str]
    valor_total: Optional[float]
    mes_referencia: Optional[str]
    data_vencimento: Optional[str]
    url_pdf: Optional[str] = None
    ja_pago: Optional[bool]

    class Config:
        from_attributes = True  # Pydantic v2 – substitui orm_mode = True
