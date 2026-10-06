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


class CodigoVinculo(models.Model):
    """
    Código de 6 dígitos que o aluno gera no site e manda pro bot (/vincular 123456).
    Vale VINCULO_VALIDADE_MINUTOS e é de uso único. Assim o telegram_id só entra na
    conta de quem provou estar logado no site — ninguém vincula a conta de outro.
    """

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="codigos_vinculo")
    codigo = models.CharField(max_length=6, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    usado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "código de vínculo"
        verbose_name_plural = "códigos de vínculo"

    def __str__(self):
        return f"{self.codigo} ({self.usuario})"

    @classmethod
    def gerar(cls, usuario) -> "CodigoVinculo":
        import secrets

        cls.objects.filter(usuario=usuario, usado_em__isnull=True).delete()  # só um ativo por vez
        return cls.objects.create(usuario=usuario, codigo=f"{secrets.randbelow(10**6):06d}")

    def valido(self, agora=None) -> bool:
        from datetime import timedelta

        from django.conf import settings
        from django.utils import timezone

        agora = agora or timezone.now()
        return self.usado_em is None and agora - self.criado_em <= timedelta(minutes=settings.VINCULO_VALIDADE_MINUTOS)

    def consumir(self, telegram_id: str) -> Usuario:
        """Marca o código como usado e grava o telegram_id no dono do código."""
        from django.utils import timezone

        Usuario.objects.filter(telegram_id=telegram_id).exclude(pk=self.usuario_id).update(telegram_id=None)
        self.usuario.telegram_id = telegram_id
        self.usuario.save(update_fields=["telegram_id"])
        self.usado_em = timezone.now()
        self.save(update_fields=["usado_em"])
        return self.usuario
