# ADR-0005: API com DRF + JWT; o bot é o único cliente

- **Status:** Aceito (grupo, 06/10/2026)
- **Data:** 2026-10-06
- **Sprint:** S3
- **Autor(es):** 

## Contexto
A S3 exige API REST documentada com autenticação. O site já usa sessão do Django; a API precisa ser consumida por um processo (o bot), não por um humano logado.

## Alternativas consideradas
- **JWT por usuário final** — cada aluno teria um token; o bot teria que guardar tokens de todo mundo. Complexo e sem ganho.
- **JWT para um usuário de serviço (`bot`)** — o bot se autentica uma vez; identifica o aluno pelo `telegram_id` no payload.
- **Sessão/CSRF na API** — não é stateless; foge do que se quer ensinar.

## Decisão
`simplejwt` com endpoint `/api/token/`. Um usuário `bot` (não-staff) obtém o token. Endpoints:
- `GET  /api/cardapio/hoje/`
- `POST /api/confirmacoes/` `{ "telegram_id": "...", "confirmado": true }`
Permissão custom: só o usuário `bot` acessa `/api/confirmacoes/`. Documentação com `drf-spectacular` em `/api/docs/`.

## Consequências
- Positivas: um token, um cliente, regra de permissão de 5 linhas; Swagger de graça.
- Negativas: o `telegram_id` vira a "identidade" na API — exige que o vínculo (ADR-0006) seja confiável.
- Saber explicar: REST (recurso/verbo/status); serializer; JWT stateless, `Authorization: Bearer`, expiração/refresh; diferença sessão vs token.
