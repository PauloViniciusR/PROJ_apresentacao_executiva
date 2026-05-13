# Análise Executiva de Vendas

Projeto de ciência de dados para transformar uma base de vendas do Superstore em uma análise executiva e um dashboard interativo em Streamlit.

## Objetivo

Responder, de forma visual e reproduzível:

- como as vendas evoluíram no período analisado;
- quais categorias concentram mais receita;
- quais produtos lideram em vendas;
- como os principais produtos se comportam ao longo dos anos.

## Estrutura

```text
.
├── app/                     # Dashboard Streamlit
├── data/raw/                # Dataset original versionado
├── data/processed/          # Dataset tratado e relatório de qualidade
├── docs/                    # Notas do projeto
├── notebooks/               # Análise exploratória
├── reports/figures/         # Figuras exportadas pelo notebook
├── scripts/                 # Rotinas reproduzíveis de processamento
├── src/                     # Pipeline reutilizável de dados e features
├── README.md
└── requirements.txt
```

## Como executar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/app.py
```

Para reconstruir a camada tratada:

```bash
python scripts/build_processed_dataset.py
```

## Deploy no Streamlit Community Cloud

1. Faça push deste repositório para o GitHub.
2. Acesse <https://share.streamlit.io/>.
3. Crie um novo app apontando para este repositório.
4. Configure o arquivo principal como `app/app.py`.
5. O Streamlit instalará as dependências a partir de `requirements.txt`.

## Pipeline

1. **Extração**: leitura do CSV em `data/raw/superstore_sales.csv`.
2. **Tratamento**: conversão de datas, validação de colunas, padronização de textos, tratamento de CEPs e remoção de duplicidades comerciais.
3. **Features**: criação de ano, mês, período mensal e prazo de envio.
4. **Persistência**: geração de `data/processed/superstore_sales_clean.csv` e `data/processed/DATASET.md`.
5. **Visualização**: notebook para análise exploratória e Streamlit para consumo interativo.

## Qualidade dos dados

- Base bruta: 9.800 linhas e 18 colunas.
- Base tratada: 9.799 linhas e 24 colunas.
- 1 duplicidade comercial removida.
- 11 CEPs ausentes corrigidos para Burlington, Vermont.
- Datas de pedido e envio validadas, sem registros inválidos.
- Vendas convertidas para numérico, sem valores nulos, zerados ou negativos.

## Principais resultados

- Base tratada com 9.799 linhas e 24 colunas.
- Receita total histórica de aproximadamente US$ 2,26 milhões.
- Categorias analisadas: Office Supplies, Furniture e Technology.
- O dashboard permite filtrar por ano, região e categoria.

## Fonte dos dados

Dataset público de vendas Superstore, originalmente disponibilizado no Kaggle:
<https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting>
