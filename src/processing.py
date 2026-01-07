import duckdb
import os

# Task: Transform Bronze Parquet into Silver Analytical Table
def transform_data():
    # Connect to the local DuckDB file
    db_path = "database/ireland_health.db"
    con = duckdb.connect(db_path)
    
    print("Creating Silver Layer...")

    # SQL Task: Clean types and handle the 'ingredients_n' as you suggested
    # We use TRY_CAST to return NULL if the string isn't a valid number
    query = """
    CREATE OR REPLACE TABLE stg_products AS
    SELECT
        product_name,
        brands,
        categories,
        nutriscore_grade,
        TRY_CAST(ingredients_n AS INTEGER) as num_ingredients,
        TRY_CAST(ecoscore_grade AS VARCHAR) as ecoscore_grade,
        url
    FROM read_parquet('data/bronze/ireland_products_raw.parquet')
    WHERE product_name IS NOT NULL;
    """
    
    con.execute(query)
    
    # Check the result
    result = con.execute("SELECT COUNT(*) FROM stg_products").fetchone()
    print(f"Silver Table created with {result[0]} records at {db_path}")
    con.close()

if __name__ == "__main__":
    transform_data()