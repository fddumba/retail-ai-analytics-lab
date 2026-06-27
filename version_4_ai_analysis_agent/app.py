"""Version 4: AI Data Analysis Agent for the Online Retail dataset.

This Streamlit app behaves like a small local analysis agent. It accepts a
business goal, detects the likely intent with keyword rules, creates a short
plan, and runs several pandas analysis steps. It does not call an external AI
API and it does not modify the source files.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Online Retail AI Analysis Agent",
    layout="wide",
)


EXAMPLE_GOALS = [
    "Investigate why revenue changed over time",
    "Find which countries drive revenue and returns",
    "Analyze product return risk",
    "Explain missing CustomerID impact",
    "Identify unusual products or countries",
    "Recommend what management should investigate next",
]


REQUIRED_COLUMNS = {
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
}


@st.cache_data
def load_data(csv_path: Path) -> pd.DataFrame:
    """Load the cleaned CSV and create reusable analysis columns."""

    data = pd.read_csv(csv_path)
    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"], errors="coerce")

    # Revenue is recalculated inside the app so the business rule is visible.
    data["Revenue"] = data["Quantity"] * data["UnitPrice"]

    # Flags make data-quality and return-style rows easy to filter and explain.
    data["IsNegativeQuantity"] = data["Quantity"] < 0
    data["IsNonPositiveUnitPrice"] = data["UnitPrice"] <= 0
    data["IsMissingCustomerID"] = data["CustomerID"].isna()
    data["IsCancellation"] = (
        data["InvoiceNo"].astype(str).str.upper().str.startswith("C")
    )
    data["Product"] = data["Description"].fillna(data["StockCode"].astype(str))

    return data


def apply_filters(
    data: pd.DataFrame,
    selected_dates,
    selected_countries: list[str],
    exclude_united_kingdom: bool,
    include_negative_quantity: bool,
    include_non_positive_price: bool,
    include_missing_customer: bool,
    product_search: str,
) -> pd.DataFrame:
    """Apply sidebar filters to the dataset before any agent analysis runs."""

    filtered = data.copy()

    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date = end_date = selected_dates

    filtered = filtered[
        filtered["InvoiceDate"].dt.date.between(start_date, end_date)
    ]

    if selected_countries:
        filtered = filtered[filtered["Country"].astype(str).isin(selected_countries)]
    else:
        filtered = filtered.iloc[0:0]

    if exclude_united_kingdom:
        filtered = filtered[filtered["Country"].astype(str) != "United Kingdom"]

    if not include_negative_quantity:
        filtered = filtered[filtered["Quantity"] >= 0]

    if not include_non_positive_price:
        filtered = filtered[filtered["UnitPrice"] > 0]

    if not include_missing_customer:
        filtered = filtered[filtered["CustomerID"].notna()]

    if product_search.strip():
        product_match = filtered["Product"].fillna("").str.contains(
            product_search.strip(),
            case=False,
            regex=False,
        )
        filtered = filtered[product_match]

    return filtered


def detect_intent(goal: str) -> str:
    """Detect the most likely analysis intent with simple keyword matching."""

    text = goal.lower().strip()

    if any(word in text for word in ["return", "returns", "cancel", "negative"]):
        return "return_risk_investigation"

    if any(word in text for word in ["missing customer", "customerid", "customer id"]):
        return "missing_customer_investigation"

    if any(word in text for word in ["country", "countries", "market", "geography"]):
        return "country_performance_investigation"

    if any(word in text for word in ["product", "products", "item", "stockcode"]):
        return "product_performance_investigation"

    if any(word in text for word in ["trend", "month", "monthly", "over time", "changed"]):
        return "revenue_trend_investigation"

    return "general_business_review"


def format_currency(value: float) -> str:
    """Format money values in a consistent GBP style."""

    return f"GBP {value:,.2f}"


def build_agent_plan(intent: str) -> list[str]:
    """Return a short multi-step plan for the detected intent."""

    plans = {
        "revenue_trend_investigation": [
            "Group filtered rows by invoice month.",
            "Calculate monthly revenue and month-over-month change.",
            "Find the best and worst months.",
            "Chart the monthly revenue trend.",
            "Summarize likely business questions for follow-up.",
        ],
        "country_performance_investigation": [
            "Group filtered rows by country.",
            "Calculate revenue, revenue share, invoices, and return activity.",
            "Rank the top countries by revenue.",
            "Chart country revenue.",
            "Recommend countries for management review.",
        ],
        "product_performance_investigation": [
            "Group filtered rows by product description.",
            "Calculate revenue, quantity, invoices, and customer reach.",
            "Find top products by revenue and quantity.",
            "Highlight products with high revenue but low quantity.",
            "Recommend product questions for follow-up.",
        ],
        "return_risk_investigation": [
            "Identify rows with negative Quantity.",
            "Measure negative quantity rows, invoices, and revenue impact.",
            "Calculate return activity by product and country.",
            "Chart the highest return-risk products and countries.",
            "State that negative Quantity is exploratory return/cancellation activity.",
        ],
        "missing_customer_investigation": [
            "Split rows into known and missing CustomerID groups.",
            "Calculate missing row count, percent, and revenue.",
            "Compare known versus missing customer revenue.",
            "Chart the revenue comparison.",
            "Recommend customer-data follow-up questions.",
        ],
        "general_business_review": [
            "Calculate high-level KPIs for the filtered data.",
            "Review top countries and products.",
            "Review monthly revenue movement.",
            "Summarize return activity.",
            "Recommend management questions for deeper investigation.",
        ],
    }

    return plans.get(intent, plans["general_business_review"])


def prepare_monthly_revenue(data: pd.DataFrame) -> pd.DataFrame:
    """Create a monthly revenue table used by several analysis paths."""

    monthly_data = data.dropna(subset=["InvoiceDate"]).copy()
    monthly_data["Month"] = monthly_data["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    monthly_revenue = (
        monthly_data.groupby("Month", as_index=False)["Revenue"]
        .sum()
        .sort_values("Month")
    )
    monthly_revenue["MoM Revenue Change"] = monthly_revenue["Revenue"].diff()
    monthly_revenue["MoM Percent Change"] = monthly_revenue["Revenue"].pct_change()
    return monthly_revenue


def run_revenue_trend_analysis(data: pd.DataFrame) -> dict:
    """Analyze revenue movement over time."""

    monthly_revenue = prepare_monthly_revenue(data)

    if monthly_revenue.empty:
        return {
            "tables": {"Monthly revenue": monthly_revenue},
            "findings": ["No valid invoice dates were available after filtering."],
            "recommendations": ["Widen the date filter and run the analysis again."],
            "limitations": ["Rows without valid InvoiceDate values cannot be trended."],
        }

    best_month = monthly_revenue.loc[monthly_revenue["Revenue"].idxmax()]
    worst_month = monthly_revenue.loc[monthly_revenue["Revenue"].idxmin()]

    return {
        "tables": {"Monthly revenue": monthly_revenue},
        "best_month": best_month,
        "worst_month": worst_month,
        "findings": [
            f"Best month: {best_month['Month']:%Y-%m} with {format_currency(best_month['Revenue'])}.",
            f"Worst month: {worst_month['Month']:%Y-%m} with {format_currency(worst_month['Revenue'])}.",
            "Month-over-month change shows whether revenue grew or fell compared with the prior month.",
        ],
        "recommendations": [
            "Review the months with the largest revenue increases and decreases.",
            "Check whether promotions, returns, stock availability, or seasonality explain the movement.",
        ],
        "limitations": [
            "The dataset ends on December 9, 2011, so December 2011 is not a complete month.",
            "Revenue is net line-level revenue using Quantity multiplied by UnitPrice.",
        ],
    }


def run_country_analysis(data: pd.DataFrame) -> dict:
    """Analyze country-level revenue and return activity."""

    country_revenue = (
        data.groupby("Country", dropna=False)
        .agg(
            Revenue=("Revenue", "sum"),
            InvoiceLines=("InvoiceNo", "size"),
            UniqueInvoices=("InvoiceNo", "nunique"),
            NegativeQuantityRows=("IsNegativeQuantity", "sum"),
        )
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )
    total_revenue = country_revenue["Revenue"].sum()
    country_revenue["RevenueShare"] = (
        country_revenue["Revenue"] / total_revenue if total_revenue else 0
    )

    top_countries = country_revenue.head(10)
    leader = top_countries.iloc[0] if not top_countries.empty else None

    findings = ["No country rows were available after filtering."]
    if leader is not None:
        findings = [
            f"Top country by revenue: {leader['Country']} with {format_currency(leader['Revenue'])}.",
            "Revenue share helps show whether sales are concentrated in a few countries.",
            "Negative quantity rows show where return or cancellation-style activity appears.",
        ]

    return {
        "tables": {
            "Top countries by revenue": top_countries,
            "Country revenue share": country_revenue,
        },
        "findings": findings,
        "recommendations": [
            "Compare the largest countries with their return activity before making market decisions.",
            "Use the sidebar option to exclude United Kingdom if it dominates the chart.",
        ],
        "limitations": [
            "Country is taken from the transaction row and may not equal customer headquarters.",
            "Revenue share can change a lot when filters exclude countries or negative rows.",
        ],
    }


def run_product_analysis(data: pd.DataFrame) -> dict:
    """Analyze product-level revenue, quantity, and unusual mixes."""

    product_summary = (
        data.groupby("Product", dropna=False)
        .agg(
            Revenue=("Revenue", "sum"),
            NetQuantity=("Quantity", "sum"),
            InvoiceLines=("InvoiceNo", "size"),
            UniqueInvoices=("InvoiceNo", "nunique"),
            UniqueCustomers=("CustomerID", "nunique"),
        )
        .reset_index()
    )

    top_revenue = product_summary.sort_values("Revenue", ascending=False).head(10)
    top_quantity = product_summary.sort_values("NetQuantity", ascending=False).head(10)

    # This is a simple way to find products that may be expensive, bundled, or unusual.
    positive_revenue = product_summary[product_summary["Revenue"] > 0].copy()
    high_revenue_low_quantity = (
        positive_revenue.sort_values(["Revenue", "NetQuantity"], ascending=[False, True])
        .head(25)
        .sort_values("Revenue", ascending=False)
        .head(10)
    )

    findings = ["No product rows were available after filtering."]
    if not top_revenue.empty:
        top_product = top_revenue.iloc[0]
        findings = [
            f"Top product by revenue: {top_product['Product']} with {format_currency(top_product['Revenue'])}.",
            "Top products by revenue and top products by quantity are useful to compare because they can tell different stories.",
            "High-revenue, low-quantity products may deserve pricing, margin, or stock review.",
        ]

    return {
        "tables": {
            "Top products by revenue": top_revenue,
            "Top products by quantity": top_quantity,
            "High revenue but low quantity products": high_revenue_low_quantity,
        },
        "findings": findings,
        "recommendations": [
            "Review whether top revenue products are also high-volume products.",
            "Investigate high-revenue products with low quantity for pricing, bundles, or unusual transactions.",
        ],
        "limitations": [
            "Description is used as the product label, with StockCode as a fallback.",
            "Net quantity can be reduced by returns or cancellations.",
        ],
    }


def run_return_analysis(data: pd.DataFrame) -> dict:
    """Analyze negative Quantity rows as exploratory return/cancellation activity."""

    return_data = data.copy()
    return_data["NegativeQuantityRevenue"] = return_data["Revenue"].where(
        return_data["IsNegativeQuantity"],
        0,
    )
    negative_rows = data[data["IsNegativeQuantity"]]
    negative_quantity_rows = len(negative_rows)
    invoices_with_negative_rows = negative_rows["InvoiceNo"].nunique()
    negative_revenue_impact = negative_rows["Revenue"].sum()

    product_return_rate = (
        return_data.groupby("Product", dropna=False)
        .agg(
            InvoiceLines=("InvoiceNo", "size"),
            NegativeQuantityRows=("IsNegativeQuantity", "sum"),
            NegativeRevenueImpact=("NegativeQuantityRevenue", "sum"),
        )
        .reset_index()
    )
    product_return_rate["ReturnRate"] = (
        product_return_rate["NegativeQuantityRows"] / product_return_rate["InvoiceLines"]
    )
    product_return_rate = product_return_rate.sort_values(
        ["ReturnRate", "NegativeQuantityRows"], ascending=False
    ).head(15)

    country_return_rate = (
        return_data.groupby("Country", dropna=False)
        .agg(
            InvoiceLines=("InvoiceNo", "size"),
            NegativeQuantityRows=("IsNegativeQuantity", "sum"),
            NegativeRevenueImpact=("NegativeQuantityRevenue", "sum"),
        )
        .reset_index()
    )
    country_return_rate["ReturnRate"] = (
        country_return_rate["NegativeQuantityRows"] / country_return_rate["InvoiceLines"]
    )
    country_return_rate = country_return_rate.sort_values(
        ["ReturnRate", "NegativeQuantityRows"], ascending=False
    ).head(15)

    summary = pd.DataFrame(
        {
            "Metric": [
                "Negative quantity rows",
                "Invoices with negative quantity rows",
                "Negative revenue impact",
            ],
            "Value": [
                f"{negative_quantity_rows:,}",
                f"{invoices_with_negative_rows:,}",
                format_currency(negative_revenue_impact),
            ],
        }
    )

    return {
        "tables": {
            "Return summary": summary,
            "Return rate by product": product_return_rate,
            "Return rate by country": country_return_rate,
        },
        "findings": [
            f"Negative quantity rows: {negative_quantity_rows:,}.",
            f"Invoices with negative quantity rows: {invoices_with_negative_rows:,}.",
            f"Negative revenue impact: {format_currency(negative_revenue_impact)}.",
            "Negative Quantity is treated as return/cancellation activity for exploration only.",
        ],
        "recommendations": [
            "Review products and countries with high return rates and enough rows to matter.",
            "Confirm the business meaning of cancellations, corrections, and returns before final reporting.",
        ],
        "limitations": [
            "Negative Quantity is an exploratory proxy, not a final accounting definition.",
            "If the sidebar excludes negative Quantity rows, this analysis will show little or no return activity.",
        ],
    }


def run_missing_customer_analysis(data: pd.DataFrame) -> dict:
    """Analyze how missing CustomerID rows affect the filtered data."""

    missing_rows = data[data["IsMissingCustomerID"]]
    known_rows = data[~data["IsMissingCustomerID"]]
    missing_count = len(missing_rows)
    missing_percent = missing_count / len(data) if len(data) else 0
    missing_revenue = missing_rows["Revenue"].sum()

    comparison = pd.DataFrame(
        {
            "CustomerID Status": ["Known CustomerID", "Missing CustomerID"],
            "Invoice Lines": [len(known_rows), len(missing_rows)],
            "Revenue": [known_rows["Revenue"].sum(), missing_revenue],
            "Unique Invoices": [
                known_rows["InvoiceNo"].nunique(),
                missing_rows["InvoiceNo"].nunique(),
            ],
        }
    )

    summary = pd.DataFrame(
        {
            "Metric": [
                "Rows missing CustomerID",
                "Percent missing CustomerID",
                "Revenue on missing CustomerID rows",
            ],
            "Value": [
                f"{missing_count:,}",
                f"{missing_percent:.2%}",
                format_currency(missing_revenue),
            ],
        }
    )

    return {
        "tables": {
            "Missing CustomerID summary": summary,
            "Known vs missing CustomerID revenue": comparison,
        },
        "findings": [
            f"Rows missing CustomerID: {missing_count:,}.",
            f"Percent missing CustomerID: {missing_percent:.2%}.",
            f"Revenue on missing CustomerID rows: {format_currency(missing_revenue)}.",
        ],
        "recommendations": [
            "Separate customer-level analysis from transaction-level revenue analysis.",
            "Investigate why CustomerID is missing before using this data for retention or loyalty work.",
        ],
        "limitations": [
            "Rows with missing CustomerID may still be valid sales activity.",
            "Missing CustomerID rows cannot support customer-level behavior analysis.",
        ],
    }


def run_general_review(data: pd.DataFrame) -> dict:
    """Run a broad business review across revenue, products, countries, and returns."""

    total_revenue = data["Revenue"].sum()
    negative_rows = data[data["IsNegativeQuantity"]]
    monthly_trend = prepare_monthly_revenue(data)
    top_countries = (
        data.groupby("Country", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
        .head(10)
    )
    top_products = (
        data.groupby("Product", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
        .head(10)
    )

    kpi_summary = pd.DataFrame(
        {
            "Metric": [
                "Total revenue",
                "Invoice lines",
                "Unique invoices",
                "Unique customers",
                "Unique products",
                "Negative quantity rows",
                "Negative revenue impact",
            ],
            "Value": [
                format_currency(total_revenue),
                f"{len(data):,}",
                f"{data['InvoiceNo'].nunique():,}",
                f"{data['CustomerID'].nunique():,}",
                f"{data['StockCode'].nunique():,}",
                f"{len(negative_rows):,}",
                format_currency(negative_rows["Revenue"].sum()),
            ],
        }
    )

    return {
        "tables": {
            "KPI summary": kpi_summary,
            "Top countries": top_countries,
            "Top products": top_products,
            "Monthly trend": monthly_trend,
        },
        "findings": [
            f"Filtered total revenue is {format_currency(total_revenue)}.",
            f"The filtered data contains {len(data):,} invoice lines and {data['InvoiceNo'].nunique():,} unique invoices.",
            f"Return-style activity includes {len(negative_rows):,} negative quantity rows.",
        ],
        "recommendations": [
            "Which months caused the biggest revenue movement?",
            "Which countries are driving most revenue and most return activity?",
            "Which products are high revenue, high volume, or high return risk?",
            "How much analysis is limited by missing CustomerID values?",
        ],
        "limitations": [
            "This review is descriptive and does not prove root causes.",
            "Final business interpretation still requires human judgment.",
        ],
    }


def show_plan(plan: list[str]) -> None:
    """Display the agent plan as numbered steps."""

    for index, step in enumerate(plan, start=1):
        st.write(f"{index}. {step}")


def show_findings(result: dict) -> None:
    """Display findings, recommendations, and limitations from an analysis result."""

    st.subheader("Findings")
    for finding in result["findings"]:
        st.write(f"- {finding}")

    st.subheader("Recommended next actions")
    for recommendation in result["recommendations"]:
        st.write(f"- {recommendation}")

    st.subheader("Limitations and assumptions")
    for limitation in result["limitations"]:
        st.write(f"- {limitation}")


def run_selected_analysis(intent: str, data: pd.DataFrame) -> dict:
    """Route the detected intent to the matching analysis function."""

    if intent == "revenue_trend_investigation":
        return run_revenue_trend_analysis(data)
    if intent == "country_performance_investigation":
        return run_country_analysis(data)
    if intent == "product_performance_investigation":
        return run_product_analysis(data)
    if intent == "return_risk_investigation":
        return run_return_analysis(data)
    if intent == "missing_customer_investigation":
        return run_missing_customer_analysis(data)
    return run_general_review(data)


project_root = Path(__file__).resolve().parent.parent
csv_file = project_root / "data" / "online_retail_clean.csv"

st.title("Online Retail AI Data Analysis Agent")
st.info(
    """
    This is Version 4 of the Retail AI Analytics Lab. Enter a business goal,
    and the app will detect the likely intent, create a short analysis plan,
    run multiple pandas steps, and suggest next actions.
    """
)

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

missing_columns = REQUIRED_COLUMNS.difference(df.columns)
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


with st.sidebar:
    st.header("Agent Filters")
    st.caption("Every analysis step respects these filters.")

    minimum_date = valid_dates.min().date()
    maximum_date = valid_dates.max().date()
    selected_dates = st.date_input(
        "Invoice date range",
        value=(minimum_date, maximum_date),
        min_value=minimum_date,
        max_value=maximum_date,
    )

    country_options = sorted(df["Country"].dropna().astype(str).unique())
    select_all_countries = st.checkbox(
        "Select all countries",
        value=True,
        help="Keep this checked to include every country.",
    )

    if select_all_countries:
        selected_countries = country_options
        st.caption("All countries are included.")
    else:
        selected_countries = st.multiselect(
            "Choose countries",
            options=country_options,
            default=[],
            help="If none are selected, the app will show no rows.",
        )

    exclude_united_kingdom = st.checkbox(
        "Exclude United Kingdom",
        value=False,
        help="Useful when the UK dominates country-level charts.",
    )

    include_negative_quantity = st.checkbox(
        "Include negative Quantity rows",
        value=True,
        help="Negative quantities may represent returns, cancellations, or corrections.",
    )
    include_non_positive_price = st.checkbox(
        "Include zero/negative UnitPrice rows",
        value=True,
        help="These rows may represent gifts, adjustments, or data-quality issues.",
    )
    include_missing_customer = st.checkbox(
        "Include missing CustomerID rows",
        value=True,
        help="Missing IDs limit customer-level analysis but may still be valid sales.",
    )

    product_search = st.text_input(
        "Product description search",
        placeholder="Example: HEART",
        help="Case-insensitive search against product descriptions.",
    )


filtered_df = apply_filters(
    data=df,
    selected_dates=selected_dates,
    selected_countries=selected_countries,
    exclude_united_kingdom=exclude_united_kingdom,
    include_negative_quantity=include_negative_quantity,
    include_non_positive_price=include_non_positive_price,
    include_missing_customer=include_missing_customer,
    product_search=product_search,
)

if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date = end_date = selected_dates

st.caption(
    f"Agent will analyze {len(filtered_df):,} of {len(df):,} invoice lines "
    f"from {start_date:%b %d, %Y} to {end_date:%b %d, %Y}."
)

if filtered_df.empty:
    st.warning("No rows match the selected filters. Adjust the sidebar filters.")
    st.stop()


st.subheader("Business analysis goal")
st.write(
    "Enter a goal. The agent will choose the closest supported intent and run a "
    "multi-step analysis using the filtered data."
)

goal_columns = st.columns(2)
for index, example_goal in enumerate(EXAMPLE_GOALS):
    if goal_columns[index % 2].button(example_goal, key=f"goal_{index}"):
        st.session_state["analysis_goal"] = example_goal

analysis_goal = st.text_area(
    "Goal",
    key="analysis_goal",
    height=110,
    placeholder="Example: Find which countries drive revenue and returns",
)

if st.button("Run agent analysis", type="primary"):
    if not analysis_goal.strip():
        st.warning("Enter a business analysis goal first.")
        st.stop()

    intent = detect_intent(analysis_goal)
    plan = build_agent_plan(intent)
    result = run_selected_analysis(intent, filtered_df)

    st.header("Detected intent")
    st.code(intent, language="text")

    st.header("Agent plan")
    show_plan(plan)

    st.header("Step-by-step analysis output")

    if intent == "revenue_trend_investigation":
        monthly_revenue = result["tables"]["Monthly revenue"]
        st.subheader("Monthly revenue table")
        st.dataframe(monthly_revenue, use_container_width=True, hide_index=True)
        st.metric(
            "Best month",
            result["best_month"]["Month"].strftime("%Y-%m"),
            format_currency(result["best_month"]["Revenue"]),
        )
        st.metric(
            "Worst month",
            result["worst_month"]["Month"].strftime("%Y-%m"),
            format_currency(result["worst_month"]["Revenue"]),
        )
        st.line_chart(monthly_revenue.set_index("Month")["Revenue"])
        st.write(
            "This analysis looks for revenue movement by month and compares each "
            "month with the month before it."
        )

    elif intent == "country_performance_investigation":
        top_countries = result["tables"]["Top countries by revenue"]
        country_share = result["tables"]["Country revenue share"]
        st.subheader("Top countries by revenue")
        st.dataframe(top_countries, use_container_width=True, hide_index=True)
        st.subheader("Revenue share by country")
        st.dataframe(country_share, use_container_width=True, hide_index=True)
        country_chart = px.bar(
            top_countries.sort_values("Revenue"),
            x="Revenue",
            y="Country",
            orientation="h",
            title="Top Countries by Revenue",
        )
        st.plotly_chart(country_chart, use_container_width=True)
        st.write(
            "This analysis shows which countries drive revenue and whether the "
            "largest countries also have negative quantity activity."
        )

    elif intent == "product_performance_investigation":
        top_revenue = result["tables"]["Top products by revenue"]
        top_quantity = result["tables"]["Top products by quantity"]
        high_revenue_low_quantity = result["tables"]["High revenue but low quantity products"]
        st.subheader("Top products by revenue")
        st.dataframe(top_revenue, use_container_width=True, hide_index=True)
        st.subheader("Top products by quantity")
        st.dataframe(top_quantity, use_container_width=True, hide_index=True)
        st.subheader("Products with high revenue but low quantity")
        st.dataframe(high_revenue_low_quantity, use_container_width=True, hide_index=True)
        product_chart = px.bar(
            top_revenue.sort_values("Revenue"),
            x="Revenue",
            y="Product",
            orientation="h",
            title="Top Products by Revenue",
        )
        st.plotly_chart(product_chart, use_container_width=True)
        st.write(
            "This analysis compares revenue and quantity so high-value products "
            "do not get hidden behind high-volume products."
        )

    elif intent == "return_risk_investigation":
        st.warning(
            "Negative Quantity is treated as return/cancellation activity for "
            "exploration only."
        )
        return_summary = result["tables"]["Return summary"]
        product_return_rate = result["tables"]["Return rate by product"]
        country_return_rate = result["tables"]["Return rate by country"]
        st.subheader("Return summary")
        st.dataframe(return_summary, use_container_width=True, hide_index=True)
        st.subheader("Return rate by product")
        st.dataframe(product_return_rate, use_container_width=True, hide_index=True)
        product_return_chart = px.bar(
            product_return_rate.sort_values("ReturnRate"),
            x="ReturnRate",
            y="Product",
            orientation="h",
            title="Highest Product Return Rates",
        )
        st.plotly_chart(product_return_chart, use_container_width=True)
        st.subheader("Return rate by country")
        st.dataframe(country_return_rate, use_container_width=True, hide_index=True)
        country_return_chart = px.bar(
            country_return_rate.sort_values("ReturnRate"),
            x="ReturnRate",
            y="Country",
            orientation="h",
            title="Highest Country Return Rates",
        )
        st.plotly_chart(country_return_chart, use_container_width=True)
        st.write(
            "This analysis looks for areas where negative quantity rows are more "
            "common, but it does not decide the final accounting treatment."
        )

    elif intent == "missing_customer_investigation":
        missing_summary = result["tables"]["Missing CustomerID summary"]
        comparison = result["tables"]["Known vs missing CustomerID revenue"]
        st.subheader("Missing CustomerID summary")
        st.dataframe(missing_summary, use_container_width=True, hide_index=True)
        st.subheader("Known vs missing CustomerID revenue")
        st.dataframe(comparison, use_container_width=True, hide_index=True)
        missing_chart = px.bar(
            comparison,
            x="CustomerID Status",
            y="Revenue",
            title="Revenue by CustomerID Status",
        )
        st.plotly_chart(missing_chart, use_container_width=True)
        st.write(
            "This analysis separates rows that can support customer-level work "
            "from rows that can only support transaction-level analysis."
        )

    else:
        kpi_summary = result["tables"]["KPI summary"]
        top_countries = result["tables"]["Top countries"]
        top_products = result["tables"]["Top products"]
        monthly_trend = result["tables"]["Monthly trend"]
        st.subheader("General KPI summary")
        st.dataframe(kpi_summary, use_container_width=True, hide_index=True)
        st.subheader("Top countries")
        st.dataframe(top_countries, use_container_width=True, hide_index=True)
        st.subheader("Top products")
        st.dataframe(top_products, use_container_width=True, hide_index=True)
        st.subheader("Monthly trend")
        st.dataframe(monthly_trend, use_container_width=True, hide_index=True)
        st.line_chart(monthly_trend.set_index("Month")["Revenue"])
        st.write(
            "This review gives management a broad starting point before choosing "
            "a narrower investigation."
        )

    show_findings(result)

else:
    st.caption("Choose an example or type a goal, then click Run agent analysis.")


st.header("About Version 4")
st.markdown(
    """
    - This is **Version 4: AI Data Analysis Agent**.
    - It is more advanced than Version 3 because it plans and runs multi-step analysis.
    - It is still rule-based and local.
    - It does not use external AI APIs.
    - It does not modify the raw Excel workbook.
    - Final business interpretation still requires human judgment.
    """
)
