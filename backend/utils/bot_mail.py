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
        print(f"🔌 Tentando conectar ao Gmail...")
        print(f"📧 Usuário: {settings.EMAIL_USER}")
        print(f"🌐 Host: {settings.EMAIL_HOST}")
        print(f"🔌 Porta: {settings.EMAIL_PORT}")
        
        if not settings.EMAIL_USER or not settings.EMAIL_PASS:
            print("❌ Credenciais de email não configuradas")
            print(f"EMAIL_USER: {'Configurado' if settings.EMAIL_USER else 'NÃO CONFIGURADO'}")
            print(f"EMAIL_PASS: {'Configurado' if settings.EMAIL_PASS else 'NÃO CONFIGURADO'}")
            return None
        
        print("🔐 Credenciais verificadas, tentando conexão IMAP...")
        
        # Tenta conexão IMAP
        mail = imaplib.IMAP4_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
        print("✅ Conexão IMAP estabelecida")
        
        # Tenta login
        print("🔑 Tentando login...")
        mail.login(settings.EMAIL_USER, settings.EMAIL_PASS)
        print("✅ Login realizado com sucesso")
        
        # Seleciona caixa de entrada
        print("📁 Selecionando caixa de entrada...")
        mail.select("inbox")
        print("✅ Caixa de entrada selecionada")
        
        print(f"🎉 Conectado ao email: {settings.EMAIL_USER}")
        return mail
        
    except imaplib.IMAP4.error as e:
        print(f"❌ Erro de autenticação IMAP: {e}")
        print("💡 Verifique se:")
        print("   - A senha de app está correta")
        print("   - A verificação em duas etapas está ativada")
        print("   - A senha de app foi gerada corretamente")
        return None
        
    except ConnectionRefusedError:
        print("❌ Conexão recusada pelo servidor")
        print("💡 Verifique se a porta 993 está correta")
        return None
        
    except Exception as e:
        print(f"❌ Erro inesperado ao conectar ao e-mail: {e}")
        import traceback
        traceback.print_exc()
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

def salvar_arquivo(conteudo: bytes, hash_arquivo: str, extensao: str = "pdf") -> Optional[str]:
    """
    Salva o arquivo no diretório de armazenamento.
    
    Args:
        conteudo: Conteúdo do arquivo em bytes
        hash_arquivo: Hash MD5 do arquivo
        extensao: Extensão do arquivo (pdf, png, jpg, etc.)
        
    Returns:
        Caminho do arquivo salvo ou None se falhar
    """
    try:
        # Cria diretório se não existir
        os.makedirs(settings.PDF_STORAGE_PATH, exist_ok=True)
        
        # Caminho completo do arquivo
        path_arquivo = os.path.join(settings.PDF_STORAGE_PATH, f"{hash_arquivo}.{extensao}")
        
        # Salva o arquivo
        with open(path_arquivo, "wb") as f:
            f.write(conteudo)
        
        print(f"✅ Arquivo salvo: {path_arquivo}")
        return path_arquivo
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")
        return None


def salvar_pdf(conteudo: bytes, hash_pdf: str) -> Optional[str]:
    """
    Salva o PDF no diretório de armazenamento.
    
    Args:
        conteudo: Conteúdo do PDF em bytes
        hash_pdf: Hash MD5 do arquivo
        
    Returns:
        Caminho do arquivo salvo ou None se falhar
    """
    return salvar_arquivo(conteudo, hash_pdf, "pdf")

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

def processar_anexo_imagem(part: Message, nome_anexo: str) -> Optional[Dict[str, Any]]:
    """
    Processa um anexo de imagem (PNG, JPG, JPEG) individual.
    
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

        # Obtém o conteúdo da imagem
        conteudo = part.get_payload(decode=True)
        if not conteudo:
            print(f"⚠️ Anexo vazio: {nome}")
            return None

        # Gera hash para verificar se é inédito
        hash_imagem = gerar_hash(conteudo)
        
        # Salva a imagem
        path_imagem = salvar_arquivo(conteudo, hash_imagem, nome_anexo.split('.')[-1]) # Salva com a extensão original
        if not path_imagem:
            return None

        # Extrai dados da fatura (assumindo que a imagem contém a fatura)
        # Para imagens, a lógica de extração de dados pode ser diferente
        # Por exemplo, pode ser necessário usar uma biblioteca de OCR
        # ou simplesmente retornar os dados da imagem
        
        # Usa a função de extração de dados de imagem
        from .pdf_parser import extrair_dados_imagem
        dados_fatura = extrair_dados_imagem(path_imagem)
        
        if dados_fatura:
            dados_fatura["url_pdf"] = path_imagem # Salva a URL da imagem como URL do PDF
            return dados_fatura
        else:
            print(f"⚠️ Falha ao extrair dados da imagem: {nome}")
            return None
        
    except Exception as e:
        print(f"❌ Erro ao processar anexo de imagem: {e}")
        return None

def buscar_e_processar_emails() -> List[Dict[str, Any]]:
    """
    Busca emails com anexos PDF e processa faturas automaticamente.
    
    Returns:
        Lista de faturas processadas
    """
    faturas_processadas = []
    
    try:
        print("🔌 Iniciando conexão com Gmail...")
        
        # Conecta ao email
        mail = conectar_email()
        if not mail:
            print("❌ Falha na conexão com Gmail")
            return faturas_processadas
        
        print("✅ Conectado ao Gmail com sucesso!")
        
        # Busca TODOS os emails (não apenas não lidos)
        print("🔍 Buscando emails na caixa de entrada...")
        status, messages = mail.search(None, "ALL")
        
        if status != "OK":
            print(f"❌ Erro ao buscar emails: {status}")
            return faturas_processadas
        
        email_ids = messages[0].split()
        print(f"📧 Encontrados {len(email_ids)} emails na caixa de entrada")
        
        # Processa apenas os últimos 50 emails para evitar sobrecarga
        emails_para_processar = email_ids[-50:] if len(email_ids) > 50 else email_ids
        print(f"📋 Processando os últimos {len(emails_para_processar)} emails")
        
        for email_id in emails_para_processar:
            try:
                print(f"📬 Processando email ID: {email_id}")
                
                # Busca o email específico
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                if status != "OK":
                    print(f"⚠️ Erro ao buscar email {email_id}: {status}")
                    continue
                
                # Parse do email
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Obtém informações do email
                subject = decode_header(msg["subject"])[0][0] if msg["subject"] else "Sem assunto"
                if isinstance(subject, bytes):
                    subject = subject.decode("utf-8", errors="ignore")
                
                from_addr = msg["from"] or "Remetente desconhecido"
                print(f"📧 Assunto: {subject}")
                print(f"👤 De: {from_addr}")
                
                # Verifica se tem anexos
                if msg.is_multipart():
                    print(f"📎 Email é multipart, verificando anexos...")
                    for part in msg.walk():
                        if part.get_content_maintype() == "multipart":
                            continue
                        if part.get("Content-Disposition") is None:
                            continue
                        
                        # Verifica se é PDF ou PNG
                        filename = part.get_filename()
                        if filename:
                            filename_lower = filename.lower()
                            print(f"📎 Anexo encontrado: {filename} (tipo: {part.get_content_type()})")
                            
                            if filename_lower.endswith(".pdf"):
                                print(f"📎 Processando anexo PDF: {filename}")
                                
                                # Processa o anexo PDF
                                dados_fatura = processar_anexo_pdf(part, filename)
                                if dados_fatura:
                                    print(f"✅ Fatura extraída: {dados_fatura.get('nome_cliente', 'N/A')}")
                                    faturas_processadas.append(dados_fatura)
                                else:
                                    print(f"⚠️ Falha ao extrair dados da fatura: {filename}")
                                    
                            elif filename_lower.endswith((".png", ".jpg", ".jpeg")):
                                print(f"📎 Processando anexo de imagem: {filename}")
                                
                                # Processa o anexo de imagem
                                dados_fatura = processar_anexo_imagem(part, filename)
                                if dados_fatura:
                                    print(f"✅ Fatura extraída da imagem: {dados_fatura.get('nome_cliente', 'N/A')}")
                                    faturas_processadas.append(dados_fatura)
                                else:
                                    print(f"⚠️ Falha ao extrair dados da imagem: {filename}")
                            else:
                                print(f"ℹ️ Anexo ignorado (formato não suportado): {filename}")
                        else:
                            print(f"ℹ️ Anexo sem nome ignorado")
                else:
                    print(f"ℹ️ Email não tem anexos")
                
                print(f"✅ Email {email_id} processado com sucesso")
                
            except Exception as e:
                print(f"❌ Erro ao processar email {email_id}: {e}")
                continue
        
        print(f"🎉 Processamento concluído: {len(faturas_processadas)} faturas extraídas")
        
    except Exception as e:
        print(f"❌ Erro geral no processamento de emails: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            if 'mail' in locals():
                mail.close()
                mail.logout()
                print("🔌 Conexão com Gmail fechada")
        except Exception as e:
            print(f"⚠️ Erro ao fechar conexão: {e}")
    
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