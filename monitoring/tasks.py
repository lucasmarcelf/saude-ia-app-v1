from celery import shared_task
from django.core.management import call_command


@shared_task
def sync_libre_patients_task():
    """
    Tarefa periódica: roda o management command que sincroniza pacientes.
    """
    call_command("sync_libre_patients")


@shared_task
def sync_libre_glucose_task():
    """
    Tarefa periódica: roda o management command que sincroniza leituras.
    """
    call_command("sync_libre_glucose")


@shared_task
def rebuild_patient_state_task():
    """
    Opcional: recalcula o estado derivado dos pacientes (has_glucose_data etc).
    """
    call_command("rebuild_patient_glucose_state")

@shared_task
def health_ping():
    """
    Task mínima usada pelo /health/ para verificar
    se o worker do Celery está aceitando jobs.
    """
    return "pong"