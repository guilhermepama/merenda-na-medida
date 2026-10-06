# ADR-0012: Painel da cozinha próprio; o Django Admin fica só para a equipe técnica

- **Status:** Aceito
- **Data:** 2026-10-06
- **Sprint:** S3
- **Autor(es):** grupo

## Contexto
Na Sprint 1 (S1.4) a cozinha cadastrava o cardápio pelo `/admin/` do Django — "zero tela custom". Funcionou, mas o admin é uma ferramenta de **dados** (CRUD por tabela), não de **tarefa**: a cozinha precisa ver a semana, lançar o jantar, saber quem vai e como foi, e lá ela enxerga tabelas, IDs, permissões e grupos. A importação do CSV mensal só existia como comando de terminal, que a cozinha não roda.

## Alternativas consideradas
- **Manter o admin padrão** — zero código; mas a cozinha continua navegando por tabelas e sem importar o CSV sozinha.
- **Re-skin do admin (tema tipo django-unfold)** — 1 pacote + settings; muda a aparência, não o fluxo. Continua sendo CRUD por tabela, e é uma dependência a mais para manter.
- **Substituir o admin inteiro por telas próprias** — refaz em código o que o Django já entrega testado (usuários, permissões, filtros); muito código para explicar e testar sem ganho para a cozinha.
- **Painel só com as tarefas da cozinha, admin mantido para a equipe técnica** — pouco código, no mesmo stack do site (Bootstrap + HTMX, ADR-0004).

## Decisão
Novo app `painel` (sem models — é interface sobre `cardapio`, `confirmacoes` e `avaliacoes`) em `/painel/`, com quatro abas:

| Aba | O que faz | Detalhe técnico |
|---|---|---|
| Cardápio | Semana seg–sex; edita o dia **no lugar** | HTMX troca só a `<div>` da linha (`_linha_cardapio.html`); sem JS, `?editar=` + POST/redirect |
| Confirmados | Lista nominal do dia, imprimível | `select_related("usuario")` — 1 query com JOIN |
| Avaliações | Média, % repetiria, distribuição 1–5, comentários | **Anônimas**: `.values("nota","repetiria","comentario")` — o usuário nem é lido do banco |
| Importar CSV | Upload do cardápio mensal | Mesma função do comando (`cardapio/importacao.py`) |

O `/producao/` (últimos 7 dias) virou a 5ª aba. Acesso por `painel.permissoes.apenas_cozinha`: anônimo → login do site; logado sem `is_staff` → 403. O `/admin/` continua registrado, para a equipe técnica.

Regras decididas junto:
- **Uma regra de importação, duas portas.** A lógica saiu do management command para `importar_csv()`; o comando e o upload chamam a mesma função.
- **Importação tudo-ou-nada** (`transaction.atomic`): uma linha errada desfaz o arquivo inteiro e a mensagem diz qual linha.
- **CSV do Excel aceito**: leitura em `utf-8-sig`, que remove o BOM que o Excel do Windows grava no início do arquivo.
- **Avaliação anônima para a cozinha**: se quem cozinha vê quem deu 1 estrela, o aluno deixa de avaliar com sinceridade e o dado perde valor.

## Consequências
- Positivas: a cozinha opera sem tocar no admin nem no terminal; edição inline mostra HTMX num caso real além do toggle; a regra de importação ficou testável num lugar só.
- Negativas: são telas nossas para manter (5 templates + 5 views); o painel mostra seg–sex fixo (`DIAS_COM_JANTAR`) — se houver jantar no sábado, muda a constante.
- Saber explicar: diferença entre ferramenta de dados (admin) e de tarefa (painel); `outerHTML` + `hx-target` na edição inline e o fallback sem JS; por que `transaction.atomic` na importação; `values_list(...).annotate(Count)` como `GROUP BY`; 302 × 403 no controle de acesso; o BOM do Excel.
