# Repository Guidelines

## Project Structure & Module Organization
- `src/app/main.py` inicializa a API FastAPI e registra os routers.
- `src/app/routers/` concentra endpoints (ex.: `auth.py`, `storage.py`); mantenha um arquivo por contexto de domínio.
- `src/app/models/` define entidades SQLAlchemy; os schemas Pydantic ficam em `src/app/schemas/`.
- `src/app/utils/` abriga utilitários compartilhados, como integrações Supabase.
- Migrações Alembic residem em `alembic/`, com configurações em `alembic.ini`.
- Crie testes sob `tests/`, espelhando a estrutura dos módulos que exercitam.

## Build, Test, and Development Commands
- `docker compose build` — gera a imagem com dependências (usa proxies/environment herdados).
- `docker compose up` — sobe API e dependências locais com hot reload.
- `make run` — executa `uvicorn` diretamente no host (útil fora de containers).
- `pytest` — roda a suíte de testes; adicione `-q` ou `-vv` conforme necessário.
- `alembic upgrade head` — aplica migrações pendentes ao banco configurado.

## Coding Style & Naming Conventions
- Utilize Python 3.12+, PEP 8 e indentação de 4 espaços; preferir type hints explícitos.
- Nomine routers com nomes de recursos (`users`, `storage`); siga o padrão `router = APIRouter(...)`.
- Schemas Pydantic terminam em `*Schema` ou `*Payload`; modelos SQLAlchemy em CamelCase.
- Configure segredos via `.env`; nunca versione chaves Supabase ou JWT.

## Testing Guidelines
- Adote `pytest` com arquivos `test_<modulo>.py` e fixtures em `conftest.py`.
- Cubra rotas novas com testes de integração usando o `TestClient`.
- Garanta que respostas críticas tratem erros externos (ex.: falhas Supabase) com asserts dedicados.
- Mantenha a cobertura acima de 80% para módulos recém-criados.

## Commit & Pull Request Guidelines
- Commits curtos, em imperativo (“Add storage router”), descrevendo o impacto principal.
- Vincule issues no corpo do commit/PR (`Refs #42`) quando pertinente.
- Antes de abrir PR, rode `pytest` e, se relevante, `alembic upgrade --sql` para validar migrações.
- PRs devem incluir descrição clara, passos de teste executados e pontos de atenção (ex.: novas variáveis de ambiente).

## Security & Configuration Tips
- Revise `.env.example` ao introduzir configs; documente valores obrigatórios.
- Use a Service Role Key apenas em ambientes controlados (server-side); para clientes, prefira a anon key.
- Periodicamente rode `pip install --upgrade --dry-run -r requirements.txt` dentro do container para identificar atualizações seguras.
