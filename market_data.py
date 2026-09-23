from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np
import pandas as pd
import requests


@dataclass
class FeedResult:
    candles: pd.DataFrame
    mode: str
    source: str
    updated_at: datetime
    message: str = ""


def _secret(name: str, default: str = "") -> str:
    try:
        import streamlit as st
        if name in st.secrets:
            return str(st.secrets[name]).strip()
    except Exception:
        pass
    return os.getenv(name, default).strip()


def demo_gold_data(periods: int = 180) -> pd.DataFrame:
    """Deterministic sample data, always labelled DEMO by the UI."""
    rng = np.random.default_rng(42)
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    dates = pd.date_range(end=now, periods=periods, freq='min')
    close = 2675 + np.cumsum(rng.normal(0.18, 3.8, periods))
    open_ = np.r_[close[0], close[:-1]] + rng.normal(0, 1.1, periods)
    high = np.maximum(open_, close) + rng.uniform(0.8, 4.5, periods)
    low = np.minimum(open_, close) - rng.uniform(0.8, 4.5, periods)
    volume = rng.integers(700, 5200, periods)
    return pd.DataFrame({'Date': dates, 'Open': open_, 'High': high, 'Low': low, 'Close': close, 'Volume': volume})


def fetch_twelve_data(interval: str = '1min', outputsize: int = 180) -> FeedResult:
    key = _secret('TWELVE_DATA_API_KEY')
    if not key:
        return FeedResult(demo_gold_data(outputsize), 'DEMO', 'Built-in sample feed', datetime.now(timezone.utc), 'Add TWELVE_DATA_API_KEY in Streamlit secrets for provider data.')

    response = requests.get(
        'https://api.twelvedata.com/time_series',
        params={'symbol': 'XAU/USD', 'interval': interval, 'outputsize': outputsize, 'format': 'JSON', 'apikey': key},
        timeout=20,
    )
    response.raise_for_status()
    payload: dict[str, Any] = response.json()
    if 'values' not in payload:
        raise RuntimeError(payload.get('message') or payload.get('status') or 'The gold provider returned no candle data.')

    rows = []
    for item in reversed(payload['values']):
        rows.append({
            'Date': pd.to_datetime(item['datetime'], utc=True),
            'Open': float(item['open']),
            'High': float(item['high']),
            'Low': float(item['low']),
            'Close': float(item['close']),
            'Volume': float(item.get('volume') or 0),
        })
    frame = pd.DataFrame(rows).dropna().sort_values('Date')
    return FeedResult(frame, 'LIVE/API', 'Twelve Data · XAU/USD', datetime.now(timezone.utc), 'Provider timestamps and latency depend on the account plan.')


def get_gold_data(interval: str = '1min', outputsize: int = 180) -> FeedResult:
    try:
        return fetch_twelve_data(interval, outputsize)
    except Exception as exc:
        return FeedResult(demo_gold_data(outputsize), 'DEMO/FALLBACK', 'Built-in sample feed', datetime.now(timezone.utc), f'Provider error: {exc}')
