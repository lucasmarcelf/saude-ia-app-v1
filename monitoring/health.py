import os
import redis
from django.db import connections
from django.db.utils import OperationalError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .tasks import health_ping
from .serializers import HealthStatusSerializer


class HealthCheckView(APIView):
    """
    Healthcheck simples da aplicação.
    - Verifica Django, Postgres, Redis e Celery.
    - Não exige autenticação (público).
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # ignora autenticação padrão do DRF

    def get(self, request):
        status = {"django": "ok"}

        # Postgres
        try:
            db_conn = connections["default"]
            db_conn.cursor()
            status["postgres"] = "ok"
        except OperationalError:
            status["postgres"] = "error"

        # Redis
        try:
            redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
            r = redis.Redis.from_url(redis_url)
            r.ping()
            status["redis"] = "ok"
        except Exception:
            status["redis"] = "error"

        # Celery
        try:
            result = health_ping.delay()
            # não esperamos resposta; só testamos enfileiramento
            status["celery"] = "ok"
        except Exception:
            status["celery"] = "error"

        # usa o serializer só pra documentar o formato
        serializer = HealthStatusSerializer(status)
        return Response(serializer.data)