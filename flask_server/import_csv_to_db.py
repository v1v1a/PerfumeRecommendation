import pandas as pd
from server_config import db, app
from sqlalchemy import Table, Column, Integer, String, Float, MetaData

# Read two CSV files
df_info = pd.read_csv("fragrance_info_with_description.csv")
df_rate = pd.read_csv("product_positive_rate.csv")

# Merge the two files by product_title
df_merged = pd.merge(
    df_info,
    df_rate,
    how="left",
    on="product_title"
)

# Fill unmatched positive_rate entries with default value 0.5 
df_merged["positive_rate"] = df_merged["positive_rate"].fillna(0.5)

# Rename columns to match database table schema
df_merged = df_merged.rename(columns={
    "product_title": "name"
})

# Select only the required fields
final_df = df_merged[[
    "name", "url", "main_accords", "longevity", "sillage",
    "gender", "suitable_season", "suitable_time", "description", "positive_rate"
]]

# Define the table schema
with app.app_context():
    metadata = MetaData()

    products_table = Table(
        'products', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String(255)),
        Column('url', String(500)),
        Column('main_accords', String(255)),
        Column('longevity', String(50)),
        Column('sillage', String(50)),
        Column('gender', String(50)),
        Column('suitable_season', String(100)),
        Column('suitable_time', String(100)),
        Column('description', String(2000)),
        Column('positive_rate', Float)
    )

    # Drop the table if it already exists, then recreate (to ensure consistent schema)
    products_table.drop(db.engine, checkfirst=True)
    metadata.create_all(db.engine)

    # Insert the final DataFrame into the database
    final_df.to_sql('products', db.engine, if_exists='append', index=False)

    print("Import successful! Combined fragrance_info and positive_rate have been inserted into the products table.")
