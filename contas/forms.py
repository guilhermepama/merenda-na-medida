from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Usuario


class CadastroForm(UserCreationForm):
    """UserCreationForm já cuida de senha dupla e validação; só dizemos quais campos extras."""

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username", "first_name", "email")
        labels = {"username": "Usuário", "first_name": "Nome", "email": "E-mail"}


class PreferenciasForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ("first_name", "email", "notificacao")
        labels = {"first_name": "Nome", "email": "E-mail", "notificacao": "Como quer ser avisado do jantar?"}
        widgets = {"notificacao": forms.RadioSelect}
