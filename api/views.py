"""
Endpoints consumidos pelo bot (ADR-0005). Todos exigem JWT do usuário de serviço `bot`.
A regra de negócio NÃO mora aqui — chamamos os mesmos métodos que o site usa.
"""
from datetime import date

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cardapio.models import Cardapio
from confirmacoes.models import Confirmacao
from contas.models import CodigoVinculo

from .permissoes import EhBot
from .serializers import (
    CardapioSerializer,
    ConfirmacaoEntradaSerializer,
    ConfirmacaoSaidaSerializer,
    UsuarioSaidaSerializer,
    VinculoEntradaSerializer,
)

Usuario = get_user_model()


def _usuario_por_telegram(telegram_id: str):
    return get_object_or_404(Usuario, telegram_id=telegram_id)


class CardapioDoDia(APIView):
    permission_classes = [EhBot]

    @extend_schema(responses=CardapioSerializer, summary="Cardápio de uma data (ou de hoje)")
    def get(self, request, data: str | None = None):
        dia = date.fromisoformat(data) if data else timezone.localdate()
        cardapio = get_object_or_404(Cardapio, data=dia)
        cardapio.total_confirmados = Confirmacao.total_do_dia(dia)
        return Response(CardapioSerializer(cardapio).data)


class Confirmar(APIView):
    permission_classes = [EhBot]

    @extend_schema(
        request=ConfirmacaoEntradaSerializer,
        responses={200: ConfirmacaoSaidaSerializer, 403: OpenApiResponse(description="Passou do horário de corte"), 404: OpenApiResponse(description="Telegram não vinculado")},
        summary="Registra 'vou' / 'não vou' de um aluno (pelo telegram_id)",
    )
    def post(self, request):
        entrada = ConfirmacaoEntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        d = entrada.validated_data
        usuario = _usuario_por_telegram(d["telegram_id"])

        if not Confirmacao.pode_alterar_agora(d["data"]):
            return Response({"detail": "Passou do horário de corte para este dia."}, status=status.HTTP_403_FORBIDDEN)

        conf = Confirmacao.definir(usuario, d["data"], d["confirmado"])
        saida = {"data": conf.data, "confirmado": conf.confirmado, "total_confirmados": Confirmacao.total_do_dia(conf.data)}
        return Response(ConfirmacaoSaidaSerializer(saida).data)


class Vincular(APIView):
    permission_classes = [EhBot]

    @extend_schema(
        request=VinculoEntradaSerializer,
        responses={200: UsuarioSaidaSerializer, 400: OpenApiResponse(description="Código inválido ou expirado")},
        summary="Vincula um telegram_id à conta dona do código de 6 dígitos",
    )
    def post(self, request):
        entrada = VinculoEntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        d = entrada.validated_data

        codigo = CodigoVinculo.objects.filter(codigo=d["codigo"], usado_em__isnull=True).order_by("-criado_em").first()
        if not codigo or not codigo.valido():
            return Response({"detail": "Código inválido ou expirado. Gere outro no site."}, status=status.HTTP_400_BAD_REQUEST)

        usuario = codigo.consumir(d["telegram_id"])
        return Response(UsuarioSaidaSerializer({"nome": usuario.first_name or usuario.username, "notificacao": usuario.notificacao}).data)


class Quem(APIView):
    permission_classes = [EhBot]

    @extend_schema(responses=UsuarioSaidaSerializer, summary="Quem é este telegram_id? (404 se não vinculado)")
    def get(self, request, telegram_id: str):
        u = _usuario_por_telegram(telegram_id)
        return Response(UsuarioSaidaSerializer({"nome": u.first_name or u.username, "notificacao": u.notificacao}).data)
