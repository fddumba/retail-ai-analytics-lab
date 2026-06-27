# Version 3: AI Data Assistant

This folder contains the **Version 3 AI Data Assistant** for the Retail AI
Analytics Lab project.

The assistant lets a user ask plain-English questions about the UCI Online
Retail dataset. It answers one question at a time using deterministic pandas
logic.

No paid API is required. No OpenAI API key is required.

## What Version 3 Does

Version 3 is a beginner-friendly Streamlit app that behaves like a simple data
assistant.

It can:

- Load the cleaned online retail CSV
- Calculate revenue as `Quantity * UnitPrice`
- Add useful data-quality flags
- Accept one plain-English question from the user
- Classify the question with simple keyword matching
- Run a matching pandas calculation
- Display a text answer
- Show a table or chart when useful
- Explain the calculation or logic used
- Say clearly when a question is not supported

## Dataset Used

The app reads:

```text
data/online_retail_clean.csv
```

The app also uses the project context files as guidance:

```text
context/business_context.md
context/data_profile.md
context/cleaning_rules.md
```

The raw Excel file is not modified.

## How to Run

From the project root folder, run:

```bash
python -m streamlit run version_3_ai_data_assistant/app.py
```

If dependencies are not installed yet, install them first:

```bash
python -m pip install -r requirements.txt
```

## Example Questions

Try questions like:

- What is the total revenue?
- How many invoice lines are in the dataset?
- How many unique invoices are there?
- How many unique customers are there?
- What are the top countries by revenue?
- What are the top products by revenue?
- Show the monthly revenue trend.
- Summarize negative quantity rows or returns.
- How many rows are missing CustomerID?
- How many rows have zero or negative UnitPrice?
- What is the average order value?

## Testing Status

Version 3 is tested and working.

It was tested with these questions:

- What is the total revenue?
- What are the top countries by revenue?
- Show the monthly revenue trend.
- How many rows are missing CustomerID?
- Summarize negative quantity rows or returns.

Key confirmed outputs:

- Total revenue: GBP 9,726,006.95
- Missing CustomerID rows in cleaned CSV: 135,037
- Negative quantity rows: 10,587
- Negative quantity revenue impact: GBP -893,979.73

## Supported Question Types

The assistant currently supports:

- Total revenue
- Total invoice lines
- Unique invoices
- Unique customers
- Top countries by revenue
- Top products by revenue
- Monthly revenue trend
- Negative quantity or return summary
- Missing `CustomerID` summary
- Zero or negative `UnitPrice` summary
- Average order value

Questions are matched using simple keywords. For example, a question containing
`top` and `countries` will be treated as a top countries by revenue question.

## How Version 3 Differs From Version 2

**Version 2 Business Intelligence Dashboard** is interactive, but the user
explores the data through filters, KPI cards, and charts.

**Version 3 AI Data Assistant** changes the interaction style. Instead of
starting with dashboard filters, the user types a plain-English question and
the app returns one direct answer with the calculation shown.

In short:

- Version 2 is a BI dashboard for visual exploration.
- Version 3 is a question-answer assistant for one data question at a time.

Version 3 still uses deterministic pandas logic. It is not a chatbot powered by
an external model.

## Important Limitations

This version is intentionally simple.

- It answers one question at a time.
- It uses keyword matching, not a large language model.
- It only supports the question types listed above.
- It does not understand every possible wording.
- It does not create new analysis plans.
- It does not automatically choose business rules.
- It does not make business recommendations.
- It does not modify the dataset.

The cleaned dataset still includes records that require business judgment:

- Negative quantities
- Cancellation-style invoices
- Missing `CustomerID` values
- Zero or negative `UnitPrice` values
- Possible non-product stock codes such as postage, discounts, or adjustments

The assistant reports these issues, but it does not decide final accounting or
business definitions.

## Why This Is Not Version 4 Agent Behavior

Version 3 is an assistant, not an autonomous analysis agent.

It does not:

- Plan multi-step investigations
- Decide which follow-up questions to ask automatically
- Explore multiple hypotheses by itself
- Make business recommendations automatically
- Take actions outside the current question

Those behaviors are reserved for a future **Version 4 AI Data Analysis Agent**.

Version 3 is the bridge between the BI dashboard and a future agent: it teaches
how natural-language questions can map to safe, explainable data calculations.
