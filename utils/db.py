from pathlib import Path
import duckdb
import streamlit as st

DB_PATH = str(Path(__file__).resolve().parent.parent / "db" / "dubai_property.duckdb")


@st.cache_resource
def get_connection():
    """
    Open ONE read-only connection and reuse it for the life of the app session.
    DuckDB does not handle multiple concurrent connections to the same file well
    (especially read-write ones), so opening a fresh connection per query causes
    lock conflicts under Streamlit's rerun model. read_only=True also lets
    multiple Streamlit sessions read the same file concurrently without issue.
    """
    return duckdb.connect(DB_PATH, read_only=True)


@st.cache_data(ttl=3600)
def run_query(sql: str, params: list = None):
    """Run a query and return a pandas DataFrame. Cached by query text + params."""
    con = get_connection()
    if params:
        return con.execute(sql, params).df()
    return con.execute(sql).df()
