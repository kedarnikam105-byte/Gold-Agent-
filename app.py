import json, os
from datetime import datetime
from pathlib import Path
import pandas as pd, plotly.graph_objects as go, streamlit as st
from dotenv import load_dotenv
from agents.analysts import create_technical_agent,create_fundamental_agent,create_sentiment_agent,create_liquidity_agent,create_chief_officer
from market_data import get_gold_data
st.set_page_config(page_title="Gold Command Center",page_icon="🥇",layout="wide",initial_sidebar_state="expanded"); load_dotenv()
LOG=Path("logs"); LOG.mkdir(exist_ok=True); HISTORY=LOG/"agent_history.json"
if "agents" not in st.session_state: st.session_state.agents={"technical":create_technical_agent(),"fundamental":create_fundamental_agent(),"sentiment":create_sentiment_agent(),"liquidity":create_liquidity_agent(),"chief":create_chief_officer()}
if "market" not in st.session_state: st.session_state.market=get_gold_data()
if "selected" not in st.session_state: st.session_state.selected=None

def valid_chief(r):
 a=r.get("suggested_action","Hold"); c=int(r.get("confidence",0) or 0); e,s,t=r.get("entry"),r.get("stop_loss"),r.get("take_profit"); n=all(isinstance(x,(int,float)) for x in (e,s,t)); ok=(a=="Buy" and n and s<e<t) or (a=="Sell" and n and t<e<s)
 if a=="Hold" or c<60 or not ok: r.update(suggested_action="Hold",bias="Neutral",entry=None,stop_loss=None,take_profit=None)
 return r

def save(reports):
 try: h=json.loads(HISTORY.read_text()) if HISTORY.exists() else []
 except: h=[]
 h.append({"run_time":datetime.now().isoformat(),"reports":reports}); HISTORY.write_text(json.dumps(h[-50:],indent=2))

def run_all(retry_only=False):
 m=st.session_state.market; reports=[]
 for k in ("technical","fundamental","sentiment","liquidity"):
  agent=st.session_state.agents[k]
  if retry_only and agent.last_report and agent.last_report.get("success"): r=agent.last_report
  else: r=agent.analyze(m)
  reports.append(r)
 successful=[r for r in reports if r.get("success")]
 if len(successful)>=3:
  chief=valid_chief(st.session_state.agents["chief"].analyze(m,"FOUR SPECIALIST REPORTS:\n"+json.dumps(reports,indent=2)))
 else:
  chief={"agent":"Chief Officer","bias":"Neutral","confidence":0,"summary":"HOLD: fewer than three specialist reports completed successfully.","key_points":[],"suggested_action":"Hold","entry":None,"stop_loss":None,"take_profit":None,"reasoning":"Retry failed agents before generating a final signal.","success":False}
  st.session_state.agents["chief"].last_report=chief
 reports.append(chief); save(reports)

st.markdown('''<style>
.stApp{background:#06101d;color:#f7fafc}.block-container{max-width:1550px;padding-top:1rem}section[data-testid="stSidebar"]{background:#081626;border-right:1px solid #263b58}h1,h2,h3{color:#f7fafc!important}.top{padding:18px 22px;border:1px solid #263b58;border-radius:18px;background:linear-gradient(135deg,#101f33,#091525);display:flex;justify-content:space-between}.gold{color:#f5b942;font-weight:900}.panel,.chief,.agent,.source{background:#0e1c2e;border:1px solid #29405f;border-radius:16px;padding:18px}.chief{border-color:#6e5720;background:linear-gradient(145deg,#101c2d,#27200f)}.big{font-size:2.6rem;font-weight:950;color:#fff}.label{font-size:.72rem;letter-spacing:.12em;color:#9fb0c6;font-weight:800}.metric{font-size:1.35rem;color:#fff;font-weight:850}.agent{min-height:195px}.muted{color:#9fb0c6}.ok{color:#28d17c}.warn{color:#ffca55}.bad{color:#ff6b76}.stButton>button{background:#10243b!important;color:#f7fafc!important;border:1px solid #42a5f5!important;border-radius:10px!important;font-weight:800!important}.stButton>button:hover{background:#183553!important;color:#fff!important}.stButton>button[kind="primary"]{background:#f5b942!important;color:#101827!important;border:0!important}.stButton>button:disabled{background:#142235!important;color:#718198!important;border-color:#263b58!important}.stTabs [data-baseweb="tab"]{color:#b9c6d6!important}</style>''',unsafe_allow_html=True)

with st.sidebar:
 st.markdown("## 🥇 GOLD COMMAND")
 page=st.radio("NAVIGATION",["Overview","AI Desk","Market Data","History","Settings"],label_visibility="collapsed")
 st.divider(); st.caption("Five-agent decision intelligence")

m=st.session_state.market; price=m.get("current_price",0); change=m.get("change_1d_pct",0)
st.markdown(f'<div class="top"><div><span class="gold">GOLD COMMAND CENTER</span><br><span class="muted">Five-agent decision intelligence</span></div><div><b>XAUUSD&nbsp; {price:,.2f}</b>&nbsp; {change:+.2f}% &nbsp; <span class="ok">● MARKET DATA</span><br><span class="muted">Last: {datetime.now().strftime("%H:%M IST")}</span></div></div>',unsafe_allow_html=True)

if page in ("Overview","AI Desk"):
 left,right=st.columns([2.4,1])
 with left:
  st.markdown("### MARKET WORKSPACE")
  chart=m.get("chart",[])
  if chart:
   d=pd.DataFrame(chart); fig=go.Figure(go.Candlestick(x=d.time,open=d.open,high=d.high,low=d.low,close=d.close,increasing_line_color="#28d17c",decreasing_line_color="#ff5d68")); fig.update_layout(height=380,margin=dict(l=10,r=10,t=20,b=10),paper_bgcolor="#0e1c2e",plot_bgcolor="#0e1c2e",font_color="#9fb0c6",xaxis_rangeslider_visible=False); st.plotly_chart(fig,use_container_width=True)
  else: st.info("Market chart is currently unavailable. Use Refresh Market Data.")
  a,b,c=st.columns(3)
  a.markdown(f'<div class="panel"><div class="label">RSI 14</div><div class="metric">{m.get("rsi_14","N/A")}</div><div class="muted">Momentum</div></div>',unsafe_allow_html=True)
  b.markdown(f'<div class="panel"><div class="label">SMA 20</div><div class="metric">{m.get("sma_20","N/A")}</div><div class="muted">Short trend</div></div>',unsafe_allow_html=True)
  c.markdown(f'<div class="panel"><div class="label">SMA 50</div><div class="metric">{m.get("sma_50","N/A")}</div><div class="muted">Medium trend</div></div>',unsafe_allow_html=True)
  x,y,z=st.columns([2,1,1])
  if x.button("⚡ Run Full Market Analysis",type="primary",use_container_width=True,disabled=not bool(os.getenv("GEMINI_API_KEY"))):
   with st.spinner("Agents are analyzing live market inputs..."): run_all(False)
   st.rerun()
  if y.button("↻ Refresh Market Data",use_container_width=True): st.session_state.market=get_gold_data(); st.rerun()
  if z.button("Retry Failed Agents",use_container_width=True):
   with st.spinner("Retrying unavailable agents..."): run_all(True)
   st.rerun()
 with right:
  st.markdown("### CHIEF SIGNAL"); r=st.session_state.agents["chief"].last_report
  if not r: r={"suggested_action":"WAITING","confidence":0,"summary":"Run the analysis to create one validated signal.","entry":None,"stop_loss":None,"take_profit":None}
  f=lambda v:f"${v:,.2f}" if isinstance(v,(int,float)) else "WAITING"
  st.markdown(f'<div class="chief"><div class="label">FINAL DECISION</div><div class="big">{r.get("suggested_action","HOLD").upper()}</div><div class="metric">Confidence {r.get("confidence",0)}%</div><p class="muted">{r.get("summary","")}</p><hr><div class="label">ENTRY</div><div class="metric">{f(r.get("entry"))}</div><br><div class="label">STOP LOSS</div><div class="metric bad">{f(r.get("stop_loss"))}</div><br><div class="label">TAKE PROFIT</div><div class="metric ok">{f(r.get("take_profit"))}</div></div>',unsafe_allow_html=True)
  with st.expander("View Chief Reasoning"): st.write(r.get("reasoning","No reasoning yet."))
 st.markdown("### AI SPECIALIST DESK")
 cols=st.columns(4); meta={"technical":"Technical","fundamental":"Fundamental","sentiment":"Sentiment","liquidity":"Liquidity"}
 for col,(k,name) in zip(cols,meta.items()):
  a=st.session_state.agents[k]; r=a.last_report or {}; success=r.get("success"); tone="ok" if success else "warn"; bias=r.get("bias","Waiting")
  col.markdown(f'<div class="agent"><div class="label">{name.upper()}</div><div class="metric">{bias}</div><div class="{tone}">{a.status}</div><div class="muted">Confidence {r.get("confidence",0)}%</div><p class="muted">{r.get("summary","Awaiting analysis.")}</p></div>',unsafe_allow_html=True)
  if col.button("View Full Report",key=f"v{k}",use_container_width=True,disabled=not bool(r)): st.session_state.selected=k; st.rerun()
 if st.session_state.selected:
  r=st.session_state.agents[st.session_state.selected].last_report; st.markdown(f"### {r.get('agent')} Report"); o,p,q=st.tabs(["Overview","Key Points","Full Reasoning"])
  with o: st.write(r.get("summary"))
  with p:
   for item in r.get("key_points",[]): st.write("•",item)
  with q: st.write(r.get("reasoning"))
 s=m.get("sources",{}); st.markdown(f'<div class="source"><b>DATA SOURCES</b>&nbsp;&nbsp; Gold {"✓" if s.get("gold") else "⚠"}&nbsp;&nbsp; DXY {"✓" if s.get("dxy") else "⚠"}&nbsp;&nbsp; Yield {"✓" if s.get("yield") else "⚠"}&nbsp;&nbsp; News ⚠&nbsp;&nbsp; Calendar ⚠&nbsp;&nbsp; <span class="muted">Updated {datetime.now().strftime("%H:%M IST")}</span></div>',unsafe_allow_html=True)
elif page=="Market Data": st.json({k:v for k,v in m.items() if k!="chart"})
elif page=="History":
 try: st.json(json.loads(HISTORY.read_text())[-10:] if HISTORY.exists() else [])
 except: st.info("No history available.")
elif page=="Settings": st.info("Configure GEMINI_API_KEY and optional GEMINI_MODEL in Streamlit Secrets. Never commit keys to GitHub.")
else: st.info("Use Overview to run the trading desk.")
st.caption("Educational and paper-trading support only. Not financial advice. Verify all market data independently.")
