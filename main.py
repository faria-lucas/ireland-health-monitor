import pandas as pd
from pathlib import Path
import duckdb

# path = Path("data/bronze/ireland_products_raw.parquet").resolve()

# df = pd.read_parquet(path)

# print("df", df.head(5))
# print("df.columns", df.columns)
# df.to_csv("ireland_products_raw.csv")

# Quick check on Silver table
con = duckdb.connect("database/ireland_health.db"), # read_only=True)
print(con.execute("SELECT * FROM stg_products LIMIT 5").df())
con.close()