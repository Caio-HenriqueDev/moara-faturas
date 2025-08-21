from pydantic import BaseModel
from typing import Optional

class FaturaSchema(BaseModel):
    id: int
    nome_cliente: Optional[str] = None
    documento_cliente: Optional[str] = None
    email_cliente: Optional[str] = None
    numero_instalacao: Optional[str] = None
    valor_total: Optional[float] = None
    mes_referencia: Optional[str] = None
    data_vencimento: Optional[str] = None
    url_pdf: Optional[str] = None
    ja_pago: Optional[bool] = False

    class Config:
        from_attributes = True  # Pydantic v2 – substitui orm_mode = True
