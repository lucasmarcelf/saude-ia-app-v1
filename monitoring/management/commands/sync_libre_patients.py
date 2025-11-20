from django.core.management.base import BaseCommand
from monitoring.libre_client import get_libre_client
from monitoring.models import Patient


class Command(BaseCommand):
    help = "Sincroniza lista de pacientes do LibreLinkUp para o banco."

    def handle(self, *args, **options):
        client = get_libre_client()
        patients = client.get_patients()

        created = 0
        updated = 0

        for p in patients:
            obj, was_created = Patient.objects.update_or_create(
                libre_connection_id=p.id,
                defaults={
                    "libre_patient_id": p.patient_id,
                    "first_name": p.first_name,
                    "last_name": p.last_name,
                    "is_active": True,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Pacientes sincronizados: novos={created}, atualizados={updated}"
            )
        )