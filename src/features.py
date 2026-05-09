import pandas as pd


def filter_sales(
    df: pd.DataFrame,
    years: list[int] | None = None,
    regions: list[str] | None = None,
    categories: list[str] | None = None,
) -> pd.DataFrame:
    """Filter sales data by the dashboard controls."""
    filtered = df.copy()

    if years:
        filtered = filtered[filtered["Year"].isin(years)]
    if regions:
        filtered = filtered[filtered["Region"].isin(regions)]
    if categories:
        filtered = filtered[filtered["Category"].isin(categories)]

    return filtered


def kpis(df: pd.DataFrame) -> dict[str, float | int]:
    order_sales = df.groupby("Order ID")["Sales"].sum()
    return {
        "total_sales": float(df["Sales"].sum()),
        "orders": int(df["Order ID"].nunique()),
        "items": int(len(df)),
        "avg_order": float(order_sales.mean()) if not order_sales.empty else 0.0,
    }


def sales_by_year(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Year", as_index=False)["Sales"]
        .sum()
        .sort_values("Year")
    )


def sales_by_month(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Year Month", as_index=False)["Sales"]
        .sum()
        .sort_values("Year Month")
    )


def sales_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Category", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )


def top_products(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    return (
        df.groupby("Product Name", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
        .head(limit)
    )


def products_by_year(df: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    top_names = top_products(df, limit=limit)["Product Name"]
    return (
        df[df["Product Name"].isin(top_names)]
        .groupby(["Year", "Product Name"], as_index=False)["Sales"]
        .sum()
        .sort_values(["Year", "Sales"], ascending=[True, False])
    )
