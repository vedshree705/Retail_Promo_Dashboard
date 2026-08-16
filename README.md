# Retail Promotion Decision Support System — Starter Code

## Setup
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Download `train.csv` from the Rossmann Store Sales dataset on Kaggle,
   put it in this folder.
3. Get a free Gemini API key from https://ai.google.dev and set it:
   ```
   export GEMINI_API_KEY="your_key_here"
   ```

## Run order
```
python data_prep.py      # cleans CSV -> builds retail_data.db
python kpi_engine.py      # sanity-check: prints KPIs for store 1
python llm_layer.py       # sanity-check: prints a sample AI recommendation
streamlit run app.py      # launches the dashboard in your browser
```

## File overview
- `data_prep.py` — cleans raw sales data, loads it into SQLite
- `kpi_engine.py` — calculates sales lift and other promotion KPIs
- `llm_layer.py` — sends KPIs to Gemini, returns a plain-language recommendation
- `app.py` — Streamlit dashboard tying everything together
