import streamlit as st
from streamlit_autorefresh import st_autorefresh
from market_data import get_gold_data
from analysis_engine import enrich,reports,supervise
from charts import chart
st.set_page_config(page_title="AURA Gold",page_icon="✦",layout="wide",initial_sidebar_state="collapsed")
st.markdown("<style>.stApp{background:radial-gradient(circle at 50% 0,#164a67,#061422 35%,#020812 80%);color:#eefaff}.block-container{max-width:100%;padding:1rem}.card{background:#081b2ddd;border:1px solid #42dfff;padding:14px;border-radius:9px;box-shadow:0 0 18px #35d7ff44}.agent{background:#081b2ddd;border:1px solid #4fe2ba;padding:12px;border-radius:9px;margin:8px 0}.signal{font-size:34px;font-weight:900}.mint{color:#55e3ba}.rose{color:#ff6f91}</style>",unsafe_allow_html=True)
st_autorefresh(interval=60000,key="auto")
f=get_gold_data(); d=enrich(f.candles); r=reports(d); s=supervise(d,r); last=float(d.Close.iloc[-1]); prev=float(d.Close.iloc[-2])
st.markdown(f"# ✦ AURA &nbsp; <small>GOLD MULTI-AGENT INTELLIGENCE</small><br>**{f.mode}** · {f.source} · auto analysis every 60 seconds", unsafe_allow_html=True)
a,b=st.columns([6.5,3.5],gap="large")
with a:
 st.markdown(f"<div class='card'><h2>Live Gold Market Chart</h2><div style='font-size:30px' class='mint'>{last:,.2f}</div><div>{last-prev:+.2f}</div></div>",unsafe_allow_html=True); st.plotly_chart(chart(d,s),use_container_width=True,config={"displaylogo":False,"scrollZoom":True})
with b:
 st.markdown("## Agent Hierarchy<br>Automatic analysis is active", unsafe_allow_html=True)
 for n,x in r.items():st.markdown(f"<div class='agent'><b>{n} · {x['role']}</b><br><small>Status: Completed</small><br>{x['report']}<br><small>Report sent to Mike</small></div>",unsafe_allow_html=True)
 cls="mint" if s['label']=="BUY SETUP" else "rose" if s['label']=="SELL SETUP" else ""
 st.markdown(f"<div class='card'><small>MIKE · SUPERVISOR / TEAM LEAD</small><div class='signal {cls}'>{s['label']}</div><p>Mike reviewed all specialist reports.</p><b>Entry reference:</b> {s['entry']:.2f}<br><b>SL reference:</b> {s['sl']:.2f}<br><b>TP reference:</b> {s['tp']:.2f}<br><b>Confidence:</b> {s['confidence']}%</div>",unsafe_allow_html=True)
 if st.button("REFRESH ANALYSIS NOW",type="primary"):st.rerun()
st.caption("Educational analytical references only. No order execution or guaranteed outcome.")
