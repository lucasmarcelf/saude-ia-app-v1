from django.urls import path
from .views import (
    PatientListAPIView,
    PatientDetailAPIView,
    PatientGlucoseStatsAPIView,
    PatientGlucoseHistoryAPIView,
    PatientsSummaryAPIView,
    GlucoseListAPIView,
    GlucoseLatestAPIView,
)

urlpatterns = [
    # Patients
    path("patients/", PatientListAPIView.as_view(), name="patient-list"),
    path("patients/summary/", PatientsSummaryAPIView.as_view(), name="patient-summary"),
    path(
        "patients/<uuid:libre_patient_id>/",
        PatientDetailAPIView.as_view(),
        name="patient-detail",
    ),
    path(
        "patients/<uuid:libre_patient_id>/glucose_stats/",
        PatientGlucoseStatsAPIView.as_view(),
        name="patient-glucose-stats",
    ),
    path(
        "patients/<uuid:libre_patient_id>/glucose_history/",
        PatientGlucoseHistoryAPIView.as_view(),
        name="patient-glucose-history",
    ),

    # Glucose
    path("glucose/", GlucoseListAPIView.as_view(), name="glucose-list"),
    path("glucose/latest/", GlucoseLatestAPIView.as_view(), name="glucose-latest"),
]