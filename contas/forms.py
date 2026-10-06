from django.contrib.auth.forms import UserCreationForm

from .models import Usuario


class CadastroForm(UserCreationForm):
    """UserCreationForm já cuida de senha dupla e validação; só dizemos quais campos extras."""

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username", "first_name", "email")
        labels = {"username": "Usuário", "first_name": "Nome", "email": "E-mail"}
