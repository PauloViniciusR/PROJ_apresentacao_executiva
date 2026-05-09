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
├── docs/                    # Notas do projeto
├── notebooks/               # Analise exploratoria
├── reports/figures/         # Figuras exportadas pelo notebook
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

## Deploy no Streamlit Community Cloud

1. Faça push deste repositorio para o GitHub.
2. Acesse <https://share.streamlit.io/>.
3. Crie um novo app apontando para este repositorio.
4. Configure o arquivo principal como `app/app.py`.
5. O Streamlit instalara as dependencias a partir de `requirements.txt`.

## Pipeline

1. **Extracao**: leitura do CSV em `data/raw/superstore_sales.csv`.
2. **Tratamento**: conversao de datas, validacao de colunas e padronizacao de tipos.
3. **Features**: criacao de ano, mes e periodo mensal para agregacoes.
4. **Visualizacao**: notebook para analise exploratoria e Streamlit para consumo interativo.

## Principais resultados

- Base com 9.800 linhas e 18 colunas.
- Receita total historica de aproximadamente US$ 2,26 milhoes.
- Categorias analisadas: Office Supplies, Furniture e Technology.
- O dashboard permite filtrar por ano, regiao e categoria.

## Fonte dos dados

Dataset publico de vendas Superstore, originalmente disponibilizado no Kaggle:
<https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting>
