# Project FORESIGHT — Demand & Inventory Intelligence

Zidio Development internship project (Data Science & Analytics track) for client NorthBay Living.

## Problem

NorthBay Living is a D2C home & lifestyle brand that plans inventory manually, resulting in stockouts on popular items and overstock on slow movers. This project builds a weekly, SKU-level demand forecast and a risk-scoring system that flags which products need reordering and which need markdown, so the operations team can act without a data scientist in the room.

## Data

Source: [Retail Store Inventory Forecasting Dataset](https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset) used as a stand-in for NorthBay's client extract (matched to the required schema: sales, product, calendar, inventory signals). 20 products, 5 stores, ~2 years of daily data, aggregated to weekly per-product demand for this project.

To reproduce: download the CSV from the Kaggle link above and place it at `data/raw/demand_forecasting.csv`.

## Setup

Install dependencies:

    pip install -r requirements.txt

Run the pipeline/model notebook: `notebooks/01_forecast_model.ipynb` (run all cells top to bottom). This regenerates `data/processed/weekly_demand.csv`, `backtest_predictions.csv`, and `latest_risk_scores.csv`, which the dashboard reads.

Run the dashboard locally:

    cd app
    streamlit run app.py

Live dashboard: https://projectforesight-il4jdapw5huus5cvapppqwq.streamlit.app/

## Method

1. Aggregated daily multi-store sales to weekly, per-product demand (single-warehouse view).
2. Built a seasonal-naive baseline (same week, previous year).
3. Engineered lag (1-4 week) and rolling mean/std features, using `.shift(1)` before rolling so the current week never leaks into its own features.
4. Trained an XGBoost regressor, backtested with expanding-window time-based folds (never a random split, to avoid leaking future data into training).
5. Scored stockout and overstock risk per SKU by comparing forecast demand to on-hand inventory over the lead time, and assigned one of four actions: Reorder Now, Markdown/Clear, Watch/Volatile, Healthy.

## Results

| Metric | Value |
|---|---|
| Baseline (Seasonal-Naive) WAPE | 17.32% |
| Model (XGBoost) WAPE | 13.77% |

The model beats the seasonal-naive baseline overall. In the earliest backtest fold the model slightly underperformed the baseline (20.58% vs 18.86%) due to limited training history at that point — this is reported honestly rather than hidden, and the model consistently beat the baseline in all later folds as more history became available.

Current snapshot: 20 SKUs tracked, 8 flagged Reorder Now, 0 flagged Markdown/Clear (NorthBay's current risk is stockout-heavy, not overstock).

## Assumptions & Limitations

- Price, Discount, and Promotion are treated as known in advance (a merchandising/promo calendar set ahead of time) — used as forecast features. Inventory Level and Competitor Pricing were excluded from features since they aren't knowable in advance at forecast time.
- The 4-week-ahead risk forecast repeats the most recent week's prediction rather than producing a true multi-step recursive forecast, to keep the engagement scope achievable in the timeline. A recursive forecast is a natural next improvement.
- Lead time and reorder point are derived/assumed since the source dataset does not include them explicitly (not present in the public dataset used).

## Project structure

    app/            Streamlit dashboard
    data/raw/       Source data (not committed — see Data section to reproduce)
    data/processed/ Model outputs used by the dashboard
    notebooks/      Main pipeline + modelling notebook
    models/         Saved model artifacts
    reports/        EDA memo, executive readout
    reference_v1/   Earlier exploratory version, kept for reference