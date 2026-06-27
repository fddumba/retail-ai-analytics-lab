# Version 4: AI Data Analysis Agent

This folder contains the **Version 4 AI Data Analysis Agent** for the Retail AI
Analytics Lab project.

The app reads the cleaned retail CSV file and helps a user investigate a
business goal with a short, rule-based analysis plan. It uses pandas and
Streamlit only. It does not call an external AI API.

## Purpose

Version 4 shows how an analysis agent can go beyond a single direct answer.
The user enters a business goal, and the app:

- Detects the likely analysis intent
- Builds a short analysis plan
- Runs several pandas analysis steps
- Shows findings, tables, and charts
- Recommends next actions
- States limitations and assumptions

The app reads:

```text
data/online_retail_clean.csv
```

The raw Excel workbook is not modified.

## How Version 4 Differs From Version 3

**Version 3 AI Data Assistant** answers one question at a time. For example, it
can answer "What is the total revenue?"

**Version 4 AI Data Analysis Agent** starts from a broader business goal. It
detects the goal type, creates a plan, runs multiple related analysis steps,
and recommends what management should investigate next.

Version 4 is still beginner-friendly and safe:

- It is rule-based.
- It runs locally.
- It uses deterministic pandas logic.
- It does not use external AI APIs.
- It does not modify the raw Excel file or cleaned CSV file.

## How to Run

From the project root folder, run:

```bash
python -m streamlit run version_4_ai_analysis_agent/app.py
```

If dependencies are not installed yet, install them first:

```bash
python -m pip install -r requirements.txt
```

## Example Business Goals

Try goals like:

- Investigate why revenue changed over time
- Find which countries drive revenue and returns
- Analyze product return risk
- Explain missing CustomerID impact
- Identify unusual products or countries
- Recommend what management should investigate next

## Supported Intents

The app classifies the request into one of these intents:

- `revenue_trend_investigation`
- `country_performance_investigation`
- `product_performance_investigation`
- `return_risk_investigation`
- `missing_customer_investigation`
- `general_business_review`

Intent detection uses simple keyword matching. It is not a large language
model.

## What the Agent Can Do

The Version 4 agent can:

- Apply date, country, product, quantity, price, and CustomerID filters
- Analyze monthly revenue trends
- Compare country revenue and revenue share
- Compare top products by revenue and quantity
- Explore negative Quantity rows as return or cancellation activity
- Measure the impact of missing CustomerID rows
- Run a general business review with KPIs, top countries, top products, monthly
  trend, and return summary
- Show supporting tables and Streamlit charts
- Recommend practical next questions for management

## What the Agent Cannot Do

The Version 4 agent cannot:

- Understand every possible business goal
- Prove the root cause of revenue changes
- Make final accounting decisions about returns or cancellations
- Decide whether missing CustomerID rows are valid or invalid sales
- Replace human business judgment
- Modify the raw Excel workbook
- Modify the cleaned CSV file

## Important Limitations

Negative Quantity rows are treated as return or cancellation activity for
exploration only. The final business meaning needs confirmation.

Revenue is calculated as:

```text
Revenue = Quantity * UnitPrice
```

All results depend on the sidebar filters. If a filter excludes negative
Quantity rows, return-risk analysis will show little or no return activity.

This app is designed for learning. It is a local, rule-based analysis agent,
not a production AI system.
