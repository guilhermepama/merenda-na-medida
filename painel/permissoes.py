from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def apenas_cozinha(view):
    """
    Só staff (cozinha/direção) entra no painel.
    - Não logado → vai para o login do SITE (não o do /admin/) e volta depois.
    - Logado sem ser staff (aluno) → 403. Mandar pro login de novo seria um loop sem explicação.
    """

    @wraps(view)
    def _view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.is_staff:
            raise PermissionDenied("Área restrita à cozinha.")
        return view(request, *args, **kwargs)

    return _view
