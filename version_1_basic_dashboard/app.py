"""Version 1: Basic Streamlit dashboard for the Online Retail dataset."""

from pathlib import Path

import pandas as pd
import streamlit as st


# Configure the browser tab and use the full page width for the charts.
st.set_page_config(
    page_title="Online Retail - Basic Dashboard",
    page_icon="🛍️",
    layout="wide",
)

st.title("Online Retail Analytics")
st.subheader("Version 1 Basic Dashboard")

st.info(
    """
    This dashboard uses the lightly cleaned dataset. Exact duplicate rows were
    removed, but returns, cancellations, missing CustomerID values, and
    zero/negative prices may still be present. Revenue includes negative values
    unless they are filtered in a later version.
    """
)


@st.cache_data
def load_data(csv_path: Path) -> pd.DataFrame:
    """Load and return the cleaned CSV."""

    return pd.read_csv(csv_path)


# Build an absolute path from this app file, so the app works regardless of
# which folder the terminal is currently using.
project_root = Path(__file__).resolve().parent.parent
csv_file = project_root / "data" / "online_retail_clean.csv"

if not csv_file.exists():
    st.error(
        "The cleaned CSV file could not be found. Expected location: "
        f"`{csv_file}`"
    )
    st.stop()

try:
    df = load_data(csv_file)
except (OSError, pd.errors.ParserError) as error:
    st.error(f"The cleaned CSV file could not be loaded: {error}")
    st.stop()
except KeyError as error:
    st.error(f"The CSV is missing a required column: {error}")
    st.stop()


# Confirm all fields required for the dashboard are present.
required_columns = {
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
}
missing_columns = required_columns.difference(df.columns)

if missing_columns:
    st.error(
        "The CSV is missing these required columns: "
        + ", ".join(sorted(missing_columns))
    )
    st.stop()

# Convert the date text from the CSV into real datetime values.
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

# Recalculate Revenue from the requested formula, even if the CSV already
# contains a Revenue column.
df["Revenue"] = df["Quantity"] * df["UnitPrice"]


# -----------------------------
# Summary metrics
# -----------------------------
total_revenue = df["Revenue"].sum()
invoice_lines = len(df)
unique_invoices = df["InvoiceNo"].nunique()
unique_customers = df["CustomerID"].nunique()
unique_products = df["StockCode"].nunique()

valid_dates = df["InvoiceDate"].dropna()
if valid_dates.empty:
    date_range = "No valid dates"
else:
    date_range = (
        f"{valid_dates.min():%b %d, %Y} to {valid_dates.max():%b %d, %Y}"
    )

st.header("Key Metrics")

metric_row_1 = st.columns(3)
metric_row_1[0].metric("Total Revenue", f"£{total_revenue:,.2f}")
metric_row_1[1].metric("Invoice Lines", f"{invoice_lines:,}")
metric_row_1[2].metric("Unique Invoices", f"{unique_invoices:,}")

metric_row_2 = st.columns(3)
metric_row_2[0].metric("Unique Customers", f"{unique_customers:,}")
metric_row_2[1].metric("Unique Products", f"{unique_products:,}")
metric_row_2[2].metric("Date Range", date_range)


# Only rows with valid dates can be included in monthly charts.
dated_df = df.dropna(subset=["InvoiceDate"]).copy()

if dated_df.empty:
    st.warning("No valid InvoiceDate values are available for monthly charts.")
else:
    # Convert each timestamp to its calendar month.
    dated_df["Month"] = dated_df["InvoiceDate"].dt.to_period("M").dt.to_timestamp()

    # -----------------------------
    # Monthly revenue trend
    # -----------------------------
    st.header("Monthly Revenue Trend")
    monthly_revenue = (
        dated_df.groupby("Month", as_index=False)["Revenue"].sum().set_index("Month")
    )
    st.line_chart(monthly_revenue, y="Revenue")


# -----------------------------
# Top products and countries
# -----------------------------
left_chart, right_chart = st.columns(2)

with left_chart:
    st.header("Top 10 Products by Revenue")

    # Use the product description when available, and StockCode as a fallback.
    product_names = df["Description"].fillna(df["StockCode"].astype(str))
    product_revenue = (
        df.assign(Product=product_names)
        .groupby("Product", as_index=False)["Revenue"]
        .sum()
        .nlargest(10, "Revenue")
        .sort_values("Revenue")
        .set_index("Product")
    )
    st.bar_chart(product_revenue, y="Revenue")

with right_chart:
    st.header("Top 10 Countries by Revenue")
    country_revenue = (
        df.groupby("Country", as_index=False)["Revenue"]
        .sum()
        .nlargest(10, "Revenue")
        .sort_values("Revenue")
        .set_index("Country")
    )
    st.bar_chart(country_revenue, y="Revenue")


# -----------------------------
# Monthly invoice count
# -----------------------------
if not dated_df.empty:
    st.header("Monthly Number of Invoices")
    monthly_invoices = (
        dated_df.groupby("Month", as_index=False)["InvoiceNo"]
        .nunique()
        .rename(columns={"InvoiceNo": "Invoices"})
        .set_index("Month")
    )
    st.bar_chart(monthly_invoices, y="Invoices")


st.caption(
    "Version 1 is a fixed basic dashboard. No filters or advanced cleaning "
    "rules are applied in this version."
)
