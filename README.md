# Gold Command Center

A dark Streamlit dashboard with four Gemini-powered Gold analysts and one Chief Officer that produces a single validated Buy, Sell, or Hold signal.

## Project structure

```text
gold-command-center/
├── app.py
├── market_data.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
└── agents/
    ├── __init__.py
    ├── base.py
    └── analysts.py
```

## Local setup

```bash
python -m venv .venv
```

Activate the virtual environment, then run:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example` and add your private Gemini key:

```env
GEMINI_API_KEY=your_private_key
GEMINI_MODEL=gemini-flash-latest
```

Start the app:

```bash
streamlit run app.py
```

## Streamlit Community Cloud

Deploy `app.py` from the repository and add these values in the Streamlit Secrets settings:

```toml
GEMINI_API_KEY = "your_private_key"
GEMINI_MODEL = "gemini-flash-latest"
```

Never commit `.env` or `.streamlit/secrets.toml`.

## Signal validation

The Chief Officer receives all four specialist reports. A Buy signal requires `Stop Loss < Entry < Take Profit`. A Sell signal requires `Take Profit < Entry < Stop Loss`. Low-confidence or invalid setups are converted to Hold with no trade levels.

## Important

For education and paper trading only. This application is not financial advice and does not guarantee outcomes.
