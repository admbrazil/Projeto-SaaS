"""Serializers da API REST."""
from rest_framework import serializers
from apps.consultations.models import Consultation
from apps.patients.models import Patient


class ConsultationCreateSerializer(serializers.Serializer):
    patient_cpf     = serializers.CharField(max_length=11)
    patient_name    = serializers.CharField(max_length=255)
    patient_birth   = serializers.DateField()
    consultation_type = serializers.ChoiceField(choices=Consultation.Type.choices, default=Consultation.Type.INSTANT)
    specialty_name  = serializers.CharField(max_length=100, required=False, allow_blank=True)
    scheduled_for   = serializers.DateTimeField(required=False, allow_null=True)


class ConsultationSerializer(serializers.ModelSerializer):
    patient_name    = serializers.CharField(source="patient.full_name", read_only=True)
    patient_token   = serializers.CharField(read_only=True)
    status_display  = serializers.CharField(source="get_status_display", read_only=True)
    type_display    = serializers.CharField(source="get_consultation_type_display", read_only=True)

    class Meta:
        model  = Consultation
        fields = ["code", "patient_name", "patient_token", "consultation_type",
                  "type_display", "status", "status_display", "requested_at",
                  "scheduled_for", "started_at", "finished_at"]
