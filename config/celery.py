import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Lê configurações CELERY_* do settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-descobrir tasks.py nos apps
app.autodiscover_tasks()

@worker_ready.connect
def at_worker_ready(sender, **kwargs):
    """
    Dispara uma sincronização inicial assim que o worker estiver pronto.
    Útil em deploy/boot para já popular o banco sem esperar o beat.
    """
    from monitoring.tasks import (
        sync_libre_patients_task,
        sync_libre_glucose_task,
        rebuild_patient_state_task,
    )

    # roda já a sync de pacientes
    sync_libre_patients_task.apply_async()

    # dá um espacinho e puxa glicose
    sync_libre_glucose_task.apply_async(countdown=30)

    # depois reconstruir o estado
    rebuild_patient_state_task.apply_async(countdown=60)