# ADR-0011: Avaliação no banco relacional; não usar MongoDB

- **Status:** Aceito (substitui o ADR-0002)
- **Data:** 2026-10-06
- **Sprint:** S2
- **Autor(es):** grupo

## Contexto
O ADR-0002 colocava `Avaliacao` no MongoDB para cumprir o requisito de NoSQL da ementa, com a justificativa de "dado semiestruturado". O professor autorizou a turma a **não usar** MongoDB se não fizer sentido na aplicação, desde que a decisão seja justificada em ADR. Ao implementar, revisamos a justificativa com o dado real na mão.

## Análise — o que a `Avaliacao` é de fato
| Critério do ADR-0002 para ir ao Mongo | `Avaliacao` real |
|---|---|
| Schema flexível / semiestruturado | **Fixo:** `nota` (1–5), `repetiria` (bool), `comentario` (texto). Três campos, sempre os mesmos. |
| Sem relacionamento forte | **Tem dois:** pertence a um `Usuario` (FK) e a uma `data` de `Cardapio`. É o mesmo formato de `Confirmacao`. |
| Não é referenciada pelo resto | O **dashboard cruza avaliações × confirmações por dia** — no relacional é uma agregação; com Mongo seriam duas consultas e junção em Python. |
| Integridade não importa | "Uma avaliação por pessoa por dia" é regra de negócio → `UNIQUE(usuario, data)`, que o Mongo só garante com índice único manual. |

Nenhum critério se sustenta. O custo, por outro lado, era concreto: um 2º serviço externo em free tier (Atlas), mais uma credencial, `pymongo` + `mongomock` nos testes, e um módulo `repositorio.py` cuja única função era esconder essa dependência.

## Alternativas consideradas
- **Manter Mongo "porque está na ementa"** — complexidade sem benefício técnico; o professor dispensou explicitamente.
- **Usar Mongo para outra coisa (logs, auditoria)** — inventar um caso de uso para justificar a ferramenta é o erro inverso.
- **`Avaliacao` como model Django** — mesmo padrão de `Confirmacao`; agregação com `Avg`/`Count`; zero infra nova.

## Decisão
`avaliacoes.models.Avaliacao` no banco relacional, com `UniqueConstraint(usuario, data)` e `resumo_do_dia()` via `aggregate(Count, Avg)`. O ADR-0002 passa a **Substituído por ADR-0011**. O projeto fica com **um único banco** (SQLite em dev, PostgreSQL em produção — ADR-0003).

## Consequências
- Positivas: um serviço externo a menos; testes sem mocks de banco; `JOIN` natural para o dashboard; menos uma tecnologia para explicar — e uma decisão de arquitetura para defender.
- Negativas: o grupo não demonstra NoSQL em código. Compensação: sabemos explicar **quando** um banco de documentos se justifica (schema variável, documentos aninhados, sem relacionamento forte) e **por que** este caso não é esse.
- Saber explicar: persistência poliglota como decisão caso a caso, não como regra; o critério da tabela acima; `aggregate` vs. `annotate`; por que `UNIQUE` composto é regra de negócio no banco.
