
import duckdb
con = duckdb.connect('dubai_property.duckdb')
con.execute("""
    CREATE TABLE IF NOT EXISTS transactions AS
    SELECT * FROM read_csv_auto('C:/Users/shrei/OneDrive/Desktop/2026 Summer/Data Engineering and Analysis/SQL/dubai-property-dashboard/data/transactions.csv')
""")

print(con.execute("SELECT COUNT(*) FROM transactions").fetchone())
print(con.execute("DESCRIBE transactions").fetchdf())
con.close()
