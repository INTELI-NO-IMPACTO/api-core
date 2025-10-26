# 🏳️‍⚧️ Meu Nome Gov - API Core

## 🔐 Sistema de Gerenciamento Completo para Suporte à Comunidade Trans

API REST robusta e segura para gerenciamento de beneficiários, ONGs, assistentes sociais e sistema de doações, com foco em inclusão e respeito à identidade de gênero.

---

# 👥 Equipe: INTELI-NO-IMPACTO

| Integrante 1 | Integrante 2 | Integrante 3 | Integrante 4 |
| :----------: | :----------: | :----------: | :----------: |
| <img src="https://media.licdn.com/dms/image/v2/D4D03AQFpuCHH7zRE6w/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1678716198904?e=1762992000&v=beta&t=RLdzg-MCyoqVbXLt6OSLU6LigBP3GfagPndLGp9gPmI" width="150" alt="Fernando Machado"> <br> [**Fernando Machado**](https://www.linkedin.com/in/fernando-machado-santos) | <img src="https://media.licdn.com/dms/image/v2/D4D03AQFEWbbQZVzBTA/profile-displayphoto-scale_400_400/B4DZl9519rH4Ak-/0/1758753940232?e=1762992000&v=beta&t=7O3oUlf2K3jwN66gi32vdRYfCjPyceCP_qCtPS9WVbQ" width="150" alt="Gabriel Pelinsari"> <br> [**Gabriel Pelinsari**](https://www.linkedin.com/in/gabriel-pelinsari) | <img src="https://media.licdn.com/dms/image/v2/D4D03AQF9VYDA7dTAkw/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1678714840944?e=1762992000&v=beta&t=v8BNYFBASek__LV44Ie1DkBWZEUaIwizMEeOHB7eUDI" width="150" alt="João Paulo Silva"> <br> [**João Paulo Silva**](https://www.linkedin.com/in/joão-paulo-da-silva-a45229215) | <img src="https://media.licdn.com/dms/image/v2/D4D03AQHprrQcSOWJ_w/profile-displayphoto-crop_800_800/B4DZlo.DN1JgAI-/0/1758402722996?e=1762992000&v=beta&t=0vmN2_Ec3DzEdHvQoUnycjyhaNHGDTUWSRJztYcC-Cc" width="150" alt="Matheus Ribeiro"> <br> [**Matheus Ribeiro**](https://www.linkedin.com/in/omatheusrsantos) |

---

# 📖 Descrição

Este projeto é a **API Core** do sistema **Meu Nome Gov**, desenvolvida para fornecer uma infraestrutura completa de backend para aplicações voltadas ao suporte da comunidade trans brasileira. A API oferece funcionalidades essenciais para:

- 👤 **Gerenciamento de Usuários**: Sistema completo com suporte a nome social, pronomes e upload de fotos de perfil
- 🏢 **Gestão de ONGs**: Cadastro e gerenciamento de organizações parceiras
- 🤝 **Assistentes Sociais**: Relacionamento entre beneficiários e assistentes
- 💰 **Sistema de Doações**: Gestão completa de doações e campanhas
- 📰 **Artigos Educacionais**: Base de conhecimento sobre retificação de nome, hormonização e prevenção de ISTs
- 📊 **Métricas e Analytics**: Acompanhamento de uso e impacto do sistema
- 💬 **Sistema de Chat**: Integração com chatbot para suporte à comunidade

### 🎯 Diferenciais do Projeto

- **Autenticação Completa**: JWT com refresh tokens para sessões seguras e longas
- **Sessões Anônimas**: Permite uso sem cadastro prévio via `session_id`
- **Upload de Arquivos**: Integração com Supabase Storage para fotos de perfil
- **Respeito à Identidade**: Priorização de nome social e pronomes corretos
- **Roles e Permissões**: Sistema de papéis (Beneficiário, Assistente, Admin)
- **Migrações Alembic**: Gerenciamento versionado do schema do banco
- **Docker Ready**: Containerização completa para desenvolvimento e produção
- **Hot Reload**: Desenvolvimento ágil com atualização automática de código

---

# 📂 Estrutura de Pastas

```
📁 api-core/
├── 📂 alembic/                       # Migrações do banco de dados
│   ├── 📂 versions/                  # Versões das migrações
│   │   ├── 132ee07ae9c5_initial_tables.py
│   │   ├── 600c4f54df2a_add_profile_image_to_users.py
│   │   ├── 8ca41948118b_fix_role_enum_values.py
│   │   ├── a7139272e46b_add_pronoun_to_users.py
│   │   └── da4eb41a29fa_add_all_models.py
│   ├── 📄 env.py                     # Configuração do ambiente Alembic
│   ├── 📄 README                     # Documentação Alembic
│   └── 📄 script.py.mako             # Template para novas migrações
│
├── 📂 src/                           # Código fonte da aplicação
│   └── 📂 app/                       # Aplicação FastAPI
│       ├── 📄 __init__.py
│       ├── 📄 main.py                # Entrada da aplicação FastAPI
│       ├── 📄 config.py              # Configurações e variáveis de ambiente
│       ├── 📄 db.py                  # Configuração do banco de dados
│       ├── 📄 dependencies.py        # Dependências reutilizáveis (auth, etc)
│       ├── 📄 security.py            # JWT, hashing de senhas, tokens
│       │
│       ├── 📂 models/                # Modelos SQLAlchemy (ORM)
│       │   ├── 📄 __init__.py
│       │   ├── 📄 user.py            # Modelo de usuário (com roles e nome social)
│       │   ├── 📄 org.py             # Modelo de organizações (ONGs)
│       │   ├── 📄 token.py           # Modelo de refresh tokens
│       │   ├── 📄 chat.py            # Modelo de chats e mensagens
│       │   ├── 📄 article.py         # Modelo de artigos educacionais
│       │   └── 📄 donation.py        # Modelo de doações
│       │
│       ├── 📂 schemas/               # Schemas Pydantic (validação/serialização)
│       │   ├── 📄 __init__.py
│       │   ├── 📄 auth.py            # Schemas de autenticação
│       │   ├── 📄 user.py            # Schemas de usuário
│       │   ├── 📄 org.py             # Schemas de organizações
│       │   ├── 📄 chat.py            # Schemas de chat
│       │   ├── 📄 article.py         # Schemas de artigos
│       │   └── 📄 donation.py        # Schemas de doações
│       │
│       ├── 📂 routers/               # Endpoints da API (controllers)
│       │   ├── 📄 __init__.py
│       │   ├── 📄 auth.py            # Autenticação (login, register, refresh)
│       │   ├── 📄 users.py           # CRUD de usuários
│       │   ├── 📄 beneficiarios.py   # Gestão de beneficiários
│       │   ├── 📄 orgs.py            # CRUD de ONGs
│       │   ├── 📄 articles.py        # Gestão de artigos
│       │   ├── 📄 donations.py       # Sistema de doações
│       │   ├── 📄 storage.py         # Upload e gerenciamento de arquivos
│       │   └── 📄 metrics.py         # Métricas e analytics
│       │
│       └── 📂 utils/                 # Utilitários compartilhados
│           ├── 📄 __init__.py
│           ├── 📄 supabase.py        # Integração com Supabase Storage
│           ├── 📄 email.py           # Envio de emails (SMTP)
│           └── 📄 seed.py            # Script de seed do banco
│
├── 📂 tests/                         # Testes automatizados
│   ├── 📄 conftest.py                # Configuração de fixtures pytest
│   └── 📄 test_beneficiarios.py      # Testes de endpoints
│
├── 📄 alembic.ini                    # Configuração do Alembic
├── 📄 docker-compose.yml             # Orquestração de containers
├── 📄 Dockerfile                     # Imagem Docker da aplicação
├── 📄 Makefile                       # Comandos úteis para desenvolvimento
├── 📄 requirements.txt               # Dependências Python
├── 📄 AGENTS.md                      # Guidelines para agentes de IA
├── 📄 TODOS.md                       # Lista de tarefas e melhorias
└── 📄 README.md                      # Este arquivo
```

---

# 🏗️ Arquitetura do Sistema

## Componentes Principais

### 1. 🚀 API REST (FastAPI)
- **Framework**: FastAPI com Uvicorn (ASGI server)
- **Documentação Automática**: Swagger UI (`/docs`) e ReDoc (`/redoc`)
- **Validação**: Pydantic schemas para request/response
- **CORS**: Configurado para permitir múltiplas origens (frontend web, mobile)

### 2. 🗄️ Banco de Dados (PostgreSQL via Supabase)
- **ORM**: SQLAlchemy 2.0 (async-ready)
- **Migrações**: Alembic para versionamento do schema
- **Modelos Principais**:
  - `users` - Usuários do sistema (beneficiários, assistentes, admins)
  - `orgs` - Organizações (ONGs parceiras)
  - `chats` - Conversas com o chatbot
  - `chat_messages` - Histórico de mensagens
  - `articles` - Base de conhecimento
  - `donations` - Gestão de doações
  - `refresh_tokens` - Tokens de atualização JWT

### 3. 🔐 Sistema de Autenticação
- **JWT (JSON Web Tokens)**:
  - Access Token (curta duração - 60 min padrão)
  - Refresh Token (longa duração - armazenado no banco)
- **Hashing**: Bcrypt para senhas
- **Sessões Anônimas**: `session_id` para uso sem cadastro
- **Roles**: Controle de permissões por papel (BENEFICIARIO, ASSISTENTE, ADMIN)

### 4. ☁️ Integração com Supabase
- **Storage**: Upload de imagens de perfil e documentos
- **Database**: PostgreSQL gerenciado na nuvem
- **Service Role**: Acesso privilegiado para operações server-side

### 5. 🐳 Docker & Containerização
- **Hot Reload**: Volume mounts para desenvolvimento ágil
- **Network Host**: Suporte a proxies corporativos
- **Environment Variables**: Configuração via `.env`

---

# 🔧 Tecnologias Utilizadas

## Backend
- **FastAPI** (0.115.0) - Framework web moderno e de alta performance
- **Uvicorn** (0.30.6) - Servidor ASGI com suporte a websockets
- **Python 3.12+** - Linguagem de programação

## Banco de Dados & ORM
- **SQLAlchemy** (2.0.36) - ORM poderoso com suporte async
- **Alembic** (1.14.0) - Migrações de banco de dados
- **PostgreSQL** (via Supabase) - Banco relacional robusto
- **psycopg2-binary** (2.9.9) - Driver PostgreSQL

## Autenticação & Segurança
- **python-jose** (3.3.0) - JWT encoding/decoding
- **bcrypt** (4.0.1) - Hashing de senhas
- **email-validator** (2.2.0) - Validação de emails

## Validação & Configuração
- **Pydantic** (2.9.2) - Validação de dados com type hints
- **pydantic-settings** (2.11.0) - Gerenciamento de configurações

## Upload & HTTP
- **python-multipart** (0.0.9) - Suporte a multipart/form-data
- **httpx** (0.27.2) - Cliente HTTP assíncrono

## Testes
- **pytest** (7.4.0) - Framework de testes

## DevOps
- **Docker** - Containerização
- **Docker Compose** - Orquestração de containers
- **Make** - Automação de comandos

---

# ⚙️ Requisitos

## Hardware Mínimo
- **Processador**: Dual-core 2.0 GHz ou superior
- **Memória RAM**: Mínimo 4GB (recomendado 8GB+)
- **Armazenamento**: 1GB de espaço livre
- **Conexão Internet**: Necessária para Supabase e APIs externas

## Software
- **Docker**: Versão 20.10+ (recomendado Docker Desktop)
- **Docker Compose**: Versão 2.0+
- **Python**: Versão 3.12 ou superior (se rodar localmente)
- **pip**: Gerenciador de pacotes Python
- **Git**: Para clonar o repositório
- **Make**: GNU Make (opcional, mas recomendado)

### Windows
- **WSL 2** (Windows Subsystem for Linux) - Recomendado para melhor performance do Docker
- **PowerShell** 5.1+ ou **PowerShell Core** 7+

### macOS
- **Homebrew** - Recomendado para instalar dependências

### Linux
- Distribuição baseada em Debian/Ubuntu ou RHEL/CentOS

## Contas e Chaves Necessárias
- **Conta Supabase** com projeto configurado
- **Banco PostgreSQL** (via Supabase)
- **Service Role Key** do Supabase
- **Secret Key JWT** (gerar aleatoriamente)
- **Conta SMTP** (opcional, para envio de emails)

---

# 🚀 Instruções para Execução

## 1. Clone o Repositório

```powershell
git clone https://github.com/INTELI-NO-IMPACTO/api-core.git
cd api-core
```

## 2. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/database
# Exemplo Supabase: postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALG=HS256
JWT_EXPIRES_MIN=60

# CORS Origins (separados por vírgula)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://yourdomain.com

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SUPABASE_BUCKET=profile-images
SUPABASE_PUBLIC_BUCKET_URL=https://your-project.supabase.co/storage/v1/object/public/profile-images

# Email Configuration (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_FROM=noreply@meunomegov.com
```

### 🔑 Como Obter as Chaves:

#### **Supabase:**
1. Acesse [supabase.com](https://supabase.com/) e faça login
2. Crie um novo projeto (aguarde ~2 minutos)
3. Vá em **Settings** > **API**
4. Copie:
   - **URL**: `SUPABASE_URL`
   - **service_role key**: `SUPABASE_SERVICE_ROLE_KEY` (⚠️ Nunca exponha esta chave!)
5. Vá em **Storage** > **Create bucket**:
   - Nome: `profile-images`
   - Public bucket: ✅ (para acesso direto às imagens)

#### **JWT Secret:**
Gere uma chave aleatória segura:

```powershell
# PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
```

Ou use um gerador online: [randomkeygen.com](https://randomkeygen.com/)

#### **Database URL (Supabase):**
1. No Supabase, vá em **Settings** > **Database**
2. Em **Connection string** > **URI**, copie a string
3. Substitua `[YOUR-PASSWORD]` pela senha do banco que você definiu na criação do projeto

#### **Gmail SMTP (opcional):**
1. Acesse [myaccount.google.com/security](https://myaccount.google.com/security)
2. Ative **Verificação em duas etapas**
3. Gere uma **Senha de app** em **Senhas de app**
4. Use essa senha no `SMTP_PASS`

---

## 3. Opção A: Executar com Docker (Recomendado)

### 🐳 Build e Start

```powershell
# Build da imagem
docker compose build

# Subir a aplicação
docker compose up
```

A API estará disponível em: **http://localhost:8000**

### 📋 Comandos Úteis do Docker

```powershell
# Subir em background (detached)
docker compose up -d

# Ver logs em tempo real
docker compose logs -f api

# Parar os containers
docker compose down

# Rebuild completo (após mudanças no Dockerfile)
docker compose up --build

# Acessar shell do container
docker compose exec api bash

# Rodar migrações dentro do container
docker compose exec api alembic upgrade head
```

---

## 4. Opção B: Executar Localmente (Sem Docker)

### Criar Ambiente Virtual

```powershell
# Criar venv
python -m venv .venv

# Ativar venv
.\.venv\Scripts\Activate.ps1

# Se houver erro de execution policy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Instalar Dependências

```powershell
pip install -r requirements.txt
```

### Rodar Migrações

```powershell
alembic upgrade head
```

### Iniciar a Aplicação

```powershell
# Usando Make (se disponível)
make run

# Ou diretamente com Uvicorn
uvicorn src.app.main:app --reload --port 8000
```

A API estará disponível em: **http://localhost:8000**

---

## 5. Configuração do Banco de Dados

### Estrutura das Tabelas

As tabelas são criadas automaticamente pelas migrações Alembic. Para visualizar a estrutura:

```powershell
# Ver SQL que será executado (sem aplicar)
alembic upgrade head --sql

# Ver histórico de migrações
alembic history

# Verificar revisão atual
alembic current
```

### Principais Tabelas

| Tabela | Descrição |
|--------|-----------|
| `users` | Usuários do sistema (beneficiários, assistentes, admins) |
| `orgs` | Organizações parceiras (ONGs) |
| `chats` | Conversas com o chatbot |
| `chat_messages` | Histórico de mensagens |
| `articles` | Base de conhecimento |
| `donations` | Gestão de doações |
| `refresh_tokens` | Tokens de atualização JWT |

### Seed do Banco (Dados Iniciais)

```powershell
# Usando Make
make seed

# Ou diretamente
python -m src.app.utils.seed
```

---

## 6. Verificação da Instalação

### Teste de Health Check

```powershell
curl http://localhost:8000/health
```

**Resposta esperada:**
```json
{
  "ok": true,
  "message": "API is running"
}
```

### Acessar Documentação

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

# 📡 Endpoints da API

## 🔐 Autenticação (`/auth`)

### POST `/auth/register`
Registra um novo usuário (beneficiário por padrão).

**Content-Type:** `multipart/form-data`

**Request (Form Data):**
```
email: usuario@email.com
password: senhaForte123
name: João Silva
social_name: Maria Silva (opcional)
pronoun: ela (opcional)
cpf: 12345678900 (opcional)
profile_image: [arquivo] (opcional)
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "usuario@email.com",
    "name": "João Silva",
    "social_name": "Maria Silva",
    "pronoun": "ela",
    "profile_image_url": "https://...",
    "role": "beneficiario",
    "is_active": true,
    "created_at": "2025-10-26T12:00:00Z"
  }
}
```

### POST `/auth/login`
Autentica um usuário existente.

**Request Body:**
```json
{
  "email": "usuario@email.com",
  "password": "senhaForte123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { /* dados do usuário */ }
}
```

### POST `/auth/refresh`
Renova o access token usando o refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### POST `/auth/anonymous-session`
Cria uma sessão anônima para uso sem cadastro.

**Request Body:**
```json
{
  "session_id": "abc-123-def-456" // Opcional: gera automaticamente se omitido
}
```

**Response:**
```json
{
  "session_id": "abc-123-def-456",
  "chat_id": 10,
  "message": "Sessão anônima criada com sucesso"
}
```

### GET `/auth/me`
Retorna dados do usuário autenticado.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "usuario@email.com",
  "name": "João Silva",
  "social_name": "Maria Silva",
  "pronoun": "ela",
  "profile_image_url": "https://...",
  "cpf": "12345678900",
  "role": "beneficiario",
  "is_active": true,
  "assistente_id": null,
  "org_id": 5,
  "created_at": "2025-10-26T12:00:00Z",
  "updated_at": "2025-10-26T12:00:00Z"
}
```

---

## 👥 Beneficiários (`/beneficiarios`)

### GET `/beneficiarios/me`
Retorna dados do beneficiário autenticado (apenas role BENEFICIARIO).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "name": "João Silva",
  "social_name": "Maria Silva",
  "email": "usuario@email.com",
  "cpf": "12345678900",
  "pronoun": "ela",
  "profile_image_url": "https://...",
  "assistente_id": 2,
  "org_id": 5
}
```

### GET `/beneficiarios/assistente-vinculos`
Lista beneficiários vinculados ao assistente autenticado (apenas role ASSISTENTE).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "João Silva",
    "social_name": "Maria Silva",
    "email": "usuario@email.com",
    "cpf": "12345678900",
    "pronoun": "ela",
    "profile_image_url": "https://..."
  },
  {
    "id": 3,
    "name": "Pedro Santos",
    "social_name": "Paula Santos",
    "email": "outro@email.com",
    "cpf": "98765432100",
    "pronoun": "ela",
    "profile_image_url": "https://..."
  }
]
```

---

## 🏢 Organizações (`/orgs`)

### GET `/orgs`
Lista todas as ONGs cadastradas.

**Response:**
```json
[
  {
    "id": 1,
    "name": "ONG Exemplo",
    "cnpj": "12345678000190",
    "address": "Rua Exemplo, 123",
    "city": "São Paulo",
    "state": "SP",
    "phone": "11999999999",
    "email": "contato@ongexemplo.com",
    "website": "https://ongexemplo.com",
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

### GET `/orgs/{org_id}`
Retorna detalhes de uma ONG específica.

**Response:**
```json
{
  "id": 1,
  "name": "ONG Exemplo",
  "cnpj": "12345678000190",
  "address": "Rua Exemplo, 123",
  "city": "São Paulo",
  "state": "SP",
  "phone": "11999999999",
  "email": "contato@ongexemplo.com",
  "website": "https://ongexemplo.com",
  "description": "Uma ONG dedicada ao suporte da comunidade trans",
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

## 📰 Artigos (`/articles`)

### GET `/articles`
Lista todos os artigos educacionais.

**Response:**
```json
[
  {
    "id": 1,
    "title": "Como retificar seu nome",
    "content": "A retificação de nome é o processo...",
    "category": "RETIFICACAO_NOME",
    "author_id": 5,
    "is_published": true,
    "created_at": "2025-10-26T12:00:00Z"
  }
]
```

### GET `/articles/{article_id}`
Retorna um artigo específico.

---

## 💰 Doações (`/donations`)

### POST `/donations`
Registra uma nova doação.

**Request Body:**
```json
{
  "amount": 50.00,
  "donor_name": "João Silva",
  "donor_email": "joao@email.com",
  "payment_method": "PIX",
  "org_id": 1
}
```

**Response:**
```json
{
  "id": 1,
  "amount": 50.00,
  "donor_name": "João Silva",
  "donor_email": "joao@email.com",
  "payment_method": "PIX",
  "status": "PENDING",
  "org_id": 1,
  "created_at": "2025-10-26T12:00:00Z"
}
```

### GET `/donations`
Lista todas as doações (apenas ADMIN).

---

## 📊 Métricas (`/metrics`)

### GET `/metrics/summary`
Retorna métricas gerais do sistema (apenas ADMIN).

**Response:**
```json
{
  "total_users": 150,
  "total_beneficiarios": 120,
  "total_assistentes": 25,
  "total_orgs": 10,
  "total_donations": 500,
  "total_donation_amount": 25000.00,
  "total_chats": 300,
  "total_articles": 15
}
```

---

## ☁️ Storage (`/storage`)

### POST `/storage/upload`
Faz upload de um arquivo para o Supabase Storage.

**Content-Type:** `multipart/form-data`

**Request:**
```
file: [arquivo]
folder: profile-images (opcional)
```

**Response:**
```json
{
  "url": "https://your-project.supabase.co/storage/v1/object/public/profile-images/uuid-filename.jpg",
  "path": "profile-images/uuid-filename.jpg"
}
```

---

# 🔐 Autenticação e Autorização

## Sistema de Roles

| Role | Descrição | Permissões |
|------|-----------|------------|
| `BENEFICIARIO` | Usuário final do sistema | Acesso aos próprios dados, chat, artigos |
| `ASSISTENTE` | Assistente social da ONG | Acesso aos beneficiários vinculados |
| `ADMIN` | Administrador do sistema | Acesso total a todas as funcionalidades |

## Fluxo de Autenticação

```
┌─────────────────────────────────────────┐
│ 1. Usuário envia email + senha         │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 2. API valida credenciais (bcrypt)     │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 3. Gera Access Token (JWT) + Refresh   │
│    Token (armazenado no banco)          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 4. Cliente armazena tokens             │
│    (localStorage / AsyncStorage)        │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 5. Cliente envia Access Token em cada  │
│    requisição (Header Authorization)    │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 6. Se expirado, usa Refresh Token para │
│    obter novo Access Token              │
└─────────────────────────────────────────┘
```

## Protegendo Endpoints

```python
from fastapi import Depends
from ..dependencies import get_current_user
from ..models.user import User

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Olá, {current_user.name}!"}
```

## Verificando Roles

```python
from ..dependencies import require_role
from ..models.user import Role

@router.get("/admin-only")
async def admin_route(current_user: User = Depends(require_role(Role.ADMIN))):
    return {"message": "Área restrita aos admins"}
```

---

# 🎨 Features de Personalização

## Sistema de Nome Social e Pronomes

### Priorização de Nome Social

O sistema sempre utiliza `social_name` quando disponível:

```python
preferred_name = user.social_name or user.name
```

**Exemplo:**
- `name`: "João Silva"
- `social_name`: "Maria Silva"
- **✅ Usa**: "Maria Silva"

### Pronomes Suportados

| Pronome | Uso no Sistema |
|---------|----------------|
| `ele` | Tratamento masculino |
| `ela` | Tratamento feminino |
| `elu` | Tratamento neutro |
| `null` | Tratamento genérico/neutro |

**Exemplos de uso:**
```python
if user.pronoun == "ele":
    message = f"{preferred_name}, você está bem-vindo!"
elif user.pronoun == "ela":
    message = f"{preferred_name}, você está bem-vinda!"
else:  # elu ou null
    message = f"{preferred_name}, você está bem-vinde!"
```

---

# 🧪 Testando o Sistema

## Usando a Documentação Interativa (Swagger)

1. Acesse http://localhost:8000/docs
2. Expanda o endpoint `/auth/register`
3. Clique em **"Try it out"**
4. Preencha os campos
5. Clique em **"Execute"**
6. Veja a resposta abaixo

## Usando cURL

### Registro de Usuário

```powershell
curl -X POST "http://localhost:8000/auth/register" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "maria@email.com",
    "password": "senhaSegura123",
    "name": "João Silva",
    "social_name": "Maria Silva",
    "pronoun": "ela"
  }'
```

### Login

```powershell
curl -X POST "http://localhost:8000/auth/login" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "maria@email.com",
    "password": "senhaSegura123"
  }'
```

### Acessar Endpoint Protegido

```powershell
# Primeiro, salve o access_token do login
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET "http://localhost:8000/auth/me" `
  -H "Authorization: Bearer $token"
```

## Usando Python (httpx)

```python
import httpx

# Registro
response = httpx.post(
    "http://localhost:8000/auth/register",
    json={
        "email": "maria@email.com",
        "password": "senhaSegura123",
        "name": "João Silva",
        "social_name": "Maria Silva",
        "pronoun": "ela"
    }
)
print(response.json())

# Login
response = httpx.post(
    "http://localhost:8000/auth/login",
    json={
        "email": "maria@email.com",
        "password": "senhaSegura123"
    }
)
data = response.json()
access_token = data["access_token"]

# Endpoint protegido
response = httpx.get(
    "http://localhost:8000/auth/me",
    headers={"Authorization": f"Bearer {access_token}"}
)
print(response.json())
```

## Executando Testes Automatizados

```powershell
# Instalar dependência de teste (se ainda não instalou)
pip install pytest

# Rodar todos os testes
pytest

# Rodar com mais detalhes
pytest -vv

# Rodar teste específico
pytest tests/test_beneficiarios.py

# Ver cobertura de código (requer pytest-cov)
pytest --cov=src --cov-report=html
```

---

# 🗄️ Gerenciamento de Migrações (Alembic)

## Comandos Principais

### Criar Nova Migração (Autogenerate)

```powershell
# Usando Make
make migrate m="descrição da mudança"

# Ou diretamente
alembic revision -m "descrição da mudança" --autogenerate
```

### Aplicar Migrações

```powershell
# Usando Make
make upgrade

# Ou diretamente
alembic upgrade head

# Aplicar até uma revisão específica
alembic upgrade abc123
```

### Reverter Migrações

```powershell
# Voltar uma migração
alembic downgrade -1

# Voltar até uma revisão específica
alembic downgrade abc123

# Voltar tudo
alembic downgrade base
```

### Ver Histórico

```powershell
# Histórico completo
alembic history

# Ver revisão atual
alembic current

# Ver diferenças
alembic show abc123
```

## Workflow de Desenvolvimento

1. **Modificar models** (`src/app/models/*.py`)
2. **Gerar migração**: `make migrate m="add new field to users"`
3. **Revisar migração** gerada em `alembic/versions/`
4. **Aplicar migração**: `make upgrade`
5. **Testar** as mudanças no banco

---

# 📊 Monitoramento e Logs

## Logs da Aplicação

### Via Docker

```powershell
# Ver logs em tempo real
docker compose logs -f api

# Ver últimas 100 linhas
docker compose logs --tail=100 api

# Logs de múltiplos serviços
docker compose logs -f api db
```

### Localmente

Os logs aparecem diretamente no terminal onde o Uvicorn está rodando.

## Estrutura dos Logs

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:54321 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:54321 - "POST /auth/login HTTP/1.1" 200 OK
INFO:     127.0.0.1:54321 - "GET /auth/me HTTP/1.1" 200 OK
```

## Health Check

Endpoint `/health` para monitoramento de disponibilidade:

```json
{
  "ok": true,
  "message": "API is running"
}
```

Use em ferramentas de monitoramento (Uptime Robot, Pingdom, etc).

---

# 🔐 Segurança e Boas Práticas

## ✅ Implementado

- **Hashing de Senhas**: Bcrypt com salt automático
- **JWT**: Tokens assinados e com expiração
- **Refresh Tokens**: Armazenados no banco (revogáveis)
- **Validação de Entrada**: Pydantic schemas em todos os endpoints
- **CORS Configurável**: Lista de origens permitidas via `.env`
- **Variáveis de Ambiente**: Credenciais nunca no código
- **Service Role Key**: Usado apenas server-side (nunca exposto ao frontend)
- **SQL Injection**: Protegido pelo SQLAlchemy ORM

## 🚧 Recomendado para Produção

- **HTTPS**: Sempre use TLS/SSL em produção
- **Rate Limiting**: Implemente limite de requisições (ex: `slowapi`)
- **Helmet/Security Headers**: Use middleware de segurança
- **Validação de Upload**: Verificar tipo MIME e tamanho de arquivos
- **Logs Sanitizados**: Nunca logar senhas ou tokens
- **Backup Regular**: Banco de dados e storage
- **Firewall**: Restringir acesso ao banco apenas da API
- **Monitoramento**: Alertas para erros e comportamento suspeito

## Proteção de Dados (LGPD)

- Armazenamento seguro de dados pessoais
- Suporte a exclusão de conta (direito ao esquecimento)
- Minimização de dados coletados
- Consentimento para uso de dados
- Logs de acesso para auditoria

---

# 🚀 Deploy em Produção

## Opções de Hospedagem

### 1. Railway (Recomendado para Iniciantes)

1. Conecte seu repositório GitHub
2. Selecione a branch `main`
3. Railway detecta automaticamente o `Dockerfile`
4. Configure as variáveis de ambiente no dashboard
5. Deploy automático a cada push

**Vantagens:**
- Setup rápido e fácil
- HTTPS automático
- CI/CD integrado
- Free tier disponível

### 2. Render

Similar ao Railway, com free tier generoso.

1. Conecte o GitHub
2. Selecione "Web Service"
3. Configure variáveis de ambiente
4. Deploy automático

### 3. AWS (Elastic Beanstalk / ECS / EC2)

Maior controle e escalabilidade:

**Elastic Beanstalk:**
```powershell
# Instalar EB CLI
pip install awsebcli

# Inicializar
eb init

# Criar ambiente
eb create production

# Deploy
eb deploy
```

**Docker em EC2:**
```bash
# SSH no servidor
ssh -i your-key.pem ubuntu@your-ec2-ip

# Clonar repositório
git clone https://github.com/INTELI-NO-IMPACTO/api-core.git
cd api-core

# Configurar .env
nano .env

# Subir com docker compose
docker compose -f docker-compose.prod.yml up -d
```

### 4. Google Cloud (Cloud Run / GKE)

**Cloud Run (Serverless):**
```bash
# Build e push da imagem
gcloud builds submit --tag gcr.io/PROJECT_ID/api-core

# Deploy
gcloud run deploy api-core \
  --image gcr.io/PROJECT_ID/api-core \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Configuração de CI/CD (GitHub Actions)

Crie `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker Image
        run: docker build -t api-core:latest .
      
      - name: Run Tests
        run: docker run api-core:latest pytest
      
      - name: Deploy to Railway
        run: |
          # Comandos de deploy
```

## Checklist de Produção

- [ ] Configurar HTTPS (TLS/SSL)
- [ ] Definir `JWT_SECRET` forte e único
- [ ] Configurar CORS para domínios específicos
- [ ] Ativar rate limiting
- [ ] Configurar backup automático do banco
- [ ] Configurar monitoramento (Sentry, DataDog, etc)
- [ ] Logs centralizados (Loggly, Papertrail, etc)
- [ ] Health checks configurados
- [ ] Documentação atualizada
- [ ] Testes passando
- [ ] Variáveis de ambiente configuradas no host

---

# 🛠️ Troubleshooting

## Problemas Comuns

### ❌ Erro: "Port 8000 is already in use"

**Solução:**

```powershell
# Windows - Encontrar processo usando a porta
netstat -ano | findstr :8000

# Matar processo (substitua PID)
taskkill /PID <PID> /F

# Ou mudar a porta no docker-compose.yml
ports:
  - "8001:8000"
```

### ❌ Erro: "ModuleNotFoundError: No module named 'fastapi'"

**Solução:**

```powershell
# Certifique-se de estar no venv
.\.venv\Scripts\Activate.ps1

# Reinstale as dependências
pip install -r requirements.txt
```

### ❌ Erro: "Cannot connect to database"

**Solução:**

1. Verifique se `DATABASE_URL` está correto no `.env`
2. Teste a conexão no Supabase Dashboard
3. Verifique se o IP está na whitelist (Supabase > Settings > Database > Connection Pooling)
4. Confirme que a senha está correta (sem caracteres especiais problemáticos)

### ❌ Erro: "Supabase storage upload failed"

**Solução:**

1. Verifique se o bucket existe no Supabase Storage
2. Confirme que `SUPABASE_SERVICE_ROLE_KEY` está correto
3. Verifique políticas de acesso do bucket (RLS - Row Level Security)

### ❌ Erro: "JWT token expired"

**Solução:**

- Tokens expiram após `JWT_EXPIRES_MIN` (padrão: 60 min)
- Use o endpoint `/auth/refresh` com o `refresh_token` para obter novo `access_token`
- Se refresh token também expirou, faça login novamente

### ❌ Docker não inicia / Container para imediatamente

**Solução:**

```powershell
# Ver logs detalhados
docker compose logs api

# Rebuild completo
docker compose down
docker compose build --no-cache
docker compose up
```

### ❌ Migrações Alembic com erro

**Solução:**

```powershell
# Ver status atual
alembic current

# Ver histórico
alembic history

# Voltar uma versão e tentar novamente
alembic downgrade -1
alembic upgrade head

# Se necessário, gerar nova migração limpa
alembic revision -m "fix: regenerate migration"
```

---

# 📚 Documentação Adicional

- **[AGENTS.md](./AGENTS.md)** - Guidelines para desenvolvimento e contribuição
- **[TODOS.md](./TODOS.md)** - Lista de melhorias e funcionalidades planejadas
- **[FastAPI Docs](https://fastapi.tiangolo.com/)** - Documentação oficial do FastAPI
- **[SQLAlchemy Docs](https://docs.sqlalchemy.org/)** - Documentação do ORM
- **[Alembic Docs](https://alembic.sqlalchemy.org/)** - Documentação de migrações
- **[Supabase Docs](https://supabase.com/docs)** - Documentação do Supabase
- **[Pydantic Docs](https://docs.pydantic.dev/)** - Validação de dados

---

# 🤝 Contribuindo

Contribuições são muito bem-vindas! Para contribuir:

## 1. Faça um Fork do Projeto

```powershell
git clone https://github.com/seu-usuario/api-core.git
cd api-core
```

## 2. Crie uma Branch para sua Feature

```powershell
git checkout -b feature/MinhaNovaFeature
```

## 3. Desenvolva e Teste

```powershell
# Faça suas alterações
# ...

# Rode os testes
pytest

# Gere migrações se alterou models
make migrate m="descrição"
```

## 4. Commit suas Mudanças

Seguimos o padrão **Conventional Commits**:

```powershell
git add .
git commit -m "feat: adiciona endpoint de estatísticas"
```

**Tipos de commit:**
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `style:` - Formatação (sem mudança de lógica)
- `refactor:` - Refatoração de código
- `test:` - Adição/correção de testes
- `chore:` - Manutenção (dependencies, config, etc)
- `perf:` - Melhoria de performance

## 5. Push e Pull Request

```powershell
git push origin feature/MinhaNovaFeature
```

Abra um Pull Request no GitHub com:
- **Título claro** descrevendo a mudança
- **Descrição detalhada** do que foi alterado e por quê
- **Screenshots** (se aplicável)
- **Como testar** as mudanças
- **Checklist**:
  - [ ] Código testado localmente
  - [ ] Testes automatizados passando
  - [ ] Documentação atualizada
  - [ ] Migrações criadas (se aplicável)

---

# 📄 Licença

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/">
  <a property="dct:title" rel="cc:attributionURL" href="https://github.com/INTELI-NO-IMPACTO/api-core">
    Meu Nome Gov - API Core
  </a> by 
  <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://www.inteli.edu.br/">
    Inteli - Instituto de Tecnologia e Liderança
  </a> is licensed under 
  <a href="https://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">
    CC BY 4.0
    <img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" alt="">
    <img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" alt="">
  </a>
</p>

---

# 📞 Contato e Suporte

- **GitHub**: [INTELI-NO-IMPACTO](https://github.com/INTELI-NO-IMPACTO)
- **Email Fernando Machado**: fernando.machado.ismart@gmail.com
- **Email Gabriel Pelinsari**: gabriel.pelinsari.projetos@gmail.com
- **Email João Paulo da Silva**: joaopaulo.silva.ismart@gmail.com
- **Email Matheus Ribeiro**: matheus.ribeiro@sou.inteli.edu.br

**Repositórios Relacionados:**
- [Chatbot](https://github.com/INTELI-NO-IMPACTO/chatbot) - Sistema de chatbot inclusivo
- [Frontend Web](https://github.com/INTELI-NO-IMPACTO/web-app) - Interface web do sistema

---

<p align="center">
  Feito com 💜 pela equipe <strong>INTELI-NO-IMPACTO</strong>
  <br>
  <em>Tecnologia com propósito, acolhimento e respeito</em>
  <br><br>
  <strong>Lua</strong> - Facilitando o acesso a direitos e dignidade para a comunidade trans brasileira
</p>
