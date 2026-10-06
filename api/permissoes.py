from django.conf import settings
from rest_framework.permissions import BasePermission


class EhBot(BasePermission):
    """
    Só o usuário de serviço do bot passa (ADR-0005). Um aluno com JWT válido não entra:
    a API fala com o bot, o aluno fala com o site.
    """

    message = "Esta API é exclusiva do bot do Telegram."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.username == settings.BOT_USERNAME)
