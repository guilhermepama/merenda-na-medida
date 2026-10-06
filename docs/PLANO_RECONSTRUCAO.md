# Plano de Reconstrução — Merenda na Medida

> Objetivo: reconstruir o projeto do zero da forma **mais simples possível**, de modo que
> todo integrante consiga **explicar cada conceito e cada função** na apresentação.
> Referência: `docs/Documento_Projeto_Merenda_na_Medida.md`.

---

## 0. Princípios da reconstrução

1. **Nada se perde de novo.** Git + GitHub antes da primeira linha de código. Commit por task. Push todo dia.
2. **Sempre existe um sistema rodando.** Cada fase termina com algo demonstrável. Nunca "metade de duas coisas".
3. **Uma tecnologia nova por vez.** Só se adiciona a próxima quando a anterior está funcionando e alguém do grupo sabe explicá-la.
4. **Toda decisão técnica vira um ADR** (ver `docs/adr/`). Se não dá pra justificar em meia página, não entra.
5. **Explicável > sofisticado.** Se há duas formas de fazer, escolhe-se a que cabe num quadro branco.

---

## 1. O que muda em relação ao documento original

| Item do documento | Decisão na reconstrução | Por quê |
|---|---|---|
| Alpine.js | **Mantido, uso mínimo** | Está no incremento esperado da S2 pelo professor. Usar só onde é natural: estado local de UI (ex: mostrar/ocultar opções de notificação). HTMX cuida de tudo que fala com o servidor. (ADR-0004) |
| Bot com framework (python-telegram-bot) | **Bot = 1 view Django (webhook) + `requests`** | Sem async, sem segundo processo. Explicável em 5 min. (ADR-0006) |
| Rotina agendada (cron/Celery) | **Management command + cron da plataforma** | Zero infra extra. `python manage.py perguntar_jantar`. (ADR-0007) |
| MongoDB espalhado | **Isolado em `avaliacoes/repositorio.py`** | O resto do sistema não sabe que o Mongo existe. (ADR-0002) |
| Sprint 4 com 22 SP | **SEO e preferências movidos pra Sprint 3** | O próprio documento já apontava o desbalanceamento. |
| Deploy Railway/Render | **Decisão adiada pra Sprint 3 (ADR-0009 em "proposto")** | Free tier do Render dorme (quebra webhook/cron). Avaliar na hora. |

Tudo que a ementa exige **continua**: Django MTV, banco relacional + NoSQL, API REST com JWT, HTMX, testes, deploy.

---

## 2. Estrutura do repositório (decidida, não discutir de novo)

```
merenda-na-medida/
├── docs/
│   ├── Documento_Projeto_Merenda_na_Medida.md
│   ├── PLANO_RECONSTRUCAO.md        ← este arquivo
│   └── adr/                          ← decisões arquiteturais
├── merenda/                          ← projeto Django (settings, urls, wsgi)
├── contas/                           ← Usuario (AbstractUser), login, vínculo Telegram, preferências
├── cardapio/                         ← Cardapio, consulta dia/semana, admin
├── confirmacoes/                     ← Confirmacao, toggle, regra de corte, dashboard
├── avaliacoes/                       ← Avaliacao no Mongo (repositorio.py isola o pymongo)
├── api/                              ← DRF: serializers, viewsets, JWT
├── bot/                              ← webhook do Telegram + management command
├── templates/                        ← base.html (Bootstrap) + parciais HTMX
├── tests/                            ← pytest
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

**Um app por domínio.** Cada integrante pode "adotar" um app e ser o responsável por explicá-lo.

---

## 3. Modelo de dados (fechado antes de codar)

### PostgreSQL (via Django ORM)

```
Usuario (AbstractUser)
  telegram_id         CharField, null, unique
  notificacao         CharField choices: site | telegram | ambos | nenhum   (default: site)

Cardapio
  data                DateField, unique
  descricao           TextField        (prato principal, acompanhamentos, sobremesa — texto livre)
  criado_em           DateTimeField auto

Confirmacao
  usuario             FK Usuario
  data                DateField
  confirmado          BooleanField
  atualizado_em       DateTimeField auto
  UNIQUE (usuario, data)        ← garante 1 registro por pessoa por dia
```

### MongoDB (coleção `avaliacoes`)

```json
{ "usuario_id": 12, "data": "2026-10-06", "nota": 4, "repetiria": true,
  "comentario": "faltou sal", "criado_em": "2026-10-06T20:15:00" }
```

**Decisão deliberada de simplicidade:** `Cardapio.descricao` é texto livre. Não há `ItemCardapio`.
Se sobrar tempo, vira melhoria futura. (ADR-0008)

### Regra de negócio central (a única que precisa de TDD de verdade)

```python
# confirmacoes/regras.py
def pode_alterar(data_jantar: date, agora: datetime, horario_corte: time) -> bool:
    """Confirmação só pode mudar até o horário de corte do próprio dia."""
```
Função pura, sem banco, testada com pytest em 5 casos. Isso é o que se mostra pro professor como "TDD".

---

## 4. Calendário real e o que ele impõe

| Sprint | Período | Incremento esperado (professor) | Situação em 06/10 |
|---|---|---|---|
| S1 | 17/08 – 14/09 | Levantamento de requisitos, modelagem de domínio, models/migrations, CRUD admin | **Encerrada.** Requisitos e modelagem existem (documento). Código: zero. |
| S2 | 21/09 – 19/10 | MongoDB Atlas, HTMX e Alpine.js | **Em andamento, faltam 13 dias.** Precisa entregar S1 + S2 na review. |
| S3 | 26/10 – 16/11 | API REST documentada, autenticação, integração com serviço externo | Normal |
| S4 | 23/11 – 07/12 | Testes, deploy, SEO, documentação e apresentação | Normal |

**Consequência:** as Fases 0, 1 e 2 abaixo têm que caber entre 06/10 e 19/10. Proposta de ritmo:

- **06–08/10** — Fase 0 (um encontro) + início da Fase 1
- **09–13/10** — Fase 1 completa (MVP rodando com SQLite)
- **14–18/10** — Fase 2 (HTMX, Alpine, Mongo)
- **19/10** — Review S2: demo do MVP + toggle sem reload + avaliação no Atlas

Se em 13/10 a Fase 1 não estiver pronta, a Fase 2 encolhe: entra HTMX no toggle (é pequeno) e Mongo só com `salvar()`; Alpine fica num único `x-show`. Melhor levar menos coisa funcionando do que tudo pela metade.

Na retrospectiva da S2, registrar a reconstrução como fato e o que o grupo mudou pra não repetir (git diário, pareamento). Isso é conteúdo legítimo de Gestão Ágil, não vergonha.

## 5. Fases de execução

No Taiga mantenham as 4 sprints originais (ver seção 6) — as fases 0 e 1 juntas = Sprint 1.

### Fase 0 — Fundação (1 encontro, todos juntos)
Objetivo: repositório vivo, projeto rodando na máquina de todo mundo.

- [ ] Criar repositório no GitHub (org ou conta de um integrante + todos como collaborators)
- [ ] `git init`, `.gitignore` (Python, `.env`, `db.sqlite3`, `venv/`), primeiro commit
- [ ] `django-admin startproject merenda .` + `startapp` dos 6 apps
- [ ] `requirements.txt` mínimo: `django`, `python-dotenv`
- [ ] `.env.example` com `SECRET_KEY`, `DEBUG`, `DATABASE_URL` (vazio = SQLite)
- [ ] `README.md`: como clonar, criar venv, rodar
- [ ] **Todos** clonam e rodam `python manage.py runserver` → página inicial aparece
- [ ] Definir papéis Scrum e registrar no README
- [ ] ADRs 0001, 0002, 0003 escritos (são decisões já tomadas no documento)

**Checkpoint:** 4+ pessoas rodando o mesmo projeto a partir do GitHub.

### Fase 1 — MVP (= Sprint 1 + S2.1 + S2.3)
Objetivo: aluno vê cardápio e confirma; produção vê a contagem. **Só Django + SQLite + Bootstrap.**

1. `contas`: `Usuario(AbstractUser)` + `AUTH_USER_MODEL` (fazer ANTES da 1ª migration, senão dói)
2. `contas`: cadastro, login, logout (views do próprio Django `LoginView`/`LogoutView` + form de cadastro)
3. `cardapio`: model + admin registrado + view "cardápio de hoje" e "semana"
4. `confirmacoes`: model + view de toggle (POST normal, com reload) + `regras.pode_alterar`
5. `confirmacoes`: dashboard `/producao/` com `Confirmacao.objects.filter(data=hoje, confirmado=True).count()`
6. `templates/base.html` com Bootstrap via CDN, navbar, mensagens
7. `tests/test_regras.py` — 5 testes da regra de corte

**Checkpoint:** demo ponta a ponta sem nenhuma tecnologia "nova". Se o resto do semestre der errado, isso já é entregável.

### Fase 2 — HTMX + Mongo (= resto da Sprint 2)
1. HTMX via CDN em `base.html`
2. Toggle vira `hx-post` + `hx-swap` devolvendo só o parcial `_botao_confirmar.html`
3. `avaliacoes/repositorio.py`: `salvar(avaliacao)`, `listar_por_data(data)` usando `pymongo` (Atlas free)
4. View + template de avaliação (só liberada após o jantar do dia)
5. Preferências de notificação: form com Alpine (`x-data` controlando quais opções aparecem) + submit normal
6. ADR-0004 (HTMX + Alpine) e ADR-0002 revisitado com o que aprenderam

**Checkpoint:** toggle sem reload; avaliação aparecendo no Atlas.

### Fase 3 — API + JWT + Postgres (= Sprint 3)
1. Trocar `DATABASE_URL` para Neon (`dj-database-url`), rodar migrations, testar
2. DRF: `CardapioSerializer`, `ConfirmacaoSerializer`; endpoints:
   - `GET  /api/cardapio/hoje/`
   - `POST /api/confirmacoes/` `{ "telegram_id": "...", "confirmado": true }`
3. `simplejwt`: `/api/token/`. **O bot é o único cliente da API** e usa um usuário de serviço.
4. `drf-spectacular` → Swagger em `/api/docs/`
5. Vínculo Telegram: página "Conectar Telegram" gera código de 6 dígitos; usuário manda `/vincular 123456` pro bot (implementado na Fase 4, mas o campo e o código já existem aqui)
6. SEO básico (meta tags) — movido da Sprint 4

**Checkpoint:** Postman/Swagger consegue ler cardápio e confirmar via JWT.

### Fase 4 — Bot + Notificação + Deploy + Testes (= Sprint 4)
1. `bot/views.py`: `POST /bot/webhook/<segredo>/` recebe update, trata `/start`, `/vincular`, `/cardapio`, e botões "Vou / Não vou"
2. `bot/telegram.py`: `enviar_mensagem(chat_id, texto, botoes=None)` com `requests`
3. `bot/management/commands/perguntar_jantar.py`: para cada usuário com `notificacao in (telegram, ambos)` e `telegram_id`, envia pergunta do dia
4. Deploy (ADR-0009 decidido aqui) + cron da plataforma chamando o command
5. `setWebhook` apontando pro domínio público
6. Testes: toggle (view), contagem (dashboard), vínculo Telegram
7. **Ensaio da apresentação**: cada um explica o seu app em 3 minutos

**Checkpoint:** URL pública, bot mandando mensagem real às X horas, testes verdes.

---

## 6. Taiga — como organizar

**Estrutura:**
- **Epics** (7): Autenticação e Perfil · Cardápio · Confirmação de Presença · Avaliação · Painel da Produção · Integração Telegram · Infra e Qualidade
- **User Stories** = linhas das tabelas de sprint do documento (S1.1, S2.1…), escritas como
  *"Como [aluno/produção], quero [ação] para [benefício]"*, com os SP já estimados
- **Tasks** = a coluna "Tasks" de cada entrega, uma por linha
- **Sprints (Milestones)** = as 4 do documento, com datas das aulas

**Rastreabilidade (o que o professor de Gestão Ágil quer ver):**
- Título do commit referencia a story: `feat(cardapio): view da semana (#14)`
- Ao fechar uma task no Taiga, colar o link do commit/PR
- ADR referenciado na US que o motivou (ex: US "Avaliação" → "ver ADR-0002")

**Cerimônias — registro mínimo que vale nota:**
- Planning: lista de US puxadas + quem pegou o quê (comentário na milestone)
- Review: print/vídeo curto da demo anexado na milestone
- Retro: 3 linhas — manter / parar / começar — num card wiki do Taiga

---

## 7. Conceitos que cada integrante precisa saber explicar

Marque quem é o "dono" de cada um. Na apresentação, o dono responde.

| Conceito | Onde aparece no código | Dono |
|---|---|---|
| MTV (Model-Template-View) e diferença pro MVC | qualquer app | |
| ORM, migrations, `AUTH_USER_MODEL` | `contas/models.py` | |
| `UNIQUE (usuario, data)` e por que evita duplicidade | `confirmacoes/models.py` | |
| Query agregada (`count`, `annotate`) | dashboard | |
| CSRF e por que o HTMX precisa do token | `base.html` | |
| HTMX: `hx-post`, `hx-target`, `hx-swap` — "troca um pedaço do HTML" | toggle | |
| Alpine: `x-data`, `x-show` — estado só no navegador, sem servidor | preferências | |
| HTMX vs Alpine: quando o dado vai pro servidor e quando não | ADR-0004 | |
| Persistência poliglota: quando relacional, quando documento | ADR-0002 | |
| REST: recurso, verbo, status code; serializer = tradutor model↔JSON | `api/` | |
| JWT: stateless, `Bearer`, expiração, por que não sessão | `api/` | |
| Webhook vs polling | `bot/views.py` | |
| Management command + cron | `bot/management/` | |
| Variáveis de ambiente / 12-factor | `.env.example` | |
| TDD: red-green-refactor, função pura é testável | `tests/test_regras.py` | |
| Scrum: SP, velocity, DoD, incremento | Taiga | |

---

## 8. Riscos específicos da reconstrução

| Risco | Mitigação |
|---|---|
| Perder o trabalho de novo | GitHub desde a Fase 0; ninguém trabalha em pasta sem git; push diário |
| 13 dias para S1+S2 | Fase 1 em grupo no mesmo horário (sessões de 3h); Fase 2 com corte de escopo pré-definido (seção 4) |
| Grupo tentar fazer tudo em paralelo e nada integrar | Fase 0 e 1 em dupla/trio no mesmo ambiente; paralelizar só a partir da Fase 2, um app por pessoa |
| `AUTH_USER_MODEL` definido depois da 1ª migration | É o item 1 da Fase 1. Se errar: apagar `db.sqlite3` e migrations, refazer |
| Serviço free (Render) dormir e quebrar webhook/cron | Decidir deploy com teste real na Fase 3 (ADR-0009); plano B: VPS |
| Apresentação virar "mostrar tela" sem explicar | Seção 7 preenchida e ensaiada na Fase 4 |

---

## 9. Próximos passos imediatos

1. Grupo lê este plano e o documento original; discorda do que quiser **por escrito** (comentário no Taiga ou issue)
2. Fase 0 marcada: data, quem leva o repositório criado
3. Preencher papéis Scrum e donos da seção 7
4. Criar os Epics e a Sprint 1 no Taiga
