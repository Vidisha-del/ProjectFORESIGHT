# Data Quality & EDA Insight Memo
**Project FORESIGHT — NorthBay Living**
Prepared by: Data Science Intern, Zidio Development

## 1. Data Quality Summary

The dataset covers 76,000 transaction-level records across 20 products, 5 stores, and 4 regions,
spanning January 2022 to January 2024 (~2 years — sufficient history to learn weekly and
yearly seasonality).

**Checks performed:**
- Missing values: none found across all columns.
- Duplicate rows: none found.
- Date range and type consistency: verified, no gaps in the calendar.

The source data was already clean; no imputation or deduplication was required. This was
confirmed rather than assumed — the checks were run and are reproducible in the pipeline
notebook.

## 2. Key Business Insights

### Insight 1: Nearly half of all demand sits in one category — concentration risk

Groceries accounts for 46.4% of total demand across the catalog, more than the next three
categories combined (Clothing 17.3%, Furniture 12.7%, Toys 12.4%, Electronics 11.2%).
This means stocking decisions for Groceries SKUs carry disproportionate weight — a stockout
in this category has a much larger revenue impact than a stockout in Electronics, and
forecasting effort should be weighted accordingly.

### Insight 2: The business is losing roughly 17.5% of demand to stockouts

Comparing recorded Demand against actual Units Sold shows a persistent gap: total demand
exceeded units actually sold by approximately 1.39 million units over the period, about
17.5% of total demand. This is not a modelling artifact — it is a direct, quantifiable
signal that stock is running out before demand is met, which matches exactly the problem
the client described ("we stock out of things people want"). This single number is the
strongest evidence for why this engagement matters financially.

### Insight 3: Promotions lift demand by ~30%, but planning should account for it explicitly

Average demand during promotional periods is 123.3 units/day versus 95.0 units/day without
a promotion — a 29.8% lift. Because this lift is large and consistent, promotion flags were
kept as a forecasting feature (treated as known in advance, since promotional calendars are
typically planned ahead of time by merchandising). Ignoring this signal would cause the
model to systematically under-forecast during promo weeks.

### Insight 4: Demand has clear seasonal peaks, not a flat pattern

Monthly average demand peaks in August (119.8) and June (117.3), and dips in May (86.5) and
April (92.8) — roughly a 38% swing between the strongest and weakest months. A seasonal-naive
baseline (same period, previous year) is a meaningful comparison point precisely because this
seasonality is strong enough to be learnable, not noise.

### Insight 5: Top and bottom movers are closer together than expected — no extreme "dead stock" in this dataset

The best-selling product (P0009, ~450K units) and the weakest (P0020, ~321K units) differ by
about 29%, not by orders of magnitude. This means the catalog does not show classic "dead
stock" (SKUs nobody buys) in this dataset — the risk in this data leans toward under-stocking
fast movers rather than clearing slow ones. This is consistent with the 0 SKUs flagged
Markdown/Clear in the current risk scoring output.

## 3. Implication for Modelling

These insights directly shaped modelling choices:
- Seasonality (Insight 4) justified using lag and rolling features plus a seasonal-naive
  baseline rather than a flat average.
- Promotion lift (Insight 3) was kept as a forecast feature.
- The stockout gap (Insight 2) is the business case for the risk-scoring layer — the model
  isn't just an accuracy exercise, it targets a concrete, quantified loss.