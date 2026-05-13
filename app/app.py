from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.data import load_sales_data
from src.features import (
    kpis,
    products_by_year,
    sales_by_category,
    sales_by_month,
    sales_by_year,
    top_products,
)


DATA_PATH = ROOT_DIR / "data" / "raw" / "superstore_sales.csv"
PROCESSED_DATA_PATH = ROOT_DIR / "data" / "processed" / "superstore_sales_clean.csv"
PALETTE = ["#2563eb", "#16a34a", "#f97316", "#7c3aed", "#0891b2", "#dc2626"]


@st.cache_data
def load_data() -> pd.DataFrame:
    if PROCESSED_DATA_PATH.exists():
        df = pd.read_csv(PROCESSED_DATA_PATH, dtype={"Postal Code": "string"})
        for column in ["Order Date", "Ship Date", "Year Month"]:
            df[column] = pd.to_datetime(df[column], errors="coerce")
        return df

    return load_sales_data(DATA_PATH)


@st.cache_data
def load_quality_summary() -> dict[str, int]:
    raw = pd.read_csv(DATA_PATH)
    cleaned = load_data()
    order_dates = pd.to_datetime(raw["Order Date"], format="%d/%m/%Y", errors="coerce")
    ship_dates = pd.to_datetime(raw["Ship Date"], format="%d/%m/%Y", errors="coerce")
    sales = pd.to_numeric(raw["Sales"], errors="coerce")
    duplicate_key = [
        "Order ID",
        "Order Date",
        "Ship Date",
        "Ship Mode",
        "Customer ID",
        "Product ID",
        "Product Name",
        "Sales",
    ]

    return {
        "raw_rows": int(len(raw)),
        "raw_columns": int(raw.shape[1]),
        "processed_rows": int(len(cleaned)),
        "processed_columns": int(cleaned.shape[1]),
        "missing_postal_before": int(raw["Postal Code"].isna().sum()),
        "missing_postal_after": int(cleaned["Postal Code"].isna().sum()),
        "invalid_order_dates": int(order_dates.isna().sum()),
        "invalid_ship_dates": int(ship_dates.isna().sum()),
        "invalid_sales": int(sales.isna().sum()),
        "non_positive_sales": int(sales.le(0).sum()),
        "invalid_shipments": int(ship_dates.lt(order_dates).sum()),
        "business_duplicates": int(raw.duplicated(subset=duplicate_key).sum()),
    }


def money(value: float) -> str:
    return f"US$ {value:,.0f}"


def short_money(value: float) -> str:
    return f"US$ {value / 1000:,.0f} mil"


def pct(value: float) -> str:
    return f"{value:.1%}"


def number(value: float) -> str:
    return f"{value:,.1f}"


def section_header(question: str, concept: str) -> None:
    st.markdown(f"### {question}")
    st.caption(concept)


def format_chart(fig, height: int = 460):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=70, t=30, b=25),
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


def trend_text(first_value: float, last_value: float) -> str:
    if first_value == 0:
        return "sem base inicial para comparar"
    variation = (last_value / first_value) - 1
    direction = "crescimento" if variation >= 0 else "queda"
    return f"{direction} de {pct(abs(variation))}"


def analysis_text(title: str, paragraphs: list[str]) -> None:
    st.markdown(f"**{title}**")
    for paragraph in paragraphs:
        st.write(paragraph)


st.set_page_config(
    page_title="Análise Executiva de Vendas",
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
    h1, h2, h3 {
        color: #172033;
    }
    div[data-testid="stMetric"] {
        border-left: 4px solid #2563eb;
        padding: 4px 0 4px 14px;
        background: transparent;
    }
    hr {
        margin: 2.5rem 0 1.6rem;
    }
    .kpi-reading p {
        margin: 0 0 0.45rem;
        line-height: 1.55;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Análise Executiva de Vendas")
st.write(
    "Projeto de análise de dados desenvolvido com uma base pública do Kaggle, "
    "transformando dados brutos de vendas em informações claras para apoio à tomada de decisão."
)
st.markdown(
    """
    A análise contempla **vendas por ano**, **vendas por mês**, **vendas por categoria**,
    **top itens** e **evolução das vendas ao longo do tempo**.
    """
)

df = load_data()
quality = load_quality_summary()

with st.expander("Como os dados foram preparados"):
    st.write(
        "A planilha original já estava organizada. O trabalho realizado foi preparar os dados "
        "para uma leitura executiva confiável: datas padronizadas, valores conferidos, "
        "endereços completos e registros repetidos revisados."
    )
    quality_cols = st.columns(4)
    quality_cols[0].metric("Registros recebidos", f"{quality['raw_rows']:,}")
    quality_cols[1].metric("Registros usados", f"{quality['processed_rows']:,}")
    quality_cols[2].metric("Endereços completados", f"{quality['missing_postal_before'] - quality['missing_postal_after']:,}")
    quality_cols[3].metric("Registros repetidos removidos", f"{quality['business_duplicates']:,}")
    st.markdown(
        """
        - As datas foram organizadas para permitir comparações por ano e por mês.
        - Os valores de venda foram conferidos para garantir cálculos consistentes.
        - Alguns endereços que estavam incompletos foram preenchidos.
        - Foi calculado o número de dias entre a data do pedido e a data de envio.
        """
    )

filtered = df.copy()
if filtered.empty:
    st.warning("Nenhum registro encontrado na base analisada.")
    st.stop()

summary = kpis(filtered)
date_min = filtered["Order Date"].min().strftime("%d/%m/%Y")
date_max = filtered["Order Date"].max().strftime("%d/%m/%Y")
customers = filtered["Customer ID"].nunique()
products = filtered["Product Name"].nunique()
items_per_order = summary["items"] / summary["orders"] if summary["orders"] else 0
sales_per_item = summary["total_sales"] / summary["items"] if summary["items"] else 0

st.caption(f"Período analisado: {date_min} a {date_max}")
metric_cols = st.columns(4)
metric_cols[0].metric("Receita total", money(summary["total_sales"]))
metric_cols[1].metric("Pedidos únicos", f"{summary['orders']:,}")
metric_cols[2].metric("Itens vendidos", f"{summary['items']:,}")
metric_cols[3].metric("Ticket médio", money(summary["avg_order"]))

st.markdown("#### Como ler os indicadores principais")
st.markdown(
    f"""
    <div class="kpi-reading">
        <p><strong>Receita total:</strong> soma de todas as vendas da base analisada. Neste recorte, representa {money(summary["total_sales"])} em volume financeiro.</p>
        <p><strong>Pedidos únicos:</strong> quantidade de pedidos distintos, usada para medir volume de transações. A base analisada reúne {summary["orders"]:,} pedidos de {customers:,} clientes.</p>
        <p><strong>Itens vendidos:</strong> total de linhas de venda registradas. Em média, cada pedido contém {number(items_per_order)} item(ns), considerando {summary["items"]:,} itens vendidos.</p>
        <p><strong>Ticket médio:</strong> receita média por pedido. O valor atual é {money(summary["avg_order"])}, enquanto a venda média por item é {money(sales_per_item)} em um universo de {products:,} produtos distintos.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

section_header(
    "1. Vendas por ano",
    "Objetivo: avaliar a evolução anual da receita e entender se o desempenho cresce de forma consistente ao longo do período.",
)
yearly = sales_by_year(filtered)
best_year, worst_year = best_and_worst_year(yearly)
yearly["Ano"] = yearly["Year"].astype(int).astype(str)
yearly["Sales Label"] = yearly["Sales"].map(money)
first_year = yearly.iloc[0]
last_year = yearly.iloc[-1]
avg_year_sales = yearly["Sales"].mean()
yearly["YoY"] = yearly["Sales"].pct_change()
last_yoy = yearly["YoY"].dropna().iloc[-1] if yearly["YoY"].notna().any() else None
previous_year = yearly.iloc[-2] if len(yearly) > 1 else None
last_yoy_text = (
    "Não há comparação anual disponível porque a base possui apenas um ano analisado."
    if last_yoy is None or previous_year is None
    else (
        f"A receita de {int(last_year['Year'])} teve variação de {pct(last_yoy)} em relação a "
        f"{int(previous_year['Year'])}."
    )
)

analysis_text(
    "Leitura executiva",
    [
        f"A análise anual mostra o comportamento macro das vendas antes de qualquer detalhamento por mês, categoria ou produto. No recorte analisado, houve {trend_text(first_year['Sales'], last_year['Sales'])} entre {int(first_year['Year'])} e {int(last_year['Year'])}.",
        f"O melhor resultado ocorreu em {int(best_year['Year'])}, com {money(best_year['Sales'])}. Esse ano concentra o maior volume financeiro da série.",
        f"{last_yoy_text} Essa variação anual da receita ajuda a diferenciar o crescimento acumulado da série de uma melhora efetiva no último ano analisado.",
    ],
)

fig = px.bar(
    yearly,
    x="Ano",
    y="Sales",
    text="Sales Label",
    labels={"Ano": "Ano", "Sales": "Vendas"},
    color_discrete_sequence=[PALETTE[0]],
)
fig.update_traces(textposition="outside", cliponaxis=False)
fig = format_chart(fig, height=430)
fig.update_xaxes(type="category")
st.plotly_chart(fig, width="stretch")

st.divider()

section_header(
    "2. Em quais meses as vendas se concentram?",
    "Objetivo: identificar sazonalidade, meses de maior pressão comercial e períodos estratégicos para ações de venda.",
)
monthly = sales_by_month(filtered)
monthly["Periodo"] = monthly["Year Month"].dt.strftime("%m/%Y")
month_labels = {
    1: "Jan",
    2: "Fev",
    3: "Mar",
    4: "Abr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Set",
    10: "Out",
    11: "Nov",
    12: "Dez",
}
monthly["Ano"] = monthly["Year Month"].dt.year
monthly["Mes Numero"] = monthly["Year Month"].dt.month
monthly["Mes Nome"] = monthly["Mes Numero"].map(month_labels)
monthly["Mes Ano"] = monthly["Mes Nome"] + "/" + monthly["Ano"].astype(str)
peak_month = monthly.loc[monthly["Sales"].idxmax()]
low_month = monthly.loc[monthly["Sales"].idxmin()]
avg_month_sales = monthly["Sales"].mean()
final_months = monthly[monthly["Year Month"].dt.month.isin([9, 10, 11, 12])]
final_month_avg = final_months["Sales"].mean() if not final_months.empty else 0

analysis_text(
    "Leitura executiva",
    [
        f"A série mensal mostra que as vendas não ficam distribuídas de forma uniforme ao longo do tempo. Existem meses de aceleração, principalmente no fim do ano, que puxam o resultado para cima.",
        f"O maior pico aparece em {peak_month['Periodo']}, com aproximadamente {short_money(peak_month['Sales'])}. Para facilitar a leitura, esse ponto foi destacado diretamente no gráfico.",
        f"Setembro, outubro, novembro e dezembro formam uma janela importante para acompanhamento comercial. Na base analisada, esses meses registram média próxima de {short_money(final_month_avg)}.",
    ],
)

tab_year, tab_full, tab_season = st.tabs(
    ["Ano selecionado", "Série completa", "Sazonalidade"]
)

with tab_year:
    available_years = sorted(monthly["Ano"].unique())
    selected_monthly_year = st.selectbox(
        "Detalhar ano",
        available_years,
        index=len(available_years) - 1,
    )
    monthly_year = monthly[monthly["Ano"] == selected_monthly_year].copy()
    monthly_year["Valor"] = monthly_year["Sales"].map(short_money)
    year_peak = monthly_year.loc[monthly_year["Sales"].idxmax()]

    fig = px.line(
        monthly_year,
        x="Mes Nome",
        y="Sales",
        markers=True,
        text="Valor",
        labels={"Mes Nome": "Mês", "Sales": "Vendas"},
        category_orders={"Mes Nome": list(month_labels.values())},
        color_discrete_sequence=[PALETTE[1]],
    )
    fig.update_traces(
        line_width=3,
        marker_size=9,
        textposition="top center",
        hovertemplate="Mês: %{x}<br>Vendas: US$ %{y:,.2f}<extra></extra>",
    )
    fig = format_chart(fig, height=460)
    fig.add_hline(
        y=monthly_year["Sales"].mean(),
        line_dash="dot",
        line_color="#94a3b8",
        annotation_text=f"Média do ano: {short_money(monthly_year['Sales'].mean())}",
        annotation_position="top left",
    )
    st.plotly_chart(fig, width="stretch")
    st.caption(
        f"Em {selected_monthly_year}, o maior mês foi {year_peak['Mes Nome']} "
        f"({short_money(year_peak['Sales'])})."
    )
    st.markdown(
        f"""
        <p class="small-note">
        A linha pontilhada representa a <strong>média mensal de {selected_monthly_year}</strong>.
        Pontos acima dela indicam meses que venderam acima do comportamento médio daquele ano;
        pontos abaixo indicam meses mais fracos dentro do mesmo ano.
        </p>
        """,
        unsafe_allow_html=True,
    )

with tab_full:
    fig = px.line(
        monthly,
        x="Year Month",
        y="Sales",
        markers=True,
        labels={"Year Month": "Mês", "Sales": "Vendas"},
        color_discrete_sequence=[PALETTE[1]],
    )
    fig.update_traces(
        line_width=3,
        marker_size=7,
        hovertemplate="Mês: %{x|%m/%Y}<br>Vendas: US$ %{y:,.2f}<extra></extra>",
    )
    fig = format_chart(fig, height=460)
    fig.update_xaxes(
        tickformat="%b/%Y",
        rangeslider=dict(visible=True),
    )
    fig.add_scatter(
        x=[peak_month["Year Month"]],
        y=[peak_month["Sales"]],
        mode="markers+text",
        marker=dict(size=13, color="#dc2626"),
        text=[f"Pico: {short_money(peak_month['Sales'])}"],
        textposition="top center",
        hovertemplate="Pico mensal<br>Mês: %{x|%m/%Y}<br>Vendas: US$ %{y:,.2f}<extra></extra>",
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")
    st.caption(
        f"Pico da série: {peak_month['Periodo']} ({short_money(peak_month['Sales'])}). "
        f"Use o seletor abaixo do gráfico para aproximar períodos específicos."
    )
    st.markdown(
        """
        <p class="small-note">
        A série completa mostra todos os meses em sequência, permitindo acompanhar a evolução
        real das vendas ao longo dos anos. Use o controle abaixo do gráfico para dar zoom em
        um intervalo específico sem perder o contexto histórico.
        </p>
        """,
        unsafe_allow_html=True,
    )

with tab_season:
    seasonality = (
        monthly.groupby(["Mes Numero", "Mes Nome"], as_index=False)["Sales"]
        .mean()
        .sort_values("Mes Numero")
    )
    seasonality["Valor"] = seasonality["Sales"].map(short_money)
    fig = px.bar(
        seasonality,
        x="Mes Nome",
        y="Sales",
        text="Valor",
        labels={"Mes Nome": "Mês", "Sales": "Vendas médias"},
        category_orders={"Mes Nome": list(month_labels.values())},
        color_discrete_sequence=[PALETTE[0]],
    )
    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        hovertemplate="Mês: %{x}<br>Venda média: US$ %{y:,.2f}<extra></extra>",
    )
    fig = format_chart(fig, height=430)
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Esta visão resume a sazonalidade: cada barra representa a média daquele mês "
        "ao longo dos anos analisados."
    )
    st.markdown(
        """
        <p class="small-note">
        A sazonalidade responde quais meses costumam vender mais, independentemente do ano.
        Por exemplo: a barra de novembro representa a média de todos os novembros disponíveis
        no recorte analisado.
        </p>
        """,
        unsafe_allow_html=True,
    )

st.divider()

section_header(
    "3. Qual categoria sustenta a maior parte da receita?",
    "Objetivo: entender a composição da receita e identificar quais linhas de negócio mais influenciam o resultado.",
)
category_sales = sales_by_category(filtered)
category_sales["Share"] = category_sales["Sales"] / category_sales["Sales"].sum()
category_sales["Sales Label"] = category_sales["Sales"].map(money)
category_orders = (
    filtered.groupby("Category")["Order ID"]
    .nunique()
    .rename("Orders")
    .reset_index()
)
category_sales = category_sales.merge(category_orders, on="Category", how="left")
category_sales["Avg Order"] = category_sales["Sales"] / category_sales["Orders"]
category_sales = category_sales.sort_values("Sales", ascending=False).reset_index(drop=True)
leader_category = category_sales.iloc[0]
second_category = category_sales.iloc[1] if len(category_sales) > 1 else None
category_comparison_text = (
    f"Na sequência aparecem {' e '.join(category_sales['Category'].iloc[1:].tolist())}, formando a composição da receita por linha de produto."
    if second_category is not None
    else "Como apenas uma categoria está selecionada, esta leitura mostra a contribuição total dessa linha no recorte atual."
)
category_plot = category_sales.sort_values("Sales", ascending=True)

analysis_text(
    "Leitura executiva",
    [
        f"No ranking por receita, {leader_category['Category']} aparece em primeiro lugar, com {money(leader_category['Sales'])}, equivalente a {pct(leader_category['Share'])} das vendas analisadas.",
        category_comparison_text,
        f"A categoria líder aparece em {int(leader_category['Orders']):,} pedidos e gera, em média, {money(leader_category['Avg Order'])} por pedido. Isso indica quanto cada pedido com essa categoria costuma contribuir para a receita.",
    ],
)

fig = px.bar(
    category_plot,
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
fig.update_yaxes(
    categoryorder="array",
    categoryarray=category_plot["Category"].tolist(),
)
st.plotly_chart(fig, width="stretch")

st.divider()

section_header(
    "4. Quais produtos mais puxam o resultado?",
    "Objetivo: identificar os itens que mais contribuem para o faturamento e avaliar concentração de receita no portfólio.",
)
top_n = st.slider("Quantidade de produtos no ranking", 5, 20, 10)
product_rank = top_products(filtered, limit=top_n)
product_rank["Share"] = product_rank["Sales"] / filtered["Sales"].sum()
product_rank["Sales Label"] = product_rank["Sales"].map(money)
top_product = product_rank.iloc[0]
top_share = product_rank["Sales"].sum() / filtered["Sales"].sum()
top_3_share = product_rank.head(3)["Sales"].sum() / filtered["Sales"].sum()
product_universe = filtered["Product Name"].nunique()
top_product_orders = filtered.loc[
    filtered["Product Name"] == top_product["Product Name"], "Order ID"
].nunique()
top_product_avg_order = top_product["Sales"] / top_product_orders if top_product_orders else 0

analysis_text(
    "Leitura executiva",
    [
        f"O item com maior faturamento é {top_product['Product Name']}, somando {money(top_product['Sales'])}. Esse resultado mostra qual produto mais puxou a receita no recorte selecionado.",
        f"Os {len(product_rank)} produtos exibidos no ranking representam {pct(top_share)} da receita analisada, dentro de um total de {product_universe:,} produtos diferentes. Essa leitura mostra se a venda está concentrada em poucos itens ou distribuída pelo portfólio.",
        f"Somente os 3 primeiros produtos respondem por {pct(top_3_share)} da receita analisada. Se esse percentual sobe, a operação fica mais dependente de poucos itens; se cai, a receita está mais espalhada.",
        f"O produto líder apareceu em {top_product_orders:,} pedido(s), com média de {money(top_product_avg_order)} por pedido.",
    ],
)

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

st.divider()

section_header(
    "5. Evolução dos principais itens ao longo do tempo",
    "Objetivo: verificar se os itens de maior faturamento mantêm desempenho ao longo dos anos ou se dependem de picos pontuais.",
)
product_year = products_by_year(filtered, limit=min(top_n, 8))
product_year["Ano"] = product_year["Year"].astype(int).astype(str)
product_year["Sales Label"] = product_year["Sales"].map(money)
year_count = product_year.groupby("Product Name")["Year"].nunique().sort_values(ascending=False)
most_consistent_product = year_count.index[0]
peak_product_year = product_year.loc[product_year["Sales"].idxmax()]
years_available = filtered["Year"].nunique()
recurring_products = int((year_count > 1).sum())
most_consistent_sales = filtered.loc[
    filtered["Product Name"] == most_consistent_product, "Sales"
].sum()
most_consistent_share = most_consistent_sales / filtered["Sales"].sum()
most_consistent_years = int(year_count.iloc[0])

analysis_text(
    "Leitura executiva",
    [
        f"Essa visão separa produtos com desempenho recorrente daqueles que aparecem apenas em momentos específicos. O produto mais consistente é {most_consistent_product}, presente entre os principais itens em {most_consistent_years} de {years_available} ano(s) analisados, somando {money(most_consistent_sales)} no período, ou {pct(most_consistent_share)} da receita analisada.",
        f"O maior destaque isolado foi {peak_product_year['Product Name']} em {int(peak_product_year['Year'])}, com {money(peak_product_year['Sales'])}. Esse tipo de leitura ajuda a diferenciar produto estrutural de pico temporário.",
        f"No ranking analisado, {recurring_products} produto(s) aparecem em mais de um ano. Quanto maior essa recorrência, mais estável tende a ser a contribuição desses itens para o resultado.",
    ],
)

fig = px.bar(
    product_year,
    x="Sales",
    y="Product Name",
    color="Ano",
    barmode="group",
    orientation="h",
    text="Sales Label",
    labels={"Sales": "Vendas", "Product Name": "Produto", "Ano": "Ano"},
    color_discrete_sequence=PALETTE,
)
fig.update_traces(textposition="outside", cliponaxis=False)
fig = format_chart(fig, height=560)
fig.update_xaxes(range=[0, product_year["Sales"].max() * 1.28])
fig.update_yaxes(automargin=True)
fig.update_layout(margin=dict(l=10, r=150, t=35, b=25))
st.plotly_chart(fig, width="stretch")

st.divider()

with st.expander("Dados tratados usados no dashboard"):
    st.dataframe(filtered.head(200), width="stretch")
