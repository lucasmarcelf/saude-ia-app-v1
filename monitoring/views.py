from django.shortcuts import render

# Create your views here.
from datetime import timedelta

from django.db.models import Avg, Min, Max, Count, Q
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics

from .models import Patient, GlucoseReading
from .serializers import (
    PatientSerializer,
    GlucoseReadingSerializer,
    GlucoseReadingCompactSerializer,
)


# ========== PATIENTS ==========

class PatientListAPIView(generics.ListAPIView):
    """
    GET /api/patients/
    Lista de pacientes com estado atual (última glicose, flags).
    """
    queryset = Patient.objects.all().order_by("first_name", "last_name")
    serializer_class = PatientSerializer


class PatientDetailAPIView(generics.RetrieveAPIView):
    """
    GET /api/patients/{libre_patient_id}/
    Detalhe do paciente por libre_patient_id (UUID vindo do Libre).
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = "libre_patient_id"


class PatientGlucoseStatsAPIView(APIView):
    """
    GET /api/patients/{id}/glucose_stats/?days=7

    Retorna estatísticas básicas:
    - total_readings
    - avg, min, max
    - percent_low (<70), in_range (70–180), high (>180)
    """
    def get(self, request, libre_patient_id):
        days = int(request.query_params.get("days", 7))
        now = timezone.now()
        since = now - timedelta(days=days)

        patient = Patient.objects.get(libre_patient_id=libre_patient_id)
        qs = GlucoseReading.objects.filter(patient=patient, timestamp__gte=since)
        
        total = qs.count()
        if total == 0:
            data = {
                "patient_id": patient.id,
                "total_readings": 0,
                "days": days,
                "avg": None,
                "min": None,
                "max": None,
                "percent_low": 0.0,
                "percent_in_range": 0.0,
                "percent_high": 0.0,
            }
            return Response(data)

        agg = qs.aggregate(
            avg=Avg("value_mg_dl"),
            min_val=Min("value_mg_dl"),
            max_val=Max("value_mg_dl"),
        )

        low_count = qs.filter(value_mg_dl__lt=70).count()
        high_count = qs.filter(value_mg_dl__gt=180).count()
        in_range_count = total - low_count - high_count

        data = {
            "patient_id": patient.id,
            "total_readings": total,
            "days": days,
            "avg": agg["avg"],
            "min": agg["min_val"],
            "max": agg["max_val"],
            "percent_low": round(low_count / total * 100, 2),
            "percent_in_range": round(in_range_count / total * 100, 2),
            "percent_high": round(high_count / total * 100, 2),
        }
        return Response(data)


class PatientGlucoseHistoryAPIView(generics.ListAPIView):
    """
    GET /api/patients/{id}/glucose_history/?days=7
    Lista de leituras de um paciente em ordem cronológica (timestamp asc).
    """
    serializer_class = GlucoseReadingCompactSerializer

    def get_queryset(self):
        libre_patient_id = self.kwargs["libre_patient_id"]
        days = int(self.request.query_params.get("days", 7))
        now = timezone.now()
        since = now - timedelta(days=days)

        return (
            GlucoseReading.objects
            .filter(patient__libre_patient_id=libre_patient_id, timestamp__gte=since)
            .order_by("timestamp")
        )


class PatientsSummaryAPIView(APIView):
    """
    GET /api/patients/summary/

    Resumo geral para ingestão:
    - total_patients
    - patients_with_data
    - patients_without_data
    - newly_active_since=? (opcional, em horas)
    """
    def get(self, request):
        total = Patient.objects.count()
        with_data = Patient.objects.filter(has_glucose_data=True).count()
        without_data = total - with_data

        newly_active_hours = int(request.query_params.get("newly_active_hours", 24))
        since = timezone.now() - timedelta(hours=newly_active_hours)

        newly_active = Patient.objects.filter(
            has_glucose_data=True,
            first_glucose_at__gte=since,
        ).count()

        data = {
            "total_patients": total,
            "patients_with_data": with_data,
            "patients_without_data": without_data,
            "newly_active_hours": newly_active_hours,
            "newly_active_count": newly_active,
        }
        return Response(data)


# ========== GLUCOSE ==========

class GlucoseListAPIView(generics.ListAPIView):
    """
    GET /api/glucose/
    Lista todas as leituras (paginadas).
    Filtros opcionais:
    - ?patient_id=ID
    - ?since=YYYY-MM-DD
    - ?until=YYYY-MM-DD
    """
    serializer_class = GlucoseReadingSerializer

    def get_queryset(self):
        qs = GlucoseReading.objects.select_related("patient").all()

        patient_id = self.request.query_params.get("patient_id")
        if patient_id:
            qs = qs.filter(patient_id=patient_id)

        since = self.request.query_params.get("since")
        until = self.request.query_params.get("until")

        if since:
            qs = qs.filter(timestamp__gte=since)
        if until:
            qs = qs.filter(timestamp__lte=until)

        return qs.order_by("-timestamp")


class GlucoseLatestAPIView(APIView):
    """
    GET /api/glucose/latest/

    Última leitura de cada paciente (apenas pacientes com dados).
    """
    def get(self, request):
        # Postgres permite distinct('patient') com order_by
        qs = (
            GlucoseReading.objects
            .select_related("patient")
            .order_by("patient_id", "-timestamp")
            .distinct("patient_id")
        )

        serializer = GlucoseReadingSerializer(qs, many=True)
        return Response(serializer.data)