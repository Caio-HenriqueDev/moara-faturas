# 🚀 Deploy Completo na Vercel - Sistema de Gestão de Faturas Moara

## 📊 **Informações do Deploy Atual**

### **🌐 URLs do Projeto:**
- **URL Principal**: https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app
- **Dashboard Vercel**: https://vercel.com/diretoriamoovestudio-5505s-projects/moara
- **Inspect Deploy**: https://vercel.com/diretoriamoovestudio-5505s-projects/moara/5cymmKpWBPHJSL2HLaFHC3DFEp8x

### **👤 Dados da Conta:**
- **Email**: diretoriamoovestudio@gmail.com
- **Scope**: diretoriamoovestudio-5505s-projects
- **Projeto**: moara

---

## 🔧 **Configuração de Variáveis de Ambiente**

### **Acesso ao Dashboard:**
1. 🔗 [Vercel Dashboard](https://vercel.com/dashboard)
2. Selecione o projeto: **moara**
3. Clique em: **Settings** → **Environment Variables**

### **📋 Variáveis Obrigatórias:**

#### **1. DATABASE_URL (PostgreSQL)**
```
Name: DATABASE_URL
Value: postgresql://username:password@host:port/database
Environment: Production, Preview, Development
Encrypt: ✅ Sim
```

**Provedores Recomendados:**
- 🟢 **Neon**: https://neon.tech (Gratuito)
- 🟢 **Supabase**: https://supabase.com (Gratuito)
- 🟢 **Railway**: https://railway.app
- 🟢 **PlanetScale**: https://planetscale.com

**Exemplo de URL:**
```
postgresql://usuario:senha@ep-cool-lab-123456.us-east-1.aws.neon.tech/neondb?sslmode=require
```

#### **2. STRIPE_SECRET_KEY**
```
Name: STRIPE_SECRET_KEY
Value: sk_live_... ou sk_test_...
Environment: Production, Preview, Development
Encrypt: ✅ Sim
```

**Como obter:**
1. 🔗 [Stripe Dashboard](https://dashboard.stripe.com)
2. **Developers** → **API keys**
3. Copie a **Secret key**

#### **3. STRIPE_PUBLIC_KEY**
```
Name: STRIPE_PUBLIC_KEY
Value: pk_live_... ou pk_test_...
Environment: Production, Preview, Development
Encrypt: ❌ Não
```

#### **4. STRIPE_WEBHOOK_SECRET**
```
Name: STRIPE_WEBHOOK_SECRET
Value: whsec_...
Environment: Production, Preview, Development
Encrypt: ✅ Sim
```

**Como configurar:**
1. No Stripe: **Developers** → **Webhooks**
2. **Add endpoint**: `https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app/stripe-webhook/`
3. **Events**: `checkout.session.completed`
4. Copie o **Signing secret**

#### **5. EMAIL_USER**
```
Name: EMAIL_USER
Value: seu_email@gmail.com
Environment: Production, Preview, Development
Encrypt: ❌ Não
```

#### **6. EMAIL_PASS**
```
Name: EMAIL_PASS
Value: senha_de_app_gmail_16_caracteres
Environment: Production, Preview, Development
Encrypt: ✅ Sim
```

**Como obter senha de app:**
1. 🔗 [Google Account](https://myaccount.google.com)
2. **Security** → **2-Step Verification** (ativar)
3. **Security** → **App passwords**
4. **Select app**: Mail
5. **Device**: Custom name → "Moara Faturas"
6. Copie a senha gerada

#### **7. URLs do Frontend**
```
Name: FRONTEND_SUCCESS_URL
Value: https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app/success
Environment: Production, Preview, Development
Encrypt: ❌ Não

Name: FRONTEND_CANCEL_URL
Value: https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app/cancel
Environment: Production, Preview, Development
Encrypt: ❌ Não
```

---

## 🔌 **Endpoints da API**

### **Base URL:**
```
https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app
```

### **Endpoints Disponíveis:**

| Método | Endpoint | Descrição | Exemplo |
|--------|----------|-----------|---------|
| `GET` | `/` | Info do sistema | `curl https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app/` |
| `GET` | `/health` | Health check | `curl https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app/health` |
| `GET` | `/docs` | Documentação Swagger | https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app/docs |
| `GET` | `/redoc` | Documentação ReDoc | https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app/redoc |
| `POST` | `/processar_email/` | Processar emails | API |
| `GET` | `/faturas/` | Listar faturas | API |
| `POST` | `/create-checkout-session/{id}` | Criar pagamento | API |
| `POST` | `/stripe-webhook/` | Webhook Stripe | Stripe apenas |

---

## 🛠️ **Configuração de Serviços Externos**

### **1. Banco PostgreSQL (Neon - Recomendado)**

#### **Criar conta e projeto:**
1. 🔗 [Neon](https://neon.tech)
2. **Sign up** com GitHub/Google
3. **Create project**
4. **Copie a connection string**

#### **Exemplo de configuração:**
```sql
-- Criar tabelas será feito automaticamente pelo sistema
-- URL exemplo:
postgresql://username:password@ep-cool-lab-123456.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### **2. Stripe (Pagamentos)**

#### **Configuração:**
1. 🔗 [Stripe](https://stripe.com)
2. **Create account**
3. **Developers** → **API keys**
4. **Webhooks** → **Add endpoint**

#### **Webhook URL:**
```
https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app/stripe-webhook/
```

#### **Events to send:**
- `checkout.session.completed`

### **3. Gmail (Processamento de E-mails)**

#### **Configuração IMAP:**
```
HOST: imap.gmail.com
PORT: 993
SSL: Enabled
```

#### **Configurar App Password:**
1. Ativar 2FA no Google
2. Gerar senha de aplicativo
3. Usar a senha de 16 caracteres

---

## 🚀 **Comandos de Deploy**

### **Deploy Automático (Script):**
```bash
python3 deploy_vercel.py
```

### **Deploy Manual:**
```bash
# Instalar CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

### **Redeploy após configurar variáveis:**
```bash
vercel --prod --force
```

---

## 🔍 **Testes e Verificação**

### **1. Testar Health Check:**
```bash
curl https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app/health
```

**Resposta esperada (após configurar variáveis):**
```json
{
  "status": "healthy",
  "environment": "production",
  "services": {
    "database": "ok",
    "stripe": "ok",
    "email": "ok"
  }
}
```

### **2. Testar Endpoint Principal:**
```bash
curl https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app/
```

### **3. Acessar Documentação:**
- **Swagger**: https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app/docs
- **ReDoc**: https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app/redoc

---

## 📱 **Frontend**

### **URLs:**
- **Principal**: https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app
- **Success**: https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app/success
- **Cancel**: https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app/cancel

### **Configuração no Frontend:**
O arquivo `frontend/config.js` deve ter:
```javascript
// Para produção
CONFIG.API_BASE_URL = 'https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app';
```

---

## 🔒 **Segurança e Proteção**

### **Headers de Segurança Configurados:**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

### **Proteção de Deploy:**
- ✅ Autenticação Vercel ativa
- ✅ Variáveis criptografadas
- ✅ HTTPS obrigatório

---

## 📊 **Monitoramento**

### **Vercel Dashboard:**
- **Logs**: https://vercel.com/diretoriamoovestudio-5505s-projects/moara/functions
- **Analytics**: https://vercel.com/diretoriamoovestudio-5505s-projects/moara/analytics
- **Settings**: https://vercel.com/diretoriamoovestudio-5505s-projects/moara/settings

### **Métricas Importantes:**
- Tempo de resposta das funções
- Taxa de erro
- Uso de recursos
- Logs de execução

---

## 🐛 **Troubleshooting**

### **Problemas Comuns:**

#### **1. Erro de Banco de Dados:**
```
"services": { "database": "error: connection failed" }
```
**Solução:**
- Verificar DATABASE_URL
- Verificar se o banco aceita conexões externas
- Verificar credenciais

#### **2. Erro do Stripe:**
```
"services": { "stripe": "not_configured" }
```
**Solução:**
- Configurar STRIPE_SECRET_KEY
- Verificar se a chave está correta

#### **3. Erro de Email:**
```
"services": { "email": "authentication_failed" }
```
**Solução:**
- Verificar EMAIL_USER e EMAIL_PASS
- Verificar se 2FA está ativo
- Gerar nova senha de app

### **Logs de Debug:**
```bash
# Ver logs em tempo real
vercel logs https://moara-eupmd1lrd-diretoriamoovestudio-5505s-projects.vercel.app
```

---

## 📞 **Suporte e Links Úteis**

### **Documentação:**
- 🔗 [Vercel Docs](https://vercel.com/docs)
- 🔗 [FastAPI Docs](https://fastapi.tiangolo.com)
- 🔗 [Stripe Docs](https://stripe.com/docs)
- 🔗 [Neon Docs](https://neon.tech/docs)

### **Suporte:**
- **Vercel**: https://vercel.com/support
- **Stripe**: https://support.stripe.com
- **GitHub Issues**: https://github.com/Caio-HenriqueDev/moara/issues

---

## ✅ **Checklist de Deploy**

### **Pré-Deploy:**
- [ ] Código commitado e pushed
- [ ] Vercel CLI instalado
- [ ] Login na Vercel feito

### **Deploy:**
- [x] Deploy realizado com sucesso
- [x] URL de produção funcionando
- [x] Estrutura do projeto validada

### **Pós-Deploy:**
- [ ] DATABASE_URL configurada
- [ ] STRIPE_SECRET_KEY configurada
- [ ] STRIPE_WEBHOOK_SECRET configurada
- [ ] EMAIL_USER configurada
- [ ] EMAIL_PASS configurada
- [ ] FRONTEND_URLs configuradas
- [ ] Health check retornando OK
- [ ] Endpoints testados
- [ ] Documentação acessível

### **Teste Final:**
- [ ] Processar email funcionando
- [ ] Listar faturas funcionando
- [ ] Criar checkout funcionando
- [ ] Webhook Stripe funcionando
- [ ] Frontend conectando com API

---

**📅 Última atualização:** $(date)  
**🚀 Status:** Deploy concluído - Aguardando configuração de variáveis  
**👨‍💻 Desenvolvedor:** Caio Henrique  

---

## 🎯 **Próximos Passos Imediatos**

1. **Configurar banco PostgreSQL** no Neon
2. **Configurar variáveis de ambiente** na Vercel
3. **Testar todos os endpoints**
4. **Configurar webhook do Stripe**
5. **Fazer deploy final** com todas as configurações

**🎉 Projeto pronto para produção após configuração das variáveis!**