# Dataset Tratado - Superstore Sales

Arquivo gerado: `data/processed/superstore_sales_clean.csv`

Este arquivo representa a camada tratada usada para apresentação do case executivo. O arquivo bruto permanece versionado em `data/raw/superstore_sales.csv` para garantir rastreabilidade.

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
| Datas de pedido inválidas | 0 |
| Datas de envio inválidas | 0 |
| Valores de venda inválidos | 0 |
| Vendas zeradas ou negativas | 0 |
| Envios antes do pedido | 0 |
| Duplicidades comerciais identificadas | 1 |

## Regras aplicadas

- Validação das colunas obrigatórias do dataset.
- Padronização de campos textuais com remoção de espaços excedentes.
- Conversão de `Order Date` e `Ship Date` para data.
- Conversão de `Sales` para valor numérico.
- Remoção de registros sem data de pedido válida, sem venda válida ou com venda menor ou igual a zero.
- Remoção de duplicidade comercial considerando pedido, cliente, produto, datas, modo de envio e valor.
- Padronização de `Postal Code` como texto de cinco caracteres para preservar zeros à esquerda.
- Correção explícita dos CEPs ausentes de Burlington, Vermont, para `05401`.
- Criação das features `Year`, `Month`, `Month Name`, `Year Month`, `Ship Days` e `Is Valid Shipment`.
- Remoção de registros com envio anterior ao pedido.
- Ordenação final por data de pedido, pedido e linha original.

## Como reproduzir

```bash
python scripts/build_processed_dataset.py
```
