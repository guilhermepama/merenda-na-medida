# ADR-0002: Persistência poliglota — PostgreSQL para o núcleo, MongoDB para avaliações

- **Status:** Substituído por [ADR-0011](0011-avaliacao-relacional-sem-mongodb.md) — a análise com o dado real não sustentou a justificativa; mantido como registro do raciocínio original
- **Data:** 2026-10-06
- **Sprint:** S1 (modelo) / S2 (Mongo)
- **Autor(es):** grupo

## Contexto
A ementa exige banco relacional e NoSQL. Precisávamos que a divisão fizesse sentido técnico, não só cumprisse tabela.

## Alternativas consideradas
- **Tudo relacional** — mais simples, mas não cumpre a ementa.
- **Tudo no Mongo** — perde integridade referencial em `Confirmacao(usuario, data)`, que é o dado mais crítico do sistema.
- **Poliglota por natureza do dado** — relacional onde há vínculo forte; documento onde o dado é opinativo, semiestruturado e não é referenciado por ninguém.

## Decisão
- PostgreSQL (via ORM): `Usuario`, `Cardapio`, `Confirmacao`.
- MongoDB Atlas (via `pymongo`): coleção `avaliacoes`.
- **O pymongo só existe em `avaliacoes/repositorio.py`.** Views chamam `repositorio.salvar()` / `repositorio.listar_por_data()`. Nenhum outro módulo importa pymongo.

## Consequências
- Positivas: justificativa técnica honesta; Mongo isolado — se cair, só avaliação para; fácil de mostrar no quadro.
- Negativas: dois serviços externos pra configurar; `usuario_id` no Mongo é um inteiro "solto" sem FK — aceitável porque avaliação é opinião, não transação.
- Saber explicar: integridade referencial; schema flexível; o que é um *repository* e por que isola a dependência.
