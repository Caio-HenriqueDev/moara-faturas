# 🚀 Deploy na Hostinger - Sistema de Gestão de Faturas

## 📋 **Pré-requisitos**

1. **Conta na Hostinger**: [hostinger.com](https://hostinger.com)
2. **Plano de hospedagem**: VPS ou Cloud Hosting (recomendado)
3. **Banco PostgreSQL**: Incluído nos planos VPS/Cloud
4. **Conta no Stripe**: Para processamento de pagamentos
5. **Conta Gmail**: Para processamento de e-mails

## 🏗️ **Estrutura do Projeto para Hostinger**

### **Arquivos Essenciais:**
```
buscador_de_faturas-main/
├── backend/
│   ├── main.py              # Aplicação FastAPI
│   ├── models.py            # Modelos SQLAlchemy
│   ├── crud.py              # Operações CRUD
│   ├── schemas.py           # Schemas Pydantic
│   ├── db_hostinger.py      # Configuração PostgreSQL Hostinger
│   ├── utils/
│   │   ├── bot_mail.py      # Automação de email
│   │   └── pdf_parser.py    # Processamento de PDFs
│   └── requirements_hostinger.txt # Dependências otimizadas
├── frontend/
│   ├── index.html           # Dashboard principal
│   ├── style.css            # Estilos
│   ├── app.js               # Lógica da aplicação
│   ├── config.js            # Configuração de ambientes
│   └── manifest.json        # Configuração PWA
├── start_hostinger.py       # Script de inicialização
├── gunicorn_config.py       # Configuração Gunicorn
└── HOSTINGER_DEPLOY.md      # Este arquivo
```

## 🔧 **Configuração do Ambiente**

### **1. Acessar o Painel da Hostinger**
1. Faça login em [hpanel.hostinger.com](https://hpanel.hostinger.com)
2. Selecione seu domínio/hosting
3. Vá para **Advanced** → **SSH Access**

### **2. Conectar via SSH**
```bash
ssh u123456789@seu-dominio.com -p 65002
```

### **3. Instalar Python e Dependências**
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.11 (mais estável)
sudo apt install python3.11 python3.11-venv python3.11-pip -y

# Instalar dependências do sistema
sudo apt install postgresql postgresql-contrib libpq-dev python3-dev build-essential -y

# Verificar versão
python3.11 --version
```

## 🗄️ **Configuração do Banco PostgreSQL**

### **1. Acessar PostgreSQL**
```bash
sudo -u postgres psql
```

### **2. Criar Banco e Usuário**
```sql
-- Criar usuário
CREATE USER moara_user WITH PASSWORD 'sua_senha_segura';

-- Criar banco
CREATE DATABASE moara_faturas OWNER moara_user;

-- Dar permissões
GRANT ALL PRIVILEGES ON DATABASE moara_faturas TO moara_user;

-- Sair
\q
```

### **3. Testar Conexão**
```bash
psql -h localhost -U moara_user -d moara_faturas
```

## 🚀 **Deploy do Backend**

### **1. Criar Diretório do Projeto**
```bash
mkdir -p ~/moara-faturas
cd ~/moara-faturas
```

### **2. Fazer Upload dos Arquivos**
```bash
# Via SCP (do seu computador local)
scp -P 65002 -r /caminho/para/buscador_de_faturas-main/* u123456789@seu-dominio.com:~/moara-faturas/

# Ou via Git
git clone https://github.com/Caio-HenriqueDev/moara.git
cd moara
```

### **3. Configurar Ambiente Virtual**
```bash
# Criar ambiente virtual
python3.11 -m venv venv

# Ativar ambiente
source venv/bin/activate

# Instalar dependências
pip install -r backend/requirements_hostinger.txt

# Verificar instalação
python -c "import fastapi; print('✅ FastAPI instalado')"
```

### **4. Configurar Variáveis de Ambiente**
```bash
# Criar arquivo .env
nano .env
```

**Conteúdo do .env:**
```bash
# Banco de dados Hostinger
DATABASE_URL=postgresql://moara_user:sua_senha_segura@localhost:5432/moara_faturas

# Stripe
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key_here
STRIPE_PUBLIC_KEY=pk_live_your_stripe_public_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Gmail
EMAIL_USER=seu_email@gmail.com
EMAIL_PASS=sua_senha_de_app_gmail
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993

# URLs do Frontend
FRONTEND_SUCCESS_URL=https://moara.app/success
FRONTEND_CANCEL_URL=https://moara.app.com/cancel

# Ambiente
ENVIRONMENT=production
```

### **5. Configurar Gunicorn**
```bash
# Instalar Gunicorn
pip install gunicorn

# Criar arquivo de configuração
nano gunicorn_config.py
```

**Conteúdo do gunicorn_config.py:**
```python
# Configuração Gunicorn para Hostinger
bind = "0.0.0.0:8000"
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

### **6. Criar Script de Inicialização**
```bash
nano start_hostinger.py
```

**Conteúdo do start_hostinger.py:**
```python
#!/usr/bin/env python3
"""
Script de Inicialização para Hostinger
Sistema de Gestão de Faturas - Moara Energia
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Iniciando Sistema na Hostinger...")
    
    # Verificar se estamos no diretório correto
    if not Path("backend/main.py").exists():
        print("❌ Erro: Execute este script na raiz do projeto")
        sys.exit(1)
    
    # Verificar variáveis de ambiente
    required_vars = ["DATABASE_URL", "STRIPE_SECRET_KEY", "EMAIL_USER"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Variáveis não configuradas: {missing_vars}")
        print("Configure-as no arquivo .env")
    
    # Iniciar com Gunicorn
    print("🔥 Iniciando com Gunicorn...")
    subprocess.run([
        "gunicorn", 
        "-c", "gunicorn_config.py",
        "backend.main:app"
    ])

if __name__ == "__main__":
    main()
```

### **7. Testar o Backend**
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Testar importação
python -c "from backend.main import app; print('✅ Backend funcionando')"

# Iniciar em modo teste
python start_hostinger.py
```

## 🌐 **Configuração do Frontend**

### **1. Configurar URLs no Frontend**
```bash
# Editar config.js
nano frontend/config.js
```

**Atualizar para:**
```javascript
const CONFIG = {
    // URLs da API para Hostinger
    API_BASE_URL: 'https://seu-dominio.com:8000', // ou IP do servidor
    
    // ... resto da configuração
};
```

### **2. Fazer Upload do Frontend**
```bash
# Copiar para diretório público
sudo cp -r frontend/* /home/u123456789/public_html/

# Ou configurar subdomínio específico
sudo mkdir -p /home/u123456789/public_html/api
sudo cp -r frontend/* /home/u123456789/public_html/api/
```

## 🔒 **Configuração de Segurança**

### **1. Firewall**
```bash
# Configurar UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # API (se necessário)
sudo ufw enable
```

### **2. SSL/HTTPS**
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Gerar certificado
sudo certbot --nginx -d seu-dominio.com
```

### **3. Proxy Reverso com Nginx**
```bash
# Instalar Nginx
sudo apt install nginx -y

# Configurar site
sudo nano /etc/nginx/sites-available/moara
```

**Configuração Nginx:**
```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;
    
    # Redirecionar para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com www.seu-dominio.com;
    
    # SSL
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    
    # Frontend
    location / {
        root /home/u123456789/public_html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # PWA
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### **4. Ativar Site**
```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/moara /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

## 🚀 **Inicialização Automática**

### **1. Criar Serviço Systemd**
```bash
sudo nano /etc/systemd/system/moara.service
```

**Conteúdo do serviço:**
```ini
[Unit]
Description=Moara Faturas API
After=network.target

[Service]
Type=simple
User=u123456789
WorkingDirectory=/home/u123456789/moara-faturas
Environment=PATH=/home/u123456789/moara-faturas/venv/bin
ExecStart=/home/u123456789/moara-faturas/venv/bin/gunicorn -c gunicorn_config.py backend.main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **2. Ativar Serviço**
```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Ativar serviço
sudo systemctl enable moara

# Iniciar serviço
sudo systemctl start moara

# Verificar status
sudo systemctl status moara
```

## 🔍 **Testes e Verificação**

### **1. Testar Backend**
```bash
# Health check
curl http://localhost:8000/health

# Endpoint principal
curl http://localhost:8000/

# Documentação
curl http://localhost:8000/docs
```

### **2. Testar Frontend**
```bash
# Acessar no navegador
https://seu-dominio.com

# Verificar console para erros
# Testar funcionalidades
```

### **3. Testar Integrações**
```bash
# Testar banco de dados
python -c "from backend.db_hostinger import get_db; print('✅ Banco OK')"

# Testar Stripe
python -c "import stripe; print('✅ Stripe OK')"

# Testar Gmail
python -c "from backend.utils.bot_mail import *; print('✅ Gmail OK')"
```

## 📊 **Monitoramento**

### **1. Logs do Sistema**
```bash
# Logs do serviço
sudo journalctl -u moara -f

# Logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs da aplicação
tail -f ~/moara-faturas/logs/app.log
```

### **2. Status dos Serviços**
```bash
# Verificar status
sudo systemctl status moara
sudo systemctl status nginx
sudo systemctl status postgresql

# Verificar portas
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

## 🐛 **Troubleshooting**

### **Problemas Comuns:**

#### **1. Erro de Conexão com Banco**
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Verificar conexão
psql -h localhost -U moara_user -d moara_faturas
```

#### **2. Erro de Porta em Uso**
```bash
# Verificar o que está usando a porta
sudo lsof -i :8000

# Matar processo se necessário
sudo kill -9 PID
```

#### **3. Erro de Permissões**
```bash
# Corrigir permissões
sudo chown -R u123456789:u123456789 ~/moara-faturas
chmod +x start_hostinger.py
```

## 📞 **Suporte e Links Úteis**

### **Documentação:**
- 🔗 [Hostinger Help Center](https://support.hostinger.com)
- 🔗 [FastAPI Docs](https://fastapi.tiangolo.com)
- 🔗 [Gunicorn Docs](https://docs.gunicorn.org)
- 🔗 [Nginx Docs](https://nginx.org/en/docs)

### **Comandos Úteis:**
```bash
# Reiniciar tudo
sudo systemctl restart moara nginx postgresql

# Ver logs em tempo real
sudo journalctl -u moara -f

# Verificar espaço em disco
df -h

# Verificar uso de memória
free -h

# Verificar processos Python
ps aux | grep python
```

---

## ✅ **Checklist de Deploy na Hostinger**

### **Pré-Deploy:**
- [ ] Conta Hostinger ativa
- [ ] Acesso SSH configurado
- [ ] Domínio configurado
- [ ] Banco PostgreSQL criado

### **Deploy Backend:**
- [ ] Arquivos enviados via SSH
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] Variáveis de ambiente configuradas
- [ ] Gunicorn configurado
- [ ] Serviço systemd criado

### **Deploy Frontend:**
- [ ] Arquivos copiados para public_html
- [ ] URLs configuradas corretamente
- [ ] Nginx configurado
- [ ] SSL configurado

### **Testes:**
- [ ] Backend respondendo
- [ ] Frontend carregando
- [ ] Banco conectando
- [ ] Stripe funcionando
- [ ] Gmail funcionando

---

**🎉 Projeto pronto para produção na Hostinger!**

**📅 Última atualização:** $(date)  
**🚀 Status:** Preparado para deploy  
**👨‍💻 Desenvolvedor:** Caio Henrique 