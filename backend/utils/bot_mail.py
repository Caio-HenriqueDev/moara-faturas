"""
Automação de email para o Sistema de Gestão de Faturas
Busca emails com anexos PDF e processa faturas automaticamente
BASEADO NO SISTEMA FUNCIONAL
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
    BASEADO NO SISTEMA FUNCIONAL
    """
    try:
        print(f"🔌 Conectando ao Gmail...")
        print(f"📧 Usuário: {settings.EMAIL_USER}")
        print(f"🌐 Host: {settings.EMAIL_HOST}")
        print(f"🔌 Porta: {settings.EMAIL_PORT}")
        
        if not settings.EMAIL_USER or not settings.EMAIL_PASS:
            print("❌ Credenciais de email não configuradas")
            return None
        
        # Conecta usando a lógica que funciona
        mail = imaplib.IMAP4_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
        mail.login(settings.EMAIL_USER, settings.EMAIL_PASS)
        mail.select("inbox")
        
        print("✅ Conectado ao Gmail com sucesso!")
        return mail
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao e-mail: {e}")
        import traceback
        traceback.print_exc()
        return None

def gerar_hash(conteudo_bytes: bytes) -> str:
    """
    Gera um hash MD5 do conteúdo para verificar se o arquivo é inédito.
    """
    return md5(conteudo_bytes).hexdigest()

def buscar_e_processar_emails() -> List[Dict[str, Any]]:
    """
    Busca emails com anexos PDF e processa faturas automaticamente.
    BASEADO NO SISTEMA FUNCIONAL
    """
    print("🚀 Iniciando processamento de emails...")
    
    # Conecta ao email
    mail = conectar_email()
    if not mail:
        print("❌ Falha na conexão com Gmail")
        return []
    
    try:
        # Busca TODOS os emails (lógica que funciona)
        print("🔍 Buscando emails na caixa de entrada...")
        status, mensagens = mail.search(None, 'ALL')
        
        if status != "OK":
            print(f"❌ Erro ao buscar emails: {status}")
            return []
        
        email_ids = mensagens[0].split()
        print(f"📧 Encontrados {len(email_ids)} emails na caixa de entrada")
        
        # Processa apenas os últimos 10 emails (lógica que funciona)
        emails_para_processar = reversed(email_ids[-10:])
        print(f"📋 Processando os últimos 10 emails")
        
        dados_faturas = []
        
        for eid in emails_para_processar:
            try:
                print(f"📬 Processando email ID: {eid}")
                
                # Busca o email específico
                _, msg_data = mail.fetch(eid, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                
                # Obtém informações do email
                subject = decode_header(msg["subject"])[0][0] if msg["subject"] else "Sem assunto"
                if isinstance(subject, bytes):
                    subject = subject.decode("utf-8", errors="ignore")
                
                from_addr = msg["from"] or "Remetente desconhecido"
                print(f"📧 Assunto: {subject}")
                print(f"👤 De: {from_addr}")
                
                # Processa anexos PDF (lógica que funciona)
                for part in msg.walk():
                    if part.get_content_type() == "application/pdf":
                        nome_anexo = part.get_filename()
                        if nome_anexo:
                            # Decodifica o nome do arquivo
                            nome, charset = decode_header(nome_anexo)[0]
                            if isinstance(nome, bytes):
                                nome = nome.decode(charset or "utf-8")
                            
                            print(f"📎 Anexo PDF encontrado: {nome}")
                            
                            # Obtém o conteúdo do PDF
                            conteudo = part.get_payload(decode=True)
                            hash_pdf = gerar_hash(conteudo)
                            
                            # Cria diretório se não existir
                            os.makedirs(settings.PDF_STORAGE_PATH, exist_ok=True)
                            
                            # Caminho completo do arquivo
                            path_pdf = os.path.join(settings.PDF_STORAGE_PATH, f"{hash_pdf}.pdf")
                            
                            # Verificação se o PDF é inédito
                            if not os.path.exists(path_pdf):
                                print(f"💾 Salvando PDF inédito: {nome}")
                                
                                # Salva o PDF
                                with open(path_pdf, "wb") as f:
                                    f.write(conteudo)
                                
                                # Chama a função de extração do pdf_parser.py
                                from .pdf_parser import extrair_dados_fatura_pdf
                                dados_extraidos = extrair_dados_fatura_pdf(path_pdf)
                                
                                if dados_extraidos:
                                    dados_extraidos['url_pdf'] = path_pdf
                                    dados_faturas.append(dados_extraidos)
                                    print(f"✅ Fatura extraída: {dados_extraidos.get('nome_cliente', 'N/A')}")
                                    print(f"   📊 Dados: {dados_extraidos}")
                                else:
                                    print(f"⚠️ Falha ao extrair dados da fatura: {nome}")
                            else:
                                print(f"ℹ️ PDF já processado: {nome}")
                
                print("-" * 60)
                
            except Exception as e:
                print(f"❌ Erro ao processar email {eid}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print("=" * 80)
        print(f"🎯 PROCESSAMENTO CONCLUÍDO")
        print(f"📊 Total de faturas processadas: {len(dados_faturas)}")
        print("=" * 80)
        
        return dados_faturas
        
    except Exception as e:
        print(f"❌ Erro geral no processamento: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    finally:
        try:
            mail.logout()
            print("🔌 Conexão com Gmail fechada")
        except:
            pass

if __name__ == "__main__":
    # Teste da funcionalidade
    print("🧪 Testando automação de email...")
    faturas = buscar_e_processar_emails()
    print(f"📊 Total de faturas processadas: {len(faturas)}")