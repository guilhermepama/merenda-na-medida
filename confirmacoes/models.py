from datetime import date

from django.conf import settings
from django.db import models
from django.utils import timezone

from .regras import pode_alterar


class Confirmacao(models.Model):
    """
    "Fulano vai jantar no dia X?" — uma linha por (usuario, data).
    O UNIQUE garante que o toggle sempre atualiza a mesma linha, nunca duplica.
    """

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data = models.DateField("Data do jantar")
    confirmado = models.BooleanField(default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["usuario", "data"], name="uma_confirmacao_por_dia")
        ]
        verbose_name = "confirmação"
        verbose_name_plural = "confirmações"

    def __str__(self):
        estado = "vai" if self.confirmado else "não vai"
        return f"{self.usuario} {estado} em {self.data:%d/%m}"

    # ---- consultas usadas pelas views (site, dashboard e, depois, bot) ----

    @staticmethod
    def pode_alterar_agora(data_jantar: date) -> bool:
        """Aplica a regra pura (ADR-0008) ao relógio real, no fuso de São Paulo."""
        return pode_alterar(data_jantar, timezone.localtime(), settings.HORARIO_CORTE)

    @classmethod
    def total_do_dia(cls, data_jantar: date) -> int:
        """Quantos confirmaram para o dia — o número que a cozinha quer ver."""
        return cls.objects.filter(data=data_jantar, confirmado=True).count()

    @classmethod
    def alternar(cls, usuario, data_jantar: date) -> "Confirmacao":
        """
        O toggle. Primeira vez: cria confirmado=True. Depois: inverte.
        get_or_create + UNIQUE = idempotente, sem race condition de duplicar.
        """
        obj, criado = cls.objects.get_or_create(usuario=usuario, data=data_jantar)
        if not criado:
            obj.confirmado = not obj.confirmado
            obj.save(update_fields=["confirmado", "atualizado_em"])
        return obj
