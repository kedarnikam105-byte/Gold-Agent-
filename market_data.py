from dataclasses import dataclass
from datetime import datetime,timezone
import os,requests,numpy as np,pandas as pd
@dataclass
class Feed: candles:pd.DataFrame; mode:str; source:str; updated_at:datetime; message:str=''
def secret(n):
 try:
  import streamlit as st
  return str(st.secrets.get(n,'')).strip()
 except:return os.getenv(n,'').strip()
def demo(n):
 rng=np.random.default_rng(42); dates=pd.date_range(end=datetime.now(timezone.utc),periods=n,freq='min'); close=2675+np.cumsum(rng.normal(.1,3.2,n)); op=np.r_[close[0],close[:-1]]+rng.normal(0,.8,n); hi=np.maximum(op,close)+rng.uniform(.5,3,n); lo=np.minimum(op,close)-rng.uniform(.5,3,n); return pd.DataFrame({'Date':dates,'Open':op,'High':hi,'Low':lo,'Close':close,'Volume':rng.integers(500,4500,n)})
def get_gold_data(interval='1min',outputsize=220):
 key=secret('TWELVE_DATA_API_KEY')
 if not key:return Feed(demo(outputsize),'DEMO','Built-in sample data',datetime.now(timezone.utc),'No provider key')
 try:
  j=requests.get('https://api.twelvedata.com/time_series',params={'symbol':'XAU/USD','interval':interval,'outputsize':outputsize,'apikey':key},timeout=20).json()
  if 'values' not in j:raise RuntimeError(j.get('message','No values'))
  rows=[(pd.to_datetime(v['datetime'],utc=True),float(v['open']),float(v['high']),float(v['low']),float(v['close']),float(v.get('volume') or 0)) for v in reversed(j['values'])]; return Feed(pd.DataFrame(rows,columns=['Date','Open','High','Low','Close','Volume']),'LIVE/API','Twelve Data · XAU/USD',datetime.now(timezone.utc))
 except Exception as e:return Feed(demo(outputsize),'DEMO/FALLBACK','Built-in sample data',datetime.now(timezone.utc),str(e))
