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

Abra http://127.0.0.1:8000 — e http://127.0.0.1:8000/admin para o painel.

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
| Product Owner | |
| Scrum Master | |
| Dev Team | |

## Convenções

- Branch `main` sempre roda. Trabalho em branches `feat/<app>-<coisa>`, PR revisado por 1 colega.
- Commit: `tipo(app): o que fez (#id-taiga)` — ex.: `feat(cardapio): consulta da semana (#14)`.
- Toda decisão técnica vira ADR em `docs/adr/`.
