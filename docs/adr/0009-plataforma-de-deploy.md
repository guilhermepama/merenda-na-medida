# ADR-0009: Plataforma de deploy

- **Status:** Proposto (decidir na S3, com teste real)
- **Data:** 2026-10-06
- **Sprint:** S3 / S4
- **Autor(es):** 

## Contexto
Precisa de: URL pública HTTPS (webhook do Telegram exige), cron para a pergunta diária, variáveis de ambiente, Postgres externo (Neon) e Mongo externo (Atlas). Custo: zero.

## Alternativas consideradas
- **Render (free)** — fácil, mas o serviço web **dorme** após inatividade: webhook demora ~30s no primeiro acesso e cron jobs não são gratuitos.
- **Railway** — tem cron e não dorme, mas o plano gratuito é por crédito/tempo; pode acabar antes de 07/12.
- **VPS própria (Coolify/Docker)** — total controle, não dorme, cron nativo. Risco: um único integrante detém a infra; a Fatec não "herda" nada.
- **PythonAnywhere (free)** — tem *scheduled tasks*, mas não permite webhook de domínio externo no free.

## Decisão
**Adiada.** Na primeira semana da S3, subir um "hello world" Django em Render e Railway e testar: (1) webhook responde em < 5s? (2) cron roda? (3) limite do free aguenta até 07/12? Registrar o resultado aqui e mudar status para Aceito.

## Consequências
- Positivas: decisão com evidência, não com achismo.
- Negativas: não dá pra demonstrar deploy na review da S2 — aceitável, deploy é incremento da S4.
- Saber explicar: `collectstatic`/whitenoise; `DEBUG=False` e `ALLOWED_HOSTS`; por que segredos ficam em env; o que "dormir" significa num free tier.
