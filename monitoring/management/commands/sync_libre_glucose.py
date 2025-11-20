# monitoring/management/commands/sync_libre_glucose.py
from django.core.management.base import BaseCommand
from django.utils import timezone

from monitoring.libre_client import get_libre_client
from monitoring.models import Patient, GlucoseReading


class Command(BaseCommand):
    help = "Sincroniza leituras de glicose dos pacientes do LibreLinkUp para o banco (GlucoseReading)."

    def handle(self, *args, **options):
        client = get_libre_client()

        patients = Patient.objects.filter(is_active=True)
        total_new = 0

        if not patients.exists():
            self.stdout.write("Nenhum paciente ativo encontrado. Rode `python manage.py test_libre` primeiro.")
            return

        self.stdout.write(self.style.NOTICE(f"Sincronizando glicose de {patients.count()} paciente(s)..."))

        for patient in patients:
            identifier = patient.libre_patient_id  # usa o patient_id, não o id da conexão

            self.stdout.write(f"\nPaciente: {patient.full_name} ({identifier})")

            # 1) Última leitura
            try:
                latest = client.latest(patient_identifier=identifier)
            except Exception as e:
                if "glucoseMeasurement" in str(e) or "glucoseItem" in str(e):
                    self.stdout.write(
                        self.style.WARNING(
                            f"Sem dados de glicemia para {patient.full_name} (latest)."
                        )
                    )
                    latest = None
                else:
                    self.stdout.write(self.style.ERROR(f"Erro em latest() para {patient.full_name}: {e}"))
                    latest = None

            # 2) Histórico curto (graph)
            try:
                graph_data = client.graph(patient_identifier=identifier)
            except Exception as e:
                if "glucoseMeasurement" in str(e) or "glucoseItem" in str(e):
                    self.stdout.write(
                        self.style.WARNING(
                            f"Sem histórico de glicemia para {patient.full_name} (graph)."
                        )
                    )
                    graph_data = []
                else:
                    self.stdout.write(self.style.ERROR(f"Erro em graph() para {patient.full_name}: {e}"))
                    graph_data = []

            new_count = 0

            if latest:
                if self._save_measurement(patient, latest):
                    new_count += 1

            for m in graph_data:
                if self._save_measurement(patient, m):
                    new_count += 1

            patient.last_glucose_sync = timezone.now()
            patient.save(update_fields=["last_glucose_sync"])

            total_new += new_count
            self.stdout.write(self.style.SUCCESS(f"Novas leituras salvas para {patient.full_name}: {new_count}"))

        self.stdout.write(self.style.SUCCESS(f"\nSync concluído. Total de novas leituras: {total_new}"))

    def _save_measurement(self, patient, measurement) -> bool:
        """
        Salva uma medição, atualiza o estado do paciente
        e retorna True se criou uma leitura nova.
        """
        ts = getattr(measurement, "factory_timestamp", None) or getattr(measurement, "timestamp", None)
        value = (
            getattr(measurement, "value_in_mg_per_dl", None)
            or getattr(measurement, "value", None)
        )

        if ts is None or value is None:
            return False

        trend_obj = getattr(measurement, "trend", None)
        if hasattr(trend_obj, "name"):
            trend_str = trend_obj.name
        else:
            trend_str = str(trend_obj) if trend_obj is not None else ""

        raw_data = None
        if hasattr(measurement, "model_dump"):
            try:
                raw_data = measurement.model_dump(mode="json")
            except TypeError:
                raw_data = measurement.model_dump()
        else:
            raw_data = str(measurement)

        obj, created = GlucoseReading.objects.get_or_create(
            patient=patient,
            timestamp=ts,
            defaults={
                "value_mg_dl": value,
                "is_high": getattr(measurement, "is_high", False),
                "is_low": getattr(measurement, "is_low", False),
                "trend": trend_str,
                "raw": raw_data,
            },
        )

        # Atualizar estado do Patient (flags para alertas)
        if created:
            # primeira vez que esse paciente tem qualquer dado?
            if not patient.has_glucose_data:
                patient.has_glucose_data = True
                patient.first_glucose_at = ts

        # se essa leitura é mais recente que o last_glucose_at, atualiza
        if patient.last_glucose_at is None or ts > patient.last_glucose_at:
            patient.last_glucose_at = ts
            patient.last_glucose_value = value
            patient.last_is_high = getattr(measurement, "is_high", False)
            patient.last_is_low = getattr(measurement, "is_low", False)
            patient.last_trend = trend_str

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

        return created