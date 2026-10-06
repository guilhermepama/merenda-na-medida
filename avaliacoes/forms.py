from django import forms

from .models import Avaliacao

NOTAS = [(i, "★" * i) for i in range(1, 6)]


class AvaliacaoForm(forms.ModelForm):
    nota = forms.TypedChoiceField(choices=NOTAS, coerce=int, widget=forms.RadioSelect, label="Nota")

    class Meta:
        model = Avaliacao
        fields = ("nota", "repetiria", "comentario")
        labels = {"comentario": "Comentário (opcional)"}
        widgets = {"comentario": forms.Textarea(attrs={"rows": 3})}
