from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Usuário do sistema. Herda username/email/senha do Django e acrescenta
    o que o Merenda precisa: vínculo com o Telegram e preferência de notificação.
    Definido ANTES da primeira migration (AUTH_USER_MODEL em settings).
    """

    class Notificacao(models.TextChoices):
        SITE = "site", "Somente no site"
        TELEGRAM = "telegram", "Somente no Telegram"
        AMBOS = "ambos", "Site e Telegram"
        NENHUM = "nenhum", "Não quero notificações"

    telegram_id = models.CharField(
        "ID do Telegram", max_length=32, blank=True, null=True, unique=True
    )
    notificacao = models.CharField(
        max_length=10, choices=Notificacao.choices, default=Notificacao.SITE
    )

    def __str__(self):
        return self.get_full_name() or self.username
