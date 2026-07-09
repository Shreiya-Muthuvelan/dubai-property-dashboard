from pathlib import Path
import duckdb
import streamlit as st

from load_data import init_database

DB_PATH = str(Path(__file__).resolve().parent.parent / "db" / "dubai_property.duckdb")


def ensure_database() -> None:
    db_path = Path(DB_PATH)
    if not db_path.exists():
        init_database(db_path)
        return

    con = duckdb.connect(DB_PATH)
    try:
        tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
        view_exists = con.execute(
            "SELECT 1 FROM information_schema.views WHERE table_name = 'vw_transactions_clean'"
        ).fetchone()
        if "transactions" not in tables or not view_exists:
            init_database(db_path)
    finally:
        con.close()


def get_connection():
    """Open a fresh connection for each query so the database file is not left locked."""
    ensure_database()
    return duckdb.connect(DB_PATH, read_only=True)


@st.cache_data(ttl=3600)
def run_query(sql: str, params: list = None):
    """Run a query and return a pandas DataFrame. Cached by query text."""
    con = get_connection()
    try:
        if params:
            return con.execute(sql, params).df()
        return con.execute(sql).df()
    finally:
        con.close()