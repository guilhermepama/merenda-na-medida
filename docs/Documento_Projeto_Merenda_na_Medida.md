# Documento de Projeto: Merenda na Medida

**Curso:** Tecnologia em Desenvolvimento de Software Multiplataforma — Fatec Olímpia
**Disciplinas integradas:** ILP-037 (Técnicas de Programação II) · ISW-030 (Desenvolvimento Web III) · AGO-021 (Gestão Ágil de Projetos de Software)
**Interlocutor:** Fatec Olímpia + Diretoria

---

## Sumário

1. Contexto e Problema
2. Tese do Produto
3. Delimitação do Projeto
4. Stack Tecnológica
5. Arquitetura do Sistema
6. Escopo
7. MVP
8. Metodologia de Trabalho
9. Sprints (Backlog Detalhado)
10. Riscos e Premissas
11. Próximos Passos

---

## 1. Contexto e Problema

No dia a dia da Fatec, o cardápio do jantar é enviado mensalmente em PDF no grupo da faculdade, acompanhado de uma pergunta manual sobre quem vai comer. Isso gera dois problemas recorrentes:

- **Para o aluno:** atrito para descobrir o que será servido em cada dia.
- **Para a equipe de produção:** dificuldade de estimar a quantidade de comida a preparar, gerando desperdício de alimentos.

Apesar de parecerem informações simples, elas têm impacto real no fim do dia — tanto na experiência do aluno quanto no planejamento da cozinha.

## 2. Tese do Produto

Um sistema informatizado que centraliza a **consulta ao cardápio** e coleta a **expectativa do número de pessoas que vão comer**, por meio do site e de um chatbot no Telegram, reduzindo o atrito de consulta e o desperdício de produção.

O usuário cria uma conta, associa seu número de Telegram, confirma presença dia a dia, avalia o jantar e indica se costuma repetir o prato. Todo o fluxo gira em torno do jantar.

## 3. Delimitação do Projeto

- O sistema cobre **exclusivamente o jantar** — não café da manhã nem almoço, nesta fase.
- Dois canais de interação: **site responsivo** (desktop e mobile) e **chatbot no Telegram**.
- Confirmação de presença é um **toggle diário**, alterável a qualquer momento até um horário de corte definido.
- Notificações são **configuráveis por usuário** (site, Telegram, ambos ou nenhum) e podem ser desativadas a qualquer momento.
- O sistema deve ser **escalável**, assumindo acesso diário de múltiplos usuários simultaneamente.
- Escopo institucional: **Fatec Olímpia**, uma única unidade.

## 4. Stack Tecnológica

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Backend | Django + Python 3 | Framework MTV robusto, exigido pela ementa de Web III |
| Front-end | Bootstrap (responsivo) | Layout único funcionando em desktop e mobile |
| Interatividade | HTMX | Atualizações parciais de tela (ex: toggle de presença) sem reload |
| Interatividade | Alpine.js | Micro-interações leves no client-side (ex: preferências de notificação) |
| Banco relacional (dev) | SQLite | Banco inicial de desenvolvimento (Sprint 1) |
| Banco relacional (produção) | PostgreSQL (Neon) | Dados com forte integridade referencial: usuários, cardápio, confirmações |
| Banco não-relacional | MongoDB (Atlas) | Avaliações — dado semiestruturado, sem relacionamento rígido, schema flexível |
| API | Django REST Framework (DRF) | Exposição de endpoints para o bot do Telegram consumir |
| Autenticação de API | JWT (`simplejwt`) | Autenticação stateless para as requisições do bot |
| Bot | Telegram Bot API | Canal alternativo de confirmação e notificação |
| Testes | pytest / pytest-django | TDD nas regras críticas do sistema |
| Deploy | Railway ou Render | Publicação do sistema em produção |
| Ambiente de desenvolvimento | WSL (Windows Subsystem for Linux) | Ambiente Linux local para desenvolvimento |

## 5. Arquitetura do Sistema

O sistema é dividido em três frentes que conversam entre si:

1. **Aplicação web (Django):** interface principal — cadastro, cardápio, confirmação, avaliação, dashboard da produção.
2. **API REST (DRF + JWT):** camada de integração, consumida pelo bot do Telegram para consultar cardápio e registrar confirmações.
3. **Bot do Telegram:** canal alternativo de interação, replicando a confirmação de presença e enviando a notificação diária.

**Persistência poliglota** (decisão deliberada, não só exigência da ementa):
- Dados com relacionamento forte e integridade referencial (`Usuario`, `Cardapio`, `Confirmacao`) → **PostgreSQL**.
- Dados semiestruturados e mais soltos, sem dependência rígida do restante do modelo (`Avaliacao`) → **MongoDB**.

```
[Aluno] ──> [Site Django (Bootstrap + HTMX/Alpine)] ──┐
                                                        ├──> [PostgreSQL: Usuario, Cardapio, Confirmacao]
[Bot Telegram] ──> [API DRF + JWT] ───────────────────┘
                                                        └──> [MongoDB: Avaliacao]
```

## 6. Escopo

### Dentro do escopo

**Autenticação e perfil**
- Cadastro/login de usuário
- Vínculo do número de Telegram à conta
- Preferências de notificação (site, Telegram, ambos, nenhum)

**Cardápio**
- Cadastro do cardápio do jantar por data
- Consulta do cardápio do dia e da semana

**Confirmação de presença**
- Toggle diário, editável até horário de corte
- Contagem agregada de confirmados por dia
- Chatbot Telegram: pergunta diária e confirmação

**Avaliação**
- Avaliação do jantar (nota e/ou "repetiria o prato")
- Histórico de avaliações por prato

**Painel da produção**
- Dashboard com confirmações do dia e comparativo com dias anteriores

### Fora do escopo (nesta fase)

- Pagamento ou controle financeiro do jantar
- Cardápio de café da manhã e almoço
- Aplicativo mobile nativo
- Recomendação automática de cardápio via histórico/IA
- Gestão de estoque e compra de insumos
- Múltiplos campi/unidades

### Propostas para versões futuras

- Estoque e planejamento de compras baseado na previsão de confirmados
- Relatório de desperdício estimado (previsto vs. realmente preparado)
- Extensão do fluxo para café da manhã e almoço
- Ranking de pratos mais bem avaliados
- Notificação preditiva de baixa adesão

## 7. MVP (Produto Mínimo Viável)

O menor conjunto de funcionalidades que resolve o problema central de ponta a ponta:

1. Cadastro/login de usuário
2. Cadastro e consulta do cardápio do jantar por data
3. Confirmação de presença (toggle) pelo site
4. Contagem agregada de confirmados, visível para a produção

Com isso, o sistema já é utilizável de verdade: o aluno sabe o que vai comer, e a produção sabe quantos vão comer. Chatbot, avaliação e dashboards mais ricos são incrementos construídos sobre essa base ao longo das sprints seguintes.

## 8. Metodologia de Trabalho

O projeto segue **Scrum**, com sprints alinhadas ao cronograma da disciplina de Web III. Cada sprint entrega algo **utilizável isoladamente** — não apenas trabalho acumulado sem valor perceptível até o final.

**Cerimônias previstas:**
- Sprint Planning (início de cada sprint)
- Sprint Review (entrega e demonstração ao final de cada sprint)
- Retrospectiva (ajustes de processo do grupo)

**Papéis Scrum** *(a definir com o grupo)*

| Papel | Responsável |
|---|---|
| Product Owner | — |
| Scrum Master | — |
| Dev Team | — |

## 9. Sprints (Backlog Detalhado)

**Convenções:** Estimativa em Story Points (Fibonacci: 1, 2, 3, 5, 8). Definition of Done geral: código commitado, revisado por 1 colega, testado (manual ou pytest), sem quebrar funcionalidade existente, template responsivo.

### Sprint 1 — Fundação (Aulas 4–6)
**Goal:** cardápio visível e gerenciável, com contas de usuário.

| # | Entrega | SP | Tasks |
|---|---|---|---|
| S1.1 | Cadastro do cardápio por data | 5 | Model `Cardapio`/`ItemCardapio` · migration · view de criação · template |
| S1.2 | Consulta do cardápio do dia/semana | 3 | View de listagem com filtro de data · template · navegação entre dias |
| S1.3 | Cadastro e login de usuário | 3 | Configurar auth · views de cadastro/login/logout · templates |
| S1.4 | Gestão de cardápios pelo Django Admin | 2 | Registro no `admin.py` · `list_display`/`list_filter` |

**Total: 13 SP** — **DoD:** CRUD de cardápio 100% funcional, login/logout operando.

### Sprint 2 — Confirmação + NoSQL + HTMX (Aulas 7–11)
**Goal:** núcleo do produto funcionando de ponta a ponta.

| # | Entrega | SP | Tasks |
|---|---|---|---|
| S2.1 | Confirmação/cancelamento de presença (toggle) até horário de corte | 5 | Model `Confirmacao` · view de toggle · regra de corte · template |
| S2.2 | Atualização da confirmação sem reload de página | 3 | Integrar HTMX (`hx-post`/`hx-swap`) |
| S2.3 | Dashboard de contagem agregada por dia | 5 | View de dashboard (query agregada) · template |
| S2.4 | Avaliação do jantar (nota + repetiria) | 5 | Conexão MongoDB (`pymongo`) · estrutura de documento `Avaliacao` · view e template de avaliação |

**Total: 18 SP** — **DoD:** toggle funcional, dashboard com números reais, avaliações persistindo no Mongo.

### Sprint 3 — API, Autenticação e Bot (Aulas 12–15)
**Goal:** sistema pronto para o bot consumir; banco em produção.

| # | Entrega | SP | Tasks |
|---|---|---|---|
| S3.1 | Migração do banco relacional para PostgreSQL (Neon) | 3 | Configurar `DATABASE_URL` · rodar migrations · testar app |
| S3.2 | Vínculo de Telegram à conta do usuário | 3 | Campo `telegram_id` · view/form de vínculo · template |
| S3.3 | API para consulta de cardápio e envio de confirmação | 8 | Serializers/ViewSets DRF · autenticação JWT · documentação Swagger |
| S3.4 | Preferências de notificação com interações leves no front | 2 | Toggle com Alpine.js |

**Total: 16 SP** — **DoD:** API testável via Swagger/Postman, JWT funcionando, bot lendo cardápio via endpoint.

### Sprint 4 — Notificações, Testes e Deploy (Aulas 17–19)
**Goal:** sistema publicado, testado, notificando automaticamente.

| # | Entrega | SP | Tasks |
|---|---|---|---|
| S4.1 | Mensagem diária automática perguntando se vai jantar | 8 | Bot: comando de pergunta diária · rotina agendada (cron) · webhook de resposta |
| S4.2 | Ativação/desativação de notificações a qualquer momento | 2 | Persistir preferência no fluxo de envio |
| S4.3 | Cobertura de testes das regras críticas | 5 | pytest: toggle, contagem, vínculo Telegram |
| S4.4 | Sistema publicado em produção | 5 | Deploy Railway/Render · `collectstatic`/whitenoise · variáveis de ambiente |
| S4.5 | SEO básico | 2 | Meta tags · `sitemap.xml` |

**Total: 22 SP** — **DoD:** sistema no ar por URL pública, bot enviando mensagem diária real, testes passando.

### Resumo de Esforço

| Sprint | Story Points |
|---|---|
| Sprint 1 | 13 |
| Sprint 2 | 18 |
| Sprint 3 | 16 |
| Sprint 4 | 22 |
| **Total** | **69** |

> A Sprint 4 concentra bem mais SP que as demais — vale reavaliar essa distribuição no Sprint Planning, redistribuindo tasks (ex: SEO) para uma sprint anterior se houver capacidade.

## 10. Riscos e Premissas

| Risco | Impacto | Mitigação |
|---|---|---|
| Curva de aprendizado em 3 tecnologias novas por sprint (Mongo, HTMX/Alpine, DRF+JWT) | Atraso na entrega | Priorizar o MVP funcional antes de refinar; usar exemplos da disciplina como base |
| Integração com API do Telegram (webhooks, deploy) | Bloqueio técnico na Sprint 3–4 | Prototipar o bot cedo, mesmo antes de a API estar 100% pronta, usando mocks |
| Dependência de serviços externos gratuitos (Neon, Mongo Atlas, Railway/Render) | Limites de plano gratuito podem ser atingidos | Monitorar uso; ter plano B de downgrade de escopo se necessário |

**Premissas assumidas:**
- O grupo tem acesso a WSL/Linux para desenvolvimento consistente com o ambiente de deploy.
- A Diretoria da Fatec valida o uso de dados reais de cardápio para testes.

## 11. Próximos Passos

- Validar este documento com o grupo e, se necessário, com o professor
- Definir papéis Scrum (Product Owner, Scrum Master, Dev Team)
- Levar as entregas para o Taiga, quebradas em tasks
- Realizar o Sprint 1 Planning oficial
