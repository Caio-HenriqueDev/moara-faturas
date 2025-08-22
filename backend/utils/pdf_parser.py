"""
Parser de PDF para o Sistema de Gestão de Faturas
Extrai dados estruturados de faturas de energia em formato PDF
"""

import PyPDF2
import re
from typing import Optional, Dict, Any
from pathlib import Path

def extrair_texto_pdf(path_pdf: str) -> Optional[str]:
    """
    Extrai texto de um arquivo PDF.
    
    Args:
        path_pdf: Caminho para o arquivo PDF
        
    Returns:
        Texto extraído ou None se falhar
    """
    try:
        with open(path_pdf, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            texto_total = ""
            
            for page in pdf_reader.pages:
                texto_pagina = page.extract_text()
                if texto_pagina:
                    texto_total += texto_pagina + "\n"
            
            return texto_total
    except Exception as e:
        print(f"❌ Erro ao extrair texto do PDF {path_pdf}: {e}")
        return None

def buscar_regex(padrao: str, texto: str, grupo: int = 1, tipo=str) -> Optional[Any]:
    """
    Função auxiliar para buscar padrões regex com conversão de tipo.
    
    Args:
        padrao: Padrão regex para buscar
        texto: Texto onde buscar
        grupo: Grupo do regex a retornar
        tipo: Tipo para converter o resultado
        
    Returns:
        Valor encontrado convertido para o tipo especificado ou None
    """
    try:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            valor = match.group(grupo).strip()
            if valor:
                return tipo(valor)
        return None
    except (ValueError, TypeError) as e:
        print(f"⚠️ Erro ao converter valor '{valor}' para tipo {tipo.__name__}: {e}")
        return None

def extrair_dados_fatura_pdf(path_pdf: str) -> Optional[Dict[str, Any]]:
    """
    Extrai dados de uma fatura de energia em formato PDF.
    
    Args:
        path_pdf: Caminho para o arquivo PDF
        
    Returns:
        Dicionário com os dados extraídos ou None se falhar
    """
    # Verifica se o arquivo existe
    if not Path(path_pdf).exists():
        print(f"❌ Arquivo PDF não encontrado: {path_pdf}")
        return None
    
    # Extrai texto do PDF
    texto_total = extrair_texto_pdf(path_pdf)
    if not texto_total:
        return None
    
    print(f"📄 Processando PDF: {Path(path_pdf).name}")
    print(f"📝 Tamanho do texto extraído: {len(texto_total)} caracteres")
    print(f"📋 Primeiros 200 caracteres: {texto_total[:200]}...")
    
    try:
        # Extração de dados via regex com validações
        dados_extraidos = {
            "nome_cliente": buscar_regex(
                r"\n([A-Z\s]{5,})\nMURIAE", 
                texto_total
            ),
            "mes_referencia": buscar_regex(
                r"(\w+\s*/\s*\d{4})", 
                texto_total
            ),
            "data_vencimento": buscar_regex(
                r"(\d{2}/\d{2}/\d{4})", 
                texto_total
            ),
            "preco_unitario_com_tributo": buscar_regex(
                r"Consumo em kWh.*?\n.*?([0-9.,]{4,})", 
                texto_total,
                tipo=lambda x: float(x.replace(",", "."))
            ),
            "quantidade_kwh": buscar_regex(
                r"\b([23][0-9]{2}),00\b", 
                texto_total,
                tipo=lambda x: int(x.replace(",", ""))
            ),
            "numero_instalacao": buscar_regex(
                r"\b(\d{6,8})\b", 
                texto_total
            ),
            "saldo_acumulado_gdii": buscar_regex(
                r"Saldo Acumulado:\s*([\d.,]+)", 
                texto_total,
                tipo=lambda x: float(x.replace(".", "").replace(",", "."))
            ),
            "documento_cliente": buscar_regex(
                r"CNPJ/CPF/RANI[:\s]*([0-9Xx./-]{11,20})", 
                texto_total
            ),
            "email_cliente": buscar_regex(
                r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", 
                texto_total
            ),
        }
        
        # Log dos dados extraídos para debug
        print(f"🔍 Dados extraídos:")
        for campo, valor in dados_extraidos.items():
            print(f"   - {campo}: {valor}")
        
        # Validação dos campos obrigatórios
        campos_obrigatorios = [
            "nome_cliente", "numero_instalacao"
        ]
        
        campos_opcionais = [
            "documento_cliente", "mes_referencia", "data_vencimento"
        ]
        
        # Verifica campos obrigatórios
        campos_faltando = [campo for campo in campos_obrigatorios if not dados_extraidos.get(campo)]
        if campos_faltando:
            print(f"❌ Campos obrigatórios não encontrados: {campos_faltando}")
            return None
        
        # Para campos opcionais, usa valores padrão se não encontrados
        if not dados_extraidos.get("documento_cliente"):
            dados_extraidos["documento_cliente"] = "N/A"
            print("⚠️ Documento do cliente não encontrado, usando 'N/A'")
        
        if not dados_extraidos.get("mes_referencia"):
            dados_extraidos["mes_referencia"] = "N/A"
            print("⚠️ Mês de referência não encontrado, usando 'N/A'")
        
        if not dados_extraidos.get("data_vencimento"):
            dados_extraidos["data_vencimento"] = "N/A"
            print("⚠️ Data de vencimento não encontrada, usando 'N/A'")
        
        # Cálculo do valor total
        valor_final = None
        if dados_extraidos["preco_unitario_com_tributo"] and dados_extraidos["quantidade_kwh"]:
            # Aplica desconto de 20% (0.8) conforme lógica existente
            preco_com_desconto = dados_extraidos["preco_unitario_com_tributo"] * 0.8
            valor_final = round(preco_com_desconto * dados_extraidos["quantidade_kwh"], 2)
        else:
            # Se não conseguir calcular, usa valor padrão
            valor_final = 100.00
            print("⚠️ Não foi possível calcular o valor total, usando R$ 100,00")
        
        # Construção do dicionário final com validações
        fatura_data = {
            "nome_cliente": dados_extraidos["nome_cliente"],
            "documento_cliente": dados_extraidos["documento_cliente"],
            "email_cliente": dados_extraidos.get("email_cliente", ""),
            "numero_instalacao": dados_extraidos["numero_instalacao"],
            "valor_total": valor_final,
            "mes_referencia": dados_extraidos["mes_referencia"],
            "data_vencimento": dados_extraidos["data_vencimento"],
        }
        
        # Log dos dados extraídos
        print(f"✅ Dados extraídos com sucesso:")
        print(f"   - Cliente: {fatura_data['nome_cliente']}")
        print(f"   - Instalação: {fatura_data['numero_instalacao']}")
        print(f"   - Valor: R$ {fatura_data['valor_total']:.2f}")
        print(f"   - Vencimento: {fatura_data['data_vencimento']}")
        
        return fatura_data
        
    except Exception as e:
        print(f"❌ Erro inesperado ao processar o PDF {path_pdf}: {e}")
        return None

def validar_dados_fatura(dados: Dict[str, Any]) -> bool:
    """
    Valida se os dados extraídos da fatura estão completos e corretos.
    
    Args:
        dados: Dicionário com os dados da fatura
        
    Returns:
        True se os dados são válidos, False caso contrário
    """
    if not dados:
        return False
    
    # Campos obrigatórios
    campos_obrigatorios = [
        "nome_cliente", "documento_cliente", "numero_instalacao",
        "valor_total", "mes_referencia", "data_vencimento"
    ]
    
    for campo in campos_obrigatorios:
        if not dados.get(campo):
            print(f"❌ Campo obrigatório faltando: {campo}")
            return False
    
    # Validações específicas
    if dados["valor_total"] <= 0:
        print("❌ Valor total deve ser maior que zero")
        return False
    
    if len(dados["documento_cliente"]) < 11:
        print("❌ Documento do cliente deve ter pelo menos 11 caracteres")
        return False
    
    if len(dados["numero_instalacao"]) < 6:
        print("❌ Número de instalação deve ter pelo menos 6 caracteres")
        return False
    
    return True
