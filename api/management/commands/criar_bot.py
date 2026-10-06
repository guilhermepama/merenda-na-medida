"""
python manage.py criar_bot

Cria (ou redefine a senha d)o usuário de serviço que o bot usa para pegar o JWT.
Imprime a senha UMA vez — guarde no .env do bot (BOT_PASSWORD). Não é staff, não loga no site.
"""
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Cria/redefine o usuário de serviço da API (settings.BOT_USERNAME)"

    def handle(self, **opts):
        senha = secrets.token_urlsafe(24)
        usuario, criado = get_user_model().objects.get_or_create(
            username=settings.BOT_USERNAME, defaults={"first_name": "Bot do Telegram", "notificacao": "nenhum"}
        )
        usuario.set_password(senha)
        usuario.is_staff = usuario.is_superuser = False
        usuario.save()
        self.stdout.write(self.style.SUCCESS(f"Usuário '{usuario.username}' {'criado' if criado else 'atualizado'}."))
        self.stdout.write(f"BOT_PASSWORD={senha}")
        self.stdout.write("Teste: POST /api/token/ com {\"username\": \"%s\", \"password\": \"...\"}" % usuario.username)
