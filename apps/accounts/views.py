"""Views de autenticação — CPF + bloqueio + magic link."""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.contrib import messages
from .models import User
from apps.audit.models import AuditLog


def _get_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR", "")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        cpf = request.POST.get("cpf", "").replace(".", "").replace("-", "")
        password = request.POST.get("password", "")
        ip = _get_ip(request)
        try:
            user = User.objects.get(cpf=cpf)
        except User.DoesNotExist:
            AuditLog.log(event_type=AuditLog.EventType.LOGIN_FAILED, ip=ip,
                         description=f"CPF não encontrado: {cpf[:3]}***", success=False)
            messages.error(request, "CPF ou senha incorretos.")
            return render(request, "accounts/login.html")
        if user.is_locked:
            AuditLog.log(event_type=AuditLog.EventType.LOCKOUT, user=user, ip=ip,
                         description="Conta bloqueada.", success=False)
            remaining = int((user.locked_until - timezone.now()).total_seconds() // 60)
            messages.error(request, f"Conta bloqueada. Tente novamente em {remaining} minutos.")
            return render(request, "accounts/login.html")
        auth_user = authenticate(request, cpf=cpf, password=password)
        if auth_user is None:
            user.record_failed_login()
            AuditLog.log(event_type=AuditLog.EventType.LOGIN_FAILED, user=user, ip=ip,
                         description="Senha incorreta.", success=False)
            messages.error(request, "CPF ou senha incorretos.")
            return render(request, "accounts/login.html")
        user.reset_login_attempts()
        user.last_login_ip = ip
        user.save(update_fields=["last_login_ip"])
        login(request, auth_user)
        AuditLog.log(event_type=AuditLog.EventType.LOGIN_SUCCESS, user=auth_user, ip=ip, success=True)
        return redirect(request.GET.get("next", "/"))
    return render(request, "accounts/login.html")


@login_required
def logout_view(request):
    AuditLog.log(event_type=AuditLog.EventType.LOGOUT, user=request.user,
                 ip=_get_ip(request), success=True)
    logout(request)
    return redirect("accounts:login")


def magic_link_login(request, token):
    from apps.patients.models import Patient
    try:
        patient = Patient.verify_magic_link(token)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect("accounts:login")
    if patient.user:
        login(request, patient.user, backend="django.contrib.auth.backends.ModelBackend")
        AuditLog.log(event_type=AuditLog.EventType.MAGIC_LINK, user=patient.user,
                     ip=_get_ip(request), success=True)
    return redirect("/")
