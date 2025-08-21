"""
Automação de email para o Sistema de Gestão de Faturas
Busca emails com anexos PDF e processa faturas automaticamente
"""

import imaplib
import email
import os
from email.header import decode_header
from hashlib import md5
from typing import List, Dict, Any, Optional

# Importações com fallback para Vercel
try:
    from ..config import settings
except ImportError:
    from config import settings

def conectar_email() -> Optional[imaplib.IMAP4_SSL]:
    """
    Conecta ao servidor IMAP e retorna a conexão.
    
    Returns:
        Conexão IMAP ou None se falhar
    """
    try:
        if not settings.EMAIL_USER or not settings.EMAIL_PASS:
            print("❌ Credenciais de email não configuradas")
            return None
            
        mail = imaplib.IMAP4_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
        mail.login(settings.EMAIL_USER, settings.EMAIL_PASS)
        mail.select("inbox")
        print(f"✅ Conectado ao email: {settings.EMAIL_USER}")
        return mail
    except Exception as e:
        print(f"❌ Erro ao conectar ao e-mail: {e}")
        return None

def gerar_hash(conteudo_bytes: bytes) -> str:
    """
    Gera um hash MD5 do conteúdo para verificar se o arquivo é inédito.
    
    Args:
        conteudo_bytes: Conteúdo do arquivo em bytes
        
    Returns:
        Hash MD5 em hexadecimal
    """
    return md5(conteudo_bytes).hexdigest()

def salvar_pdf(conteudo: bytes, hash_pdf: str) -> Optional[str]:
    """
    Salva o PDF no diretório de armazenamento.
    
    Args:
        conteudo: Conteúdo do PDF em bytes
        hash_pdf: Hash MD5 do arquivo
        
    Returns:
        Caminho do arquivo salvo ou None se falhar
    """
    try:
        # Cria diretório se não existir
        os.makedirs(settings.PDF_STORAGE_PATH, exist_ok=True)
        
        # Caminho completo do arquivo
        path_pdf = os.path.join(settings.PDF_STORAGE_PATH, f"{hash_pdf}.pdf")
        
        # Salva o arquivo
        with open(path_pdf, "wb") as f:
            f.write(conteudo)
        
        print(f"✅ PDF salvo: {path_pdf}")
        return path_pdf
    except Exception as e:
        print(f"❌ Erro ao salvar PDF: {e}")
        return None

def processar_anexo_pdf(part: email.message.Message, nome_anexo: str) -> Optional[Dict[str, Any]]:
    """
    Processa um anexo PDF individual.
    
    Args:
        part: Parte do email contendo o anexo
        nome_anexo: Nome do arquivo anexo
        
    Returns:
        Dados extraídos da fatura ou None se falhar
    """
    try:
        # Decodifica o nome do arquivo
        nome, charset = decode_header(nome_anexo)[0]
        if isinstance(nome, bytes):
            nome = nome.decode(charset or "utf-8")

        # Obtém o conteúdo do PDF
        conteudo = part.get_payload(decode=True)
        if not conteudo:
            print(f"⚠️ Anexo vazio: {nome}")
            return None

        # Gera hash para verificar se é inédito
        hash_pdf = gerar_hash(conteudo)
        
        # Verifica se o PDF já foi processado
        path_pdf = os.path.join(settings.PDF_STORAGE_PATH, f"{hash_pdf}.pdf")
        if os.path.exists(path_pdf):
            print(f"📄 PDF já processado: {nome}")
            return None

        # Salva o PDF
        path_salvo = salvar_pdf(conteudo, hash_pdf)
        if not path_salvo:
            return None

        # Extrai dados do PDF
        try:
            from .pdf_parser import extrair_dados_fatura_pdf
        except ImportError:
            from pdf_parser import extrair_dados_fatura_pdf
            
        dados_extraidos = extrair_dados_fatura_pdf(path_salvo)
        
        if dados_extraidos:
            dados_extraidos['url_pdf'] = path_salvo
            print(f"✅ PDF processado com sucesso: {nome}")
            return dados_extraidos
        else:
            print(f"⚠️ Não foi possível extrair dados do PDF: {nome}")
            return None

    except Exception as e:
        print(f"❌ Erro ao processar anexo {nome_anexo}: {e}")
        return None

def buscar_e_processar_emails() -> List[Dict[str, Any]]:
    """
    Busca e-mails com anexos PDF, salva os inéditos e extrai os dados.
    
    Returns:
        Lista de dicionários com os dados de cada fatura processada
    """
    # Verifica se as credenciais estão configuradas
    if not settings.EMAIL_USER or not settings.EMAIL_PASS:
        print("❌ Credenciais de email não configuradas")
        return []
    
    # Conecta ao email
    mail = conectar_email()
    if not mail:
        return []

    try:
        print("🔍 Buscando emails...")
        
        # Busca todos os emails
        status, mensagens = mail.search(None, 'ALL')
        if status != 'OK':
            print("❌ Erro ao buscar emails")
            return []
            
        email_ids = mensagens[0].split()
        dados_faturas = []
        
        # Processa os últimos 10 emails para evitar sobrecarga
        emails_para_processar = reversed(email_ids[-10:])
        
        for eid in emails_para_processar:
            try:
                # Busca o email completo
                status, msg_data = mail.fetch(eid, "(RFC822)")
                if status != 'OK':
                    continue
                    
                msg = email.message_from_bytes(msg_data[0][1])
                
                # Processa anexos
                for part in msg.walk():
                    if part.get_content_type() == "application/pdf":
                        nome_anexo = part.get_filename()
                        if nome_anexo:
                            dados_fatura = processar_anexo_pdf(part, nome_anexo)
                            if dados_fatura:
                                dados_faturas.append(dados_fatura)
                
            except Exception as e:
                print(f"⚠️ Erro ao processar email {eid}: {e}")
                continue

        print(f"📊 Total de faturas processadas: {len(dados_faturas)}")
        return dados_faturas

    except Exception as e:
        print(f"❌ Erro ao processar emails: {e}")
        return []
    finally:
        try:
            mail.logout()
            print("🔒 Conexão com email encerrada")
        except:
            pass