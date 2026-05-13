# Dataset Tratado - Superstore Sales

Arquivo gerado: `data/processed/superstore_sales_clean.csv`

Este arquivo representa a camada tratada usada para apresentacao do case executivo. O arquivo bruto permanece versionado em `data/raw/superstore_sales.csv` para garantir rastreabilidade.

## Resumo do tratamento

| Indicador | Valor |
| --- | ---: |
| Linhas no bruto | 9,800 |
| Colunas no bruto | 18 |
| Linhas no tratado | 9,799 |
| Colunas no tratado | 24 |
| Linhas removidas no tratamento | 1 |
| CEPs ausentes antes | 11 |
| CEPs ausentes depois | 0 |
| Datas de pedido invalidas | 0 |
| Datas de envio invalidas | 0 |
| Valores de venda invalidos | 0 |
| Vendas zeradas ou negativas | 0 |
| Envios antes do pedido | 0 |
| Duplicidades comerciais identificadas | 1 |

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
