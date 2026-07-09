import streamlit as st
from utils.db import run_query


def init_filter_options():
    """
    Fetch the values needed to populate filter widgets (min/max date, area list,
    property type list). Cached via run_query, so this is cheap after first call.
    """
    date_bounds = run_query("""
        SELECT MIN(instance_date) AS min_date, MAX(instance_date) AS max_date
        FROM vw_transactions_clean
    """).iloc[0]

    areas = run_query("""
        SELECT DISTINCT area_name_en FROM vw_transactions_clean ORDER BY 1
    """)["area_name_en"].tolist()

    property_types = run_query("""
        SELECT DISTINCT property_type_en FROM vw_transactions_clean ORDER BY 1
    """)["property_type_en"].tolist()

    return date_bounds["min_date"], date_bounds["max_date"], areas, property_types


def render_sidebar_filters():
    """
    Renders filter widgets in the sidebar and stores selections in st.session_state
    so they persist across page navigation. Call this at the top of every page.
    Returns the current filter selections as a dict.
    """
    min_date, max_date, areas, property_types = init_filter_options()

    st.sidebar.header("Filters")

    # Use session_state defaults so filters persist across pages
    if "date_range" not in st.session_state:
        st.session_state.date_range = (min_date, max_date)
    if "selected_areas" not in st.session_state:
        st.session_state.selected_areas = []
    if "selected_types" not in st.session_state:
        st.session_state.selected_types = []

    st.session_state.date_range = st.sidebar.date_input(
        "Date range",
        value=st.session_state.date_range,
        min_value=min_date,
        max_value=max_date,
    )

    st.session_state.selected_areas = st.sidebar.multiselect(
        "Area",
        options=areas,
        default=st.session_state.selected_areas,
    )

    st.session_state.selected_types = st.sidebar.multiselect(
        "Property Type",
        options=property_types,
        default=st.session_state.selected_types,
    )

    if st.sidebar.button("Reset filters"):
        st.session_state.date_range = (min_date, max_date)
        st.session_state.selected_areas = []
        st.session_state.selected_types = []
        st.rerun()

    return {
        "date_range": st.session_state.date_range,
        "areas": st.session_state.selected_areas,
        "types": st.session_state.selected_types,
    }


def build_where_clause(filters: dict) -> str:
    """
    Builds a SQL WHERE clause (without the WHERE keyword) from the filter dict
    returned by render_sidebar_filters(). Safe against empty selections.
    """
    conditions = []

    # date_range is a tuple only when the user has picked both start and end
    date_range = filters.get("date_range")
    if date_range and len(date_range) == 2:
        start, end = date_range
        conditions.append(f"instance_date BETWEEN '{start}' AND '{end}'")

    areas = filters.get("areas")
    if areas:
        area_list = "','".join(a.replace("'", "''") for a in areas)
        conditions.append(f"area_name_en IN ('{area_list}')")

    types = filters.get("types")
    if types:
        type_list = "','".join(t.replace("'", "''") for t in types)
        conditions.append(f"property_type_en IN ('{type_list}')")

    return " AND ".join(conditions) if conditions else "1=1"