# 📡 Saúde-IA API — Documentação (v1)

Esta é a documentação oficial da API utilizada para ingestão e consulta de dados de glicose provenientes do LibreLinkUp.

A API é protegida via **JWT (JSON Web Tokens)** e segue o padrão de versionamento:

`/api/v1/`

## Autenticação (JWT)

### Obter token de acesso
**POST** `/api/v1/auth/token/`

Request:
```json
{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

Response:
```json
{
  "access": "<ACCESS_TOKEN>",
  "refresh": "<REFRESH_TOKEN>"
}
```

### Renovar token
**POST** `/api/v1/auth/token/refresh/`

```json
{
  "refresh": "<REFRESH_TOKEN>"
}
```

### Usando o token
```
Authorization: Bearer <ACCESS_TOKEN>
```

# Healthcheck
**GET** `/health/` — público

```json
{"django":"ok","postgres":"ok","redis":"ok","celery":"ok"}
```

# 👥 Pacientes

## Listar pacientes
`GET /api/v1/patients/`
```json
[
  {
    "id": 1,
    "first_name": "Lucas",
    "last_name": "Emmanuel",
    "libre_connection_id": "60021a89-c3c1-11f0-94dd-2a8c427d6d5c",
    "libre_patient_id": "738bbd35-c0bb-11f0-bb92-326171c61dfc",
    "has_glucose_data": true,
    "first_glucose_at": "2025-11-19T12:24:58Z",
    "last_glucose_at": "2025-11-20T06:06:12Z"
  }
]
```

## Detalhe
`GET /api/v1/patients/{libre_patient_id}/`
```bash
/api/v1/patients/738bbd35-c0bb-11f0-bb92-326171c61dfc/
```

## Resumo
`GET /api/v1/patients/summary/`
```json
{
  "total_patients": 2,
  "patients_with_glucose": 1,
  "patients_without_glucose": 1,
  "latest_glucose_at": "2025-11-20T06:06:12Z"
}
```

## Estatísticas
`GET /api/v1/patients/{libre_patient_id}/glucose_stats/?days=7`
```json
{
  "patient": {
    "libre_patient_id": "738bbd35-c0bb-11f0-bb92-326171c61dfc",
    "first_name": "Lucas",
    "last_name": "Emmanuel"
  },
  "window_days": 7,
  "count": 320,
  "avg_mg_dl": 108.4,
  "min_mg_dl": 72,
  "max_mg_dl": 188
}
```

## Histórico
`GET /api/v1/patients/{libre_patient_id}/glucose_history/?days=7`
```json
{
  "patient": { ... },
  "window_days": 7,
  "readings": [
    {
      "timestamp": "2025-11-19T12:24:58Z",
      "value_mg_dl": 106,
      "is_low": false,
      "is_high": false,
      "trend": "STABLE"
    }
  ]
}
```

# Glicose

## Todas leituras
`GET /api/v1/glucose/`

## Últimas por paciente
`GET /api/v1/glucose/latest/`
```json
[
  {
    "patient": { ... },
    "timestamp": "2025-11-20T06:06:12Z",
    "value_mg_dl": 110,
    "trend": "RISING"
  }
]
```