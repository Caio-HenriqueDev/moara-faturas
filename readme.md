# Sistema de Gestão de Faturas - Moara Energia

## 📋 Descrição do Projeto

Este projeto é um sistema completo para automação do processamento de faturas de energia. Ele busca PDFs de faturas em uma conta de e-mail, extrai os dados relevantes, armazena em um banco de dados e apresenta-os em uma interface web moderna. Os clientes podem então realizar o pagamento dessas faturas através de uma integração segura com o Stripe.

## 🚀 Tecnologias Utilizadas

- **Backend**: Python (FastAPI, SQLAlchemy, PyPDF2, imaplib)
- **Frontend**: HTML, CSS, JavaScript (PWA)
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Pagamentos**: Stripe
- **Deploy**: Vercel

## 🏗️ Estrutura do Projeto

```
buscador_de_faturas-main/
├── backend/
│   ├── utils/
│   │   ├── bot_mail.py      # Automação de email
│   │   └── pdf_parser.py    # Processamento de PDFs
│   ├── data/                # Armazenamento de PDFs
│   ├── main.py              # Aplicação FastAPI
│   ├── models.py            # Modelos SQLAlchemy
│   ├── crud.py              # Operações CRUD
│   ├── schemas.py           # Schemas Pydantic
│   ├── db.py                # Configuração SQLite
│   ├── db_vercel.py         # Configuração PostgreSQL
│   └── requirements.txt     # Dependências Python
├── frontend/
│   ├── index.html           # Dashboard principal
│   ├── style.css            # Estilos
│   ├── app.js               # Lógica da aplicação
│   ├── manifest.json        # Configuração PWA
│   └── sw.js                # Service Worker
├── start_system.py          # Script de inicialização
├── ESPECIFICACOES_TECNICAS.md # Documentação técnica
└── readme.md                # Este arquivo
```

## ⚙️ Configuração do Ambiente

### 1. **Clone o repositório:**
```bash
git clone https://github.com/Caio-HenriqueDev/moara.git
cd moara
```

### 2. **Configure as variáveis de ambiente:**
Crie um arquivo `.env` na raiz do projeto baseado no `env_template.txt`:

```bash
# Email (Gmail)
EMAIL_USER=seu_email@gmail.com
EMAIL_PASS=sua_senha_de_app_gmail
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# URLs Frontend
FRONTEND_SUCCESS_URL=http://localhost:3000/success
FRONTEND_CANCEL_URL=http://localhost:3000/cancel
```

### 3. **Instale as dependências:**
```bash
cd backend
pip install -r requirements.txt
```

## 🚀 Como Executar o Projeto

### **Método Simples (Recomendado):**
```bash
# Execute o script de inicialização automática
python3 start_system.py
```

### **Método Manual:**
1. **Backend:**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. **Frontend:**
   ```bash
   cd frontend
   python3 -m http.server 3000
   ```

### 📱 **Acessos:**
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 🔌 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/` | Health check e informações do sistema |
| `GET` | `/health` | Verificação de saúde dos serviços |
| `POST` | `/processar_email/` | Processa emails e extrai faturas |
| `GET` | `/faturas/` | Lista todas as faturas |
| `POST` | `/create-checkout-session/{id}` | Cria sessão de pagamento Stripe |
| `POST` | `/stripe-webhook/` | Webhook para eventos Stripe |

## 🔒 Configuração do Gmail

Para usar o sistema de automação de email:

1. **Ative a verificação em 2 etapas** na sua conta Google
2. **Gere uma senha de aplicativo** específica para este projeto
3. **Ative o IMAP** nas configurações do Gmail
4. **Configure as variáveis** `EMAIL_USER` e `EMAIL_PASS` no arquivo `.env`

## 💳 Configuração do Stripe

1. **Crie uma conta** no [Stripe](https://stripe.com)
2. **Obtenha as chaves** de API (teste e produção)
3. **Configure webhooks** para receber eventos de pagamento
4. **Configure as variáveis** `STRIPE_SECRET_KEY` e `STRIPE_WEBHOOK_SECRET`

## 🚀 Deploy na Vercel

O projeto está configurado para deploy automático na Vercel:

1. **Conecte o repositório** GitHub à Vercel
2. **Configure as variáveis de ambiente** no painel da Vercel
3. **Deploy automático** a cada push para a branch main

## 📚 Documentação

- **Especificações Técnicas**: [ESPECIFICACOES_TECNICAS.md](ESPECIFICACOES_TECNICAS.md)
- **API Docs**: Disponível em `/docs` quando o backend estiver rodando

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

Para suporte ou dúvidas, abra uma [issue](https://github.com/Caio-HenriqueDev/moara/issues) no GitHub.

---

**Desenvolvido com ❤️ por Caio Henrique**
