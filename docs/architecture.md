# Arquitetura — Saúde-IA

Esta documentação descreve a arquitetura do sistema Saúde-IA.

# Visão Geral
LibreLinkUp → Celery Beat → Celery Worker → Postgres → Django API → Nginx → Cliente

Componentes:

- **Django + DRF**  
  API REST, token JWT, endpoints `/api/v1/*`.

- **pylibrelinkup**  
  Cliente oficial em Python usado para sincronizar pacientes e leituras.

- **Celery Worker**  
  Executa tasks assíncronas:
  - sincronização de pacientes
  - sincronização de glicose
  - reconstrução de estados
  - health_ping

- **Celery Beat**  
  Scheduler das tasks periódicas:
  - a cada 5 minutos: sync de glicose
  - a cada 10 minutos: sync de pacientes

- **Redis**  
  Broker do Celery.

- **Postgres**  
  Banco de dados principal.

- **Gunicorn**  
  Servidor WSGI de produção.

- **Nginx**  
  Reverse proxy servindo porta 80.

- **Portainer**  
  Painel de gestão Docker (porta 9443).

---

# Containers (Docker)

### 1. `web`
- Django + Gunicorn
- Expõe internamente `8000`
- Depende de Postgres e Redis

### 2. `db`
- Postgres 16
- Volume persistente: `postgres_data`

### 3. `redis`
- Redis 7
- Broker para Celery Worker/Beat

### 4. `celery-worker`
- Executa tasks assíncronas

### 5. `celery-beat`
- Dispara tasks periódicas

### 6. `nginx`
- Recebe tráfego externo (porta 80)
- Proxy para `web:8000`
- Serve arquivos estáticos

### 7. `portainer`
- Dashboard de gerenciamento Docker
- Porta externa 9443

---

# Fluxo de Ingestão

1. Celery Beat dispara:
   - `sync_libre_patients_task`
   - `sync_libre_glucose_task`

2. Celery Worker:
   - autentica no LibreLinkUp
   - obtém pacientes conectados
   - obtém últimas leituras de glicose
   - salva no Postgres

3. Django expõe:
   - pacientes
   - histórico
   - estatísticas
   - última leitura global

---

# Healthcheck

Endereço: `/health/`  
Verifica:

- Django OK?
- PostgreSQL responde?
- Redis responde?
- Celery enfileira tasks?

Resposta:

```json
{
  "django": "ok",
  "postgres": "ok",
  "redis": "ok",
  "celery": "ok"
}
```
---

# Segurança

- JWT para APIs /api/v1/
- ALLOWED_HOSTS com IP/host em .env.prod
- Portainer exposto somente em 9443 → deve ser limitado a IP específico
- Nginx como única porta pública: 80 (ou 443, futuro)
