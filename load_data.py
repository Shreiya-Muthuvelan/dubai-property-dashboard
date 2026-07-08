
import duckdb

# creates the file if it doesn't exist, connects if it does
con = duckdb.connect('dubai_property.duckdb')

# load CSV directly into a table
con.execute("""
    CREATE TABLE IF NOT EXISTS transactions AS
    SELECT * FROM read_csv_auto('C:/Users/shrei/OneDrive/Desktop/2026 Summer/Data Engineering and Analysis/SQL/dubai-property-dashboard/data/transactions.csv')
""")

# sanity check
print(con.execute("SELECT COUNT(*) FROM transactions").fetchone())
print(con.execute("DESCRIBE transactions").fetchdf())

con.close()




import duckdb
import os

con = duckdb.connect('dubai_property.duckdb')

# This will print the absolute physical path of the file Python is using
print("Your database is actually located at:")
print(os.path.abspath('dubai_property.duckdb'))

con.close()