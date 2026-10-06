from django.db import models


class Cardapio(models.Model):
    """
    O jantar de UM dia. Uma linha por data (unique) — não existe "dois cardápios no mesmo dia".
    Texto livre por decisão (ADR-0008): a cozinha cola o que já manda no PDF.
    """

    data = models.DateField("Data do jantar", unique=True)
    descricao = models.TextField("Cardápio", help_text="Prato principal, acompanhamentos, sobremesa…")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data"]
        verbose_name = "cardápio"
        verbose_name_plural = "cardápios"

    def __str__(self):
        return f"Jantar de {self.data:%d/%m/%Y}"
