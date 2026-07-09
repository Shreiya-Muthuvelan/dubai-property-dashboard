import streamlit as st
import plotly.express as px

from utils.db import run_query
from utils.filters import render_sidebar_filters, build_where_clause
from utils.format import format_aed
from utils.theme import apply_theme, PALETTE

st.set_page_config(page_title="Area Analysis - Dubai Property Dashboard", layout="wide")
st.title("Area Analysis")

filters = render_sidebar_filters()
where_clause = build_where_clause(filters)

# --- Top 10 areas: transaction count, avg price, total value ---
st.subheader("Top 10 Areas")

metric_choice = st.radio(
    "Rank by:",
    ["Transaction Count", "Average Price", "Total Transaction Value"],
    horizontal=True,
)

metric_map = {
    "Transaction Count": ("COUNT(*)", "txn_count", False),
    "Average Price": ("ROUND(AVG(actual_worth), 2)", "avg_price", False),
    "Total Transaction Value": ("ROUND(SUM(actual_worth), 2)", "total_value", False),
}
sql_expr, col_name, _ = metric_map[metric_choice]

with st.spinner("Loading area rankings..."):
    top_areas = run_query(f"""
        SELECT area_name_en, {sql_expr} AS {col_name}
        FROM vw_transactions_clean
        WHERE {where_clause}
        GROUP BY area_name_en
        ORDER BY {col_name} DESC
        LIMIT 10
    """)

if top_areas.empty:
    st.info("No data matches the selected filters.")
    st.stop()

fig = px.bar(
    top_areas.sort_values(col_name),
    x=col_name, y="area_name_en", orientation="h",
    labels={"area_name_en": "Area", col_name: metric_choice},
    title=f"Top 10 Areas by {metric_choice}",
    color=col_name, color_continuous_scale=[PALETTE[2], PALETTE[0]],
)
fig.update_layout(coloraxis_showscale=False)
apply_theme(fig)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Price per sqft vs market average ---
st.subheader("Price per Sqft: Area vs Market Average")

market_avg = run_query(f"""
    SELECT ROUND(AVG(meter_sale_price), 2) AS market_avg_ppsf
    FROM vw_transactions_clean
    WHERE {where_clause}
""")["market_avg_ppsf"].iloc[0]

ppsf_by_area = run_query(f"""
    SELECT area_name_en, ROUND(AVG(meter_sale_price), 2) AS avg_ppsf
    FROM vw_transactions_clean
    WHERE {where_clause}
    GROUP BY area_name_en
    ORDER BY avg_ppsf DESC
    LIMIT 15
""")

fig_ppsf = px.bar(
    ppsf_by_area, x="area_name_en", y="avg_ppsf",
    labels={"area_name_en": "Area", "avg_ppsf": "Avg Price per Sqft (AED)"},
    title="Avg Price per Sqft by Area (Top 15)",
    color_discrete_sequence=[PALETTE[0]],
)
fig_ppsf.add_hline(
    y=market_avg, line_dash="dash", line_color=PALETTE[5],
    annotation_text=f"Market Avg: {market_avg:,.0f}", annotation_position="top right",
)
apply_theme(fig_ppsf)
st.plotly_chart(fig_ppsf, use_container_width=True)

st.divider()

# --- Price volatility (STDDEV), shown as a heatmap-style table so spread jumps out ---
st.subheader("Price Volatility by Area")
st.caption("Areas with the highest standard deviation in transaction price — a wide spread can mean a mix of very different property tiers within the same area.")

volatility = run_query(f"""
    SELECT area_name_en,
           ROUND(AVG(actual_worth), 2) AS avg_price,
           ROUND(STDDEV(actual_worth), 2) AS price_stddev
    FROM vw_transactions_clean
    WHERE {where_clause}
    GROUP BY area_name_en
    HAVING COUNT(*) >= 5
    ORDER BY price_stddev DESC
    LIMIT 10
""")

vol_styled = volatility.rename(columns={
    "area_name_en": "Area", "avg_price": "Avg Price (AED)", "price_stddev": "Price Std Dev"
}).style.background_gradient(subset=["Price Std Dev"], cmap="Oranges").format(
    {"Avg Price (AED)": "{:,.0f}", "Price Std Dev": "{:,.0f}"}
)
st.dataframe(vol_styled, use_container_width=True, hide_index=True)

st.divider()

# --- Pivot: avg price by area x property type, shown as a heatmap ---
st.subheader("Average Price by Area × Property Type")
st.caption("Top 15 areas by transaction volume, shown against each property type. Darker = higher average price.")

with st.spinner("Building pivot table..."):
    pivot_df = run_query(f"""
        PIVOT (
            SELECT * FROM vw_transactions_clean
            WHERE {where_clause}
            AND area_name_en IN (
                SELECT area_name_en FROM vw_transactions_clean
                WHERE {where_clause}
                GROUP BY area_name_en
                ORDER BY COUNT(*) DESC
                LIMIT 15
            )
        )
        ON property_type_en
        USING ROUND(AVG(actual_worth), 0)
        GROUP BY area_name_en
        ORDER BY area_name_en
    """)

numeric_cols = pivot_df.select_dtypes(include="number").columns
pivot_styled = pivot_df.style.background_gradient(
    subset=numeric_cols, cmap="YlOrBr", axis=None
).format({c: "{:,.0f}" for c in numeric_cols}, na_rep="—")

st.dataframe(pivot_styled, use_container_width=True, hide_index=True)

st.download_button(
    "Download area rankings as CSV",
    top_areas.to_csv(index=False),
    file_name="area_rankings.csv",
    mime="text/csv",
)