"""Version 2: Interactive Business Intelligence dashboard."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Configure the Streamlit page before displaying any content.
st.set_page_config(
    page_title="Online Retail - BI Dashboard",
    layout="wide",
)

st.title("Online Retail Analytics")
st.subheader("Version 2 Business Intelligence Dashboard")
st.info(
    """
    Use the sidebar filters to explore the data. This dashboard is more
    interactive than Version 1, but it still depends on business decisions
    about returns, cancellations, non-positive prices, and missing CustomerID
    values. It is not yet an AI assistant or AI agent.
    """
)


@st.cache_data
def load_data(csv_path: Path) -> pd.DataFrame:
    """Load the cleaned CSV and prepare the columns used by the dashboard."""

    data = pd.read_csv(csv_path)
    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"], errors="coerce")

    # Always calculate Revenue from the required formula.
    data["Revenue"] = data["Quantity"] * data["UnitPrice"]
    return data


# Build the path from this file so the app can be launched from any folder.
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
except (OSError, pd.errors.ParserError, UnicodeError) as error:
    st.error(f"The cleaned CSV file could not be loaded: {error}")
    st.stop()


# Check the input before attempting any calculations.
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

valid_dates = df["InvoiceDate"].dropna()
if valid_dates.empty:
    st.error("The CSV does not contain any valid InvoiceDate values.")
    st.stop()


# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.header("Dashboard Filters")
st.sidebar.caption("Every KPI, chart, preview, and download uses these filters.")

minimum_date = valid_dates.min().date()
maximum_date = valid_dates.max().date()
selected_dates = st.sidebar.date_input(
    "Invoice date range",
    value=(minimum_date, maximum_date),
    min_value=minimum_date,
    max_value=maximum_date,
)

country_options = sorted(df["Country"].dropna().astype(str).unique())

# Selecting every country in a multiselect can make the sidebar crowded because
# Streamlit displays each selected country as a tag. This checkbox keeps the
# default behavior the same while making the sidebar easier to read.
select_all_countries = st.sidebar.checkbox(
    "Select all countries",
    value=True,
    help="Keep this checked to include every country without showing many tags.",
)

if select_all_countries:
    selected_countries = country_options
    st.sidebar.caption(
        "All countries are included. Uncheck this box to choose specific "
        "countries from a list."
    )
else:
    selected_countries = st.sidebar.multiselect(
        "Choose countries",
        options=country_options,
        default=[],
        help="Choose one or more countries to include in the dashboard.",
    )
    st.sidebar.caption(
        "Only the countries selected above will be included. If none are "
        "selected, the dashboard will show no rows."
    )

exclude_united_kingdom = st.sidebar.checkbox(
    "Exclude United Kingdom",
    value=False,
    help="The United Kingdom has many rows and can dominate the revenue charts.",
)
st.sidebar.caption(
    "Use this if you want to compare smaller country markets without the UK "
    "overpowering the charts."
)

product_search = st.sidebar.text_input(
    "Product description search",
    placeholder="Example: HEART",
    help="The search is not case-sensitive and can match part of a description.",
)

include_negative_quantity = st.sidebar.checkbox(
    "Include negative Quantity rows",
    value=True,
    help="Negative quantities may represent returns, cancellations, or corrections.",
)
include_non_positive_price = st.sidebar.checkbox(
    "Include zero/negative UnitPrice rows",
    value=True,
    help="These rows may represent gifts, adjustments, or data-quality issues.",
)
include_missing_customer = st.sidebar.checkbox(
    "Include missing CustomerID rows",
    value=True,
    help="Missing IDs limit customer-level analysis but may still be valid activity.",
)


# Start with a copy so the original loaded DataFrame stays unchanged.
filtered_df = df.copy()

# Streamlit normally returns two dates, but this check keeps the filter safe if
# a user has selected only one date while editing the range.
if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date = end_date = selected_dates

filtered_df = filtered_df[
    filtered_df["InvoiceDate"].dt.date.between(start_date, end_date)
]

if selected_countries:
    filtered_df = filtered_df[
        filtered_df["Country"].astype(str).isin(selected_countries)
    ]
else:
    # An empty country selection means no countries are selected.
    filtered_df = filtered_df.iloc[0:0]

if exclude_united_kingdom:
    filtered_df = filtered_df[
        filtered_df["Country"].astype(str) != "United Kingdom"
    ]

if product_search.strip():
    product_match = filtered_df["Description"].fillna("").str.contains(
        product_search.strip(),
        case=False,
        regex=False,
    )
    filtered_df = filtered_df[product_match]

if not include_negative_quantity:
    filtered_df = filtered_df[filtered_df["Quantity"] >= 0]

if not include_non_positive_price:
    filtered_df = filtered_df[filtered_df["UnitPrice"] > 0]

if not include_missing_customer:
    filtered_df = filtered_df[filtered_df["CustomerID"].notna()]

st.caption(
    f"Showing {len(filtered_df):,} of {len(df):,} invoice lines from "
    f"{start_date:%b %d, %Y} to {end_date:%b %d, %Y}."
)

if filtered_df.empty:
    st.warning("No rows match the selected filters. Adjust the sidebar filters.")
    st.stop()


def format_gbp_compact(value: float) -> str:
    """Format GBP amounts so large KPI values fit inside Streamlit metric cards."""

    # The calculations stay unchanged. This function only changes how the
    # number is displayed on screen.
    amount = abs(value)

    if amount >= 1_000_000_000:
        formatted_value = f"{value / 1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        formatted_value = f"{value / 1_000_000:.2f}M"
    elif amount >= 1_000:
        formatted_value = f"{value / 1_000:.2f}K"
    else:
        # Smaller values are easiest to read as normal currency.
        formatted_value = f"{value:,.2f}"

    return f"GBP {formatted_value}"


# ---------------------------------------------------------------------------
# Filtered KPI calculations
# ---------------------------------------------------------------------------
total_revenue = filtered_df["Revenue"].sum()
invoice_lines = len(filtered_df)
unique_invoices = filtered_df["InvoiceNo"].nunique()
unique_customers = filtered_df["CustomerID"].nunique()
unique_products = filtered_df["StockCode"].nunique()
average_order_value = (
    total_revenue / unique_invoices if unique_invoices else 0
)
units_sold = filtered_df.loc[
    filtered_df["Quantity"] > 0, "Quantity"
].sum()
units_returned = abs(
    filtered_df.loc[filtered_df["Quantity"] < 0, "Quantity"].sum()
)

st.header("Filtered Key Performance Indicators")

kpi_row_1 = st.columns(4)
kpi_row_1[0].metric("Total Revenue", format_gbp_compact(total_revenue))
kpi_row_1[1].metric("Invoice Lines", f"{invoice_lines:,}")
kpi_row_1[2].metric("Unique Invoices", f"{unique_invoices:,}")
kpi_row_1[3].metric("Unique Customers", f"{unique_customers:,}")

kpi_row_2 = st.columns(4)
kpi_row_2[0].metric("Unique Products", f"{unique_products:,}")
kpi_row_2[1].metric(
    "Average Order Value",
    format_gbp_compact(average_order_value),
)
kpi_row_2[2].metric("Units Sold", f"{units_sold:,.0f}")
kpi_row_2[3].metric("Units Returned", f"{units_returned:,.0f}")

st.caption(
    "Average order value = filtered net revenue / unique invoices. "
    "Units sold counts positive quantities; units returned is the absolute "
    "total of negative quantities."
)


# Add reusable display columns after the KPI calculations.
chart_df = filtered_df.copy()
chart_df["Month"] = (
    chart_df["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
)
chart_df["Product"] = chart_df["Description"].fillna(
    chart_df["StockCode"].astype(str)
)


# ---------------------------------------------------------------------------
# Revenue and invoice trend charts
# ---------------------------------------------------------------------------
st.header("Revenue and Invoice Trends")
trend_left, trend_right = st.columns(2)

monthly_revenue = (
    chart_df.groupby("Month", as_index=False)["Revenue"].sum()
)
with trend_left:
    revenue_figure = px.line(
        monthly_revenue,
        x="Month",
        y="Revenue",
        markers=True,
        title="Monthly Revenue Trend",
        labels={"Revenue": "Revenue (GBP)"},
    )
    st.plotly_chart(revenue_figure, use_container_width=True)

monthly_invoices = (
    chart_df.groupby("Month", as_index=False)["InvoiceNo"]
    .nunique()
    .rename(columns={"InvoiceNo": "Invoices"})
)
with trend_right:
    invoice_figure = px.bar(
        monthly_invoices,
        x="Month",
        y="Invoices",
        title="Monthly Number of Invoices",
    )
    st.plotly_chart(invoice_figure, use_container_width=True)


# ---------------------------------------------------------------------------
# Country and product revenue charts
# ---------------------------------------------------------------------------
st.header("Revenue Breakdown")
breakdown_left, breakdown_right = st.columns(2)

country_revenue = (
    chart_df.groupby("Country", as_index=False)["Revenue"]
    .sum()
    .sort_values("Revenue", ascending=False)
)
with breakdown_left:
    country_figure = px.bar(
        country_revenue.head(15).sort_values("Revenue"),
        x="Revenue",
        y="Country",
        orientation="h",
        title="Revenue by Country (Top 15)",
        labels={"Revenue": "Revenue (GBP)"},
    )
    st.plotly_chart(country_figure, use_container_width=True)

product_revenue = (
    chart_df.groupby("Product", as_index=False)["Revenue"]
    .sum()
    .nlargest(10, "Revenue")
    .sort_values("Revenue")
)
with breakdown_right:
    product_figure = px.bar(
        product_revenue,
        x="Revenue",
        y="Product",
        orientation="h",
        title="Top 10 Products by Revenue",
        labels={"Revenue": "Revenue (GBP)"},
    )
    st.plotly_chart(product_figure, use_container_width=True)


# ---------------------------------------------------------------------------
# Revenue versus quantity
# ---------------------------------------------------------------------------
st.header("Revenue vs Quantity")
comparison_level = st.radio(
    "Group the comparison by:",
    options=["Country", "Product"],
    horizontal=True,
)

comparison = (
    chart_df.groupby(comparison_level, as_index=False)
    .agg(Quantity=("Quantity", "sum"), Revenue=("Revenue", "sum"))
)

# Keep a product-level scatter readable by showing the 50 largest products by
# absolute revenue. Country-level analysis normally has far fewer points.
if comparison_level == "Product" and len(comparison) > 50:
    comparison = (
        comparison.assign(AbsoluteRevenue=comparison["Revenue"].abs())
        .nlargest(50, "AbsoluteRevenue")
        .drop(columns="AbsoluteRevenue")
    )

comparison_figure = px.scatter(
    comparison,
    x="Quantity",
    y="Revenue",
    hover_name=comparison_level,
    title=f"Revenue vs Quantity by {comparison_level}",
    labels={"Revenue": "Revenue (GBP)", "Quantity": "Net Quantity"},
)
st.plotly_chart(comparison_figure, use_container_width=True)


# ---------------------------------------------------------------------------
# Return / negative quantity summary
# ---------------------------------------------------------------------------
st.header("Return / Negative Quantity Summary")

negative_rows = chart_df[chart_df["Quantity"] < 0]
negative_revenue = negative_rows["Revenue"].sum()
negative_invoice_lines = len(negative_rows)
negative_invoices = negative_rows["InvoiceNo"].nunique()

return_metrics = st.columns(3)
return_metrics[0].metric("Negative Quantity Lines", f"{negative_invoice_lines:,}")
return_metrics[1].metric("Invoices with Negative Lines", f"{negative_invoices:,}")
return_metrics[2].metric(
    "Negative-Line Revenue Impact", f"GBP {negative_revenue:,.2f}"
)

quantity_summary = pd.DataFrame(
    {
        "Quantity Type": ["Positive quantity", "Negative quantity"],
        "Invoice Lines": [
            int((chart_df["Quantity"] > 0).sum()),
            int((chart_df["Quantity"] < 0).sum()),
        ],
        "Absolute Units": [
            chart_df.loc[chart_df["Quantity"] > 0, "Quantity"].sum(),
            abs(chart_df.loc[chart_df["Quantity"] < 0, "Quantity"].sum()),
        ],
    }
)
quantity_summary_long = quantity_summary.melt(
    id_vars="Quantity Type",
    var_name="Measure",
    value_name="Total",
)
return_figure = px.bar(
    quantity_summary_long,
    x="Quantity Type",
    y="Total",
    color="Measure",
    barmode="group",
    title="Positive vs Negative Quantity Activity",
)
st.plotly_chart(return_figure, use_container_width=True)
st.caption(
    "Negative quantities are labeled as return activity for exploration only. "
    "The business meaning of returns, cancellations, and corrections still "
    "needs confirmation."
)


# ---------------------------------------------------------------------------
# Preview and download
# ---------------------------------------------------------------------------
st.header("Filtered Data")
st.dataframe(filtered_df.head(1_000), use_container_width=True, hide_index=True)
st.caption(
    "The preview displays the first 1,000 filtered rows. The download contains "
    "all filtered rows."
)

download_csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download filtered data as CSV",
    data=download_csv,
    file_name="online_retail_filtered.csv",
    mime="text/csv",
)


# ---------------------------------------------------------------------------
# Version notes
# ---------------------------------------------------------------------------
st.header("About This Version")
st.markdown(
    """
    - This is **Version 2: Business Intelligence Dashboard**.
    - Users can explore the dataset using date, country, product, quantity,
      price, and CustomerID filters.
    - Results still depend on business rules for returns, cancellations,
      non-positive prices, and missing CustomerID values.
    - This version is more interactive than Version 1, but it is not an AI
      assistant or an AI agent.
    - The dashboard reads the cleaned CSV and does not modify the raw Excel
      workbook.
    """
)
