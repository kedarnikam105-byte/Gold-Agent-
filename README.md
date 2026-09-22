# Gold Command AI Specialist Desk

Futuristic Streamlit dashboard with a polled 1-minute Gold Futures chart, four specialist Gemini agents, and one Chief Officer signal.

## Streamlit secrets
```toml
GEMINI_API_KEY = "your_private_key"
GEMINI_MODEL = "gemini-flash-latest"
```

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

Yahoo Finance data is for personal research and is polled rather than exchange-grade streaming. The app is for education and paper trading only.
