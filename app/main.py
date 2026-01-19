import streamlit as st
import duckdb
import pandas as pd

# Connect to DuckDB with caching to improve performance
@st.cache_resource
def get_connection():
    # Using read_only=True to avoid locking issues with the processing script
    db_path = "database/ireland_health.db"
    connection = duckdb.connect(db_path, read_only=True)
    return connection

def main():
    st.set_page_config(page_title="Ireland Health Monitor", layout="wide")
    st.title("Ireland Food Health Dashboard")
    st.markdown("Analyzing nutritional quality of products in the Irish market.")

    con = get_connection()

    # Sidebar Filters
    st.sidebar.header("Filters")
    # Fetching unique grades from the Silver layer for the filter
    grades = con.execute("SELECT DISTINCT nutriscore_grade FROM stg_products ORDER BY nutriscore_grade").df()
    # print(grades.head())
    selected_grade = st.sidebar.multiselect("Select Nutri-Score Grade", options=grades['nutriscore_grade'].tolist())

    # We join Gold with Silver to allow filtering by individual product grades
    base_query = """
        SELECT 
            s.brands, 
            COUNT(*) as product_count,
            AVG(s.num_ingredients) as avg_ingredients
        FROM stg_products s
    """

    if selected_grade:
        # In a real app, you'd filter the gold table or join with silver
        # Format list for SQL: ('a', 'b')
        filter_str = "('" + "','".join(selected_grade) + "')"
        query = f"{base_query} WHERE s.nutriscore_grade IN {filter_str} GROUP BY s.brands ORDER BY product_count DESC"
    else:
        query = f"{base_query} GROUP BY s.brands ORDER BY product_count DESC"

    df_filtered = con.execute(query).df()

    st.subheader("Market Summary")
    col1, col2, col3 = st.columns(3)
    
    if not df_filtered.empty:
        # Total of products after filtering
        total_p = df_filtered['product_count'].sum()
        # Weighted average of ingredients based on products per brand
        avg_ing = (df_filtered['avg_ingredients'] * df_filtered['product_count']).sum() / total_p
        # Brand with most products in the current selection
        top_brand = df_filtered.sort_values(by='product_count', ascending=False).iloc[0]['brands']
        
        col1.metric("Selected Products", int(total_p))
        # col2.metric("Avg Ingredients", f"{avg_ing:.1f}")
        col3.metric("Lead Brand", top_brand)
    else:
        col1.metric("Selected Products", 0)
        # col2.metric("Avg Ingredients", 0)
        col3.metric("Lead Brand", "N/A")

    # Layout: Charts
    st.subheader("Brand Analysis based on Filters")
    if not df_filtered.empty:
        st.bar_chart(data=df_filtered, x="brands", y="product_count")
    else:
        st.warning("No products found for the selected filters.")

    # Add context by showing specific products
    st.divider()
    st.subheader("Product Inspector")
    st.markdown("Select a brand to see their products and health scores.")

    if not df_filtered.empty:
        available_brands = sorted(df_filtered['brands'].unique())
        
        selected_brand = st.selectbox(
            "Pick a Brand to inspect:", 
            options=available_brands,
            key='brand_selector',
        )
        
        print(f"DEBUG - Selected brand: {selected_brand}")
        
        # Query the Silver layer for details of that specific brand
        product_details_query = """
            SELECT 
                product_name, 
                nutriscore_grade, 
                num_ingredients,
                url
            FROM stg_products 
            WHERE brands = ?
            ORDER BY num_ingredients ASC
        """
        df_details = con.execute(product_details_query, [selected_brand]).df()
        print(f"DEBUG - Rows returned: {len(df_details)}")
        
        # Display as a clean table
        st.dataframe(
            df_details, 
            column_config={
                "url": st.column_config.LinkColumn("Product Link"),
                "num_ingredients": "Ingredients Count",
                "nutriscore_grade": "Grade",
                "product_name": "Product Name",
            },
            width="stretch",
            hide_index=True
        )
    else:
        st.info("Select filters to see product details.")

if __name__ == "__main__":
    main()