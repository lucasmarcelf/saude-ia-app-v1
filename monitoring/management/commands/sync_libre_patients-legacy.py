# monitoring/management/commands/test_libre.py
from django.core.management.base import BaseCommand

from monitoring.libre_client import get_libre_client
from monitoring.models import Patient


class Command(BaseCommand):
    help = "Testa integração com LibreLinkUp e salva/atualiza pacientes no banco"

    def handle(self, *args, **options):
        client = get_libre_client()

        self.stdout.write(self.style.NOTICE("Buscando pacientes do LibreLinkUp..."))
        patients = client.get_patients()

        self.stdout.write(f"Qtd pacientes retornados: {len(patients)}")

        created = 0
        updated = 0

        for p in patients:
            # p é pylibrelinkup.models.data.Patient
            self.stdout.write(f"- {p.first_name} {p.last_name} | id={p.id} | patient_id={p.patient_id}")

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
                f"Pacientes salvos no Postgres. Novos: {created}, atualizados: {updated}."
            )
        )

        # Opcional: testar a última glicemia do primeiro paciente
        if patients:
            first = patients[0]
            self.stdout.write(self.style.NOTICE("\nBuscando última glicemia do primeiro paciente..."))
            latest = client.latest(patient_identifier=first)
            if latest:
                self.stdout.write(
                    f"Último valor: {latest.value_in_mg_per_dl} mg/dL "
                    f"em {latest.timestamp} "
                    f"(factory={latest.factory_timestamp}, "
                    f"is_low={latest.is_low}, is_high={latest.is_high}, trend={latest.trend})"
                )
            else:
                self.stdout.write("Nenhuma leitura encontrada (latest).")