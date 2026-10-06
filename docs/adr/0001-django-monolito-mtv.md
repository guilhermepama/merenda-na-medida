# ADR-0001: Usar Django como monólito MTV

- **Status:** Aceito
- **Data:** 2026-10-06
- **Sprint:** S1
- **Autor(es):** grupo

## Contexto
A disciplina ISW-030 (Web III) exige Django. O produto tem 3 frentes (site, API, bot) e um grupo de 3º semestre que precisa explicar tudo.

## Alternativas consideradas
- **Monólito Django com apps por domínio** — um deploy, um banco de sessão, um `settings`. Simples de rodar e explicar.
- **Serviços separados (site, API, bot)** — "mais arquitetura", mas 3 deploys, 3 configs, e nada a ganhar para uma única unidade da Fatec.

## Decisão
Um único projeto Django (`merenda/`) com apps `contas`, `cardapio`, `confirmacoes`, `avaliacoes`, `api`, `bot`. A API (DRF) e o webhook do bot são **views dentro do mesmo processo**.

## Consequências
- Positivas: um `runserver` roda tudo; um integrante por app; deploy único.
- Negativas: escalabilidade horizontal limitada — irrelevante para o escopo (uma unidade).
- Saber explicar: MTV vs MVC (a *View* do Django é o *Controller* do MVC; o *Template* é a *View*); por que "monólito" não é palavrão.
