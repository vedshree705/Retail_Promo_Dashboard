"""
Step 2: Calculate promotion KPIs from the cleaned data.
"""

import sqlite3
import pandas as pd
from scipy import stats

DB_FILE = "retail_data.db"
DEFAULT_DISCOUNT_RATE = 0.15  # assumed avg promo discount; adjustable in the dashboard

def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM sales", conn)
    conn.close()
    return df

def load_store_info():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM stores", conn)
    conn.close()
    return df

def sales_lift(df, store_id):
    store_df = df[df["Store"] == store_id]
    promo_avg = store_df[store_df["Promo"] == 1]["Sales"].mean()
    no_promo_avg = store_df[store_df["Promo"] == 0]["Sales"].mean()
    if not no_promo_avg:
        return None
    return round((promo_avg - no_promo_avg) / no_promo_avg * 100, 2)

def significance_test(df, store_id):
    """
    Independent t-test: is the promo vs no-promo sales difference statistically
    real, or could it just be random day-to-day noise? p < 0.05 = likely real.
    """
    store_df = df[df["Store"] == store_id]
    promo_sales = store_df[store_df["Promo"] == 1]["Sales"]
    no_promo_sales = store_df[store_df["Promo"] == 0]["Sales"]

    if len(promo_sales) < 2 or len(no_promo_sales) < 2:
        return {"p_value": None, "significant": False}

    _, p_value = stats.ttest_ind(promo_sales, no_promo_sales, equal_var=False)
    return {"p_value": round(p_value, 4), "significant": p_value < 0.05}

def promo_roi(df, store_id, discount_rate=DEFAULT_DISCOUNT_RATE):
    """
    Estimated ROI of running promotions, since the dataset has no actual discount
    cost column. discount_rate is the assumed average % off during promo days.

    Extra revenue = (promo sales - what it would have made at the no-promo average)
    Estimated cost = discount_rate * total promo revenue
    ROI = (extra revenue - cost) / cost
    """
    store_df = df[df["Store"] == store_id]
    promo_df = store_df[store_df["Promo"] == 1]
    no_promo_avg = store_df[store_df["Promo"] == 0]["Sales"].mean()

    if not no_promo_avg or promo_df.empty:
        return None

    extra_revenue = (promo_df["Sales"] - no_promo_avg).sum()
    estimated_cost = promo_df["Sales"].sum() * discount_rate

    if estimated_cost == 0:
        return None

    return round((extra_revenue - estimated_cost) / estimated_cost * 100, 2)

def promo_summary(df, store_id, discount_rate=DEFAULT_DISCOUNT_RATE):
    """Returns a dict of KPIs for one store — feed this to the LLM layer."""
    store_df = df[df["Store"] == store_id]
    sig = significance_test(df, store_id)
    return {
        "store_id": store_id,
        "avg_sales_promo": round(store_df[store_df["Promo"] == 1]["Sales"].mean(), 2),
        "avg_sales_no_promo": round(store_df[store_df["Promo"] == 0]["Sales"].mean(), 2),
        "sales_lift_pct": sales_lift(df, store_id),
        "roi_pct": promo_roi(df, store_id, discount_rate),
        "p_value": sig["p_value"],
        "statistically_significant": sig["significant"],
        "promo_days": int(store_df["Promo"].sum()),
        "total_days": len(store_df),
    }

def store_type_summary(df, store_info):
    """
    The dataset has no product-level data, so this segments promotion performance
    by store type (A/B/C/D) instead — the closest real diagnostic cut available.
    """
    merged = df.merge(store_info[["Store", "StoreType", "Assortment"]], on="Store", how="left")
    rows = []
    for store_type, group in merged.groupby("StoreType"):
        promo_avg = group[group["Promo"] == 1]["Sales"].mean()
        no_promo_avg = group[group["Promo"] == 0]["Sales"].mean()
        lift = round((promo_avg - no_promo_avg) / no_promo_avg * 100, 2) if no_promo_avg else None
        rows.append({
            "store_type": store_type,
            "avg_sales_promo": round(promo_avg, 2),
            "avg_sales_no_promo": round(no_promo_avg, 2),
            "sales_lift_pct": lift,
            "num_stores": group["Store"].nunique(),
        })
    return pd.DataFrame(rows).sort_values("sales_lift_pct", ascending=False)

if __name__ == "__main__":
    df = load_data()
    print(promo_summary(df, store_id=1))
