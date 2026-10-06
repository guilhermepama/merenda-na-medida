# ADR-0003: SQLite em desenvolvimento, PostgreSQL (Neon) em produção

- **Status:** Aceito
- **Data:** 2026-10-06
- **Sprint:** S1 (SQLite) / S3 (Postgres)
- **Autor(es):** grupo

## Contexto
Na reconstrução, cada minuto de setup é minuto a menos de código. Postgres local em WSL para 4+ pessoas é atrito.

## Alternativas consideradas
- **Postgres desde o dia 1** — ambiente igual à produção, mas setup em cada máquina.
- **SQLite em dev, Postgres em prod via `DATABASE_URL`** — zero setup; a troca é uma variável de ambiente.

## Decisão
`DATABASES` lido de `DATABASE_URL` com `dj-database-url`. Vazio → SQLite. Na S3, apontar para o Neon e rodar `migrate`.

## Consequências
- Positivas: todo mundo roda em 2 minutos.
- Negativas: diferenças sutis SQLite/Postgres (tipos, case-sensitivity em `LIKE`). Mitigação: usar só ORM, nada de SQL cru; testar no Neon na S3 antes da review.
- Saber explicar: variáveis de ambiente / 12-factor; por que não commitar `.env`.
