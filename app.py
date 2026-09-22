import json, os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
import pandas as pd, plotly.graph_objects as go, streamlit as st
from dotenv import load_dotenv
from agents.analysts import create_technical_agent,create_fundamental_agent,create_sentiment_agent,create_liquidity_agent,create_chief_officer
from market_data import get_market_data
st.set_page_config(page_title="Gold Command AI Desk",page_icon="🥇",layout="wide",initial_sidebar_state="expanded");load_dotenv()
H=Path("logs/history.json");H.parent.mkdir(exist_ok=True)
if "agents" not in st.session_state:st.session_state.agents={"technical":create_technical_agent(),"fundamental":create_fundamental_agent(),"sentiment":create_sentiment_agent(),"liquidity":create_liquidity_agent(),"chief":create_chief_officer()}
if "market" not in st.session_state:st.session_state.market=get_market_data()
if "selected" not in st.session_state:st.session_state.selected=None
if "logs" not in st.session_state:st.session_state.logs=[]
def log(msg):st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
def validate(r):
 a=r.get("suggested_action","Hold");c=int(r.get("confidence",0) or 0);e,s,t=r.get("entry"),r.get("stop_loss"),r.get("take_profit");n=all(isinstance(x,(int,float)) for x in(e,s,t));ok=(a=="Buy" and n and s<e<t)or(a=="Sell" and n and t<e<s)
 if a=="Hold" or c<60 or not ok:r.update(suggested_action="Hold",bias="Neutral",entry=None,stop_loss=None,take_profit=None)
 return r
def analyze(retry=False):
 m={k:v for k,v in st.session_state.market.items() if k!="candles"};keys=["technical","fundamental","sentiment","liquidity"]
 todo=[k for k in keys if not retry or not(st.session_state.agents[k].last_report or{}).get("success")]
 with ThreadPoolExecutor(max_workers=4) as ex:results=dict(zip(todo,ex.map(lambda k:st.session_state.agents[k].analyze(m),todo)))
 reports=[]
 for k in keys:
  r=results.get(k) or st.session_state.agents[k].last_report;reports.append(r);log(f"{k.title()}: {'complete' if r and r.get('success') else 'retry required'}")
 if sum(bool(r and r.get("success")) for r in reports)>=3:
  chief=st.session_state.agents["chief"].analyze(m,"SPECIALIST REPORTS:\n"+json.dumps(reports,indent=2));chief=validate(chief) if chief.get("success") else chief
 else:chief={"agent":"Chief Officer","bias":"Neutral","confidence":0,"summary":"HOLD: insufficient completed specialist reports.","key_points":[],"suggested_action":"Hold","entry":None,"stop_loss":None,"take_profit":None,"reasoning":"Retry failed agents before creating a setup.","success":False}
 st.session_state.agents["chief"].last_report=chief;log(f"Chief signal: {chief.get('suggested_action','Hold')}")
 try:h=json.loads(H.read_text()) if H.exists() else[]
 except:h=[]
 h.append({"time":datetime.now().isoformat(),"reports":reports+[chief]});H.write_text(json.dumps(h[-30:],indent=2))
st.markdown('''<style>
.stApp{background:radial-gradient(circle at 5% 50%,#0b5060 0,#071a2a 13%,#030d17 35%);color:#dffaff}.block-container{max-width:1500px;padding:1rem 1rem 2rem}section[data-testid="stSidebar"]{background:linear-gradient(90deg,#082a38,#061522);border-right:1px solid #20d9e5}h1,h2,h3{color:#c9f8ff!important;letter-spacing:.06em}.neon,.panel,.agent,.chief{background:linear-gradient(145deg,rgba(16,44,58,.94),rgba(5,21,34,.97));border:1px solid #2b6073;border-radius:15px;box-shadow:0 0 22px rgba(16,216,232,.10);padding:14px}.title{text-align:center;color:#aeeaf4;font-size:1.55rem;letter-spacing:.12em}.cyan{color:#53f3f2}.green{color:#5cffae}.gold{color:#ffe45c}.red{color:#ff6b76}.muted{color:#9ab8c5}.big{font-size:2.7rem;font-weight:900}.agent{min-height:220px}.chief{min-height:540px}.bot{width:145px;height:145px;margin:auto;border:2px solid #37eff4;border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:70px;box-shadow:0 0 25px #22dbe8}.stButton>button{background:linear-gradient(#17394c,#0b2232)!important;color:#dffaff!important;border:1px solid #39d9e6!important;border-radius:20px!important;font-weight:700!important}.stButton>button:hover{box-shadow:0 0 18px #27dce8!important}.stButton>button[kind="primary"]{background:linear-gradient(90deg,#176b79,#20bdc8)!important;color:white!important}.log{font-family:monospace;font-size:.78rem;color:#69e49d;text-align:center}.source{padding:10px;border-top:1px solid #245366;color:#8fb5c2}@media(max-width:900px){.chief{min-height:auto}.big{font-size:2rem}}
</style>''',unsafe_allow_html=True)
with st.sidebar:
 st.markdown("## ◉ GOLD COMMAND");page=st.radio("",["OVERVIEW","AI DESK","MARKET DATA","HISTORY","SETTINGS","SYSTEM INTEL"],label_visibility="collapsed");st.divider();st.caption("1-minute market polling • Multi-agent synthesis")
st.markdown('<div class="title">GOLD COMMAND – AI SPECIALIST DESK</div>',unsafe_allow_html=True)
if page in("OVERVIEW","AI DESK"):
 main,side=st.columns([3.35,1],gap="large")
 with main:
  m=st.session_state.market;st.markdown("### Live Gold (XAU/USD) 1-Min Candlestick Chart")
  if m.get("candles"):
   d=pd.DataFrame(m["candles"]);fig=go.Figure();fig.add_trace(go.Candlestick(x=d.time,open=d.open,high=d.high,low=d.low,close=d.close,increasing_line_color="#20e0e5",decreasing_line_color="#ff855e",name="1m"));fig.add_trace(go.Scatter(x=d.time,y=d.close.rolling(20).mean(),line=dict(color="#5ef1d0",width=1),name="SMA20"));fig.add_trace(go.Scatter(x=d.time,y=d.close.rolling(50).mean(),line=dict(color="#d6b28a",width=1),name="SMA50"));fig.update_layout(height=405,margin=dict(l=5,r=5,t=15,b=5),paper_bgcolor="#071827",plot_bgcolor="#071827",font_color="#b9dce5",xaxis_rangeslider_visible=False,legend=dict(orientation="h"));st.plotly_chart(fig,width="stretch")
  else:st.error("1-minute market candles are unavailable. Use Sync Data.")
  a,b,c,d=st.columns(4);a.metric("RSI 14",m.get("rsi_14","N/A"));b.metric("SMA 20",m.get("sma_20","N/A"));c.metric("SMA 50",m.get("sma_50","N/A"));d.metric("DXY",m.get("dxy","N/A"))
  x,y,z,w=st.columns(4)
  if x.button("ANALYZE MARKET",type="primary",width="stretch",disabled=not bool(os.getenv("GEMINI_API_KEY"))):
   with st.spinner("Orchestrating multi-agent analysis..."):analyze(False)
   st.rerun()
  if y.button("SYNC DATA",width="stretch"):st.session_state.market=get_market_data();log("1-minute market data synchronized");st.rerun()
  if z.button("RETRY ALL AGENTS",width="stretch"):
   with st.spinner("Retrying failed agents..."):analyze(True)
   st.rerun()
  if w.button("VIEW SYSTEM LOGS",width="stretch"):st.session_state.selected="logs"
  st.markdown("### AI SPECIALIST DESK");cols=st.columns(4);names={"technical":"TECHNICAL","fundamental":"FUNDAMENTAL","sentiment":"SENTIMENT","liquidity":"LIQUIDITY"}
  for col,(k,name) in zip(cols,names.items()):
   ag=st.session_state.agents[k];r=ag.last_report or{};confidence=r.get("confidence",0);color="green" if r.get("success") else "gold"
   col.markdown(f'<div class="agent"><b>{name}</b><h3>{r.get("bias","Waiting")}</h3><div class="{color}">{ag.status}</div><div class="big">{confidence}%</div><p class="muted">{r.get("summary","Awaiting analysis.")}</p></div>',unsafe_allow_html=True)
   if col.button("VIEW FULL REPORT",key=k,width="stretch",disabled=not bool(r)):st.session_state.selected=k;st.rerun()
  if st.session_state.selected=="logs":st.markdown("<div class='log'>"+"<br>".join(st.session_state.logs[-12:])+"</div>",unsafe_allow_html=True)
  elif st.session_state.selected in names:
   r=st.session_state.agents[st.session_state.selected].last_report;st.markdown(f"### {r.get('agent')} FULL REPORT");t1,t2,t3=st.tabs(["SUMMARY","KEY POINTS","REASONING"])
   with t1:st.write(r.get("summary"))
   with t2:
    for q in r.get("key_points",[]):st.write("•",q)
   with t3:st.write(r.get("reasoning"))
 with side:
  r=st.session_state.agents["chief"].last_report or{"suggested_action":"WAITING","confidence":0,"summary":"Run market analysis.","reasoning":"No signal yet."};fmt=lambda v:f"${v:,.2f}" if isinstance(v,(int,float)) else "WAITING"
  st.markdown(f'<div class="chief"><h3>CHIEF AGENT WORKSPACE</h3><div class="bot">◈</div><p class="cyan">CHIEF INTEL AGENT [COMMAND]</p><div class="big">{r.get("suggested_action","HOLD").upper()}</div><div class="green">SYSTEM SYNC: {sum(bool((st.session_state.agents[k].last_report or{{}}).get("success")) for k in names)*25}%</div><p class="muted">{r.get("summary","")}</p><hr><b>ENTRY</b><div>{fmt(r.get("entry"))}</div><b>STOP LOSS</b><div class="red">{fmt(r.get("stop_loss"))}</div><b>TAKE PROFIT</b><div class="green">{fmt(r.get("take_profit"))}</div><hr><div class="muted">Technical • Fundamental • Sentiment • Liquidity orchestration</div></div>',unsafe_allow_html=True)
  with st.expander("VIEW REASONING"):st.write(r.get("reasoning"))
 st.markdown(f'<div class="source">1-Min Gold: {m.get("data_status")} • DXY: {m.get("dxy","N/A")} • US10Y: {m.get("us10y","N/A")} • Updated: {m.get("updated","")[:19]}</div>',unsafe_allow_html=True)
elif page=="MARKET DATA":st.json({k:v for k,v in st.session_state.market.items() if k!="candles"})
elif page=="HISTORY":
 try:st.json(json.loads(H.read_text())[-10:] if H.exists() else[])
 except:st.info("No history")
elif page=="SETTINGS":st.info("Add GEMINI_API_KEY in Streamlit Secrets. Optional: GEMINI_MODEL.")
else:st.info("System intelligence dashboard. Use AI DESK to analyze the 1-minute Gold market.")
st.caption("Yahoo Finance data is polled, not exchange-grade streaming. Educational and paper-trading support only. Not financial advice.")
