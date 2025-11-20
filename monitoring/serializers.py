# monitoring/serializers.py
from rest_framework import serializers
from .models import Patient, GlucoseReading

class HealthStatusSerializer(serializers.Serializer):
    django = serializers.CharField()
    postgres = serializers.CharField()
    redis = serializers.CharField()
    celery = serializers.CharField()
    
class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "libre_patient_id",
            "has_glucose_data",
            "first_glucose_at",
            "last_glucose_at",
            "last_glucose_value",
            "last_is_high",
            "last_is_low",
            "last_trend",
        ]


class GlucoseReadingSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(source="patient.id", read_only=True)
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)

    class Meta:
        model = GlucoseReading
        fields = [
            "id",
            "patient_id",
            "patient_name",
            "timestamp",
            "value_mg_dl",
            "is_high",
            "is_low",
            "trend",
        ]


class GlucoseReadingCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlucoseReading
        fields = [
            "timestamp",
            "value_mg_dl",
            "is_high",
            "is_low",
            "trend",
        ]