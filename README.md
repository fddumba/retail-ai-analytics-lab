# Retail AI Analytics Lab

## Project Overview

Retail AI Analytics Lab is a step-by-step analytics learning project built with
the UCI Online Retail dataset. It shows how the same retail data can support
four increasingly advanced analytics products:

1. Basic Dashboard
2. Business Intelligence Dashboard
3. AI Data Assistant
4. AI Data Analysis Agent

The project progresses from static reporting to interactive business
intelligence (BI), direct natural-language data questions, and multi-step
agent-style business analysis.

## Dataset

This project uses the UCI Online Retail dataset, which contains transaction
data from a UK-based online retailer.

The applications read from the cleaned CSV file:

```text
data/online_retail_clean.csv
```

The raw Excel workbook is kept as the original source and is not modified.

The dataset files are stored locally in the `data/` folder. Large raw or
cleaned data files may be excluded from GitHub. Users can download the UCI
Online Retail dataset and run the cleaning script to recreate
`data/online_retail_clean.csv`.

## Project Progress

| Version | Product | Status |
| --- | --- | --- |
| Version 1 | Basic Dashboard | Complete |
| Version 2 | Business Intelligence Dashboard | Complete |
| Version 3 | AI Data Assistant | Complete and tested |
| Version 4 | AI Data Analysis Agent | Complete and tested |

## Learning Progression

- **Version 1** reports what happened using a fixed dashboard and core KPIs.
- **Version 2** allows interactive BI exploration with filters and detailed views.
- **Version 3** answers direct natural-language data questions using rule-based pandas logic.
- **Version 4** plans and runs multi-step business investigations, then presents findings, charts, next actions, assumptions, and limitations.

## Screenshots

### Version 1: Basic Dashboard

![Version 1 Basic Dashboard](screenshots/version_1_basic_dashboard.png)

### Version 2: Business Intelligence Dashboard

![Version 2 BI Dashboard](screenshots/version_2_bi_dashboard.png)

### Version 3: AI Data Assistant

![Version 3 AI Data Assistant](screenshots/version_3_ai_data_assistant.png)

### Version 4: AI Data Analysis Agent

![Version 4 AI Data Analysis Agent](screenshots/version_4_ai_analysis_agent.png)

## Tools Used

- Python
- pandas
- Streamlit
- CSV / Excel
- VS Code
- Codex assistance

## Folder Structure

```text
retail-ai-analytics_lab/
|-- context/
|-- data/
|   `-- online_retail_clean.csv
|-- scripts/
|-- version_1_basic_dashboard/
|-- version_2_bi_dashboard/
|-- version_3_ai_data_assistant/
`-- version_4_ai_analysis_agent/
```

## How to Run Each Version

Run these commands from the project root.

### Version 1: Basic Dashboard

```bash
python -m streamlit run version_1_basic_dashboard/app.py
```

### Version 2: Business Intelligence Dashboard

```bash
python -m streamlit run version_2_bi_dashboard/app.py
```

### Version 3: AI Data Assistant

```bash
python -m streamlit run version_3_ai_data_assistant/app.py
```

### Version 4: AI Data Analysis Agent

```bash
python -m streamlit run version_4_ai_analysis_agent/app.py
```

## What I Learned

This project provided hands-on practice with:

- Data cleaning
- Data profiling
- KPI design
- Dashboard development
- BI filters
- Rule-based natural-language question detection
- Agent-style analysis planning
- Communicating findings and limitations

## BI and Data Engineering Upgrade

### Purpose

This upgrade turns the project from dashboard-only analytics into a reusable
BI and data engineering workflow. It adds a more production-style approach to
handling retail data, preparing trusted outputs, and supporting downstream
analytics and dashboard work.

### Pipeline Flow

```text
Raw Excel data
→ src/extract.py
→ src/validation.py
→ src/transform.py
→ data/processed/online_retail_clean.csv
→ src/build_marts.py
→ data/marts/*.csv
→ SQL analytics / dashboards / Power BI
```

### Key Folders

- src/ = reusable Python pipeline code
- data/raw or data/ = local source data
- data/processed/ = processed clean CSV output
- data/marts/ = BI-ready fact, dimension, and summary tables
- sql/ = business analysis queries
- docs/ = project documentation
- dashboards/ = future BI dashboard notes or Power BI/Streamlit BI material

### How to Run the Pipeline

Run the following commands from the project root:

```bash
python src/transform.py
python src/build_marts.py
```

### SQL Analytics Layer

The sql/ folder contains portfolio-friendly SQL queries for:

- revenue trends
- country performance
- product performance
- returns and data quality checks

### Portfolio Value

This upgrade demonstrates:

- data processing
- reusable Python modules
- data validation
- BI-ready marts
- SQL analytics
- dashboard readiness

## Portfolio Summary

Built a four-stage retail analytics lab using Python, pandas, and Streamlit,
progressing from a basic dashboard to interactive BI, natural-language data
assistance, and a rule-based AI analysis agent.
