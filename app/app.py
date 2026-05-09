from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.data import load_sales_data
from src.features import (
    filter_sales,
    kpis,
    products_by_year,
    sales_by_category,
    sales_by_month,
    sales_by_year,
    top_products,
)


DATA_PATH = ROOT_DIR / "data" / "raw" / "superstore_sales.csv"
PALETTE = ["#2563eb", "#16a34a", "#f97316", "#7c3aed", "#0891b2", "#dc2626"]


@st.cache_data
def load_data() -> pd.DataFrame:
    return load_sales_data(DATA_PATH)


def money(value: float) -> str:
    return f"US$ {value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.1%}"


def section_header(question: str, concept: str) -> None:
    st.markdown(f"### {question}")
    st.caption(concept)


def format_chart(fig, height: int = 460):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148, 163, 184, 0.25)")
    fig.update_yaxes(showgrid=False)
    return fig


def best_and_worst_year(yearly_sales: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    return (
        yearly_sales.loc[yearly_sales["Sales"].idxmax()],
        yearly_sales.loc[yearly_sales["Sales"].idxmin()],
    )


st.set_page_config(
    page_title="Analise Executiva de Vendas",
    page_icon=":bar_chart:",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
    }
    div[data-testid="stMetric"] {
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 8px;
        padding: 14px 16px;
        background: rgba(248, 250, 252, 0.55);
    }
    hr {
        margin: 2.2rem 0 1.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Analise Executiva de Vendas")
st.write(
    "Dashboard para explorar a evolucao de vendas, concentracao por categoria e "
    "desempenho dos principais produtos da base Superstore."
)

df = load_data()

with st.sidebar:
    st.header("Filtros")
    years = st.multiselect(
        "Ano",
        sorted(df["Year"].unique()),
        default=sorted(df["Year"].unique()),
    )
    regions = st.multiselect(
        "Regiao",
        sorted(df["Region"].unique()),
        default=sorted(df["Region"].unique()),
    )
    categories = st.multiselect(
        "Categoria",
        sorted(df["Category"].unique()),
        default=sorted(df["Category"].unique()),
    )
    top_n = st.slider("Quantidade de produtos no ranking", 5, 20, 10)

filtered = filter_sales(df, years=years, regions=regions, categories=categories)
if filtered.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
    st.stop()

summary = kpis(filtered)
date_min = filtered["Order Date"].min().strftime("%d/%m/%Y")
date_max = filtered["Order Date"].max().strftime("%d/%m/%Y")

st.caption(f"Periodo filtrado: {date_min} a {date_max}")
metric_cols = st.columns(4)
metric_cols[0].metric("Receita total", money(summary["total_sales"]))
metric_cols[1].metric("Pedidos unicos", f"{summary['orders']:,}")
metric_cols[2].metric("Itens vendidos", f"{summary['items']:,}")
metric_cols[3].metric("Ticket medio", money(summary["avg_order"]))

st.divider()

section_header(
    "1. Como foi a evolucao anual das vendas?",
    "Conceito: observar tendencia macro de crescimento ou retracao antes de detalhar produtos e categorias.",
)
yearly = sales_by_year(filtered)
best_year, worst_year = best_and_worst_year(yearly)
yearly["Sales Label"] = yearly["Sales"].map(money)

fig = px.bar(
    yearly,
    x="Year",
    y="Sales",
    text="Sales Label",
    labels={"Year": "Ano", "Sales": "Vendas"},
    color_discrete_sequence=[PALETTE[0]],
)
fig.update_traces(textposition="outside", cliponaxis=False)
fig = format_chart(fig, height=430)
st.plotly_chart(fig, width="stretch")
st.info(
    f"O melhor ano foi {int(best_year['Year'])}, com {money(best_year['Sales'])}. "
    f"O menor volume ocorreu em {int(worst_year['Year'])}, com {money(worst_year['Sales'])}."
)

st.divider()

section_header(
    "2. Em quais meses as vendas se concentram?",
    "Conceito: sazonalidade. A serie mensal ajuda a enxergar picos, quedas e periodos de maior pressao comercial.",
)
monthly = sales_by_month(filtered)
peak_month = monthly.loc[monthly["Sales"].idxmax()]
monthly["Periodo"] = monthly["Year Month"].dt.strftime("%Y-%m")

fig = px.line(
    monthly,
    x="Year Month",
    y="Sales",
    markers=True,
    labels={"Year Month": "Mes", "Sales": "Vendas"},
    color_discrete_sequence=[PALETTE[1]],
)
fig.update_traces(line_width=3, marker_size=8)
fig = format_chart(fig, height=470)
st.plotly_chart(fig, width="stretch")
st.info(
    f"O maior pico mensal aconteceu em {peak_month['Periodo']}, "
    f"com {money(peak_month['Sales'])} em vendas."
)

st.divider()

section_header(
    "3. Qual categoria sustenta a maior parte da receita?",
    "Conceito: composicao de receita. A comparacao por categoria mostra onde o faturamento esta mais concentrado.",
)
category_sales = sales_by_category(filtered)
category_sales["Share"] = category_sales["Sales"] / category_sales["Sales"].sum()
category_sales["Sales Label"] = category_sales["Sales"].map(money)
leader_category = category_sales.iloc[0]

fig = px.bar(
    category_sales.sort_values("Sales"),
    x="Sales",
    y="Category",
    orientation="h",
    text="Sales Label",
    labels={"Sales": "Vendas", "Category": "Categoria"},
    color="Category",
    color_discrete_sequence=PALETTE,
)
fig.update_traces(textposition="outside", cliponaxis=False)
fig = format_chart(fig, height=390)
fig.update_layout(showlegend=False)
st.plotly_chart(fig, width="stretch")
st.info(
    f"A categoria lider e {leader_category['Category']}, responsavel por "
    f"{pct(leader_category['Share'])} da receita filtrada."
)

st.divider()

section_header(
    "4. Quais produtos mais puxam o resultado?",
    "Conceito: ranking de Pareto. Poucos produtos podem explicar uma parte relevante do faturamento.",
)
product_rank = top_products(filtered, limit=top_n)
product_rank["Share"] = product_rank["Sales"] / filtered["Sales"].sum()
product_rank["Sales Label"] = product_rank["Sales"].map(money)
top_product = product_rank.iloc[0]
top_share = product_rank["Sales"].sum() / filtered["Sales"].sum()

fig = px.bar(
    product_rank.sort_values("Sales"),
    x="Sales",
    y="Product Name",
    orientation="h",
    text="Sales Label",
    labels={"Sales": "Vendas", "Product Name": "Produto"},
    color_discrete_sequence=[PALETTE[2]],
)
fig.update_traces(textposition="outside", cliponaxis=False)
fig = format_chart(fig, height=max(470, top_n * 34))
st.plotly_chart(fig, width="stretch")
st.info(
    f"O produto lider e {top_product['Product Name']}, com {money(top_product['Sales'])}. "
    f"Os {top_n} primeiros produtos representam {pct(top_share)} da receita filtrada."
)

st.divider()

section_header(
    "5. Esses produtos mantem desempenho ao longo dos anos?",
    "Conceito: consistencia. Comparar os principais produtos por ano separa picos isolados de desempenho recorrente.",
)
product_year = products_by_year(filtered, limit=min(top_n, 8))
product_year["Sales Label"] = product_year["Sales"].map(money)

fig = px.bar(
    product_year,
    x="Sales",
    y="Product Name",
    color="Year",
    barmode="group",
    orientation="h",
    text="Sales Label",
    labels={"Sales": "Vendas", "Product Name": "Produto", "Year": "Ano"},
    color_continuous_scale="Viridis",
)
fig.update_traces(textposition="outside", cliponaxis=False)
fig = format_chart(fig, height=560)
st.plotly_chart(fig, width="stretch")

year_count = product_year.groupby("Product Name")["Year"].nunique().sort_values(ascending=False)
most_consistent_product = year_count.index[0]
st.info(
    f"Produto com presenca mais consistente entre os anos filtrados: "
    f"{most_consistent_product}, aparecendo em {int(year_count.iloc[0])} ano(s)."
)

st.divider()

with st.expander("Dados tratados usados no dashboard"):
    st.dataframe(filtered.head(200), width="stretch")
