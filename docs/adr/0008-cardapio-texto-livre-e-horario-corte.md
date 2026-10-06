# ADR-0008: Cardápio como texto livre; horário de corte como função pura configurável

- **Status:** Proposto
- **Data:** 2026-10-06
- **Sprint:** S1 / S2
- **Autor(es):** 

## Contexto
O documento previa `Cardapio` + `ItemCardapio`. Na reconstrução, cada model a mais custa migration, admin, form e template. E a regra de corte é a única lógica de negócio que realmente merece teste.

## Alternativas consideradas
- **`Cardapio` + `ItemCardapio` (1:N)** — permite avaliar por prato e montar ranking futuro; custa um CRUD inteiro a mais.
- **`Cardapio.descricao` texto livre** — a cozinha cola o cardápio do dia como já faz no PDF. Avaliação é por dia, não por prato.

## Decisão
- `Cardapio(data unique, descricao)`. Sem `ItemCardapio` nesta fase. Avaliação referencia a `data`.
- `confirmacoes/regras.py::pode_alterar(data_jantar, agora, horario_corte) -> bool`, função pura; `HORARIO_CORTE` em `settings` (default `16:00`), lido de env.
- Toggle no site e no bot chamam a mesma função.

## Consequências
- Positivas: menos um model; a regra crítica é testável sem banco (5 testes cobrem).
- Negativas: ranking de pratos e avaliação por item ficam para versão futura (já estavam fora do escopo).
- Saber explicar: por que função pura é fácil de testar; `UNIQUE(usuario, data)`; o que acontece se tentar alterar após o corte (view devolve 403 e o parcial com botão desabilitado).
