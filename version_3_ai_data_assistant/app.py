"""Version 3: AI-style Data Assistant for the Online Retail dataset.

This app answers one plain-English data question at a time using simple,
deterministic pandas logic. It does not call an external AI API.
"""

from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Online Retail AI Data Assistant",
    layout="wide",
)


EXAMPLE_QUESTIONS = [
    "What is the total revenue?",
    "How many invoice lines are in the dataset?",
    "How many unique invoices are there?",
    "How many unique customers are there?",
    "What are the top countries by revenue?",
    "What are the top products by revenue?",
    "Show the monthly revenue trend.",
    "Summarize negative quantity rows or returns.",
    "How many rows are missing CustomerID?",
    "How many rows have zero or negative UnitPrice?",
    "What is the average order value?",
]


@st.cache_data
def load_text_file(file_path: Path) -> str:
    """Read a markdown context file if it exists."""

    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    return "Context file not found."


@st.cache_data
def load_data(csv_path: Path) -> pd.DataFrame:
    """Load the cleaned CSV and add the columns used by the assistant."""

    data = pd.read_csv(csv_path)

    # Convert InvoiceDate into a real datetime column so monthly trends work.
    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"], errors="coerce")

    # Revenue is always recalculated from the required project formula.
    data["Revenue"] = data["Quantity"] * data["UnitPrice"]

    # These flags make the data-quality rules visible in the assistant.
    data["IsCancellation"] = (
        data["InvoiceNo"].astype(str).str.upper().str.startswith("C")
    )
    data["IsNegativeQuantity"] = data["Quantity"] < 0
    data["IsNonPositiveUnitPrice"] = data["UnitPrice"] <= 0
    data["IsMissingCustomerID"] = data["CustomerID"].isna()

    return data


def format_gbp(value: float) -> str:
    """Format money values in a readable GBP style."""

    return f"GBP {value:,.2f}"


def normalize_question(question: str) -> str:
    """Make keyword matching simpler."""

    return question.lower().strip()


def classify_question(question: str) -> str:
    """Classify a plain-English question using beginner-friendly keywords."""

    q = normalize_question(question)

    if not q:
        return "empty"

    if "average order" in q or "aov" in q:
        return "average_order_value"

    if "missing" in q and ("customer" in q or "customerid" in q):
        return "missing_customer"

    if (
        "unitprice" in q
        or "unit price" in q
        or "zero price" in q
        or "negative price" in q
        or "non-positive" in q
    ):
        return "non_positive_price"

    if (
        "negative quantity" in q
        or "negative quantities" in q
        or "return" in q
        or "returns" in q
        or "cancellation" in q
        or "cancelled" in q
    ):
        return "negative_quantity"

    if "monthly" in q and "revenue" in q:
        return "monthly_revenue"

    if ("top" in q or "highest" in q or "best" in q) and (
        "country" in q or "countries" in q
    ):
        return "top_countries"

    if ("top" in q or "highest" in q or "best" in q) and (
        "product" in q or "products" in q or "item" in q or "items" in q
    ):
        return "top_products"

    if (
        "unique invoice" in q
        or "number of invoices" in q
        or "how many invoices" in q
        or "invoice count" in q
    ):
        return "unique_invoices"

    if (
        "unique customer" in q
        or "number of customers" in q
        or "how many customers" in q
        or "customer count" in q
    ):
        return "unique_customers"

    if (
        "invoice line" in q
        or "invoice lines" in q
        or "rows" in q
        or "records" in q
    ):
        return "invoice_lines"

    if "revenue" in q or "sales" in q:
        return "total_revenue"

    return "unsupported"


def show_logic(logic_text: str) -> None:
    """Display the calculation steps used for the answer."""

    with st.expander("Calculation / logic used"):
        st.code(logic_text, language="text")


def answer_total_revenue(data: pd.DataFrame) -> None:
    total_revenue = data["Revenue"].sum()

    st.success(f"Total revenue is {format_gbp(total_revenue)}.")
    st.write(
        "This is net line-level revenue using all rows in the cleaned CSV, "
        "including negative quantities unless the dataset is changed upstream."
    )
    show_logic("Revenue = Quantity * UnitPrice\nTotal revenue = sum(Revenue)")


def answer_invoice_lines(data: pd.DataFrame) -> None:
    invoice_lines = len(data)

    st.success(f"The dataset contains {invoice_lines:,} invoice lines.")
    st.write("Each row is one product line on an invoice, not a full order.")
    show_logic("Invoice lines = number of rows in the cleaned CSV")


def answer_unique_invoices(data: pd.DataFrame) -> None:
    unique_invoices = data["InvoiceNo"].nunique()

    st.success(f"There are {unique_invoices:,} unique invoices.")
    show_logic("Unique invoices = count distinct InvoiceNo")


def answer_unique_customers(data: pd.DataFrame) -> None:
    unique_customers = data["CustomerID"].nunique()

    st.success(f"There are {unique_customers:,} unique non-missing customers.")
    st.write("Rows with missing CustomerID are not counted as unique customers.")
    show_logic("Unique customers = count distinct CustomerID, excluding missing values")


def answer_top_countries(data: pd.DataFrame) -> None:
    country_revenue = (
        data.groupby("Country", dropna=False)["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    st.success("Here are the top 10 countries by revenue.")
    st.dataframe(country_revenue, use_container_width=True)
    st.bar_chart(country_revenue.set_index("Country")["Revenue"])
    show_logic(
        "Revenue = Quantity * UnitPrice\n"
        "Group rows by Country\n"
        "Sum Revenue for each country\n"
        "Sort descending and show the top 10"
    )


def answer_top_products(data: pd.DataFrame) -> None:
    product_data = data.copy()
    product_data["Product"] = product_data["Description"].fillna(
        product_data["StockCode"].astype(str)
    )
    product_revenue = (
        product_data.groupby("Product", dropna=False)["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    st.success("Here are the top 10 products by revenue.")
    st.dataframe(product_revenue, use_container_width=True)
    st.bar_chart(product_revenue.set_index("Product")["Revenue"])
    show_logic(
        "Revenue = Quantity * UnitPrice\n"
        "Use Description as the product label; use StockCode if Description is missing\n"
        "Group rows by product\n"
        "Sum Revenue for each product\n"
        "Sort descending and show the top 10"
    )


def answer_monthly_revenue(data: pd.DataFrame) -> None:
    monthly_data = data.dropna(subset=["InvoiceDate"]).copy()
    monthly_data["Month"] = monthly_data["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    monthly_revenue = (
        monthly_data.groupby("Month")["Revenue"].sum().reset_index()
    )

    st.success("Here is the monthly revenue trend.")
    st.dataframe(monthly_revenue, use_container_width=True)
    st.line_chart(monthly_revenue.set_index("Month")["Revenue"])
    st.caption(
        "Note: the dataset ends on December 9, 2011, so December 2011 is not "
        "a complete month."
    )
    show_logic(
        "Revenue = Quantity * UnitPrice\n"
        "Convert InvoiceDate to month\n"
        "Group rows by month\n"
        "Sum Revenue for each month"
    )


def answer_negative_quantity(data: pd.DataFrame) -> None:
    negative_rows = data[data["IsNegativeQuantity"]]
    negative_revenue = negative_rows["Revenue"].sum()
    negative_quantity_total = negative_rows["Quantity"].sum()

    summary = pd.DataFrame(
        {
            "Metric": [
                "Negative quantity rows",
                "Invoices with negative quantity rows",
                "Total negative quantity",
                "Revenue impact from negative quantity rows",
                "Cancellation-style invoice rows",
            ],
            "Value": [
                f"{len(negative_rows):,}",
                f"{negative_rows['InvoiceNo'].nunique():,}",
                f"{negative_quantity_total:,.0f}",
                format_gbp(negative_revenue),
                f"{data['IsCancellation'].sum():,}",
            ],
        }
    )

    st.success("Here is the negative quantity / return summary.")
    st.dataframe(summary, use_container_width=True)
    st.write(
        "Negative quantities may represent returns, cancellations, or corrections. "
        "This assistant reports them but does not decide the final business rule."
    )
    show_logic(
        "Flag negative rows where Quantity < 0\n"
        "Count negative rows\n"
        "Count distinct InvoiceNo for those rows\n"
        "Sum Quantity for those rows\n"
        "Sum Revenue for those rows\n"
        "Flag cancellation-style rows where InvoiceNo starts with C"
    )


def answer_missing_customer(data: pd.DataFrame) -> None:
    missing_rows = data[data["IsMissingCustomerID"]]
    missing_percent = len(missing_rows) / len(data) if len(data) else 0
    missing_revenue = missing_rows["Revenue"].sum()

    summary = pd.DataFrame(
        {
            "Metric": [
                "Rows missing CustomerID",
                "Percent of invoice lines missing CustomerID",
                "Revenue on rows missing CustomerID",
            ],
            "Value": [
                f"{len(missing_rows):,}",
                f"{missing_percent:.2%}",
                format_gbp(missing_revenue),
            ],
        }
    )

    st.success("Here is the missing CustomerID summary.")
    st.dataframe(summary, use_container_width=True)
    st.write(
        "Missing CustomerID values limit customer-level analysis, but the rows "
        "may still represent valid transaction activity."
    )
    show_logic(
        "Flag rows where CustomerID is missing\n"
        "Count those rows\n"
        "Divide by total rows for the percentage\n"
        "Sum Revenue for those rows"
    )


def answer_non_positive_price(data: pd.DataFrame) -> None:
    non_positive_rows = data[data["IsNonPositiveUnitPrice"]]
    zero_price_rows = data[data["UnitPrice"] == 0]
    negative_price_rows = data[data["UnitPrice"] < 0]

    summary = pd.DataFrame(
        {
            "Metric": [
                "Rows with UnitPrice <= 0",
                "Rows with UnitPrice == 0",
                "Rows with UnitPrice < 0",
                "Revenue on UnitPrice <= 0 rows",
            ],
            "Value": [
                f"{len(non_positive_rows):,}",
                f"{len(zero_price_rows):,}",
                f"{len(negative_price_rows):,}",
                format_gbp(non_positive_rows["Revenue"].sum()),
            ],
        }
    )

    st.success("Here is the zero or negative UnitPrice summary.")
    st.dataframe(summary, use_container_width=True)
    st.write(
        "Rows with zero or negative UnitPrice may represent gifts, promotions, "
        "adjustments, or data-quality issues."
    )
    show_logic(
        "Flag rows where UnitPrice <= 0\n"
        "Count UnitPrice <= 0 rows\n"
        "Separately count UnitPrice == 0 and UnitPrice < 0 rows\n"
        "Sum Revenue for UnitPrice <= 0 rows"
    )


def answer_average_order_value(data: pd.DataFrame) -> None:
    total_revenue = data["Revenue"].sum()
    unique_invoices = data["InvoiceNo"].nunique()
    average_order_value = total_revenue / unique_invoices if unique_invoices else 0

    st.success(
        "Average order value is "
        f"{format_gbp(average_order_value)} per unique invoice."
    )
    st.write(
        "This uses net revenue divided by unique invoices. It does not separate "
        "gross sales from returns or cancellations."
    )
    show_logic(
        "Revenue = Quantity * UnitPrice\n"
        "Total revenue = sum(Revenue)\n"
        "Unique invoices = count distinct InvoiceNo\n"
        "Average order value = total revenue / unique invoices"
    )


def answer_unsupported() -> None:
    st.warning(
        "I do not support that question yet. Version 3 uses simple keyword "
        "matching and answers one question at a time."
    )
    st.write("Try one of these example questions:")
    for example in EXAMPLE_QUESTIONS:
        st.markdown(f"- {example}")


def answer_question(question_type: str, data: pd.DataFrame) -> None:
    """Route each supported question type to the matching pandas answer."""

    if question_type == "total_revenue":
        answer_total_revenue(data)
    elif question_type == "invoice_lines":
        answer_invoice_lines(data)
    elif question_type == "unique_invoices":
        answer_unique_invoices(data)
    elif question_type == "unique_customers":
        answer_unique_customers(data)
    elif question_type == "top_countries":
        answer_top_countries(data)
    elif question_type == "top_products":
        answer_top_products(data)
    elif question_type == "monthly_revenue":
        answer_monthly_revenue(data)
    elif question_type == "negative_quantity":
        answer_negative_quantity(data)
    elif question_type == "missing_customer":
        answer_missing_customer(data)
    elif question_type == "non_positive_price":
        answer_non_positive_price(data)
    elif question_type == "average_order_value":
        answer_average_order_value(data)
    else:
        answer_unsupported()


project_root = Path(__file__).resolve().parent.parent
csv_file = project_root / "data" / "online_retail_clean.csv"
context_folder = project_root / "context"


st.title("Online Retail AI Data Assistant")
st.info(
    """
    This is Version 3 of the Retail AI Analytics Lab. It answers one
    plain-English data question at a time using deterministic pandas logic.
    It does not use a paid API and does not require an OpenAI API key.
    """
)
st.warning(
    """
    This is not a full AI agent. It does not plan multi-step investigations or
    make business recommendations automatically.
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

with st.sidebar:
    st.header("Version 3 Assistant")
    st.caption("Ask one supported data question at a time.")
    st.metric("Invoice lines", f"{len(df):,}")
    st.metric("Unique invoices", f"{df['InvoiceNo'].nunique():,}")
    st.metric("Unique customers", f"{df['CustomerID'].nunique():,}")

    with st.expander("Project context used"):
        st.markdown("The assistant is designed around these local context files:")
        st.markdown("- `context/business_context.md`")
        st.markdown("- `context/data_profile.md`")
        st.markdown("- `context/cleaning_rules.md`")

    with st.expander("Important business-rule reminder"):
        st.write(
            "Revenue uses `Quantity * UnitPrice`. Negative quantities, "
            "cancellation-style invoices, missing CustomerID rows, and "
            "non-positive prices are still present in the cleaned dataset."
        )

st.subheader("Ask a data question")
st.write(
    "Type a question in plain English. The assistant will classify it with "
    "simple keywords, run a pandas calculation, and show the logic used."
)

st.markdown("#### Example questions")
example_columns = st.columns(2)

for index, example_question in enumerate(EXAMPLE_QUESTIONS):
    column = example_columns[index % 2]
    if column.button(example_question, key=f"example_{index}"):
        st.session_state["user_question"] = example_question

user_question = st.text_input(
    "Your question",
    key="user_question",
    placeholder="Example: What are the top countries by revenue?",
)

if st.button("Answer question", type="primary"):
    question_type = classify_question(user_question)
    st.caption(f"Question type detected: `{question_type}`")
    answer_question(question_type, df)
elif not user_question:
    st.caption("Choose an example or type your own question to begin.")

with st.expander("Supported question types"):
    st.markdown(
        """
        - Total revenue
        - Total invoice lines
        - Unique invoices
        - Unique customers
        - Top countries by revenue
        - Top products by revenue
        - Monthly revenue trend
        - Negative quantity or return summary
        - Missing CustomerID summary
        - Zero or negative UnitPrice summary
        - Average order value
        """
    )

with st.expander("Optional: local project context preview"):
    context_tabs = st.tabs(["Business context", "Data profile", "Cleaning rules"])
    with context_tabs[0]:
        st.markdown(load_text_file(context_folder / "business_context.md"))
    with context_tabs[1]:
        st.markdown(load_text_file(context_folder / "data_profile.md"))
    with context_tabs[2]:
        st.markdown(load_text_file(context_folder / "cleaning_rules.md"))
