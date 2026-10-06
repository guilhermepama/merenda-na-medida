# Merenda na Medida

Sistema de cardápio do jantar e confirmação de presença — Fatec Olímpia (DSM, 3º semestre).
Disciplinas: ILP-037 · ISW-030 · AGO-021.

- 📄 Documento do projeto: `docs/Documento_Projeto_Merenda_na_Medida.md`
- 🗺️ Plano de execução: `docs/PLANO_RECONSTRUCAO.md`
- 🧭 Decisões de arquitetura (ADRs): `docs/adr/`

## Rodando localmente

```bash
git clone <url-do-repo>
cd merenda-na-medida
python -m venv venv
source venv/bin/activate        # Windows/WSL: idem; PowerShell: venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env            # ajuste se quiser; o padrão já funciona com SQLite
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abra http://127.0.0.1:8000. Logado com um usuário **staff**, o link "Painel da cozinha" leva a
http://127.0.0.1:8000/painel/ — cardápio da semana, confirmados, avaliações e importação do CSV (ADR-0012).
O http://127.0.0.1:8000/admin/ continua disponível para a equipe técnica.

## API (Sprint 3 — consumida pelo bot)

```bash
python manage.py criar_bot          # cria o usuário de serviço e imprime BOT_PASSWORD (guarde)
```

- Swagger: http://127.0.0.1:8000/api/docs/
- Token: `POST /api/token/` com `{"username": "bot", "password": "..."}` → `access` (12h) e `refresh`
- Depois, header `Authorization: Bearer <access>` em `GET /api/cardapio/hoje/`, `POST /api/confirmacoes/`, `POST /api/vincular/`, `GET /api/usuarios/<telegram_id>/`
- Só o usuário `bot` passa (`api/permissoes.py`); um aluno com JWT recebe 403.

## PostgreSQL (Neon) — produção

1. Crie um projeto em https://neon.tech (free), banco `merenda`, região `sa-east-1`.
2. Copie a connection string para `DATABASE_URL` no `.env` (com `?sslmode=require`).
3. `python manage.py migrate` — pronto; o código não muda (ADR-0003).

## Testes

```bash
pytest
```

## Estrutura

| Pasta | Responsabilidade | Dono |
|---|---|---|
| `contas/` | usuário, login, vínculo Telegram, preferências | |
| `cardapio/` | cardápio por data, consulta dia/semana | |
| `confirmacoes/` | toggle de presença, regra de corte, dashboard | |
| `avaliacoes/` | avaliação do jantar (MongoDB) | |
| `api/` | DRF + JWT, consumida pelo bot | |
| `bot/` | webhook do Telegram, pergunta diária | |

## Papéis Scrum

| Papel | Quem |
|---|---|
| Product Owner | Guilherme Pama |
| Scrum Master | Heitor D'Ávila |
| Relatora (documentação, atas, Taiga) | Érica Crepald |
| Dev Team | Guilherme Pama, Heitor D'Ávila, João Suficier |

## Convenções

- Branch `main` sempre roda. Trabalho em branches `feat/<app>-<coisa>`, PR revisado por 1 colega.
- Commit: `tipo(app): o que fez (#id-taiga)` — ex.: `feat(cardapio): consulta da semana (#14)`.
- Toda decisão técnica vira ADR em `docs/adr/`.
