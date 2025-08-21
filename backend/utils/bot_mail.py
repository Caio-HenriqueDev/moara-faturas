"""
Automação de email para o Sistema de Gestão de Faturas
Busca emails com anexos PDF e processa faturas automaticamente
"""

import imaplib
import email
import os
from email.header import decode_header
from email.message import Message
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

def processar_anexo_pdf(part: Message, nome_anexo: str) -> Optional[Dict[str, Any]]:
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
        
        # Salva o PDF
        path_pdf = salvar_pdf(conteudo, hash_pdf)
        if not path_pdf:
            return None

        # Extrai dados da fatura
        from .pdf_parser import extrair_dados_fatura_pdf
        dados_fatura = extrair_dados_fatura_pdf(path_pdf)
        
        if dados_fatura:
            dados_fatura["url_pdf"] = path_pdf
            print(f"✅ Dados extraídos da fatura: {nome}")
            return dados_fatura
        else:
            print(f"⚠️ Não foi possível extrair dados da fatura: {nome}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao processar anexo PDF: {e}")
        return None

def buscar_e_processar_emails() -> List[Dict[str, Any]]:
    """
    Busca emails com anexos PDF e processa faturas automaticamente.
    
    Returns:
        Lista de faturas processadas
    """
    faturas_processadas = []
    
    try:
        # Conecta ao email
        mail = conectar_email()
        if not mail:
            return faturas_processadas
        
        # Busca emails não lidos
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            print("❌ Erro ao buscar emails")
            return faturas_processadas
        
        email_ids = messages[0].split()
        print(f"📧 Encontrados {len(email_ids)} emails não lidos")
        
        for email_id in email_ids:
            try:
                # Busca o email específico
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                if status != "OK":
                    continue
                
                # Parse do email
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Verifica se tem anexos
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_maintype() == "multipart":
                            continue
                        if part.get("Content-Disposition") is None:
                            continue
                        
                        # Verifica se é PDF
                        filename = part.get_filename()
                        if filename and filename.lower().endswith(".pdf"):
                            print(f"📎 Processando anexo PDF: {filename}")
                            
                            # Processa o anexo
                            dados_fatura = processar_anexo_pdf(part, filename)
                            if dados_fatura:
                                faturas_processadas.append(dados_fatura)
                
                # Marca como lido
                mail.store(email_id, "+FLAGS", "\\Seen")
                
            except Exception as e:
                print(f"❌ Erro ao processar email {email_id}: {e}")
                continue
        
        print(f"✅ Processamento concluído: {len(faturas_processadas)} faturas extraídas")
        
    except Exception as e:
        print(f"❌ Erro geral no processamento de emails: {e}")
    
    finally:
        try:
            if 'mail' in locals():
                mail.close()
                mail.logout()
        except:
            pass
    
    return faturas_processadas

def processar_email_especifico(email_id: str) -> Optional[Dict[str, Any]]:
    """
    Processa um email específico por ID.
    
    Args:
        email_id: ID do email a ser processado
        
    Returns:
        Dados da fatura processada ou None se falhar
    """
    try:
        # Conecta ao email
        mail = conectar_email()
        if not mail:
            return None
        
        # Busca o email específico
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status != "OK":
            print(f"❌ Erro ao buscar email {email_id}")
            return None
        
        # Parse do email
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        # Verifica se tem anexos PDF
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                if part.get("Content-Disposition") is None:
                    continue
                
                # Verifica se é PDF
                filename = part.get_filename()
                if filename and filename.lower().endswith(".pdf"):
                    print(f"📎 Processando anexo PDF: {filename}")
                    
                    # Processa o anexo
                    dados_fatura = processar_anexo_pdf(part, filename)
                    if dados_fatura:
                        return dados_fatura
        
        print(f"⚠️ Email {email_id} não contém anexos PDF válidos")
        return None
        
    except Exception as e:
        print(f"❌ Erro ao processar email {email_id}: {e}")
        return None
    
    finally:
        try:
            if 'mail' in locals():
                mail.close()
                mail.logout()
        except:
            pass

if __name__ == "__main__":
    # Teste da funcionalidade
    print("🧪 Testando automação de email...")
    faturas = buscar_e_processar_emails()
    print(f"📊 Total de faturas processadas: {len(faturas)}")