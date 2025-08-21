# 🔧 CONFIGURAÇÃO DO AMBIENTE - Sistema Moara Energia

## 📋 **VARIÁVEIS DE AMBIENTE NECESSÁRIAS**

### **1. Configurações de Email (Gmail)**

Para usar o sistema de automação de email, configure:

```bash
# Ative a verificação em 2 etapas na sua conta Google
# Gere uma senha de aplicativo específica para este projeto
# Ative o IMAP nas configurações do Gmail

EMAIL_USER=seu_email@gmail.com
EMAIL_PASS=sua_senha_de_app_gmail
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
```

**Como configurar:**
1. Acesse [myaccount.google.com](https://myaccount.google.com)
2. Vá em "Segurança" → "Verificação em 2 etapas"
3. Ative a verificação em 2 etapas
4. Vá em "Senhas de app"
5. Gere uma senha para "Moara Energia"
6. Use essa senha no `EMAIL_PASS`

### **2. Configurações do Stripe**

Para usar o sistema de pagamentos:

```bash
STRIPE_SECRET_KEY=sk_test_sua_chave_secreta_aqui
STRIPE_PUBLIC_KEY=pk_test_sua_chave_publica_aqui
STRIPE_WEBHOOK_SECRET=whsec_seu_webhook_secret_aqui
```

**Como configurar:**
1. Acesse [stripe.com](https://stripe.com) e crie uma conta
2. Vá em "Desenvolvedores" → "Chaves da API"
3. Copie as chaves de teste (test keys)
4. Configure webhooks em "Desenvolvedores" → "Webhooks"

### **3. URLs do Frontend**

```bash
FRONTEND_SUCCESS_URL=http://localhost:3000/success
FRONTEND_CANCEL_URL=http://localhost:3000/cancel
```

## 🌍 **CONFIGURAÇÃO DE AMBIENTES**

### **Desenvolvimento Local**
- **Backend:** `http://localhost:8000`
- **Frontend:** `http://localhost:3000`
- **Banco:** SQLite local

### **Produção Vercel**
- **Backend:** `https://moara.vercel.app`
- **Frontend:** `https://moaraenergiasolar.vercel.app`
- **Banco:** PostgreSQL (Vercel)

## 🚀 **COMO CONFIGURAR**

### **1. Desenvolvimento Local**

```bash
# 1. Clone o repositório
git clone https://github.com/Caio-HenriqueDev/moara.git
cd moara

# 2. Ative o ambiente virtual
source venv/bin/activate

# 3. Instale as dependências
pip install -r backend/requirements.txt

# 4. Configure as variáveis de ambiente
cp env_template.txt .env
# Edite o arquivo .env com suas credenciais

# 5. Inicie o sistema
python3 start_system.py
```

### **2. Produção Vercel**

```bash
# 1. Configure as variáveis no painel da Vercel
# Vá em: https://vercel.com/dashboard
# Selecione seu projeto
# Vá em "Settings" → "Environment Variables"

# 2. Adicione as variáveis:
EMAIL_USER=seu_email@gmail.com
EMAIL_PASS=sua_senha_de_app_gmail
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
DATABASE_URL=postgresql://...

# 3. Faça o deploy
git push origin main
```

## 🔄 **ALTERNANDO ENTRE AMBIENTES**

### **No Frontend**
Use o seletor de ambiente no cabeçalho:
- **🏠 Local** - `http://localhost:8000`
- **☁️ Vercel** - `https://moara.vercel.app`
- **☁️ Vercel 2** - `https://moaraenergiasolar.vercel.app`

### **Programaticamente**
```javascript
// Alternar para ambiente local
switchEnvironment('local');

// Alternar para Vercel
switchEnvironment('vercel');

// Verificar ambiente atual
console.log(CONFIG.API_BASE_URL);
```

## 📱 **TESTANDO A CONFIGURAÇÃO**

### **1. Teste do Backend**
```bash
# Health check
curl http://localhost:8000/health

# Listar faturas
curl http://localhost:8000/faturas/

# Documentação
open http://localhost:8000/docs
```

### **2. Teste do Frontend**
```bash
# Abra no navegador
open http://localhost:3000

# Verifique o console para logs
# Use o seletor de ambiente para testar diferentes APIs
```

## ⚠️ **PROBLEMAS COMUNS**

### **1. Erro de Email**
- Verifique se a verificação em 2 etapas está ativa
- Use senha de aplicativo, não sua senha principal
- Verifique se o IMAP está ativo no Gmail

### **2. Erro de Stripe**
- Use chaves de teste (test keys) para desenvolvimento
- Configure webhooks corretamente
- Verifique se as chaves estão corretas

### **3. Erro de Banco de Dados**
- Local: Verifique se o SQLite está funcionando
- Vercel: Verifique a URL do PostgreSQL
- Verifique se as tabelas foram criadas

## 🎯 **PRÓXIMOS PASSOS**

1. **Configure suas credenciais** no arquivo `.env`
2. **Teste localmente** com `python3 start_system.py`
3. **Configure as variáveis** no painel da Vercel
4. **Faça o deploy** para produção
5. **Teste a integração** entre frontend e backend

---

**📞 Suporte:** Para dúvidas, abra uma issue no GitHub ou consulte a documentação da API em `/docs`. 