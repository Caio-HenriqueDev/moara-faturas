#!/usr/bin/env python3
"""
Script de Deploy Automatizado para Hostinger
Sistema de Gestão de Faturas - Moara Energia

Este script automatiza todo o processo de deploy na Hostinger
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
import getpass

class HostingerDeploy:
    def __init__(self):
        self.config = {
            "ssh_host": None,
            "ssh_user": None,
            "ssh_port": "65002",
            "domain": None,
            "project_path": "~/moara-faturas",
            "public_html": "~/public_html"
        }
        
    def print_banner(self):
        """Imprime o banner do sistema"""
        print("🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭")
        print("🏭 DEPLOY AUTOMATIZADO - HOSTINGER 🏭")
        print("🏭 SISTEMA DE GESTÃO DE FATURAS 🏭")
        print("🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭🏭")
        print("🚀 Deploy automatizado com um clique!")
        print()

    def get_deploy_config(self):
        """Obtém as configurações de deploy do usuário"""
        print("🔧 Configuração do Deploy")
        print("=" * 50)
        
        # SSH Host
        self.config["ssh_host"] = input("🌐 Host SSH (ex: seu-dominio.com): ").strip()
        if not self.config["ssh_host"]:
            print("❌ Host SSH é obrigatório!")
            sys.exit(1)
        
        # SSH User
        self.config["ssh_user"] = input("👤 Usuário SSH (ex: u123456789): ").strip()
        if not self.config["ssh_user"]:
            print("❌ Usuário SSH é obrigatório!")
            sys.exit(1)
        
        # SSH Port
        port = input(f"🔌 Porta SSH (padrão: {self.config['ssh_port']}): ").strip()
        if port:
            self.config["ssh_port"] = port
        
        # Domain
        self.config["domain"] = input("🌍 Domínio (ex: seu-dominio.com): ").strip()
        if not self.config["domain"]:
            self.config["domain"] = self.config["ssh_host"]
        
        # Project Path
        path = input(f"📁 Caminho do projeto (padrão: {self.config['project_path']}): ").strip()
        if path:
            self.config["project_path"] = path
        
        # Public HTML
        html_path = input(f"🌐 Caminho public_html (padrão: {self.config['public_html']}): ").strip()
        if html_path:
            self.config["public_html"] = html_path
        
        print("\n✅ Configuração salva!")
        return True

    def test_ssh_connection(self):
        """Testa a conexão SSH"""
        print("\n🔗 Testando conexão SSH...")
        
        try:
            cmd = [
                "ssh", "-p", self.config["ssh_port"],
                f"{self.config['ssh_user']}@{self.config['ssh_host']}",
                "echo '✅ Conexão SSH estabelecida'"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Conexão SSH funcionando!")
                return True
            else:
                print(f"❌ Erro na conexão SSH: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout na conexão SSH")
            return False
        except Exception as e:
            print(f"❌ Erro ao testar SSH: {e}")
            return False

    def create_remote_directories(self):
        """Cria diretórios remotos necessários"""
        print("\n📁 Criando diretórios remotos...")
        
        commands = [
            f"mkdir -p {self.config['project_path']}",
            f"mkdir -p {self.config['public_html']}/api",
            f"mkdir -p {self.config['project_path']}/logs",
            f"mkdir -p {self.config['project_path']}/uploads",
            f"mkdir -p {self.config['project_path']}/backups"
        ]
        
        for cmd in commands:
            try:
                ssh_cmd = [
                    "ssh", "-p", self.config["ssh_port"],
                    f"{self.config['ssh_user']}@{self.config['ssh_host']}",
                    cmd
                ]
                
                result = subprocess.run(ssh_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {cmd}")
                else:
                    print(f"⚠️  {cmd} - {result.stderr}")
                    
            except Exception as e:
                print(f"❌ Erro ao executar {cmd}: {e}")
        
        return True

    def install_remote_dependencies(self):
        """Instala dependências no servidor remoto"""
        print("\n📦 Instalando dependências no servidor...")
        
        commands = [
            "sudo apt update -y",
            "sudo apt install -y python3.11 python3.11-venv python3.11-pip",
            "sudo apt install -y postgresql postgresql-contrib libpq-dev python3-dev build-essential",
            "sudo apt install -y nginx certbot python3-certbot-nginx",
            "sudo apt install -y ufw"
        ]
        
        for cmd in commands:
            try:
                print(f"🔄 Executando: {cmd}")
                ssh_cmd = [
                    "ssh", "-p", self.config["ssh_port"],
                    f"{self.config['ssh_user']}@{self.config['ssh_host']}",
                    cmd
                ]
                
                result = subprocess.run(ssh_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {cmd}")
                else:
                    print(f"⚠️  {cmd} - {result.stderr}")
                    
            except Exception as e:
                print(f"❌ Erro ao executar {cmd}: {e}")
        
        return True

    def setup_postgresql(self):
        """Configura PostgreSQL no servidor"""
        print("\n🗄️  Configurando PostgreSQL...")
        
        # Gerar senha aleatória
        import secrets
        db_password = secrets.token_urlsafe(16)
        
        sql_commands = [
            f"CREATE USER moara_user WITH PASSWORD '{db_password}';",
            "CREATE DATABASE moara_faturas OWNER moara_user;",
            "GRANT ALL PRIVILEGES ON DATABASE moara_faturas TO moara_user;"
        ]
        
        for sql in sql_commands:
            try:
                cmd = f"sudo -u postgres psql -c \"{sql}\""
                ssh_cmd = [
                    "ssh", "-p", self.config["ssh_port"],
                    f"{self.config['ssh_user']}@{self.config['ssh_host']}",
                    cmd
                ]
                
                result = subprocess.run(ssh_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {sql}")
                else:
                    print(f"⚠️  {sql} - {result.stderr}")
                    
            except Exception as e:
                print(f"❌ Erro ao executar {sql}: {e}")
        
        # Salvar senha para o usuário
        print(f"\n🔑 Senha do banco gerada: {db_password}")
        print("💾 Salve esta senha para configurar no .env!")
        
        return db_password

    def upload_files(self):
        """Faz upload dos arquivos para o servidor"""
        print("\n📤 Fazendo upload dos arquivos...")
        
        try:
            # Comando SCP para upload
            scp_cmd = [
                "scp", "-P", self.config["ssh_port"], "-r",
                "backend/", "frontend/", "*.py", "*.md", "*.txt",
                f"{self.config['ssh_user']}@{self.config['ssh_host']}:{self.config['project_path']}/"
            ]
            
            print("🔄 Enviando arquivos...")
            result = subprocess.run(scp_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Arquivos enviados com sucesso!")
                return True
            else:
                print(f"❌ Erro no upload: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao fazer upload: {e}")
            return False

    def setup_python_environment(self):
        """Configura ambiente Python no servidor"""
        print("\n🐍 Configurando ambiente Python...")
        
        commands = [
            f"cd {self.config['project_path']}",
            "python3.11 -m venv venv",
            "source venv/bin/activate",
            "pip install --upgrade pip",
            "pip install -r backend/requirements_hostinger.txt",
            "pip install gunicorn"
        ]
        
        # Executar comandos em sequência
        full_command = " && ".join(commands)
        
        try:
            ssh_cmd = [
                "ssh", "-p", self.config["ssh_port"],
                f"{self.config['ssh_user']}@{self.config['ssh_host']}",
                full_command
            ]
            
            print("🔄 Configurando ambiente...")
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Ambiente Python configurado!")
                return True
            else:
                print(f"⚠️  Aviso: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao configurar Python: {e}")
            return False

    def create_env_file(self, db_password):
        """Cria arquivo .env no servidor"""
        print("\n🔧 Criando arquivo .env...")
        
        env_content = f"""# Configuração automática para Hostinger
DATABASE_URL=postgresql://moara_user:{db_password}@localhost:5432/moara_faturas
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key_here
STRIPE_PUBLIC_KEY=pk_live_your_stripe_public_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
EMAIL_USER=seu_email@gmail.com
EMAIL_PASS=sua_senha_de_app_gmail
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
FRONTEND_SUCCESS_URL=https://{self.config['domain']}/success
FRONTEND_CANCEL_URL=https://{self.config['domain']}/cancel
ENVIRONMENT=production
"""
        
        try:
            # Criar arquivo .env no servidor
            ssh_cmd = [
                "ssh", "-p", self.config["ssh_port"],
                f"{self.config['ssh_user']}@{self.config['ssh_host']}",
                f"cd {self.config['project_path']} && echo '{env_content}' > .env"
            ]
            
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Arquivo .env criado!")
                print("⚠️  IMPORTANTE: Configure as variáveis reais no arquivo .env!")
                return True
            else:
                print(f"❌ Erro ao criar .env: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao criar .env: {e}")
            return False

    def setup_nginx(self):
        """Configura Nginx no servidor"""
        print("\n🌐 Configurando Nginx...")
        
        nginx_config = f"""server {{
    listen 80;
    server_name {self.config['domain']} www.{self.config['domain']};
    
    # Frontend
    location / {{
        root {self.config['public_html']};
        index index.html;
        try_files $uri $uri/ /index.html;
    }}
    
    # API Backend
    location /api/ {{
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # PWA
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}
"""
        
        try:
            # Criar configuração Nginx
            ssh_cmd = [
                "ssh", "-p", self.config["ssh_port"],
                f"{self.config['ssh_user']}@{self.config['ssh_host']}",
                f"echo '{nginx_config}' | sudo tee /etc/nginx/sites-available/moara"
            ]
            
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Configuração Nginx criada!")
                
                # Ativar site
                activate_cmd = [
                    "ssh", "-p", self.config["ssh_port"],
                    f"{self.config['ssh_user']}@{self.config['ssh_host']}",
                    "sudo ln -sf /etc/nginx/sites-available/moara /etc/nginx/sites-enabled/ && sudo nginx -t && sudo systemctl restart nginx"
                ]
                
                result = subprocess.run(activate_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Nginx configurado e ativo!")
                    return True
                else:
                    print(f"⚠️  Aviso Nginx: {result.stderr}")
                    return False
            else:
                print(f"❌ Erro ao configurar Nginx: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao configurar Nginx: {e}")
            return False

    def setup_systemd_service(self):
        """Configura serviço systemd"""
        print("\n⚙️  Configurando serviço systemd...")
        
        service_content = f"""[Unit]
Description=Moara Faturas API
After=network.target postgresql.service

[Service]
Type=simple
User={self.config['ssh_user']}
WorkingDirectory={self.config['project_path']}
Environment=PATH={self.config['project_path']}/venv/bin
ExecStart={self.config['project_path']}/venv/bin/gunicorn -c gunicorn_config.py backend.main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        try:
            # Criar serviço systemd
            ssh_cmd = [
                "ssh", "-p", self.config["ssh_port"],
                f"{self.config['ssh_user']}@{self.config['ssh_host']}",
                f"echo '{service_content}' | sudo tee /etc/systemd/system/moara.service"
            ]
            
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Serviço systemd criado!")
                
                # Ativar serviço
                activate_cmd = [
                    "ssh", "-p", self.config["ssh_port"],
                    f"{self.config['ssh_user']}@{self.config['ssh_host']}",
                    "sudo systemctl daemon-reload && sudo systemctl enable moara && sudo systemctl start moara"
                ]
                
                result = subprocess.run(activate_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Serviço ativado e iniciado!")
                    return True
                else:
                    print(f"⚠️  Aviso serviço: {result.stderr}")
                    return False
            else:
                print(f"❌ Erro ao criar serviço: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao configurar serviço: {e}")
            return False

    def setup_ssl(self):
        """Configura SSL com Let's Encrypt"""
        print("\n🔒 Configurando SSL...")
        
        try:
            ssl_cmd = [
                "ssh", "-p", self.config["ssh_port"],
                f"{self.config['ssh_user']}@{self.config['ssh_host']}",
                f"sudo certbot --nginx -d {self.config['domain']} --non-interactive --agree-tos --email admin@{self.config['domain']}"
            ]
            
            print("🔄 Gerando certificado SSL...")
            result = subprocess.run(ssl_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ SSL configurado com sucesso!")
                return True
            else:
                print(f"⚠️  Aviso SSL: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao configurar SSL: {e}")
            return False

    def copy_frontend(self):
        """Copia frontend para public_html"""
        print("\n📱 Copiando frontend...")
        
        try:
            copy_cmd = [
                "ssh", "-p", self.config["ssh_port"],
                f"{self.config['ssh_user']}@{self.config['ssh_host']}",
                f"cp -r {self.config['project_path']}/frontend/* {self.config['public_html']}/"
            ]
            
            result = subprocess.run(copy_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Frontend copiado!")
                return True
            else:
                print(f"❌ Erro ao copiar frontend: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao copiar frontend: {e}")
            return False

    def test_deployment(self):
        """Testa o deploy"""
        print("\n🧪 Testando deploy...")
        
        tests = [
            ("Health Check", f"curl -s http://localhost:8000/health"),
            ("Frontend", f"curl -s http://localhost:8000/"),
            ("Nginx", f"curl -s http://localhost/"),
            ("SSL", f"curl -s https://{self.config['domain']}/")
        ]
        
        for test_name, test_cmd in tests:
            try:
                ssh_cmd = [
                    "ssh", "-p", self.config["ssh_port"],
                    f"{self.config['ssh_user']}@{self.config['ssh_host']}",
                    test_cmd
                ]
                
                result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    print(f"✅ {test_name}: OK")
                else:
                    print(f"⚠️  {test_name}: Não respondeu")
                    
            except Exception as e:
                print(f"❌ {test_name}: Erro - {e}")
        
        return True

    def show_final_info(self, db_password):
        """Mostra informações finais"""
        print("\n" + "="*60)
        print("🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
        print("="*60)
        
        print(f"\n🌐 URLs do Sistema:")
        print(f"   Frontend: https://{self.config['domain']}")
        print(f"   API: https://{self.config['domain']}/api/")
        print(f"   Health: https://{self.config['domain']}/api/health")
        print(f"   Docs: https://{self.config['domain']}/api/docs")
        
        print(f"\n🔑 Credenciais:")
        print(f"   Banco: moara_user / {db_password}")
        print(f"   Host: localhost:5432")
        print(f"   Database: moara_faturas")
        
        print(f"\n📁 Diretórios:")
        print(f"   Projeto: {self.config['project_path']}")
        print(f"   Frontend: {self.config['public_html']}")
        print(f"   Logs: {self.config['project_path']}/logs")
        
        print(f"\n⚙️  Serviços:")
        print(f"   Backend: sudo systemctl status moara")
        print(f"   Nginx: sudo systemctl status nginx")
        print(f"   PostgreSQL: sudo systemctl status postgresql")
        
        print(f"\n🔧 Comandos Úteis:")
        print(f"   Ver logs: sudo journalctl -u moara -f")
        print(f"   Reiniciar: sudo systemctl restart moara")
        print(f"   Verificar: curl https://{self.config['domain']}/api/health")
        
        print(f"\n⚠️  IMPORTANTE:")
        print(f"   1. Configure as variáveis reais no arquivo .env")
        print(f"   2. Configure o Stripe com suas chaves")
        print(f"   3. Configure o Gmail com senha de app")
        print(f"   4. Teste todos os endpoints")
        
        print(f"\n📚 Documentação:")
        print(f"   HOSTINGER_DEPLOY.md - Guia completo")
        print(f"   Logs do sistema para troubleshooting")
        
        print("\n🚀 Sistema pronto para uso!")

    def run_deploy(self):
        """Executa o deploy completo"""
        try:
            self.print_banner()
            
            # Obter configurações
            if not self.get_deploy_config():
                return False
            
            # Testar conexão SSH
            if not self.test_ssh_connection():
                print("❌ Falha na conexão SSH. Verifique as credenciais.")
                return False
            
            # Executar etapas do deploy
            steps = [
                ("Criando diretórios", self.create_remote_directories),
                ("Instalando dependências", self.install_remote_dependencies),
                ("Configurando PostgreSQL", self.setup_postgresql),
                ("Fazendo upload dos arquivos", self.upload_files),
                ("Configurando Python", self.setup_python_environment),
                ("Configurando Nginx", self.setup_nginx),
                ("Configurando serviço", self.setup_systemd_service),
                ("Copiando frontend", self.copy_frontend),
                ("Configurando SSL", self.setup_ssl),
                ("Testando deploy", self.test_deployment)
            ]
            
            db_password = None
            
            for step_name, step_func in steps:
                print(f"\n{'='*50}")
                print(f"🔄 {step_name}...")
                print(f"{'='*50}")
                
                if step_name == "Configurando PostgreSQL":
                    db_password = step_func()
                else:
                    step_func()
                
                time.sleep(2)  # Pausa entre etapas
            
            # Mostrar informações finais
            if db_password:
                self.show_final_info(db_password)
            else:
                self.show_final_info("N/A")
            
            return True
            
        except KeyboardInterrupt:
            print("\n⚠️  Deploy interrompido pelo usuário")
            return False
        except Exception as e:
            print(f"\n❌ Erro durante deploy: {e}")
            return False

def main():
    """Função principal"""
    deployer = HostingerDeploy()
    
    if deployer.run_deploy():
        print("\n🎉 Deploy concluído com sucesso!")
        sys.exit(0)
    else:
        print("\n❌ Deploy falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main() 