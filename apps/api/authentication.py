"""Bearer Token authentication por clínica."""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from apps.clinics.models import ClinicAPIToken


class APIUser:
    """Objeto mínimo compatível com DRF para autenticação por token de clínica."""
    def __init__(self, clinic):
        self.clinic = clinic
        self.is_authenticated = True
        self.is_active = True

    def __str__(self):
        return f"APIUser({self.clinic})"


class ClinicBearerTokenAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith(f"{self.keyword} "):
            return None
        token_value = auth_header[len(self.keyword) + 1:].strip()
        if not token_value:
            return None
        try:
            api_token = ClinicAPIToken.objects.select_related("clinic").get(
                token=token_value, is_active=True, clinic__is_active=True
            )
        except ClinicAPIToken.DoesNotExist:
            raise AuthenticationFailed("Token inválido ou inativo.")
        api_token.last_used = timezone.now()
        api_token.save(update_fields=["last_used"])
        return (APIUser(api_token.clinic), api_token)
