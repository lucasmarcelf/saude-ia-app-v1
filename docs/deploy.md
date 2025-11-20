# Deploy em Produção — Saúde-IA (EC2 Ubuntu)

Este guia descreve como subir o sistema Saúde-IA em uma VM Ubuntu (AWS EC2), integrando:

- Docker
- Docker Compose
- Django
- Postgres
- Redis
- Celery (worker + beat)
- Nginx
- Portainer

---

# 1. Pré-requisitos

Na VM:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker ubuntu
```
Re-login

## Clonar projeto
```bash
git clone https://github.com/lucasmarcelf/saude-ia-app-v1.git
cd saude-ia-app-v1
```
## Criar arquivo .env.prod
Copiar exemplo:
```bash
cp .env.example .env.prod
nano .env.prod
```
Configurar:
```bash
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,IP_DA_VM

LIBRE_EMAIL=...
LIBRE_PASSWORD=...

DB_NAME=saude_ia
DB_USER=saude_ia
DB_PASSWORD=senha_forte
DB_HOST=db
DB_PORT=5432

POSTGRES_DB=saude_ia
POSTGRES_USER=saude_ia
POSTGRES_PASSWORD=senha_forte

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```
## Buildar aplicação
```bash
sudo docker compose -f docker-compose.prod.yaml build
```

## Rodar migrações
```bash
sudo docker compose -f docker-compose.prod.yaml run --rm web python manage.py migrate
```

## Criar superuser
```bash
sudo docker compose -f docker-compose.prod.yaml run --rm web python manage.py createsuperuser
```

## Coletar estáticos
```bash
sudo docker compose -f docker-compose.prod.yaml run --rm web python manage.py collectstatic --noinput
```

## Subir a stack completa
```bash
sudo docker compose -f docker-compose.prod.yaml up -d --build
```