"""Views do portal LGPD — consentimento e direitos Art. 18."""
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.contrib import messages
from .models import ConsentVersion, LGPDRequest, UserConsent


def _get_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR", "")


@login_required
def consent_required(request):
    version = ConsentVersion.get_current()
    if not version:
        return redirect("/")
    if request.method == "POST":
        UserConsent.objects.create(
            user=request.user,
            version=version,
            ip_address=_get_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            consent_terms=True,
            consent_privacy=True,
            consent_health_data=request.POST.get("consent_health_data") == "on",
            consent_communications=request.POST.get("consent_communications") == "on",
        )
        request.user.lgpd_consent = True
        request.user.lgpd_consent_at = timezone.now()
        request.user.save(update_fields=["lgpd_consent", "lgpd_consent_at"])
        return redirect(request.GET.get("next", "/"))
    return render(request, "lgpd/consent.html", {"version": version})


@login_required
def my_data_portal(request):
    requests_qs = LGPDRequest.objects.filter(user=request.user).order_by("-requested_at")
    consents = UserConsent.objects.filter(user=request.user).order_by("-accepted_at")
    return render(request, "lgpd/portal.html", {"lgpd_requests": requests_qs, "consents": consents})


@login_required
def new_lgpd_request(request):
    if request.method == "POST":
        req_type = request.POST.get("request_type")
        description = request.POST.get("description", "")
        if req_type not in dict(LGPDRequest.RequestType.choices):
            messages.error(request, "Tipo de solicitação inválido.")
            return redirect("lgpd:new_request")
        lgpd_req = LGPDRequest.objects.create(
            user=request.user,
            requester_name=request.user.full_name,
            requester_email=request.user.email,
            request_type=req_type,
            description=description,
        )
        from django.conf import settings
        from django.core.mail import send_mail
        try:
            send_mail(
                subject=f"[LGPD] Nova solicitação {lgpd_req.protocol}",
                message=f"Tipo: {lgpd_req.get_request_type_display()}\nUsuário: {request.user}\nDescrição: {description}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DPO_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass
        messages.success(request, f"Solicitação registrada. Protocolo: {lgpd_req.protocol}")
        return redirect("lgpd:portal")
    return render(request, "lgpd/new_request.html", {"request_types": LGPDRequest.RequestType.choices})


@login_required
def export_my_data(request):
    user = request.user
    data = {
        "usuario": {
            "nome": user.full_name,
            "email": user.email,
            "cpf_masked": user.cpf_masked,
            "role": user.role,
            "data_cadastro": str(user.date_joined),
            "lgpd_consent": user.lgpd_consent,
        },
        "solicitacoes_lgpd": [
            {"protocolo": r.protocol, "tipo": r.get_request_type_display(),
             "status": r.get_status_display(), "data": str(r.requested_at)}
            for r in LGPDRequest.objects.filter(user=user)
        ],
    }
    return JsonResponse(data, json_dumps_params={"ensure_ascii": False, "indent": 2})
