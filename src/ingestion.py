import requests
import pandas as pd
import os
import json
import numpy as np
pd.set_option('future.no_silent_downcasting', True)

# Fetch data from Open Food Facts for Ireland
def fetch_ireland_food_data(category="dairy"):
    print(f"Starting ingestion for category: {category}...")
    
    # API URL with specific filters for Ireland
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "action": "process",
        "tagtype_0": "countries",
        "tag_contains_0": "contains",
        "tag_0": "ireland",
        "tagtype_1": "categories",
        "tag_contains_1": "contains",
        "tag_1": category,
        "json": "true",
        "page_size": 100,
        "page": 1
    }
    
    # Custom User-Agent (Mandatory by OFF API terms)
    headers = {
        "User-Agent": "IrelandHealthMonitor - Version 1.0 - Educational Project"
    }

    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        
        if not products:
            print("No products found.")
            return

        df = pd.DataFrame(products)

        # Convert dictionaries and lists to strings for the Bronze layer (avoid ArrowInvalid errors)
        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
                df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else str(x))
            
            if df[col].dtype == 'object':
                # Convert lists/dicts to JSON strings, and everything else to plain string
                df[col] = df[col].apply(
                    lambda x: json.dumps(x) if isinstance(x, (dict, list)) else str(x)
                )
        
        # Replaces 'None' string or empty values with actual NaN for Parquet
        df = df.replace(['None', 'nan', ''], np.nan)
        
        # Save to Bronze
        output_path = "data/bronze/ireland_products_raw.parquet"
        df.to_parquet(output_path, index=False)
        print(f"Success! {len(df)} products saved to {output_path}")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    fetch_ireland_food_data()