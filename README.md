# Analise Executiva de Vendas

Projeto de ciencia de dados para transformar uma base de vendas do Superstore em uma analise executiva e um dashboard interativo em Streamlit.

## Objetivo

Responder, de forma visual e reproduzivel:

- como as vendas evoluiram no periodo analisado;
- quais categorias concentram mais receita;
- quais produtos lideram em vendas;
- como os principais produtos se comportam ao longo dos anos.

## Estrutura

```text
.
├── app/                     # Dashboard Streamlit
├── data/raw/                # Dataset original versionado
├── data/processed/          # Dataset tratado e relatorio de qualidade
├── docs/                    # Notas do projeto
├── notebooks/               # Analise exploratoria
├── reports/figures/         # Figuras exportadas pelo notebook
├── scripts/                 # Rotinas reproduziveis de processamento
├── src/                     # Pipeline reutilizavel de dados e features
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

1. Faça push deste repositorio para o GitHub.
2. Acesse <https://share.streamlit.io/>.
3. Crie um novo app apontando para este repositorio.
4. Configure o arquivo principal como `app/app.py`.
5. O Streamlit instalara as dependencias a partir de `requirements.txt`.

## Pipeline

1. **Extracao**: leitura do CSV em `data/raw/superstore_sales.csv`.
2. **Tratamento**: conversao de datas, validacao de colunas, padronizacao de textos, tratamento de CEPs e remocao de duplicidades comerciais.
3. **Features**: criacao de ano, mes, periodo mensal e prazo de envio.
4. **Persistencia**: geracao de `data/processed/superstore_sales_clean.csv` e `data/processed/DATASET.md`.
5. **Visualizacao**: notebook para analise exploratoria e Streamlit para consumo interativo.

## Qualidade dos dados

- Base bruta: 9.800 linhas e 18 colunas.
- Base tratada: 9.799 linhas e 24 colunas.
- 1 duplicidade comercial removida.
- 11 CEPs ausentes corrigidos para Burlington, Vermont.
- Datas de pedido e envio validadas, sem registros invalidos.
- Vendas convertidas para numerico, sem valores nulos, zerados ou negativos.

## Principais resultados

- Base tratada com 9.799 linhas e 24 colunas.
- Receita total historica de aproximadamente US$ 2,26 milhoes.
- Categorias analisadas: Office Supplies, Furniture e Technology.
- O dashboard permite filtrar por ano, regiao e categoria.

## Fonte dos dados

Dataset publico de vendas Superstore, originalmente disponibilizado no Kaggle:
<https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting>
