# ADRs — Architecture Decision Records

Um ADR registra **uma** decisão técnica: o contexto, as alternativas, a escolha e as consequências.
Serve pra duas coisas: (1) o grupo não rediscutir o que já foi decidido; (2) na apresentação,
qualquer integrante consegue justificar "por que X e não Y".

**Regras**
- Um arquivo por decisão, numerado: `NNNN-titulo-curto.md`. Nunca renumerar.
- Status: `Proposto` → `Aceito` → (`Substituído por ADR-NNNN` | `Descontinuado`). Um ADR aceito **não se edita**; se mudou de ideia, cria-se outro que o substitui.
- Curto. Meia página. Se precisa de mais, a decisão está grande demais — quebre.
- Copie `0000-template.md`.

| # | Título | Status | Sprint |
|---|---|---|---|
| [0001](0001-django-monolito-mtv.md) | Django como monólito MTV | Aceito | S1 |
| [0002](0002-persistencia-poliglota.md) | Persistência poliglota: PostgreSQL + MongoDB | Substituído por 0011 | S1/S2 |
| [0003](0003-sqlite-dev-postgres-prod.md) | SQLite em dev, PostgreSQL (Neon) em produção | Aceito | S1/S3 |
| [0004](0004-htmx-alpine-frontend.md) | HTMX para servidor, Alpine.js para estado local | Aceito | S2 |
| [0005](0005-drf-jwt-api-bot.md) | DRF + JWT; o bot é o único cliente da API | Aceito | S3 |
| [0006](0006-bot-telegram-webhook-view.md) | Bot do Telegram como view Django (webhook), sem framework | Aceito | S3/S4 |
| [0007](0007-agendamento-management-command.md) | Notificação diária via management command + cron da plataforma | Aceito | S4 |
| [0008](0008-cardapio-texto-livre-e-horario-corte.md) | Cardápio como texto livre; horário de corte como regra pura | Aceito | S1/S2 |
| [0009](0009-plataforma-de-deploy.md) | Plataforma de deploy | Proposto | S3/S4 |
| [0010](0010-escopo-de-testes.md) | Escopo de testes: TDD só nas regras críticas | Aceito | S4 |
| [0011](0011-avaliacao-relacional-sem-mongodb.md) | Avaliação no relacional; não usar MongoDB | Aceito | S2 |
| [0012](0012-painel-da-cozinha.md) | Painel da cozinha próprio; admin só para a equipe técnica | Aceito | S3 |
