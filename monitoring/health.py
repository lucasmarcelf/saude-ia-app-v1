# monitoring/health.py
from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
import os
import redis

from .tasks import health_ping  # vamos criar já já


def health_check(request):
    status = {"django": "ok"}

    # Check Postgres
    try:
        db_conn = connections["default"]
        db_conn.cursor()
        status["postgres"] = "ok"
    except OperationalError:
        status["postgres"] = "error"

    # Check Redis (broker do Celery)
    try:
        redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
        r = redis.Redis.from_url(redis_url)
        r.ping()
        status["redis"] = "ok"
    except Exception:
        status["redis"] = "error"

    # Check Celery (bonus) – ver se o worker consegue receber uma task
    try:
        result = health_ping.delay()
        # não vamos esperar o resultado, só testar se conseguimos enfileirar
        status["celery"] = "ok"
    except Exception:
        status["celery"] = "error"

    return JsonResponse(status)