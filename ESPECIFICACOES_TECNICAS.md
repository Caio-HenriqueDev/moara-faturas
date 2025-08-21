# ESPECIFICAÇÕES TÉCNICAS E OBJETIVAS
## Sistema de Gestão de Faturas - Moara Energia

---

## 📋 SUMÁRIO EXECUTIVO

O **Sistema de Gestão de Faturas da Usina Cliente** é uma solução completa de automação para processamento de faturas de energia elétrica, desenvolvida com arquitetura moderna e tecnologias robustas para operação em ambientes de desenvolvimento, teste e produção.

---

## 🎯 OBJETIVOS DO PROJETO

### **Objetivo Principal**
Automatizar completamente o fluxo de processamento de faturas de energia, desde a recepção por email até o processamento de pagamentos, eliminando processos manuais e reduzindo erros operacionais.

### **Objetivos Específicos**
1. **Automação de Coleta**: Buscar automaticamente faturas em PDF via email
2. **Processamento Inteligente**: Extrair dados estruturados das faturas
3. **Gestão Centralizada**: Armazenar e organizar informações em banco de dados
4. **Interface Intuitiva**: Dashboard web para visualização e gestão
5. **Processamento de Pagamentos**: Integração segura com gateway de pagamento
6. **Escalabilidade**: Suporte para múltiplos ambientes e crescimento

---

## 🏗️ ARQUITETURA DO SISTEMA

### **Visão Geral da Arquitetura**
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

### **Padrão Arquitetural**
- **Backend**: Arquitetura em camadas com separação de responsabilidades
- **Frontend**: Arquitetura SPA (Single Page Application) com PWA
- **Banco de Dados**: Padrão Repository com ORM SQLAlchemy
- **API**: RESTful com documentação automática (OpenAPI/Swagger)

---

## 🔧 ESPECIFICAÇÕES TÉCNICAS

### **Backend (Python/FastAPI)**

#### **Framework e Dependências**
```python
# Core Framework
fastapi==0.104.1          # Framework web assíncrono
uvicorn==0.24.0           # Servidor ASGI de produção

# Banco de Dados
sqlalchemy==2.0.23        # ORM para Python
psycopg2-binary==2.9.9    # Driver PostgreSQL

# Processamento de PDFs
PyPDF2==3.0.1             # Leitura e extração de PDFs

# Integrações
stripe==7.6.0             # Gateway de pagamentos
requests==2.31.0          # Cliente HTTP

# Utilitários
python-dotenv==1.0.0      # Gerenciamento de variáveis de ambiente
```

#### **Estrutura de Módulos**
```
backend/
├── main.py               # Aplicação FastAPI e endpoints
├── models.py             # Modelos SQLAlchemy
├── crud.py               # Operações CRUD
├── schemas.py            # Schemas Pydantic
├── db.py                 # Configuração local SQLite
├── db_vercel.py          # Configuração Vercel PostgreSQL
├── utils/
│   ├── bot_mail.py       # Automação de email
│   └── pdf_parser.py     # Processamento de PDFs
└── data/                 # Armazenamento de PDFs
```

#### **Endpoints da API**
| Método | Endpoint | Descrição | Resposta |
|--------|----------|-----------|----------|
| `GET` | `/` | Health check e informações do sistema | JSON com status |
| `GET` | `/health` | Verificação de saúde dos serviços | JSON com status dos serviços |
| `POST` | `/processar_email/` | Processa emails e extrai faturas | Confirmação de processamento |
| `GET` | `/faturas/` | Lista todas as faturas | Array de faturas |
| `POST` | `/create-checkout-session/{id}` | Cria sessão de pagamento | URL de checkout Stripe |
| `POST` | `/stripe-webhook/` | Webhook para eventos Stripe | Confirmação de recebimento |

### **Frontend (Vanilla JavaScript/HTML/CSS)**

#### **Tecnologias e Bibliotecas**
```html
<!-- CSS Framework -->
- CSS Custom Properties (Variáveis CSS)
- Flexbox e Grid para layout
- CSS Transitions e Animations

<!-- JavaScript -->
- ES6+ (Arrow functions, destructuring, async/await)
- Fetch API para comunicação com backend
- Local Storage para persistência local

<!-- Bibliotecas Externas -->
- Font Awesome 6.4.0 (Ícones)
- Google Fonts (Inter)
- Stripe.js (Integração de pagamentos)
```

#### **Estrutura de Componentes**
```
frontend/
├── index.html            # Página principal (Dashboard)
├── style.css             # Estilos globais e componentes
├── app.js                # Lógica principal da aplicação
├── manifest.json         # Configuração PWA
├── sw.js                 # Service Worker
├── success.html          # Página de sucesso de pagamento
├── cancel.html           # Página de cancelamento
└── icons/                # Ícones PWA (16x16 até 512x512)
```

#### **Funcionalidades PWA**
- **Service Worker**: Cache offline e sincronização
- **Manifest**: Instalação como aplicativo
- **Responsivo**: Design mobile-first
- **Offline**: Funcionalidades básicas sem internet

### **Banco de Dados**

#### **Modelo de Dados**
```sql
-- Tabela: faturas
CREATE TABLE faturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_cliente VARCHAR NOT NULL,
    documento_cliente VARCHAR UNIQUE NOT NULL,
    email_cliente VARCHAR NOT NULL,
    numero_instalacao VARCHAR UNIQUE NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    mes_referencia VARCHAR NOT NULL,
    data_vencimento VARCHAR NOT NULL,
    url_pdf VARCHAR,
    ja_pago BOOLEAN DEFAULT FALSE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX idx_faturas_nome ON faturas(nome_cliente);
CREATE INDEX idx_faturas_documento ON faturas(documento_cliente);
CREATE INDEX idx_faturas_instalacao ON faturas(numero_instalacao);
```

#### **Configurações de Ambiente**
- **Desenvolvimento**: SQLite (arquivo local)
- **Produção**: PostgreSQL (Vercel)
- **Migração**: Automática baseada em variável de ambiente

---

## 🔄 FLUXO DE PROCESSAMENTO

### **1. Coleta Automática de Emails**
```mermaid
graph TD
    A[Início] --> B[Conectar Gmail via IMAP]
    B --> C[Buscar emails com anexos PDF]
    C --> D[Gerar hash MD5 do PDF]
    D --> E{PDF já processado?}
    E -->|Sim| F[Pular PDF]
    E -->|Não| G[Salvar PDF localmente]
    G --> H[Extrair dados via regex]
    H --> I[Salvar no banco de dados]
    I --> J[Fim]
    F --> J
```

### **2. Processamento de PDFs**
- **Extração de Texto**: PyPDF2 para conversão PDF → texto
- **Regex Patterns**: Padrões específicos para cada campo
- **Validação**: Verificação de integridade dos dados
- **Cálculos**: Computação automática de valores

### **3. Gestão de Faturas**
- **CRUD Completo**: Create, Read, Update, Delete
- **Busca Inteligente**: Filtros por cliente, instalação, status
- **Paginação**: Suporte para grandes volumes de dados
- **Auditoria**: Rastreamento de mudanças e datas

### **4. Processamento de Pagamentos**
- **Integração Stripe**: Checkout seguro e responsivo
- **Webhooks**: Atualização automática de status
- **Validação**: Verificação de integridade das transações
- **Notificações**: Confirmação de pagamentos

---

## 🚀 DEPLOY E INFRAESTRUTURA

### **Ambiente de Desenvolvimento**
```bash
# Inicialização automática
python3 start_system.py

# Inicialização manual
cd backend && uvicorn main:app --reload --port 8000
cd frontend && python3 -m http.server 3000
```

### **Ambiente de Produção (Vercel)**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "backend/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "backend/main.py"
    }
  ]
}
```

### **Variáveis de Ambiente**
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
FRONTEND_SUCCESS_URL=https://seu-dominio.com/success
FRONTEND_CANCEL_URL=https://seu-dominio.com/cancel

# Banco de Dados (Vercel)
DATABASE_URL=postgresql://user:pass@host:port/db
```

---

## 📱 ESPECIFICAÇÕES DE INTERFACE

### **Design System**
- **Paleta de Cores**: Azul primário (#2563eb), verde sucesso (#10b981)
- **Tipografia**: Inter (Google Fonts) - Legibilidade e modernidade
- **Componentes**: Cards com sombras, botões com estados, modais responsivos
- **Layout**: Grid system responsivo com sidebar fixa

### **Responsividade**
- **Mobile First**: Design otimizado para dispositivos móveis
- **Breakpoints**: 320px, 768px, 1024px, 1440px
- **Navegação**: Menu hambúrguer para mobile, sidebar para desktop

### **Acessibilidade**
- **Contraste**: WCAG AA compliance
- **Navegação**: Suporte a teclado e leitores de tela
- **Semântica**: HTML5 semântico e ARIA labels

---

## 🔒 SEGURANÇA E COMPLIANCE

### **Autenticação e Autorização**
- **CORS**: Configurado para origens específicas
- **Rate Limiting**: Proteção contra ataques de força bruta
- **Validação**: Schemas Pydantic para validação de entrada

### **Proteção de Dados**
- **HTTPS**: Obrigatório em produção
- **Sanitização**: Limpeza de dados de entrada
- **Logs**: Auditoria de operações sensíveis

### **Integração Stripe**
- **Webhooks**: Verificação de assinatura
- **Metadata**: Rastreamento seguro de transações
- **Error Handling**: Tratamento robusto de falhas

---

## 📊 MONITORAMENTO E LOGS

### **Health Checks**
- **Endpoint `/health`**: Status dos serviços
- **Database**: Verificação de conectividade
- **External APIs**: Stripe e Gmail status

### **Logs e Debugging**
- **Console Logs**: Logs estruturados para desenvolvimento
- **Error Tracking**: Captura e registro de exceções
- **Performance**: Métricas de tempo de resposta

---

## 🧪 TESTES E QUALIDADE

### **Estratégia de Testes**
- **Unit Tests**: Funções individuais e módulos
- **Integration Tests**: APIs e banco de dados
- **E2E Tests**: Fluxos completos de usuário

### **Qualidade de Código**
- **Linting**: PEP 8 para Python
- **Type Hints**: Anotações de tipo Python
- **Documentation**: Docstrings e comentários

---

## 📈 ROADMAP E MELHORIAS

### **Fase 1 (Atual)**
- ✅ Sistema básico de processamento
- ✅ Interface web responsiva
- ✅ Integração com Stripe
- ✅ Deploy na Vercel

### **Fase 2 (Próximas)**
- 🔄 Sistema de usuários e autenticação
- 🔄 Relatórios e analytics
- 🔄 Notificações push
- 🔄 API para terceiros

### **Fase 3 (Futuras)**
- 📋 Dashboard administrativo avançado
- 📋 Machine Learning para extração de dados
- 📋 Integração com sistemas ERP
- 📋 Mobile app nativo

---

## 📋 REQUISITOS TÉCNICOS

### **Sistema Operacional**
- **Backend**: Linux, macOS, Windows (Python 3.8+)
- **Frontend**: Qualquer navegador moderno (Chrome 80+, Firefox 75+, Safari 13+)

### **Recursos Mínimos**
- **RAM**: 512MB para backend, 256MB para frontend
- **Storage**: 100MB para aplicação + espaço para PDFs
- **CPU**: 1 core para operações básicas

### **Requisitos de Rede**
- **Backend**: Porta 8000 (HTTP) ou 443 (HTTPS)
- **Frontend**: Porta 3000 (HTTP) ou 443 (HTTPS)
- **Banco**: Conexão PostgreSQL (produção) ou acesso a arquivo SQLite (desenvolvimento)

---

## 📚 DOCUMENTAÇÃO E SUPORTE

### **Documentação da API**
- **Swagger UI**: Disponível em `/docs`
- **OpenAPI**: Especificação completa da API
- **Exemplos**: Casos de uso e respostas

### **Guia de Desenvolvimento**
- **Setup**: Instruções de instalação e configuração
- **Arquitetura**: Documentação técnica detalhada
- **Contribuição**: Padrões de código e pull requests

---

## 🏆 CONCLUSÃO

O Sistema de Gestão de Faturas representa uma solução robusta e escalável para automação de processos financeiros, construída com tecnologias modernas e arquitetura bem definida. Sua estrutura modular permite fácil manutenção e expansão, enquanto a integração com serviços externos garante funcionalidades completas de pagamento e comunicação.

O projeto demonstra excelente arquitetura para crescimento futuro, com suporte para múltiplos ambientes e tecnologias que facilitam a manutenção e escalabilidade do sistema. 