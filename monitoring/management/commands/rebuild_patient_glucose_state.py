# monitoring/management/commands/rebuild_patient_glucose_state.py
from django.core.management.base import BaseCommand
from django.utils import timezone

from monitoring.models import Patient, GlucoseReading


class Command(BaseCommand):
    help = "Recalcula has_glucose_data, first_glucose_at e last_* dos pacientes a partir das leituras existentes."

    def handle(self, *args, **options):
        patients = Patient.objects.all()
        total = patients.count()
        updated = 0

        self.stdout.write(f"Recalculando estado de glicose para {total} paciente(s)...")

        for patient in patients:
            qs = GlucoseReading.objects.filter(patient=patient).order_by("timestamp")

            if not qs.exists():
                # Sem leituras: limpa estado
                patient.has_glucose_data = False
                patient.first_glucose_at = None
                patient.last_glucose_at = None
                patient.last_glucose_value = None
                patient.last_is_high = False
                patient.last_is_low = False
                patient.last_trend = ""
                patient.save(
                    update_fields=[
                        "has_glucose_data",
                        "first_glucose_at",
                        "last_glucose_at",
                        "last_glucose_value",
                        "last_is_high",
                        "last_is_low",
                        "last_trend",
                    ]
                )
                self.stdout.write(f"- {patient.full_name}: sem leituras, estado limpo.")
                continue

            first = qs.first()
            last = qs.last()

            patient.has_glucose_data = True
            patient.first_glucose_at = first.timestamp
            patient.last_glucose_at = last.timestamp
            patient.last_glucose_value = last.value_mg_dl
            patient.last_is_high = last.is_high
            patient.last_is_low = last.is_low
            patient.last_trend = last.trend

            patient.save(
                update_fields=[
                    "has_glucose_data",
                    "first_glucose_at",
                    "last_glucose_at",
                    "last_glucose_value",
                    "last_is_high",
                    "last_is_low",
                    "last_trend",
                ]
            )
            updated += 1
            self.stdout.write(f"- {patient.full_name}: {qs.count()} leituras, estado recalculado.")

        self.stdout.write(self.style.SUCCESS(f"Backfill concluído. Pacientes atualizados: {updated}"))