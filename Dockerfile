# Usar Python 3.12 como base
FROM python:3.12-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias para psycopg2

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY
ARG http_proxy
ARG https_proxy
ARG no_proxy

ENV HTTP_PROXY=${HTTP_PROXY} \
    HTTPS_PROXY=${HTTPS_PROXY} \
    NO_PROXY=${NO_PROXY} \
    http_proxy=${http_proxy} \
    https_proxy=${https_proxy} \
    no_proxy=${no_proxy}

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta 8000
EXPOSE 8000

# Comando padrão (será sobrescrito no docker-compose para dev)
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
