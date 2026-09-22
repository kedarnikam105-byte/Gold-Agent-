import json, os
from datetime import datetime
from pathlib import Path
import pandas as pd, plotly.graph_objects as go, streamlit as st
from streamlit_autorefresh import st_autorefresh
from dotenv import load_dotenv
from agents.analysts import create_technical_agent,create_fundamental_agent,create_sentiment_agent,create_liquidity_agent,create_chief_officer
from market_data import get_market_data
st.set_page_config(page_title="Gold Command AI Desk",page_icon="🥇",layout="wide",initial_sidebar_state="expanded");load_dotenv()
H=Path("logs/history.json");H.parent.mkdir(exist_ok=True)
if "agents" not in st.session_state:st.session_state.agents={"technical":create_technical_agent(),"fundamental":create_fundamental_agent(),"sentiment":create_sentiment_agent(),"liquidity":create_liquidity_agent(),"chief":create_chief_officer()}
if "market" not in st.session_state:st.session_state.market=get_market_data()
if "selected" not in st.session_state:st.session_state.selected=None
if "logs" not in st.session_state:st.session_state.logs=[]
if "auto_refresh" not in st.session_state:st.session_state.auto_refresh=True
refresh_count=st_autorefresh(interval=15000,limit=None,key="market_auto_refresh") if st.session_state.auto_refresh else 0
if st.session_state.auto_refresh and refresh_count>0:
 fresh=get_market_data()
 if fresh.get("candles"):st.session_state.market=fresh
def log(msg):st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
def validate(r):
 a=r.get("suggested_action","Hold");c=int(r.get("confidence",0) or 0);e,s,t=r.get("entry"),r.get("stop_loss"),r.get("take_profit");n=all(isinstance(x,(int,float)) for x in(e,s,t));ok=(a=="Buy" and n and s<e<t)or(a=="Sell" and n and t<e<s)
 if a=="Hold" or c<60 or not ok:r.update(suggested_action="Hold",bias="Neutral",entry=None,stop_loss=None,take_profit=None)
 return r
def analyze(retry=False):
 m={k:v for k,v in st.session_state.market.items() if k!="candles"};keys=["technical","fundamental","sentiment","liquidity"]
 reports=[]
 # Streamlit session state is not thread-safe. Run agents sequentially to avoid KeyError.
 for k in keys:
  agent=st.session_state.agents[k]
  if retry and agent.last_report and agent.last_report.get("success"):
   r=agent.last_report
  else:
   r=agent.analyze(m)
  reports.append(r);log(f"{k.title()}: {'complete' if r and r.get('success') else 'retry required'}")
 if sum(bool(r and r.get("success")) for r in reports)>=3:
  chief=st.session_state.agents["chief"].analyze(m,"SPECIALIST REPORTS:\n"+json.dumps(reports,indent=2));chief=validate(chief) if chief.get("success") else chief
 else:chief={"agent":"Chief Officer","bias":"Neutral","confidence":0,"summary":"HOLD: insufficient completed specialist reports.","key_points":[],"suggested_action":"Hold","entry":None,"stop_loss":None,"take_profit":None,"reasoning":"Retry failed agents before creating a setup.","success":False}
 st.session_state.agents["chief"].last_report=chief;log(f"Chief signal: {chief.get('suggested_action','Hold')}")
 try:h=json.loads(H.read_text()) if H.exists() else[]
 except:h=[]
 h.append({"time":datetime.now().isoformat(),"reports":reports+[chief]});H.write_text(json.dumps(h[-30:],indent=2))
st.markdown('''<style>
:root{--cyan:#45edf3;--cyan2:#17b9c8;--bg:#020c16;--panel:#0a1c2a;--line:#2c6070;--text:#d7f6fb;--muted:#8babb7}
html,body,[class*="css"]{font-family:Inter,Segoe UI,sans-serif}.stApp{background:radial-gradient(circle at -8% 50%,#0e8793 0,#064353 13%,#031825 28%,#020b14 55%);color:var(--text)}
[data-testid="stHeader"]{background:transparent;height:0}[data-testid="stToolbar"]{display:none}.block-container{max-width:1540px;padding:12px 18px 24px!important}
section[data-testid="stSidebar"]{width:235px!important;background:radial-gradient(circle at -35% 48%,#16a8b8 0,#075361 25%,#041b29 55%,#03111d 100%);border-right:1px solid #2dcbd3;box-shadow:12px 0 40px rgba(0,220,235,.12)}
section[data-testid="stSidebar"]>div{padding-top:78px}section[data-testid="stSidebar"] [role="radiogroup"] label{padding:11px 8px;border-radius:8px;color:#9eb8c2}section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){color:#dfffff;background:linear-gradient(90deg,rgba(31,229,239,.27),transparent);box-shadow:inset 3px 0 #45edf3,0 0 18px rgba(69,237,243,.18)}
h1,h2,h3{color:#d8fbff!important}.title{text-align:center;color:#b9e9ef;font-size:1.62rem;letter-spacing:.12em;padding:4px 0 14px;border-bottom:1px solid rgba(61,237,243,.16);margin-bottom:10px}
.neon,.panel,.agent,.chief{background:linear-gradient(145deg,rgba(11,40,54,.96),rgba(4,20,31,.98));border:1px solid #2d6170;border-radius:15px;box-shadow:inset 0 0 24px rgba(6,205,220,.04),0 0 24px rgba(10,208,225,.09);padding:14px}.cyan{color:#55f5f0}.green{color:#64efaa}.gold{color:#ffe663}.red{color:#ff6d79}.muted{color:#94b0bc}.big{font-size:2.55rem;font-weight:900}.agent{min-height:226px}.chief{min-height:555px;border-color:#347b89}.bot{width:142px;height:142px;margin:6px auto 12px;border:2px solid #3ef2f2;border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:70px;background:radial-gradient(circle,#134b59,#061824 70%);box-shadow:0 0 15px #1dd7df,inset 0 0 20px #107888}.stButton>button{background:linear-gradient(#173b4d,#091d2c)!important;color:#dcfbff!important;border:1px solid #3cdde7!important;border-radius:22px!important;font-weight:750!important;min-height:39px}.stButton>button:hover{box-shadow:0 0 18px #20dbe6!important;border-color:#7cffff!important}.stButton>button[kind="primary"]{background:linear-gradient(90deg,#126475,#24bac6)!important;color:#fff!important}.stButton>button:disabled{opacity:.5}.stMetric{background:transparent}.stMetric label{color:#8dabba!important}.stMetric [data-testid="stMetricValue"]{color:#e6fbff!important}.log{font-family:monospace;font-size:.78rem;color:#69e49d;text-align:center;padding:8px}.source{padding:11px;border-top:1px solid #245366;color:#8fb5c2;text-align:center}.js-plotly-plot{border:1px solid #315f6e;border-radius:14px;overflow:hidden;box-shadow:0 0 25px rgba(22,213,226,.08)}
@media(max-width:1100px){section[data-testid="stSidebar"]{width:190px!important}.chief{min-height:auto}.big{font-size:2rem}}@media(max-width:800px){.block-container{padding:8px!important}.title{font-size:1.1rem}.agent{min-height:auto}}
</style>''',unsafe_allow_html=True)
with st.sidebar:
 st.markdown("## ◉ GOLD COMMAND");page=st.radio("",["OVERVIEW","AI DESK","MARKET DATA","HISTORY","SETTINGS","SYSTEM INTEL"],label_visibility="collapsed");st.divider();st.session_state.auto_refresh=st.toggle("AUTO SYNC",value=st.session_state.auto_refresh,help="Refreshes the 1-minute feed every 15 seconds");st.caption("1-minute candles • 15-second polling")
st.markdown('<div class="title">GOLD COMMAND – AI SPECIALIST DESK</div>',unsafe_allow_html=True)
if page in("OVERVIEW","AI DESK"):
 main,side=st.columns([3.5,1],gap="medium")
 with main:
  m=st.session_state.market;st.markdown("### Live Gold (XAU/USD) 1-Min Candlestick Chart")
  if m.get("candles"):
   d=pd.DataFrame(m["candles"]);fig=go.Figure();fig.add_trace(go.Candlestick(x=d.time,open=d.open,high=d.high,low=d.low,close=d.close,increasing_line_color="#20e0e5",decreasing_line_color="#ff855e",name="1m"));fig.add_trace(go.Scatter(x=d.time,y=d.close.rolling(20).mean(),line=dict(color="#5ef1d0",width=1),name="SMA20"));fig.add_trace(go.Scatter(x=d.time,y=d.close.rolling(50).mean(),line=dict(color="#d6b28a",width=1),name="SMA50"));fig.update_layout(height=365,margin=dict(l=5,r=5,t=15,b=5),paper_bgcolor="#071827",plot_bgcolor="#071827",font_color="#b9dce5",xaxis_rangeslider_visible=False,legend=dict(orientation="h"));st.plotly_chart(fig,width="stretch")
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
  st.markdown("<h2 style='text-align:center'>AI SPECIALIST DESK</h2>",unsafe_allow_html=True);cols=st.columns(4);names={"technical":"TECHNICAL","fundamental":"FUNDAMENTAL","sentiment":"SENTIMENT","liquidity":"LIQUIDITY"}
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
  st.markdown(f'<div class="chief"><h3>CHIEF AGENT WORKSPACE</h3><div class="bot">◈</div><p class="cyan">CHIEF INTEL AGENT [COMMAND]</p><div class="big">{r.get("suggested_action","HOLD").upper()}</div><div class="green">SYSTEM SYNC: {sum(bool((st.session_state.agents[k].last_report or {}).get("success")) for k in names)*25}%</div><p class="muted">{r.get("summary","")}</p><hr><b>ENTRY</b><div>{fmt(r.get("entry"))}</div><b>STOP LOSS</b><div class="red">{fmt(r.get("stop_loss"))}</div><b>TAKE PROFIT</b><div class="green">{fmt(r.get("take_profit"))}</div><hr><div class="muted">Technical • Fundamental • Sentiment • Liquidity orchestration</div></div>',unsafe_allow_html=True)
  with st.expander("VIEW REASONING"):st.write(r.get("reasoning"))
 st.markdown(f'<div class="source">1-Min Gold: {m.get("data_status")} • Auto Sync: {"ON" if st.session_state.auto_refresh else "OFF"} • DXY: {m.get("dxy","N/A")} • US10Y: {m.get("us10y","N/A")} • Updated: {m.get("updated","")[:19]}</div>',unsafe_allow_html=True)
elif page=="MARKET DATA":st.json({k:v for k,v in st.session_state.market.items() if k!="candles"})
elif page=="HISTORY":
 try:st.json(json.loads(H.read_text())[-10:] if H.exists() else[])
 except:st.info("No history")
elif page=="SETTINGS":st.info("Add GEMINI_API_KEY in Streamlit Secrets. Optional: GEMINI_MODEL.")
else:st.info("System intelligence dashboard. Use AI DESK to analyze the 1-minute Gold market.")
st.caption("Yahoo Finance data is polled, not exchange-grade streaming. Educational and paper-trading support only. Not financial advice.")
