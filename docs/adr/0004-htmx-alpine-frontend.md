# ADR-0004: HTMX para tudo que fala com o servidor; Alpine.js só para estado local de UI

- **Status:** Aceito
- **Data:** 2026-10-06
- **Sprint:** S2
- **Autor(es):** grupo

## Contexto
O incremento esperado da S2 cita HTMX e Alpine.js. Sem um critério, o grupo usaria os dois para a mesma coisa e não saberia explicar a diferença.

## Alternativas consideradas
- **Só HTMX** — cobre o toggle, mas não cumpre o incremento da sprint.
- **Framework SPA (React/Vue)** — fora da ementa e dobra a complexidade.
- **HTMX + Alpine com fronteira clara** — cada um com um papel.

## Decisão
- **HTMX** quando o dado **vai ou vem do servidor**: toggle de confirmação (`hx-post` → devolve o parcial `_botao_confirmar.html`), envio de avaliação.
- **Alpine** quando o estado **vive só no navegador**: mostrar/ocultar opções no form de preferências (`x-data`, `x-show`), feedback visual imediato.
- Regra de bolso: *se precisa de uma view Django, é HTMX; se não, é Alpine.*

## Consequências
- Positivas: critério simples de explicar; nenhum JS "escrito à mão".
- Negativas: duas libs via CDN; CSRF precisa ir no header do HTMX (`hx-headers` no `<body>`).
- Saber explicar: `hx-post`/`hx-target`/`hx-swap`; por que o servidor devolve HTML e não JSON; `x-data`/`x-show`; por que CSRF existe.
