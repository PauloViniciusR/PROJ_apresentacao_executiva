from pathlib import Path
import sys

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.data import clean_sales_data, data_quality_summary


RAW_PATH = ROOT_DIR / "data" / "raw" / "superstore_sales.csv"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
PROCESSED_PATH = PROCESSED_DIR / "superstore_sales_clean.csv"
REPORT_PATH = PROCESSED_DIR / "DATASET.md"


def build_processed_dataset() -> None:
    raw = pd.read_csv(RAW_PATH)
    cleaned = clean_sales_data(raw)
    summary = data_quality_summary(raw, cleaned)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    export = cleaned.copy()
    for column in ["Order Date", "Ship Date", "Year Month"]:
        export[column] = export[column].dt.strftime("%Y-%m-%d")
    export.to_csv(PROCESSED_PATH, index=False)

    REPORT_PATH.write_text(dataset_report(summary), encoding="utf-8")

    print(f"Processed dataset: {PROCESSED_PATH}")
    print(f"Quality report: {REPORT_PATH}")


def dataset_report(summary: dict[str, int]) -> str:
    return f"""# Dataset Tratado - Superstore Sales

Arquivo gerado: `data/processed/superstore_sales_clean.csv`

Este arquivo representa a camada tratada usada para apresentacao do case executivo. O arquivo bruto permanece versionado em `data/raw/superstore_sales.csv` para garantir rastreabilidade.

## Resumo do tratamento

| Indicador | Valor |
| --- | ---: |
| Linhas no bruto | {summary["raw_rows"]:,} |
| Colunas no bruto | {summary["raw_columns"]:,} |
| Linhas no tratado | {summary["processed_rows"]:,} |
| Colunas no tratado | {summary["processed_columns"]:,} |
| Linhas removidas no tratamento | {summary["removed_rows"]:,} |
| CEPs ausentes antes | {summary["missing_postal_before"]:,} |
| CEPs ausentes depois | {summary["missing_postal_after"]:,} |
| Datas de pedido invalidas | {summary["invalid_order_dates"]:,} |
| Datas de envio invalidas | {summary["invalid_ship_dates"]:,} |
| Valores de venda invalidos | {summary["invalid_sales"]:,} |
| Vendas zeradas ou negativas | {summary["non_positive_sales"]:,} |
| Envios antes do pedido | {summary["invalid_shipments"]:,} |
| Duplicidades comerciais identificadas | {summary["business_duplicates"]:,} |

## Regras aplicadas

- Validacao das colunas obrigatorias do dataset.
- Padronizacao de campos textuais com remocao de espacos excedentes.
- Conversao de `Order Date` e `Ship Date` para data.
- Conversao de `Sales` para valor numerico.
- Remocao de registros sem data de pedido valida, sem venda valida ou com venda menor ou igual a zero.
- Remocao de duplicidade comercial considerando pedido, cliente, produto, datas, modo de envio e valor.
- Padronizacao de `Postal Code` como texto de cinco caracteres para preservar zeros a esquerda.
- Correcao explicita dos CEPs ausentes de Burlington, Vermont, para `05401`.
- Criacao das features `Year`, `Month`, `Month Name`, `Year Month`, `Ship Days` e `Is Valid Shipment`.
- Remocao de registros com envio anterior ao pedido.
- Ordenacao final por data de pedido, pedido e linha original.

## Como reproduzir

```bash
python scripts/build_processed_dataset.py
```
"""


if __name__ == "__main__":
    build_processed_dataset()
