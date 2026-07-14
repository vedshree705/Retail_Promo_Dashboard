"""
Step 4: Interactive dashboard.
Run with: python -m streamlit run app.py
"""

import streamlit as st
import pandas as pd
from kpi_engine import load_data, load_store_info, promo_summary, store_type_summary
from llm_layer import get_recommendation

st.title("Retail Promotion Decision Support System")

df = load_data()
store_info = load_store_info()
store_ids = sorted(df["Store"].unique())

col_a, col_b = st.columns([2, 1])
with col_a:
    store_id = st.selectbox("Select a store", store_ids)
with col_b:
    discount_pct = st.slider("Assumed promo discount %", 5, 40, 15)

kpis = promo_summary(df, store_id, discount_rate=discount_pct / 100)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Sales (Promo)", kpis["avg_sales_promo"])
col2.metric("Avg Sales (No Promo)", kpis["avg_sales_no_promo"])
col3.metric("Sales Lift", f"{kpis['sales_lift_pct']}%")
col4.metric("Estimated ROI", f"{kpis['roi_pct']}%")

st.caption(
    "ROI is an estimate: the dataset has no real discount-cost column, so cost is "
    "approximated as (assumed discount %) x (total promo revenue)."
)

chart_data = pd.DataFrame(
    {"Sales": [kpis["avg_sales_promo"], kpis["avg_sales_no_promo"]]},
    index=["Promo", "No Promo"]
)
st.bar_chart(chart_data)

if kpis["statistically_significant"]:
    st.success(f"Statistically significant (p = {kpis['p_value']}) — this lift is unlikely to be random chance.")
else:
    st.warning(f"Not statistically significant (p = {kpis['p_value']}) — this lift could just be noise.")

st.divider()
st.subheader("Performance by Store Type")
st.caption("No product-level data exists in this dataset, so this compares promotion performance across store types (A/B/C/D) instead.")
type_df = store_type_summary(df, store_info)
st.dataframe(type_df, use_container_width=True)

st.divider()
if st.button("Get AI Recommendation"):
    with st.spinner("Thinking..."):
        recommendation = get_recommendation(kpis)
    st.success(recommendation)
