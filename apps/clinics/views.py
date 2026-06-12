"""Views do painel da clinica."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from apps.patients.models import Patient
from apps.doctors.models import Doctor
from apps.consultations.models import Consultation


@login_required
def dashboard(request):
    ctx = {
        'total_pacientes': Patient.objects.count(),
        'total_medicos': Doctor.objects.filter(is_active=True).count(),
        'total_consultas': Consultation.objects.count(),
        'consultas_hoje': Consultation.objects.filter(
            requested_at__date=timezone.now().date()
        ).count(),
    }
    return render(request, "clinics/dashboard.html", ctx)


@login_required
def pacientes_list(request):
    pacientes = Patient.objects.order_by('full_name')
    return render(request, "clinics/pacientes.html", {'pacientes': pacientes})


@login_required
def medicos_list(request):
    medicos = Doctor.objects.select_related('user').prefetch_related('specialties').filter(is_active=True)
    return render(request, "clinics/medicos.html", {'medicos': medicos})


@login_required
def consultas_list(request):
    consultas = Consultation.objects.select_related('patient', 'doctor').order_by('-requested_at')[:100]
    return render(request, "clinics/consultas.html", {'consultas': consultas})
