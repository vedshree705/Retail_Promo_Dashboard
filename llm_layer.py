"""
Step 3: Send KPI data to an LLM and get back a plain-language recommendation.
Set your API key as an environment variable before running:
  export GEMINI_API_KEY="your_key_here"
"""

import os
import requests

API_KEY = os.environ.get("GEMINI_API_KEY")
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"

def get_recommendation(kpi_dict):
    prompt = f"""
    You are a retail business advisor. Based on this promotion data, give a
    2-3 sentence, plain-language recommendation for a small store owner:

    {kpi_dict}
    """

    response = requests.post(
        f"{URL}?key={API_KEY}",
        json={"contents": [{"parts": [{"text": prompt}]}]},
    )
    result = response.json()

    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        print("RAW RESPONSE:", result)
        return "Could not generate a recommendation. Check your API key and response format."

if __name__ == "__main__":
    sample_kpi = {
        "store_id": 1,
        "avg_sales_promo": 7200,
        "avg_sales_no_promo": 6100,
        "sales_lift_pct": 18.0,
        "promo_days": 120,
        "total_days": 365,
    }

    print(get_recommendation(sample_kpi))