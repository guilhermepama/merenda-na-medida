# Cardápios mensais

Um CSV por mês, `cardapio-AAAA-MM.csv`, com duas colunas: `data` (AAAA-MM-DD) e `descricao`.
`FERIADO` na descrição = não há jantar; o importador **não** cria cardápio nesse dia
(e sem cardápio o botão "Vou jantar" não aparece).

O PDF da Prefeitura (STARB) é digitalizado, sem camada de texto — a transcrição pro CSV é manual.
Fonte de outubro/2026: "Cardápios IV — Outubro 2026", RTs Franciele G. de Andrade CRN3-31612 /
Camila Ap. Mialichi Viseli CRN3-47671. Jantar servido às 20:40.

Importar:

```bash
python manage.py importar_cardapio dados/cardapio-2026-10.csv
```

Rodar de novo é seguro: atualiza o que mudou, não duplica (upsert por data).
