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


@st.cache_data
def load_data() -> pd.DataFrame:
    return load_sales_data(DATA_PATH)


def money(value: float) -> str:
    return f"${value:,.0f}"


st.set_page_config(
    page_title="Analise Executiva de Vendas",
    page_icon=":bar_chart:",
    layout="wide",
)

st.title("Analise Executiva de Vendas")

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
    top_n = st.slider("Top produtos", min_value=5, max_value=20, value=10, step=1)

filtered = filter_sales(df, years=years, regions=regions, categories=categories)
if filtered.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
    st.stop()

summary = kpis(filtered)

metric_cols = st.columns(4)
metric_cols[0].metric("Receita", money(summary["total_sales"]))
metric_cols[1].metric("Pedidos", f"{summary['orders']:,}")
metric_cols[2].metric("Linhas vendidas", f"{summary['items']:,}")
metric_cols[3].metric("Ticket medio", money(summary["avg_order"]))

chart_cols = st.columns((1.1, 1))

with chart_cols[0]:
    st.subheader("Vendas por mes")
    fig = px.line(
        sales_by_month(filtered),
        x="Year Month",
        y="Sales",
        markers=True,
        labels={"Year Month": "Mes", "Sales": "Vendas"},
    )
    fig.update_traces(line_color="#1f77b4")
    fig.update_layout(height=390, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, width="stretch")

with chart_cols[1]:
    st.subheader("Vendas por categoria")
    fig = px.bar(
        sales_by_category(filtered),
        x="Sales",
        y="Category",
        orientation="h",
        text_auto=".2s",
        labels={"Sales": "Vendas", "Category": "Categoria"},
        color="Category",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(showlegend=False, height=390, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, width="stretch")

lower_cols = st.columns((1, 1))

with lower_cols[0]:
    st.subheader("Vendas por ano")
    fig = px.bar(
        sales_by_year(filtered),
        x="Year",
        y="Sales",
        text_auto=".2s",
        labels={"Year": "Ano", "Sales": "Vendas"},
        color_discrete_sequence=["#2ca02c"],
    )
    fig.update_layout(height=390, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, width="stretch")

with lower_cols[1]:
    st.subheader("Top produtos")
    fig = px.bar(
        top_products(filtered, limit=top_n).sort_values("Sales"),
        x="Sales",
        y="Product Name",
        orientation="h",
        text_auto=".2s",
        labels={"Sales": "Vendas", "Product Name": "Produto"},
        color_discrete_sequence=["#ff7f0e"],
    )
    fig.update_layout(height=390, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, width="stretch")

st.subheader("Principais produtos por ano")
fig = px.bar(
    products_by_year(filtered, limit=min(top_n, 8)),
    x="Sales",
    y="Product Name",
    color="Year",
    barmode="group",
    orientation="h",
    labels={"Sales": "Vendas", "Product Name": "Produto", "Year": "Ano"},
    color_continuous_scale="Viridis",
)
fig.update_layout(height=520, margin=dict(l=10, r=10, t=20, b=10))
st.plotly_chart(fig, width="stretch")

with st.expander("Amostra dos dados tratados"):
    st.dataframe(filtered.head(100), width="stretch")
