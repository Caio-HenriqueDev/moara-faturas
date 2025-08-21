# 🚀 Guia de Deploy na Vercel - Sistema de Gestão de Faturas

## 📋 Pré-requisitos

- Conta na [Vercel](https://vercel.com)
- Projeto no GitHub
- Banco PostgreSQL configurado
- Conta Stripe configurada
- Gmail com senha de aplicativo

## 🔧 Configuração do Projeto

### 1. Estrutura de Arquivos
Certifique-se de que seu projeto tenha esta estrutura:
```
buscador_de_faturas-main/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── requirements.txt
│   └── utils/
│       ├── bot_mail.py
│       └── pdf_parser.py
├── vercel.json
├── package.json
└── env_vercel.txt
```

### 2. Configuração do vercel.json
O arquivo `vercel.json` já está configurado corretamente para Python/FastAPI.

### 3. Configuração do package.json
O arquivo `package.json` já está configurado para o projeto Python.

## 🌍 Configuração de Variáveis de Ambiente

### 1. No Painel da Vercel
Acesse seu projeto na Vercel e vá em **Settings > Environment Variables**

### 2. Variáveis Obrigatórias
Configure as seguintes variáveis:

```bash
# Email (Gmail)
EMAIL_USER=seu_email@gmail.com
EMAIL_PASS=sua_senha_de_app_gmail
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993

# Stripe (Produção)
STRIPE_SECRET_KEY=sk_live_sua_chave_secreta
STRIPE_PUBLIC_KEY=pk_live_sua_chave_publica
STRIPE_WEBHOOK_SECRET=whsec_seu_webhook_secret

# Banco de Dados
DATABASE_URL=postgresql://user:password@host:port/database

# Frontend URLs
FRONTEND_SUCCESS_URL=https://moara.vercel.app/success
FRONTEND_CANCEL_URL=https://moara.vercel.app/cancel

# Ambiente
VERCEL_ENV=production
DEBUG=false
```

### 3. Configuração do Gmail
1. Ative autenticação de 2 fatores no Gmail
2. Gere uma senha de aplicativo
3. Use essa senha na variável `EMAIL_PASS`

### 4. Configuração do Stripe
1. Acesse o painel do Stripe
2. Vá em **Developers > API keys**
3. Use as chaves de **produção** (não de teste)
4. Configure o webhook em **Developers > Webhooks**

### 5. Configuração do Banco PostgreSQL
1. Use um serviço como:
   - [Neon](https://neon.tech)
   - [Supabase](https://supabase.com)
   - [PlanetScale](https://planetscale.com)
2. Configure a URL no formato: `postgresql://user:password@host:port/database`

## 🚀 Deploy

### 1. Conectar ao GitHub
1. Na Vercel, clique em **New Project**
2. Importe seu repositório do GitHub
3. Configure o projeto

### 2. Configurações de Build
- **Framework Preset**: Other
- **Build Command**: `echo "Build não necessário para Python/FastAPI"`
- **Output Directory**: `.`
- **Install Command**: `pip install -r backend/requirements.txt`

### 3. Deploy
1. Clique em **Deploy**
2. Aguarde o build completar
3. Verifique se não há erros

## 🧪 Testes Pós-Deploy

### 1. Teste de Saúde da API
```bash
curl https://seu-projeto.vercel.app/health
```

### 2. Teste de Documentação
Acesse: `https://seu-projeto.vercel.app/docs`

### 3. Teste de Endpoints
```bash
# Teste raiz
curl https://seu-projeto.vercel.app/

# Teste de faturas
curl https://seu-projeto.vercel.app/faturas/

# Teste de processamento de email
curl -X POST https://seu-projeto.vercel.app/processar_email/
```

## 🔍 Solução de Problemas

### Erro 500 - Imports
**Problema**: Erro de import de módulos
**Solução**: Verifique se todos os arquivos têm imports com fallback para Vercel

### Erro de Conexão com Banco
**Problema**: Não consegue conectar ao PostgreSQL
**Solução**: 
1. Verifique se `DATABASE_URL` está configurada
2. Teste a conexão localmente
3. Verifique se o banco aceita conexões externas

### Erro de Email
**Problema**: Não consegue conectar ao Gmail
**Solução**:
1. Verifique se `EMAIL_USER` e `EMAIL_PASS` estão configurados
2. Confirme se a senha de aplicativo está correta
3. Verifique se o Gmail permite conexões IMAP

### Erro de Stripe
**Problema**: Erro nas operações do Stripe
**Solução**:
1. Verifique se as chaves estão configuradas
2. Confirme se está usando chaves de produção
3. Verifique se o webhook está configurado

## 📊 Monitoramento

### 1. Logs da Vercel
- Acesse **Functions** no painel da Vercel
- Clique na função `backend/main.py`
- Verifique os logs de execução

### 2. Métricas
- **Function Duration**: Deve ser < 30s
- **Memory Usage**: Deve ser < 1024MB
- **Error Rate**: Deve ser < 1%

### 3. Alertas
Configure alertas para:
- Erro rate > 1%
- Function duration > 25s
- Memory usage > 900MB

## 🔄 Atualizações

### 1. Deploy Automático
- Cada push para a branch principal gera um novo deploy
- Use branches para testar mudanças

### 2. Rollback
- Na Vercel, vá em **Deployments**
- Clique em um deploy anterior
- Clique em **Promote to Production**

## 📱 Frontend

### 1. Configuração
O frontend deve apontar para a URL da API da Vercel:
```javascript
const API_BASE_URL = 'https://seu-projeto.vercel.app';
```

### 2. CORS
O backend já está configurado para aceitar requisições do frontend.

## 🎯 Checklist Final

- [ ] Todas as variáveis de ambiente configuradas
- [ ] Banco PostgreSQL funcionando
- [ ] Stripe configurado e testado
- [ ] Gmail configurado e testado
- [ ] API respondendo corretamente
- [ ] Frontend apontando para a API correta
- [ ] Logs sem erros críticos
- [ ] Métricas dentro dos limites

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs da Vercel
2. Teste localmente com as mesmas variáveis
3. Use o script `test_vercel_compatibility.py`
4. Consulte a documentação da Vercel para Python

---

**🎉 Parabéns!** Seu sistema está rodando na Vercel com sucesso! 