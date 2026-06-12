"""Views da API REST pública."""
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.audit.models import AuditLog
from apps.clinics.models import Specialty
from apps.consultations.models import Consultation
from apps.patients.models import Patient
from .serializers import ConsultationCreateSerializer, ConsultationSerializer


class BaseClinicAPIView(APIView):
    def _log(self, event_type, description="", success=True, target_id=""):
        clinic = self.request.user.clinic
        AuditLog.log(event_type=event_type, clinic=clinic, description=description,
                     success=success, target_id=target_id,
                     ip=self.request.META.get("REMOTE_ADDR", ""))


class ConsultationCreateView(BaseClinicAPIView):
    """POST /api/clinic/add-consultation/"""
    def post(self, request):
        s = ConsultationCreateSerializer(data=request.data)
        if not s.is_valid():
            return Response({"error": s.errors}, status=status.HTTP_400_BAD_REQUEST)
        d = s.validated_data
        clinic = request.user.clinic
        cpf = d["patient_cpf"].replace(".", "").replace("-", "")
        patient, _ = Patient.objects.get_or_create(
            clinic=clinic, cpf=cpf,
            defaults={"full_name": d["patient_name"], "birth_date": d["patient_birth"]},
        )
        specialty = None
        if d.get("specialty_name"):
            specialty, _ = Specialty.objects.get_or_create(clinic=clinic, name=d["specialty_name"])
        consultation = Consultation.objects.create(
            clinic=clinic, patient=patient,
            consultation_type=d.get("consultation_type", Consultation.Type.INSTANT),
            specialty=specialty, scheduled_for=d.get("scheduled_for"),
        )
        self._log(AuditLog.EventType.CONSULTATION_CREATED, target_id=consultation.code)
        return Response(ConsultationSerializer(consultation).data, status=status.HTTP_201_CREATED)


class ConsultationListView(BaseClinicAPIView):
    """GET /api/clinic/consultations/"""
    def get(self, request):
        qs = Consultation.objects.filter(clinic=request.user.clinic).order_by("-requested_at")[:100]
        return Response(ConsultationSerializer(qs, many=True).data)


class ConsultationDetailView(BaseClinicAPIView):
    """GET /api/clinic/consultation/<code>/"""
    def get(self, request, code):
        try:
            c = Consultation.objects.get(code=code, clinic=request.user.clinic)
        except Consultation.DoesNotExist:
            return Response({"error": "Consulta não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ConsultationSerializer(c).data)


class ConsultationCancelView(BaseClinicAPIView):
    """POST /api/clinic/consultation/<code>/cancel/"""
    def post(self, request, code):
        try:
            c = Consultation.objects.get(code=code, clinic=request.user.clinic)
        except Consultation.DoesNotExist:
            return Response({"error": "Consulta não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        if c.status in (Consultation.Status.FINISHED, Consultation.Status.CANCELLED):
            return Response({"error": "Consulta já encerrada."}, status=status.HTTP_400_BAD_REQUEST)
        c.transition_to(Consultation.Status.CANCELLED)
        self._log(AuditLog.EventType.CONSULTATION_CANCELLED, target_id=code)
        return Response({"status": "cancelled"})


class MevoDataView(BaseClinicAPIView):
    """GET /api/check-clinics-mevo-data/ — usado pela integração MEVO."""
    def get(self, request):
        clinic = request.user.clinic
        waiting = Consultation.objects.filter(clinic=clinic, status=Consultation.Status.WAITING).count()
        in_progress = Consultation.objects.filter(clinic=clinic, status=Consultation.Status.IN_PROGRESS).count()
        self._log(AuditLog.EventType.API_ACCESS, description="MEVO data check")
        return Response({"clinic": clinic.slug, "waiting": waiting, "in_progress": in_progress, "timestamp": timezone.now().isoformat()})
