import duckdb

def create_silver_layer(con, db_path):
    # Clean and type raw data from Bronze
    print("Creating Silver Layer...")

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
    print("Silver layer (stg_products) created!")

    # Check the result of stg_products
    result = con.execute("SELECT COUNT(*) FROM stg_products").fetchone()
    print(f"Silver Table created with {result[0]} records at {db_path}")

def create_gold_layer(con, db_path):
    # Create business metrics for the dashboard
    print("Creating Silver Layer...")

    query = """
    CREATE OR REPLACE TABLE gold_brand_metrics AS
    SELECT
        brands,
        COUNT(*) as total_products,
        AVG(num_ingredients) as avg_ingredients,
        MODE(nutriscore_grade) as common_nutriscore
    FROM stg_products
    GROUP BY brands;
    """
    con.execute(query)
    print("Gold layer (gold_brand_metrics) created!")

    # Check the result of gold_brand_metrics
    result = con.execute("SELECT COUNT(*) FROM gold_brand_metrics").fetchone()
    print(f"Gold Table created with {result[0]} records at {db_path}")

def run_pipeline():
    # Main orchestrator
    db_path = "database/ireland_health.db"
    con = duckdb.connect(db_path)
    try:
        create_silver_layer(con, db_path)
        create_gold_layer(con, db_path)
    finally:
        con.close()
        print("Pipeline execution finished.")

if __name__ == "__main__":
    run_pipeline()