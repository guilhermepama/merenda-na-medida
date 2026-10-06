"""Fixtures compartilhadas. pytest-django cria um banco de teste vazio por sessão."""
from datetime import date

import pytest
from django.contrib.auth import get_user_model

from cardapio.models import Cardapio


@pytest.fixture
def usuario(db):
    return get_user_model().objects.create_user(username="ana", password="senha-forte-123", first_name="Ana")


@pytest.fixture
def cozinha(db):
    return get_user_model().objects.create_user(username="cozinha", password="senha-forte-123", is_staff=True)


@pytest.fixture
def amanha():
    from django.utils import timezone
    from datetime import timedelta
    return timezone.localdate() + timedelta(days=1)


@pytest.fixture
def cardapio_amanha(db, amanha):
    return Cardapio.objects.create(data=amanha, descricao="Arroz, feijão, frango grelhado, salada")

