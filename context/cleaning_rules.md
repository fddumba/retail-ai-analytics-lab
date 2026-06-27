# Cleaning Rules for Online Retail Dataset

## Purpose

This document explains what was changed, what was not changed, and what still needs business judgment before dashboard or AI-agent analysis.

## Source Files

Raw file:

`data/Online Retail.xlsx`

Cleaned file:

`data/online_retail_clean.csv`

## Cleaning Applied So Far

The first cleaning step removed only exact duplicate rows.

Confirmed results:

- Raw rows: 541,909
- Cleaned rows: 536,641
- Exact duplicate rows removed: 5,268

## What Was Not Removed Yet

The following records are still kept in the cleaned dataset:

- Negative Quantity rows
- Zero or negative UnitPrice rows
- Missing CustomerID rows
- Cancellation or return transactions
- Product rows with missing descriptions
- Extreme quantity or price values

## Why These Were Not Removed Yet

These records may have business meaning.

For example:

- Negative Quantity may represent returns or cancellations.
- Invoice numbers beginning with `C` may represent cancelled invoices.
- Missing CustomerID may still be valid sales transactions.
- Zero UnitPrice may represent samples, gifts, promotions, or data errors.
- Extreme values may be real bulk orders or data entry errors.

Because of this, they should not be removed blindly.

## Revenue Formula

Basic line revenue:

`Revenue = Quantity * UnitPrice`

However, revenue interpretation depends on business rules.

Possible revenue views:

1. Gross revenue  
2. Return/cancellation value  
3. Net revenue  
4. Revenue excluding unclear records  

## Dashboard Rule

For the first dashboard, use the cleaned dataset with exact duplicates removed.

When reporting revenue, clearly state whether returns and cancellations are included or excluded.

## AI Assistant / Agent Rule

Any AI assistant or agent must:

- Read `business_context.md`
- Read `data_profile.md`
- Read this `cleaning_rules.md`
- Explain which filters it used
- Separate confirmed facts from assumptions
- Ask clarifying questions when the user says vague words like:
  - sales
  - orders
  - revenue
  - customers
  - best products
  - performance

## Current Status

The dataset is lightly cleaned and ready for exploratory analysis and Version 1 dashboard development.