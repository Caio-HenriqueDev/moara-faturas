#!/usr/bin/env python3
"""
Script de teste para verificar conexão com Gmail
"""
import os
import imaplib
from dotenv import load_dotenv

def test_gmail_connection():
    """Testa a conexão com Gmail usando as credenciais do .env"""
    
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    # Obtém as credenciais
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    email_host = os.getenv('EMAIL_HOST')
    email_port = int(os.getenv('EMAIL_PORT', 993))
    
    print("🔍 Testando conexão com Gmail...")
    print(f"📧 Email: {email_user}")
    print(f"🌐 Host: {email_host}")
    print(f"🔌 Porta: {email_port}")
    print(f"🔑 Senha: {email_pass[:4]}...{email_pass[-4:] if email_pass else 'N/A'}")
    print("-" * 50)
    
    try:
        # Conecta ao servidor IMAP
        print("📡 Conectando ao servidor IMAP...")
        mail = imaplib.IMAP4_SSL(email_host, email_port)
        
        # Faz login
        print("🔐 Fazendo login...")
        mail.login(email_user, email_pass)
        print("✅ Login realizado com sucesso!")
        
        # Lista as pastas de email
        print("📁 Listando pastas de email...")
        status, folders = mail.list()
        
        if status == 'OK':
            print("✅ Pastas encontradas:")
            for folder in folders[:5]:  # Mostra apenas as primeiras 5
                folder_name = folder.decode().split('"')[-2]
                print(f"   📂 {folder_name}")
            
            if len(folders) > 5:
                print(f"   ... e mais {len(folders) - 5} pastas")
        
        # Verifica a caixa de entrada
        print("\n📬 Verificando caixa de entrada...")
        mail.select('INBOX')
        status, messages = mail.search(None, 'ALL')
        
        if status == 'OK':
            email_count = len(messages[0].split())
            print(f"✅ Caixa de entrada: {email_count} emails encontrados")
        
        # Fecha a conexão
        mail.logout()
        print("\n🎉 Teste concluído com sucesso!")
        print("✅ Gmail configurado corretamente!")
        
    except imaplib.IMAP4.error as e:
        print(f"❌ Erro de autenticação IMAP: {e}")
        print("💡 Verifique se:")
        print("   - A verificação em 2 etapas está ativada")
        print("   - A senha de aplicativo está correta")
        print("   - O IMAP está ativado no Gmail")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        print("💡 Verifique se:")
        print("   - O arquivo .env está na raiz do projeto")
        print("   - Todas as variáveis estão configuradas")
        print("   - A conexão com a internet está funcionando")

if __name__ == "__main__":
    test_gmail_connection() 