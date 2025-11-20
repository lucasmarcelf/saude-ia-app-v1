# monitoring/models.py
from django.db import models


class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    libre_connection_id = models.UUIDField(unique=True)
    libre_patient_id = models.UUIDField()

    is_active = models.BooleanField(default=True)

    has_glucose_data = models.BooleanField(default=False)
    first_glucose_at = models.DateTimeField(blank=True, null=True)
    last_glucose_at = models.DateTimeField(blank=True, null=True)
    last_glucose_value = models.FloatField(blank=True, null=True)
    last_is_high = models.BooleanField(default=False)
    last_is_low = models.BooleanField(default=False)
    last_trend = models.CharField(max_length=32, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_glucose_sync = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    

class GlucoseReading(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="readings",
    )

    timestamp = models.DateTimeField(db_index=True)  # factory_timestamp / timestamp
    value_mg_dl = models.FloatField()

    is_high = models.BooleanField(default=False)
    is_low = models.BooleanField(default=False)
    trend = models.CharField(max_length=32, blank=True)

    raw = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("patient", "timestamp")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.patient.full_name} @ {self.timestamp} = {self.value_mg_dl} mg/dL"