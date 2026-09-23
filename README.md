# AURA XAU/USD Live Dashboard

A GitHub-ready Streamlit application styled after the supplied AURA Markets reference. The application focuses on one market, XAU/USD, and includes animated agent cards, a four-panel Plotly chart, automatic refresh, and a clear feed-status indicator.

## Important data behavior

- With `TWELVE_DATA_API_KEY` configured, the app requests XAU/USD one-minute candles from Twelve Data.
- Without a key, or if the provider request fails, the app is clearly labelled `DEMO` or `DEMO/FALLBACK`.
- Provider availability, latency, commodity entitlement, and limits depend on the selected API plan.
- The app is analysis and monitoring software only. It does not execute trades or provide personalized financial advice.

## Deploy directly from GitHub to Streamlit Community Cloud

1. Create a new GitHub repository, for example `aura-xau-dashboard`.
2. Upload every file and folder from this ZIP. Keep `.streamlit/config.toml` in the repository.
3. Do not upload a real `.streamlit/secrets.toml` file.
4. Open https://share.streamlit.io and sign in with GitHub.
5. Select **Create app** and choose the repository.
6. Set the main file path to `streamlit_app.py`.
7. Open **Advanced settings** and add this secret:

```toml
TWELVE_DATA_API_KEY = "your_actual_api_key"
```

8. Deploy. Streamlit will install `requirements.txt` automatically.

## Run locally if required

```powershell
python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".\.venv\Scripts\python.exe" -m streamlit run streamlit_app.py
```

## Project structure

```text
streamlit_app.py
market_data.py
indicators.py
charts.py
requirements.txt
README.md
.gitignore
.streamlit/
  config.toml
  secrets.toml.example
```
