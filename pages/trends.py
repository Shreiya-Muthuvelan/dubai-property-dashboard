import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.db import run_query
from utils.filters import render_sidebar_filters, build_where_clause
from utils.format import format_aed
from utils.theme import apply_theme, PALETTE

st.set_page_config(page_title="Trends - Dubai Property Dashboard", layout="wide")
st.title("Market Trends")

# --- Shared filters (same pattern as app.py, persisted via session_state) ---
filters = render_sidebar_filters()
where_clause = build_where_clause(filters)

# --- Base monthly aggregation, with MoM change and 3-month rolling avg computed in SQL ---
with st.spinner("Loading trend data..."):
    monthly = run_query(f"""
        WITH monthly_agg AS (
            SELECT
                DATE_TRUNC('month', instance_date) AS month,
                COUNT(*) AS txn_count,
                ROUND(AVG(actual_worth), 2) AS avg_price
            FROM vw_transactions_clean
            WHERE {where_clause}
            GROUP BY 1
        )
        SELECT
            month,
            txn_count,
            avg_price,
            ROUND(
                (avg_price - LAG(avg_price) OVER (ORDER BY month))
                / NULLIF(LAG(avg_price) OVER (ORDER BY month), 0) * 100,
            2) AS mom_change_pct,
            ROUND(
                AVG(txn_count) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),
            2) AS rolling_3mo_volume
        FROM monthly_agg
        ORDER BY month
    """)

if monthly.empty:
    st.info("No data matches the selected filters.")
    st.stop()

# --- Highest-value month, for a quick callout ---
peak_month = monthly.loc[monthly["avg_price"].idxmax()]

col1, col2, col3 = st.columns(3)
col1.metric("Months in range", len(monthly))
col2.metric("Peak avg price month", peak_month["month"].strftime("%b %Y"))
col3.metric("Peak avg price", format_aed(peak_month["avg_price"]))

st.divider()

# --- Volume + price combo chart ---
st.subheader("Monthly Transaction Volume & Average Price")

fig = go.Figure()
fig.add_bar(x=monthly["month"], y=monthly["txn_count"], name="Transaction Count",
            yaxis="y1", marker_color=PALETTE[0])
fig.add_trace(go.Scatter(
    x=monthly["month"], y=monthly["avg_price"],
    name="Avg Price (AED)", yaxis="y2", mode="lines+markers",
    line=dict(color=PALETTE[1], width=3),
))
fig.update_layout(
    yaxis=dict(title="Transaction Count"),
    yaxis2=dict(title="Avg Price (AED)", overlaying="y", side="right"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
apply_theme(fig)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Rolling average overlay ---
st.subheader("3-Month Rolling Average Volume")
fig_roll = px.line(
    monthly, x="month", y=["txn_count", "rolling_3mo_volume"],
    labels={"value": "Transaction Count", "month": "Month", "variable": "Series"},
    color_discrete_sequence=PALETTE,
)
apply_theme(fig_roll)
st.plotly_chart(fig_roll, use_container_width=True)

st.divider()

# --- MoM change table, color-coded so gains/losses jump out instantly ---
st.subheader("Month-over-Month Price Change")
display_df = monthly[["month", "avg_price", "mom_change_pct"]].copy()
display_df["month"] = display_df["month"].dt.strftime("%b %Y")
display_df.columns = ["Month", "Avg Price (AED)", "MoM Change (%)"]

styled = display_df.style.background_gradient(
    subset=["MoM Change (%)"], cmap="RdYlGn", vmin=-10, vmax=10
).format({"Avg Price (AED)": "{:,.0f}", "MoM Change (%)": "{:+.2f}%"})

st.dataframe(styled, use_container_width=True, hide_index=True)

st.download_button(
    "Download trend data as CSV",
    monthly.to_csv(index=False),
    file_name="monthly_trends.csv",
    mime="text/csv",
)