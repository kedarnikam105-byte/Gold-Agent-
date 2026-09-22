from datetime import datetime
import pandas as pd, yfinance as yf
def _price(symbol):
 h=yf.Ticker(symbol).history(period="1d",interval="1m");return None if h.empty else round(float(h.Close.dropna().iloc[-1]),2)
def get_market_data():
 try:
  h=yf.Ticker("GC=F").history(period="1d",interval="1m",prepost=True).dropna(subset=["Close"])
  if h.empty:raise RuntimeError("No 1-minute candles returned")
  c=h.Close; cur=float(c.iloc[-1]); prev=float(c.iloc[-2]) if len(c)>1 else cur
  s20=c.rolling(20).mean().iloc[-1] if len(c)>=20 else cur;s50=c.rolling(50).mean().iloc[-1] if len(c)>=50 else cur
  d=c.diff();g=d.clip(lower=0).rolling(14).mean();l=(-d.clip(upper=0)).rolling(14).mean();rs=g/l.replace(0,pd.NA);rsi=100-(100/(1+rs.iloc[-1])) if len(c)>=14 and not pd.isna(rs.iloc[-1]) else 50
  candles=[{"time":i.isoformat(),"open":round(float(r.Open),2),"high":round(float(r.High),2),"low":round(float(r.Low),2),"close":round(float(r.Close),2)} for i,r in h.tail(180).iterrows()]
  return {"symbol":"GC=F","timeframe":"1m","current_price":round(cur,2),"change_pct":round((cur-prev)/prev*100,3),"rsi_14":round(float(rsi),1),"sma_20":round(float(s20),2),"sma_50":round(float(s50),2),"high":round(float(h.High.tail(60).max()),2),"low":round(float(h.Low.tail(60).min()),2),"dxy":_price("DX-Y.NYB"),"us10y":_price("^TNX"),"candles":candles,"updated":datetime.now().isoformat(),"data_status":"LIVE/POLLING"}
 except Exception as e:return {"current_price":0,"change_pct":0,"candles":[],"error":str(e),"updated":datetime.now().isoformat(),"data_status":"UNAVAILABLE"}
