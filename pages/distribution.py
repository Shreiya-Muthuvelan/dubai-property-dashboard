import streamlit as st
import plotly.express as px

from utils.db import run_query
from utils.filters import render_sidebar_filters, build_where_clause
from utils.format import format_aed
from utils.theme import apply_theme, PALETTE

st.set_page_config(page_title="Distribution - Dubai Property Dashboard", layout="wide")
st.title("Price Distribution")

filters = render_sidebar_filters()
where_clause = build_where_clause(filters)

# --- Percentile summary ---
st.subheader("Price Percentiles")

with st.spinner("Loading percentile stats..."):
    percentiles = run_query(f"""
        SELECT
            MIN(actual_worth) AS min_price,
            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY actual_worth) AS p25,
            MEDIAN(actual_worth) AS median_price,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY actual_worth) AS p75,
            PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY actual_worth) AS p99,
            MAX(actual_worth) AS max_price
        FROM vw_transactions_clean
        WHERE {where_clause}
    """).iloc[0]

if percentiles.isnull().all():
    st.info("No data matches the selected filters.")
    st.stop()

labels = ["P25", "Median", "P75", "P99", "Max"]
values = [percentiles["p25"], percentiles["median_price"],
          percentiles["p75"], percentiles["p99"], percentiles["max_price"]]

cols = st.columns(5)
for c, label, val in zip(cols, labels, values):
    c.metric(label, format_aed(val))

st.divider()

# --- Price bucket histogram ---
st.subheader("Price Distribution by Bucket")

with st.spinner("Building histogram..."):
    buckets = run_query(f"""
        SELECT
            CASE
                WHEN actual_worth < 500000 THEN '< 500K'
                WHEN actual_worth < 1000000 THEN '500K - 1M'
                WHEN actual_worth < 2000000 THEN '1M - 2M'
                WHEN actual_worth < 5000000 THEN '2M - 5M'
                WHEN actual_worth < 10000000 THEN '5M - 10M'
                ELSE '10M+'
            END AS price_bucket,
            MIN(actual_worth) AS bucket_min,
            COUNT(*) AS txn_count
        FROM vw_transactions_clean
        WHERE {where_clause}
        GROUP BY price_bucket
        ORDER BY bucket_min
    """)

fig_bucket = px.bar(
    buckets, x="price_bucket", y="txn_count",
    labels={"price_bucket": "Price Range", "txn_count": "Transaction Count"},
    title="Transaction Count by Price Range",
    color="txn_count", color_continuous_scale=[PALETTE[2], PALETTE[0]],
)
fig_bucket.update_layout(coloraxis_showscale=False)
apply_theme(fig_bucket)
st.plotly_chart(fig_bucket, use_container_width=True)

st.caption(
    "Buckets are fixed ranges (not adaptive) so they stay comparable across "
    "different filter selections. Adjust the ranges in code if your data skews "
    "heavily toward one end."
)

st.divider()

# --- Outliers: top 1% most expensive transactions ---
st.subheader("Top 1% Most Expensive Transactions")

with st.spinner("Finding outliers..."):
    outliers = run_query(f"""
        SELECT area_name_en, property_type_en, actual_worth, procedure_area,
               ROUND(meter_sale_price, 2) AS price_per_sqft
        FROM vw_transactions_clean
        WHERE {where_clause}
        QUALIFY PERCENT_RANK() OVER (ORDER BY actual_worth) >= 0.99
        ORDER BY actual_worth DESC
    """)

outliers_styled = outliers.rename(columns={
    "area_name_en": "Area", "property_type_en": "Property Type",
    "actual_worth": "Price (AED)", "procedure_area": "Area (sqft)",
    "price_per_sqft": "Price/Sqft (AED)",
}).style.background_gradient(subset=["Price (AED)"], cmap="YlOrRd").format(
    {"Price (AED)": "{:,.0f}", "Area (sqft)": "{:,.0f}", "Price/Sqft (AED)": "{:,.0f}"}
)

st.dataframe(outliers_styled, use_container_width=True, hide_index=True)

st.download_button(
    "Download outlier transactions as CSV",
    outliers.to_csv(index=False),
    file_name="top_1pct_outliers.csv",
    mime="text/csv",
)