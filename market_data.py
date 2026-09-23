from dataclasses import dataclass
from datetime import datetime,timezone
import os,requests,numpy as np,pandas as pd
@dataclass
class Feed: candles:pd.DataFrame; mode:str; source:str; updated_at:datetime; message:str=""
def key():
 try:
  import streamlit as st
  return str(st.secrets.get("TWELVE_DATA_API_KEY","")).strip()
 except Exception:return os.getenv("TWELVE_DATA_API_KEY","").strip()
def demo(n):
 g=np.random.default_rng(42); dt=pd.date_range(end=datetime.now(timezone.utc),periods=n,freq="min"); c=4280+np.cumsum(g.normal(.02,1.4,n)); o=np.r_[c[0],c[:-1]]+g.normal(0,.3,n); h=np.maximum(o,c)+g.uniform(.2,1.5,n); l=np.minimum(o,c)-g.uniform(.2,1.5,n)
 return pd.DataFrame({"Date":dt,"Open":o,"High":h,"Low":l,"Close":c,"Volume":g.integers(500,4000,n)})
def get_gold_data(interval="1min",n=220):
 k=key()
 if not k:return Feed(demo(n),"DEMO","Sample data",datetime.now(timezone.utc),"No API key")
 try:
  j=requests.get("https://api.twelvedata.com/time_series",params={"symbol":"XAU/USD","interval":interval,"outputsize":n,"apikey":k},timeout=20).json()
  if "values" not in j:raise RuntimeError(j.get("message","No values"))
  rows=[(pd.to_datetime(x["datetime"],utc=True),float(x["open"]),float(x["high"]),float(x["low"]),float(x["close"]),float(x.get("volume") or 0)) for x in reversed(j["values"])]
  return Feed(pd.DataFrame(rows,columns=["Date","Open","High","Low","Close","Volume"]),"LIVE/API","Twelve Data · XAU/USD",datetime.now(timezone.utc))
 except Exception as e:return Feed(demo(n),"DEMO/FALLBACK","Sample data",datetime.now(timezone.utc),str(e))
