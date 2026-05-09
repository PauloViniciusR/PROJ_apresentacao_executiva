from pathlib import Path

import pandas as pd


DATE_COLUMNS = ["Order Date", "Ship Date"]


def load_sales_data(path: str | Path) -> pd.DataFrame:
    """Load and validate the raw Superstore sales dataset."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)
    required_columns = {
        "Order ID",
        "Order Date",
        "Ship Date",
        "Segment",
        "Region",
        "Category",
        "Sub-Category",
        "Product Name",
        "Sales",
    }
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Dataset missing required columns: {missing}")

    return clean_sales_data(df)


def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply deterministic data treatment used by both notebook and app."""
    cleaned = df.copy()

    for column in DATE_COLUMNS:
        cleaned[column] = pd.to_datetime(cleaned[column], format="%d/%m/%Y", errors="coerce")

    cleaned["Sales"] = pd.to_numeric(cleaned["Sales"], errors="coerce")
    cleaned = cleaned.dropna(subset=["Order Date", "Sales"])

    cleaned["Year"] = cleaned["Order Date"].dt.year
    cleaned["Month"] = cleaned["Order Date"].dt.month
    cleaned["Month Name"] = cleaned["Order Date"].dt.strftime("%b")
    cleaned["Year Month"] = cleaned["Order Date"].dt.to_period("M").dt.to_timestamp()

    cleaned["Postal Code"] = cleaned["Postal Code"].astype("Int64")

    return cleaned
