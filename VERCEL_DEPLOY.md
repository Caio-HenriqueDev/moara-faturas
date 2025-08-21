# 🚀 Deploy na Vercel - Sistema de Gestão de Faturas

## 📋 Pré-requisitos

1. **Conta na Vercel**: [vercel.com](https://vercel.com)
2. **Banco PostgreSQL**: Recomendamos [Neon](https://neon.tech) ou [Supabase](https://supabase.com)
3. **Conta no Stripe**: Para processamento de pagamentos
4. **Conta Gmail**: Para processamento de e-mails

## 🔧 Configuração do Banco de Dados

### 1. Criar banco PostgreSQL
- Use [Neon](https://neon.tech) (gratuito) ou [Supabase](https://supabase.com)
- Anote a URL de conexão: `postgresql://user:password@host:port/database`

### 2. Configurar variáveis de ambiente na Vercel

```bash
# Banco de dados
DATABASE_URL=postgresql://user:password@host:port/database

# Stripe
STRIPE_SECRET_KEY=sk_test_... ou sk_live_...
STRIPE_PUBLIC_KEY=pk_test_... ou pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Gmail
EMAIL_USER=seu_email@gmail.com
EMAIL_PASS=sua_senha_de_app_gmail
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993

# URLs do Frontend
FRONTEND_SUCCESS_URL=https://seu-dominio.vercel.app/success
FRONTEND_CANCEL_URL=https://seu-dominio.vercel.app/cancel

# Ambiente
VERCEL_ENV=production
```

## 🚀 Deploy na Vercel

### 1. Conectar repositório
```bash
# Na Vercel Dashboard
1. New Project
2. Import Git Repository
3. Selecione seu repositório
4. Configure as variáveis de ambiente
```

### 2. Configurações de Build
- **Framework Preset**: Other
- **Build Command**: `pip install -r backend/requirements.txt`
- **Output Directory**: `backend`
- **Install Command**: `pip install -r backend/requirements.txt`

### 3. Deploy
```bash
# A Vercel detectará automaticamente o vercel.json
# O deploy será feito automaticamente
```

## 🔍 Verificação do Deploy

### 1. Testar endpoints
```bash
# Health check
curl https://seu-projeto.vercel.app/health

# Root endpoint
curl https://seu-projeto.vercel.app/

# Documentação
https://seu-projeto.vercel.app/docs
```

### 2. Verificar logs
- Vercel Dashboard → Functions → Logs
- Verificar se não há erros de conexão com banco

## 🐛 Troubleshooting

### Erro de conexão com banco
```bash
# Verificar se DATABASE_URL está correta
# Verificar se o banco aceita conexões externas
# Verificar se as credenciais estão corretas
```

### Erro de dependências
```bash
# Verificar se todas as dependências estão em requirements.txt
# Verificar se as versões são compatíveis
```

### Erro de CORS
```bash
# Verificar se as origens estão configuradas corretamente
# Verificar se o frontend está acessando a URL correta
```

## 📱 Frontend

### 1. Configurar URLs
- Atualizar `frontend/config.js` com a URL da Vercel
- Fazer deploy do frontend separadamente ou usar o mesmo projeto

### 2. Deploy do Frontend
```bash
# Opção 1: Mesmo projeto Vercel
# Adicionar build do frontend no vercel.json

# Opção 2: Projeto separado
# Criar novo projeto para o frontend
```

## 🔒 Segurança

### 1. Variáveis de ambiente
- ✅ Nunca commitar credenciais
- ✅ Usar variáveis de ambiente da Vercel
- ✅ Rotacionar chaves regularmente

### 2. Headers de segurança
- ✅ Configurados no vercel.json
- ✅ CORS configurado adequadamente
- ✅ Rate limiting (considerar implementar)

## 📊 Monitoramento

### 1. Vercel Analytics
- Performance das funções
- Uso de recursos
- Logs de erro

### 2. Health Checks
- Endpoint `/health` para monitoramento
- Verificar conectividade com banco
- Verificar serviços externos (Stripe, Gmail)

## 🔄 Atualizações

### 1. Deploy automático
- Configurar para fazer deploy em cada push
- Usar branches para staging/produção

### 2. Rollback
- Vercel mantém histórico de deploys
- Pode reverter para versão anterior facilmente

## 📞 Suporte

- **Vercel**: [vercel.com/support](https://vercel.com/support)
- **Documentação**: [vercel.com/docs](https://vercel.com/docs)
- **Status**: [vercel-status.com](https://vercel-status.com)

---

## 🎯 Próximos Passos

1. ✅ Configurar banco PostgreSQL
2. ✅ Configurar variáveis de ambiente na Vercel
3. ✅ Fazer primeiro deploy
4. ✅ Testar todos os endpoints
5. ✅ Configurar frontend
6. ✅ Configurar monitoramento
7. ✅ Configurar CI/CD

**Boa sorte com o deploy! 🚀** 