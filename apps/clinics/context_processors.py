"""Context processors para o app clinics."""


def current_clinic(request):
    """Injeta a clinica atual no contexto dos templates."""
    clinic = getattr(request, "current_clinic", None)
    return {"current_clinic": clinic}
