# 🏭 Sistema de Gestão de Faturas - Moara Energia

Sistema completo para automação de processamento de faturas de energia elétrica, desenvolvido com FastAPI, React e integração com Stripe.

## 🚀 **Deploy na Vercel**

### **Deploy Automático**
```bash
# Clone o repositório
git clone https://github.com/Caio-HenriqueDev/moara.git
cd moara

# Execute o script de deploy
python3 deploy_vercel.py
```

### **Deploy Manual**
```bash
# Instale o Vercel CLI
npm i -g vercel

# Login na Vercel
vercel login

# Deploy
vercel --prod
```

## 🔧 **Configuração de Variáveis de Ambiente**

### **1. Banco de Dados (PostgreSQL)**
```bash
DATABASE_URL=postgresql://username:password@host:port/database
```

**Provedores Recomendados:**
- 🟢 **Neon**: https://neon.tech (Gratuito)
- 🟢 **Supabase**: https://supabase.com (Gratuito)
- 🟢 **Railway**: https://railway.app

### **2. Stripe (Pagamentos)**
```bash
STRIPE_SECRET_KEY=sk_test_... ou sk_live_...
STRIPE_PUBLIC_KEY=pk_test_... ou pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### **3. Email (Gmail)**
```bash
EMAIL_USER=seu_email@gmail.com
EMAIL_PASS=sua_senha_de_app_gmail
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
```

### **4. URLs do Frontend**
```bash
FRONTEND_SUCCESS_URL=https://seu-dominio.vercel.app/success
FRONTEND_CANCEL_URL=https://seu-dominio.vercel.app/cancel
```

## 🏃‍♂️ **Desenvolvimento Local**

### **1. Configuração do Ambiente**
```bash
# Crie um ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r backend/requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

### **2. Inicialização do Sistema**
```bash
# Inicialização automática
python3 start_system.py

# Ou manualmente:
# Terminal 1 - Backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && python3 -m http.server 3000
```

## 📱 **Acessos**

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🏗️ **Arquitetura**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Banco de      │
│   (PWA)         │◄──►│   (FastAPI)     │◄──►│   Dados         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Stripe        │    │   Gmail IMAP    │    │   Sistema de    │
│   (Pagamentos)  │    │   (Emails)      │    │   Arquivos      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔒 **Segurança**

- ✅ CORS configurado
- ✅ Headers de segurança
- ✅ Validação de entrada com Pydantic
- ✅ Autenticação de webhooks Stripe
- ✅ Variáveis de ambiente criptografadas

## 📊 **Funcionalidades**

- 🔍 **Processamento Automático de Emails**
- 📄 **Extração de Dados de PDFs**
- 💳 **Integração com Stripe**
- 📱 **Interface PWA Responsiva**
- 📊 **Dashboard com Estatísticas**
- 🔄 **Sincronização em Tempo Real**

## 🧪 **Testes**

### **Teste de Conectividade**
```bash
# Health Check
curl http://localhost:8000/health

# Listar Faturas
curl http://localhost:8000/faturas/

# Documentação
open http://localhost:8000/docs
```

### **Teste de Produção**
```bash
# Build local
npm run build

# Teste de produção
npm start
```

## 🐛 **Troubleshooting**

### **Erro 500 na Vercel**
1. Verifique as variáveis de ambiente
2. Confirme a DATABASE_URL
3. Verifique os logs da Vercel
4. Teste localmente primeiro

### **Problemas de Import**
1. Verifique a estrutura de pastas
2. Confirme os arquivos `__init__.py`
3. Use imports relativos (`.`)

## 📚 **Documentação**

- **API Docs**: `/docs` (Swagger UI)
- **ReDoc**: `/redoc`
- **Especificações**: `ESPECIFICACOES_TECNICAS.md`
- **Deploy Vercel**: `VERCEL_DEPLOY_COMPLETO.md`

## 🤝 **Contribuição**

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**🚀 Projeto pronto para produção na Vercel!**

Para suporte, abra uma issue no GitHub ou consulte a documentação da API.
