"""Serializers = tradutores entre objetos Python e JSON, com validação de entrada."""
from rest_framework import serializers

from cardapio.models import Cardapio


class CardapioSerializer(serializers.ModelSerializer):
    total_confirmados = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cardapio
        fields = ("data", "descricao", "total_confirmados")


class ConfirmacaoEntradaSerializer(serializers.Serializer):
    telegram_id = serializers.CharField(max_length=32)
    data = serializers.DateField()
    confirmado = serializers.BooleanField()


class ConfirmacaoSaidaSerializer(serializers.Serializer):
    data = serializers.DateField()
    confirmado = serializers.BooleanField()
    total_confirmados = serializers.IntegerField()


class VinculoEntradaSerializer(serializers.Serializer):
    telegram_id = serializers.CharField(max_length=32)
    codigo = serializers.RegexField(r"^\d{6}$")


class UsuarioSaidaSerializer(serializers.Serializer):
    nome = serializers.CharField()
    notificacao = serializers.CharField()
