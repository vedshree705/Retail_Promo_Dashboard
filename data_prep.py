"""
Step 1: Clean the raw Rossmann CSVs and load them into a local SQLite database.
Run this once: python data_prep.py
Needs BOTH train.csv and store.csv in this folder.
"""

import pandas as pd
import sqlite3

SALES_CSV = "train.csv"
STORE_CSV = "store.csv"
DB_FILE = "retail_data.db"

def clean_sales(path):
    df = pd.read_csv(path, low_memory=False)
    df = df[["Store", "Date", "Sales", "Customers", "Promo", "Open"]]
    df = df[df["Open"] == 1]
    df = df.dropna()
    df["Date"] = pd.to_datetime(df["Date"])
    return df

def clean_store(path):
    df = pd.read_csv(path)
    df = df[["Store", "StoreType", "Assortment", "CompetitionDistance", "Promo2"]]
    # Fill missing competition distance with the median instead of dropping stores
    df["CompetitionDistance"] = df["CompetitionDistance"].fillna(df["CompetitionDistance"].median())
    return df

def save_to_sqlite(sales_df, store_df, db_file):
    conn = sqlite3.connect(db_file)
    sales_df.to_sql("sales", conn, if_exists="replace", index=False)
    store_df.to_sql("stores", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Saved {len(sales_df)} sales rows and {len(store_df)} store records to {db_file}")

if __name__ == "__main__":
    sales_df = clean_sales(SALES_CSV)
    store_df = clean_store(STORE_CSV)
    save_to_sqlite(sales_df, store_df, DB_FILE)
