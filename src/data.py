from pathlib import Path

import pandas as pd


DATE_COLUMNS = ["Order Date", "Ship Date"]
STRING_COLUMNS = [
    "Order ID",
    "Ship Mode",
    "Customer ID",
    "Customer Name",
    "Segment",
    "Country",
    "City",
    "State",
    "Region",
    "Product ID",
    "Category",
    "Sub-Category",
    "Product Name",
]
BUSINESS_KEY_COLUMNS = [
    "Order ID",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Customer ID",
    "Product ID",
    "Product Name",
    "Sales",
]
POSTAL_CODE_FIXES = {
    ("United States", "Vermont", "Burlington"): "05401",
}


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

    for column in STRING_COLUMNS:
        cleaned[column] = cleaned[column].astype("string").str.strip()

    for column in DATE_COLUMNS:
        cleaned[column] = pd.to_datetime(cleaned[column], format="%d/%m/%Y", errors="coerce")

    cleaned["Sales"] = pd.to_numeric(cleaned["Sales"], errors="coerce")
    cleaned = cleaned.dropna(subset=["Order Date", "Sales"])
    cleaned = cleaned[cleaned["Sales"] > 0]
    cleaned = cleaned.drop_duplicates(subset=BUSINESS_KEY_COLUMNS, keep="first")

    cleaned["Year"] = cleaned["Order Date"].dt.year
    cleaned["Month"] = cleaned["Order Date"].dt.month
    cleaned["Month Name"] = cleaned["Order Date"].dt.strftime("%b")
    cleaned["Year Month"] = cleaned["Order Date"].dt.to_period("M").dt.to_timestamp()
    cleaned["Ship Days"] = (cleaned["Ship Date"] - cleaned["Order Date"]).dt.days
    cleaned["Is Valid Shipment"] = cleaned["Ship Days"].ge(0)

    cleaned["Postal Code"] = cleaned["Postal Code"].apply(format_postal_code)
    missing_postal = cleaned["Postal Code"].isna()
    if missing_postal.any():
        fixed_codes = cleaned.loc[missing_postal].apply(postal_code_from_location, axis=1)
        cleaned.loc[missing_postal, "Postal Code"] = fixed_codes

    cleaned = cleaned[cleaned["Is Valid Shipment"]].copy()
    cleaned = cleaned.sort_values(["Order Date", "Order ID", "Row ID"]).reset_index(drop=True)

    return cleaned


def format_postal_code(value: object) -> object:
    """Format US ZIP codes as five-character strings, preserving leading zeros."""
    if pd.isna(value):
        return pd.NA
    return f"{int(float(value)):05d}"


def postal_code_from_location(row: pd.Series) -> object:
    """Fill known missing ZIP codes using an explicit location mapping."""
    key = (row["Country"], row["State"], row["City"])
    return POSTAL_CODE_FIXES.get(key, pd.NA)


def data_quality_summary(raw: pd.DataFrame, cleaned: pd.DataFrame) -> dict[str, int]:
    """Return the main treatment indicators for documentation and audit."""
    order_dates = pd.to_datetime(raw["Order Date"], format="%d/%m/%Y", errors="coerce")
    ship_dates = pd.to_datetime(raw["Ship Date"], format="%d/%m/%Y", errors="coerce")
    sales = pd.to_numeric(raw["Sales"], errors="coerce")

    return {
        "raw_rows": int(len(raw)),
        "raw_columns": int(raw.shape[1]),
        "processed_rows": int(len(cleaned)),
        "processed_columns": int(cleaned.shape[1]),
        "removed_rows": int(len(raw) - len(cleaned)),
        "missing_postal_before": int(raw["Postal Code"].isna().sum()),
        "missing_postal_after": int(cleaned["Postal Code"].isna().sum()),
        "invalid_order_dates": int(order_dates.isna().sum()),
        "invalid_ship_dates": int(ship_dates.isna().sum()),
        "invalid_sales": int(sales.isna().sum()),
        "non_positive_sales": int(sales.le(0).sum()),
        "invalid_shipments": int(ship_dates.lt(order_dates).sum()),
        "business_duplicates": int(raw.duplicated(subset=BUSINESS_KEY_COLUMNS).sum()),
    }
