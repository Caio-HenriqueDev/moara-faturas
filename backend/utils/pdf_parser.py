# USINA_CLIENTE/backend/utils/pdf_parser.py
import PyPDF2
import re
from typing import Optional

def extrair_dados_fatura_pdf(path_pdf: str) -> Optional[dict]:
    """
    Extrai dados de uma fatura de energia em formato PDF usando PyPDF2.
    Retorna um dicionário com os campos necessários para o nosso modelo de dados.
    """
    try:
        with open(path_pdf, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            texto_total = ""
            for page in pdf_reader.pages:
                texto_total += page.extract_text()

        def buscar_regex(padrao, texto, grupo=1, tipo=str):
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                return tipo(match.group(grupo).strip())
            return None

        # Extração de dados via regex
        dados_extraidos = {
            "nome_cliente": buscar_regex(r"\n([A-Z\s]{5,})\nMURIAE", texto_total),
            "mes_referencia": buscar_regex(r"(\w+\s*/\s*\d{4})", texto_total),
            "data_vencimento": buscar_regex(r"(\d{2}/\d{2}/\d{4})", texto_total),
            "preco_unitario_com_tributo": buscar_regex(
                r"Consumo em kWh.*?\n.*?([0-9.,]{4,})", texto_total,
                tipo=lambda x: float(x.replace(",", "."))
            ),
            "quantidade_kwh": buscar_regex(
                r"\b([23][0-9]{2}),00\b", texto_total,
                tipo=lambda x: int(x.replace(",", ""))
            ),
            "numero_instalacao": buscar_regex(r"\b(\d{6})\s*Ponta", texto_total),
            "saldo_acumulado_gdii": buscar_regex(
                r"Saldo Acumulado:\s*([\d.,]+)", texto_total,
                tipo=lambda x: float(x.replace(".", "").replace(",", "."))
            ),
            "documento_cliente": buscar_regex(
                r"CNPJ/CPF/RANI[:\s]*([0-9Xx./-]{11,20})", texto_total
            ),
            "email_cliente": buscar_regex(
                r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", texto_total
            ),
        }

        # Cálculo do valor total
        valor_final = None
        if dados_extraidos["preco_unitario_com_tributo"] and dados_extraidos["quantidade_kwh"]:
            preco_com_desconto = dados_extraidos["preco_unitario_com_tributo"] * 0.8
            valor_final = round(preco_com_desconto * dados_extraidos["quantidade_kwh"], 2)

        # Construção do dicionário final
        return {
            "nome_cliente": dados_extraidos.get("nome_cliente"),
            "documento_cliente": dados_extraidos.get("documento_cliente"),
            "email_cliente": dados_extraidos.get("email_cliente"),
            "numero_instalacao": dados_extraidos.get("numero_instalacao"),
            "valor_total": valor_final,
            "mes_referencia": dados_extraidos.get("mes_referencia"),
            "data_vencimento": dados_extraidos.get("data_vencimento"),
        }

    except Exception as e:
        print(f"Erro inesperado ao processar o PDF {path_pdf}: {e}")
        return None
