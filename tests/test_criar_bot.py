from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command


def test_criar_bot_cria_usuario_sem_staff(db, settings):
    saida = StringIO()
    call_command("criar_bot", stdout=saida)
    bot = get_user_model().objects.get(username=settings.BOT_USERNAME)
    assert not bot.is_staff and "BOT_PASSWORD=" in saida.getvalue()
