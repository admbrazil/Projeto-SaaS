"""TenantMiddleware — detecta a clínica pelo subdomínio."""
from django.http import Http404
from .models import Clinic


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0]
        parts = host.split(".")
        # Ex: minhaclinica.telesaas.com.br → slug = minhaclinica
        if len(parts) >= 3:
            slug = parts[0]
            try:
                request.clinic = Clinic.objects.get(slug=slug, is_active=True)
            except Clinic.DoesNotExist:
                request.clinic = None
        else:
            request.clinic = None
        return self.get_response(request)
