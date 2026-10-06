# ADR-0006: Bot do Telegram como view Django (webhook), sem framework de bot

- **Status:** Aceito (grupo, 06/10/2026)
- **Data:** 2026-10-06
- **Sprint:** S3 (vínculo) / S4 (bot)
- **Autor(es):** 

## Contexto
O bot precisa: responder `/start`, vincular conta, mostrar cardápio e registrar "vou / não vou". Frameworks como `python-telegram-bot` são assíncronos e exigem um processo separado — difícil de explicar e de hospedar.

## Alternativas consideradas
- **python-telegram-bot com polling** — fácil em dev, mas precisa de um worker sempre rodando em produção.
- **Webhook via framework** — ainda traz o modelo async do framework.
- **Webhook como view Django + chamadas HTTP diretas** — o Telegram faz `POST` numa URL nossa; respondemos chamando `https://api.telegram.org/bot<token>/sendMessage` com `requests`.

## Decisão
- `POST /bot/webhook/<segredo>/` em `bot/views.py` recebe o update, roteia por comando/callback, chama as mesmas funções de domínio que o site usa (`confirmacoes.regras`, `cardapio`).
- `bot/telegram.py` com `enviar_mensagem(chat_id, texto, botoes=None)`.
- **Vínculo:** página "Conectar Telegram" gera código de 6 dígitos com validade de 10 min; o aluno envia `/vincular 123456`; o bot grava `telegram_id` no usuário.
- Em dev: `ngrok` (ou similar) para expor o webhook.

## Consequências
- Positivas: zero processo extra; o bot é "só mais uma view"; o fluxo cabe num diagrama de 4 caixas.
- Negativas: sem ngrok não testa localmente; o segredo na URL precisa ser forte.
- Saber explicar: webhook vs polling; o que é um *update* do Telegram; *inline keyboard* e *callback_query*; por que o bot reutiliza a regra de corte em vez de reimplementar.
