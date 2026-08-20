import streamlit as st
import pandas as pd
import plotly.express as px

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "processed")

st.set_page_config(page_title="NorthBay Living - Demand & Inventory Dashboard", layout="wide")

@st.cache_data
def load_data():
    weekly = pd.read_csv(os.path.join(DATA_DIR, "weekly_demand.csv"))
    weekly["Week"] = pd.to_datetime(weekly["Week"])

    backtest = pd.read_csv(os.path.join(DATA_DIR, "backtest_predictions.csv"))
    backtest["Week"] = pd.to_datetime(backtest["Week"])

    risk = pd.read_csv(os.path.join(DATA_DIR, "latest_risk_scores.csv"))

    return weekly, backtest, risk

weekly, backtest, risk = load_data()

st.title("NorthBay Living - Demand & Inventory Intelligence")
st.caption("Project FORESIGHT | Weekly demand forecast, stockout & overstock risk")

st.sidebar.header("Filters")
categories = ["All"] + sorted(weekly["Category"].unique().tolist())
selected_category = st.sidebar.selectbox("Category", categories)

if selected_category != "All":
    sku_options = sorted(weekly[weekly["Category"] == selected_category]["Product ID"].unique().tolist())
else:
    sku_options = sorted(weekly["Product ID"].unique().tolist())

selected_sku = st.sidebar.selectbox("Product / SKU", sku_options)

st.divider()

col1, col2, col3, col4 = st.columns(4)

total_skus = risk["Product ID"].nunique()
reorder_count = (risk["Recommended_Action"] == "Reorder Now").sum()
markdown_count = (risk["Recommended_Action"] == "Markdown/Clear").sum()
total_revenue_at_stake = risk[risk["Recommended_Action"] != "Healthy"]["Revenue_at_Stake"].sum()

col1.metric("Total SKUs Tracked", total_skus)
col2.metric("Reorder Now", reorder_count)
col3.metric("Markdown / Clear", markdown_count)
col4.metric("Revenue at Stake (Rs)", f"{total_revenue_at_stake:,.0f}")

st.divider()

st.subheader(f"Forecast vs Actual — {selected_sku}")

sku_history = weekly[weekly["Product ID"] == selected_sku].sort_values("Week")
sku_backtest = backtest[backtest["Product ID"] == selected_sku].sort_values("Week")

if sku_backtest.empty:
    st.info("Backtest data not available for this SKU in the test period.")
else:
    fig = px.line(
        sku_backtest,
        x="Week",
        y=["Demand", "Model_Pred", "Seasonal_Naive"],
        labels={"value": "Units", "variable": "Series"},
        title=None,
    )
    fig.update_layout(legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Stockout & Overstock Risk — All SKUs")

if selected_category != "All":
    risk_filtered = risk[risk["Category"] == selected_category]
else:
    risk_filtered = risk

def highlight_action(val):
    if val == "Reorder Now":
        return "background-color: #ffcccc"
    elif val == "Markdown/Clear":
        return "background-color: #cce5ff"
    elif val == "Watch/Volatile":
        return "background-color: #fff3cd"
    return ""

if risk_filtered.empty:
    st.warning("No SKUs found for this filter.")
else:
    st.dataframe(
        risk_filtered.sort_values("Revenue_at_Stake", ascending=False).style.map(
            highlight_action, subset=["Recommended_Action"]
        ),
        use_container_width=True,
    )

st.divider()

st.subheader("Priority Action List")

priority = risk[risk["Recommended_Action"] != "Healthy"].sort_values("Revenue_at_Stake", ascending=False)

if priority.empty:
    st.success("No urgent actions right now. All SKUs are healthy.")
else:
    for _, row in priority.head(10).iterrows():
        st.write(
            f"**{row['Product ID']}** ({row['Category']}) — {row['Recommended_Action']} "
            f"— Rs {row['Revenue_at_Stake']:,.0f} at stake"
        )