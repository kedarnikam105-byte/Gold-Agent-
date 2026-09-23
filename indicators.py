from __future__ import annotations
import numpy as np
import pandas as pd


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d['EMA20'] = d['Close'].ewm(span=20, adjust=False).mean()
    d['EMA50'] = d['Close'].ewm(span=50, adjust=False).mean()
    delta = d['Close'].diff()
    gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    d['RSI14'] = (100 - 100 / (1 + rs)).fillna(50)
    d['MACD'] = d['Close'].ewm(span=12, adjust=False).mean() - d['Close'].ewm(span=26, adjust=False).mean()
    d['MACD_SIGNAL'] = d['MACD'].ewm(span=9, adjust=False).mean()
    d['MACD_HIST'] = d['MACD'] - d['MACD_SIGNAL']
    returns = d['Close'].pct_change()
    d['VOL20'] = returns.rolling(20).std() * np.sqrt(252 * 24 * 60) * 100
    return d


def market_snapshot(d: pd.DataFrame) -> dict:
    last = float(d['Close'].iloc[-1])
    previous = float(d['Close'].iloc[-2])
    change = last - previous
    pct = change / previous * 100 if previous else 0.0
    rsi = float(d['RSI14'].iloc[-1])
    macd = float(d['MACD'].iloc[-1])
    signal = float(d['MACD_SIGNAL'].iloc[-1])
    ema20 = float(d['EMA20'].iloc[-1])
    ema50 = float(d['EMA50'].iloc[-1])
    trend = 'Above both EMAs' if last > ema20 > ema50 else 'Below both EMAs' if last < ema20 < ema50 else 'Mixed EMA structure'
    momentum = 'Elevated' if rsi >= 70 else 'Soft' if rsi <= 30 else 'Neutral range'
    volatility = float(d['VOL20'].iloc[-1]) if pd.notna(d['VOL20'].iloc[-1]) else 0.0
    return {'last': last, 'change': change, 'pct': pct, 'rsi': rsi, 'macd': macd, 'macd_signal': signal, 'ema20': ema20, 'ema50': ema50, 'trend': trend, 'momentum': momentum, 'volatility': volatility}
