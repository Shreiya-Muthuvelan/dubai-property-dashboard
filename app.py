import streamlit as st
import plotly.express as px

from utils.db import run_query
from utils.filters import render_sidebar_filters, build_where_clause
from utils.format import format_aed
from utils.theme import apply_theme, PALETTE

st.set_page_config(page_title="Dubai Property Market Dashboard", layout="wide")
st.title("Dubai Property Market Dashboard")

# --- Sidebar filters (persisted in session_state, shared across all pages) ---
filters = render_sidebar_filters()
where_clause = build_where_clause(filters)

# --- KPI row ---
with st.spinner("Loading KPIs..."):
    kpis = run_query(f"""
        SELECT 
            COUNT(*) AS total_txns,
            SUM(actual_worth) AS total_value,
            ROUND(AVG(actual_worth), 0) AS avg_price,
            ROUND(MEDIAN(actual_worth), 0) AS median_price
        FROM vw_transactions_clean
        WHERE {where_clause}
    """).iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Transactions", f"{kpis['total_txns']:,}")
col2.metric("Total Value", format_aed(kpis['total_value']))
col3.metric("Avg Price", format_aed(kpis['avg_price']))
col4.metric("Median Price", format_aed(kpis['median_price']))

st.divider()

# --- Transaction type breakdown ---
st.subheader("Transactions by Type")

with st.spinner("Loading chart..."):
    txn_types = run_query(f"""
        SELECT trans_group_en, COUNT(*) AS txn_count
        FROM vw_transactions_clean
        WHERE {where_clause}
        GROUP BY trans_group_en
        ORDER BY txn_count DESC
    """)

if txn_types.empty:
    st.info("No data matches the selected filters.")
else:
    fig = px.bar(
        txn_types,
        x="trans_group_en",
        y="txn_count",
        color="trans_group_en",
        color_discrete_sequence=PALETTE,
        labels={"trans_group_en": "Transaction Type", "txn_count": "Count"},
        title="Transactions by Type",
    )
    fig.update_layout(showlegend=False)
    apply_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.download_button(
        "Download this data as CSV",
        txn_types.to_csv(index=False),
        file_name="transactions_by_type.csv",
        mime="text/csv",
    )