# Dockerfile
FROM python:3.12-slim

# Evitar prompts interativos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependências de sistema (psycopg2, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements se você tiver (se ainda não tem, podemos gerar com pip freeze)
# Por enquanto, vamos usar um requirements.txt simples. Se ainda não existir, cria um depois.
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do projeto
COPY . /app/

# Expor a porta do Gunicorn
EXPOSE 8000

# Comando padrão: rodar gunicorn com o WSGI do Django
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]