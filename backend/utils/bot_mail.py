# USINA_CLIENTE/backend/utils/bot_mail.py
import imaplib
import email
import os
from email.header import decode_header
from hashlib import md5
from dotenv import load_dotenv
from .pdf_parser import extrair_dados_fatura_pdf # Importa a função de extração

# Carrega as variáveis do arquivo .env
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
IMAP_SERVER = os.getenv("EMAIL_HOST", "imap.gmail.com")
IMAP_PORT = int(os.getenv("EMAIL_PORT", "993"))

PASTA_DESTINO = "data/sample_emails"
os.makedirs(PASTA_DESTINO, exist_ok=True)

def conectar_email():
    """Conecta ao servidor IMAP e retorna a conexão."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        return mail
    except Exception as e:
        print(f"Erro ao conectar ao e-mail: {e}")
        return None

def gerar_hash(conteudo_bytes):
    """Gera um hash MD5 do conteúdo para verificar se o arquivo é inédito."""
    return md5(conteudo_bytes).hexdigest()

def buscar_e_processar_emails():
    """
    Busca e-mails com anexos PDF, salva os inéditos e extrai os dados.
    Retorna uma lista de dicionários com os dados de cada fatura.
    """
    mail = conectar_email()
    if not mail:
        return []

    status, mensagens = mail.search(None, 'ALL')
    email_ids = mensagens[0].split()
    dados_faturas = []

    # Iterar sobre os últimos 10 e-mails para teste.
    # Em produção, você pode usar uma lógica mais robusta.
    for eid in reversed(email_ids[-10:]):
        _, msg_data = mail.fetch(eid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        for part in msg.walk():
            if part.get_content_type() == "application/pdf":
                nome_anexo = part.get_filename()
                if nome_anexo:
                    nome, charset = decode_header(nome_anexo)[0]
                    if isinstance(nome, bytes):
                        nome = nome.decode(charset or "utf-8")

                    conteudo = part.get_payload(decode=True)
                    hash_pdf = gerar_hash(conteudo)

                    path_pdf = os.path.join(PASTA_DESTINO, f"{hash_pdf}.pdf")

                    # Verificação se o PDF é inédito
                    if not os.path.exists(path_pdf):
                        with open(path_pdf, "wb") as f:
                            f.write(conteudo)
                        
                        # Chama a função de extração do pdf_parser.py
                        dados_extraidos = extrair_dados_fatura_pdf(path_pdf)
                        if dados_extraidos:
                            dados_extraidos['url_pdf'] = path_pdf # Adiciona o caminho do arquivo
                            dados_faturas.append(dados_extraidos)
                            print(f"PDF inédito processado: {nome}")
                    else:
                        print(f"PDF já processado: {nome}")

    mail.logout()
    return dados_faturas