"""Django signals para auditoria automática de login/logout."""
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import AuditLog


def _get_ip(request):
    if not request:
        return ""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR", "")


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    AuditLog.log(event_type=AuditLog.EventType.LOGIN_SUCCESS, user=user,
                 ip=_get_ip(request), request=request, success=True)


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    AuditLog.log(event_type=AuditLog.EventType.LOGOUT, user=user,
                 ip=_get_ip(request), request=request, success=True)


@receiver(user_login_failed)
def on_login_failed(sender, credentials, request, **kwargs):
    AuditLog.log(event_type=AuditLog.EventType.LOGIN_FAILED,
                 ip=_get_ip(request), request=request,
                 description=f"CPF tentado: {str(credentials.get('cpf',''))[:3]}***",
                 success=False)
