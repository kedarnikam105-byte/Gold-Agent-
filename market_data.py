from datetime import datetime
import pandas as pd, yfinance as yf
def _last(symbol):
 h=yf.Ticker(symbol).history(period="5d",interval="1h"); return None if h.empty else round(float(h["Close"].dropna().iloc[-1]),2)
def get_gold_data():
 try:
  h=yf.Ticker("GC=F").history(period="5d",interval="1h");
  if h.empty: raise RuntimeError("No Gold data returned")
  c=h["Close"].dropna(); current=float(c.iloc[-1]); previous=float(c.iloc[-2]); s20=c.rolling(20).mean().iloc[-1] if len(c)>=20 else current; s50=c.rolling(50).mean().iloc[-1] if len(c)>=50 else current; d=c.diff(); g=d.clip(lower=0).rolling(14).mean(); l=(-d.clip(upper=0)).rolling(14).mean(); rs=g/l.replace(0,pd.NA); rsi=100-(100/(1+rs.iloc[-1])) if len(c)>=14 and not pd.isna(rs.iloc[-1]) else 50
  chart=[{"time":i.isoformat(),"open":float(r.Open),"high":float(r.High),"low":float(r.Low),"close":float(r.Close)} for i,r in h.tail(80).iterrows()]
  return {"symbol":"XAUUSD (GC=F)","current_price":round(current,2),"change_1d_pct":round((current-previous)/previous*100,2),"sma_20":round(float(s20),2),"sma_50":round(float(s50),2),"rsi_14":round(float(rsi),1),"high_24h":round(float(h.tail(24)["High"].max()),2),"low_24h":round(float(h.tail(24)["Low"].min()),2),"dxy":_last("DX-Y.NYB"),"us10y":_last("^TNX"),"chart":chart,"timestamp":datetime.now().isoformat(),"sources":{"gold":True,"dxy":True,"yield":True,"news":False,"calendar":False}}
 except Exception as e: return {"current_price":0,"change_1d_pct":0,"chart":[],"error":str(e),"timestamp":datetime.now().isoformat(),"sources":{}}
