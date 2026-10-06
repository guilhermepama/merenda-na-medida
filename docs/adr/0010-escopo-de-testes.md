# ADR-0010: Testes automatizados só nas regras críticas (TDD seletivo)

- **Status:** Proposto
- **Data:** 2026-10-06
- **Sprint:** S4 (mas a regra de corte é testada desde a S1)
- **Autor(es):** 

## Contexto
Cobertura total de um Django com 6 apps não cabe no tempo e não ensina mais do que uma cobertura focada. O professor quer ver TDD, não número de cobertura.

## Alternativas consideradas
- **Cobrir tudo** — irreal em 13 dias + S4.
- **Nenhum teste** — não cumpre a S4.
- **TDD nas regras de negócio + smoke test nas views** — o que quebra o produto é testado a fundo; o resto só "abre sem erro 500".

## Decisão
`pytest` + `pytest-django`. Obrigatórios:
1. `tests/test_regras.py` — `pode_alterar` (antes do corte, no corte, depois, dia anterior, dia seguinte). **Escrito antes da implementação** — esse é o TDD demonstrável.
2. `tests/test_confirmacoes.py` — toggle cria, toggle inverte, toggle após corte → 403; `UNIQUE` impede duplicata.
3. `tests/test_dashboard.py` — contagem bate com os registros.
4. `tests/test_vinculo.py` — código válido vincula; expirado não.
Smoke: cada URL principal responde 200/302 logado e deslogado.

## Consequências
- Positivas: ~15 testes que contam a história do produto; rodam em segundos.
- Negativas: API e bot ficam só com smoke — se sobrar tempo, testar `POST /api/confirmacoes/` com JWT.
- Saber explicar: ciclo red-green-refactor; fixture; por que função pura testa sem banco; o que `pytest-django` resolve (banco de teste).
