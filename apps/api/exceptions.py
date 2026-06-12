"""Handler de exceções customizado para a API."""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return Response(
            {"error": "Erro interno do servidor.", "detail": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    response.data = {"error": response.data if isinstance(response.data, str) else str(response.data.get("detail", response.data))}
    return response
