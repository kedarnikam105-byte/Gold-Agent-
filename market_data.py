from datetime import datetime

import pandas as pd
import yfinance as yf


def get_gold_data():
    """Fetch recent Gold Futures data from Yahoo Finance."""
    try:
        hist = yf.Ticker("GC=F").history(period="5d", interval="1h")
        if hist.empty:
            raise RuntimeError("Yahoo Finance returned no Gold Futures data.")

        close = hist["Close"].dropna()
        current = float(close.iloc[-1])
        previous = float(close.iloc[-2]) if len(close) > 1 else current
        sma20 = close.rolling(20).mean().iloc[-1] if len(close) >= 20 else current
        sma50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else current

        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss.replace(0, pd.NA)
        rsi = 100 - (100 / (1 + rs.iloc[-1])) if len(close) >= 14 and not pd.isna(rs.iloc[-1]) else 50
        recent = hist.tail(min(24, len(hist)))

        return {
            "symbol": "XAUUSD (GC=F)",
            "current_price": round(current, 2),
            "change_1d_pct": round(((current - previous) / previous) * 100, 2) if previous else 0,
            "sma_20": round(float(sma20), 2),
            "sma_50": round(float(sma50), 2),
            "rsi_14": round(float(rsi), 1),
            "high_24h": round(float(recent["High"].max()), 2),
            "low_24h": round(float(recent["Low"].min()), 2),
            "volume": int(recent["Volume"].iloc[-1]) if "Volume" in recent else 0,
            "timestamp": datetime.now().isoformat(),
            "source": "Yahoo Finance Gold Futures GC=F",
        }
    except Exception as exc:
        return {
            "symbol": "XAUUSD",
            "current_price": 0,
            "change_1d_pct": 0,
            "error": str(exc),
            "timestamp": datetime.now().isoformat(),
        }
