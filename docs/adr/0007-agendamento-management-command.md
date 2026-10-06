# ADR-0007: Pergunta diária via management command disparado por cron da plataforma

- **Status:** Proposto
- **Data:** 2026-10-06
- **Sprint:** S4
- **Autor(es):** 

## Contexto
Todo dia, num horário fixo, o sistema pergunta "vai jantar hoje?" a quem optou por Telegram.

## Alternativas consideradas
- **Celery + Redis/beat** — padrão de mercado, mas 2 serviços novos para 1 tarefa por dia.
- **`django-crontab` / APScheduler dentro do processo** — morre se o processo reinicia; frágil em free tier.
- **Management command + cron externo** — `python manage.py perguntar_jantar`; quem agenda é a plataforma de deploy (cron job) ou um GitHub Action.

## Decisão
Command em `bot/management/commands/perguntar_jantar.py`: para cada `Usuario` com `telegram_id` e `notificacao in ('telegram','ambos')`, chama `enviar_mensagem` com botões "Vou / Não vou". Agendamento definido junto com o ADR-0009.

## Consequências
- Positivas: testável na mão (`manage.py perguntar_jantar`); zero infra; o código é um `for`.
- Negativas: depende de a plataforma oferecer cron; se não, usar GitHub Actions `schedule` chamando um endpoint protegido.
- Saber explicar: o que é um management command; cron; idempotência (rodar duas vezes não manda duas mensagens — guardar `ultima_pergunta_em`).
