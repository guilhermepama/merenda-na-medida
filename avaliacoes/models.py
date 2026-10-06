from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Count, Q


class Avaliacao(models.Model):
    """
    Nota do jantar de um dia por um usuário. Uma por (usuario, data) — UNIQUE.
    Relacional por decisão (ADR-0011): schema fixo, pertence a usuário e data,
    e o dashboard cruza com Confirmacao por dia.
    """

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data = models.DateField("Data do jantar")
    nota = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    repetiria = models.BooleanField("Repetiria o prato", default=False)
    comentario = models.CharField(max_length=500, blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["usuario", "data"], name="uma_avaliacao_por_dia")]
        verbose_name = "avaliação"
        verbose_name_plural = "avaliações"

    def __str__(self):
        return f"{self.usuario} deu {self.nota}★ em {self.data:%d/%m}"

    @classmethod
    def resumo_do_dia(cls, data_jantar) -> dict:
        """{'total': n, 'media': 4.2, 'pct_repetiria': 75} — uma query agregada."""
        r = cls.objects.filter(data=data_jantar).aggregate(
            total=Count("id"), media=Avg("nota"), repetiriam=Count("id", filter=Q(repetiria=True))
        )
        if not r["total"]:
            return {"total": 0, "media": None, "pct_repetiria": None}
        return {
            "total": r["total"],
            "media": round(r["media"], 1),
            "pct_repetiria": round(100 * r["repetiriam"] / r["total"]),
        }
