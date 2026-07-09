import streamlit as st
import plotly.express as px

from utils.db import run_query
from utils.filters import render_sidebar_filters, build_where_clause
from utils.format import format_aed
from utils.theme import apply_theme, PALETTE

st.set_page_config(page_title="Property Types - Dubai Property Dashboard", layout="wide")
st.title("Property Type Breakdown")

filters = render_sidebar_filters()
where_clause = build_where_clause(filters)

# --- Property type breakdown: count, avg price, % of total ---
st.subheader("Transactions by Property Type")

with st.spinner("Loading property type data..."):
    by_type = run_query(f"""
        WITH base AS (
            SELECT property_type_en, actual_worth
            FROM vw_transactions_clean
            WHERE {where_clause}
        ),
        totals AS (SELECT COUNT(*) AS total_count FROM base)
        SELECT
            property_type_en,
            COUNT(*) AS txn_count,
            ROUND(AVG(actual_worth), 2) AS avg_price,
            ROUND(COUNT(*)::DOUBLE / MAX(totals.total_count) * 100, 2) AS pct_of_transactions
        FROM base, totals
        GROUP BY property_type_en
        ORDER BY txn_count DESC
    """)

if by_type.empty:
    st.info("No data matches the selected filters.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    fig_pie = px.pie(
        by_type, names="property_type_en", values="txn_count",
        title="Share of Transactions by Property Type", hole=0.4,
        color_discrete_sequence=PALETTE,
    )
    apply_theme(fig_pie)
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    fig_bar = px.bar(
        by_type.sort_values("avg_price"),
        x="avg_price", y="property_type_en", orientation="h",
        labels={"property_type_en": "Property Type", "avg_price": "Avg Price (AED)"},
        title="Average Price by Property Type",
        color_discrete_sequence=[PALETTE[0]],
    )
    apply_theme(fig_bar)
    st.plotly_chart(fig_bar, use_container_width=True)

st.dataframe(
    by_type.rename(columns={
        "property_type_en": "Property Type",
        "txn_count": "Transaction Count",
        "avg_price": "Avg Price (AED)",
        "pct_of_transactions": "% of Transactions",
    }),
    use_container_width=True, hide_index=True,
)

st.divider()

# --- Parking comparison ---
st.subheader("Parking Availability vs Price")

parking = run_query(f"""
    SELECT
        CASE WHEN has_parking THEN 'With Parking' ELSE 'Without Parking' END AS parking_status,
        COUNT(*) AS txn_count,
        ROUND(AVG(actual_worth), 2) AS avg_price
    FROM vw_transactions_clean
    WHERE {where_clause}
    GROUP BY has_parking
""")

col3, col4 = st.columns(2)
with col3:
    fig_park = px.bar(
        parking, x="parking_status", y="avg_price",
        labels={"parking_status": "", "avg_price": "Avg Price (AED)"},
        title="Average Price: With vs Without Parking",
        color="parking_status", color_discrete_sequence=[PALETTE[0], PALETTE[5]],
    )
    fig_park.update_layout(showlegend=False)
    apply_theme(fig_park)
    st.plotly_chart(fig_park, use_container_width=True)

with col4:
    st.dataframe(
        parking.rename(columns={
            "parking_status": "Parking",
            "txn_count": "Transaction Count",
            "avg_price": "Avg Price (AED)",
        }),
        use_container_width=True, hide_index=True,
    )

st.download_button(
    "Download property type breakdown as CSV",
    by_type.to_csv(index=False),
    file_name="property_type_breakdown.csv",
    mime="text/csv",
)
