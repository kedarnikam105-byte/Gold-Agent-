from __future__ import annotations
import json, time
from datetime import datetime, timezone
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from market_data import get_gold_data
from analysis_engine import enrich, build_agent_reports, supervisor_consensus
from charts import build_market_chart

st.set_page_config(page_title='AURA Gold Intelligence',page_icon='✦',layout='wide',initial_sidebar_state='collapsed')
st.markdown(r"""<style>
:root{--cyan:#5ee6ff;--mint:#55e3ba;--rose:#ff6f91;--panel:#081b2ddd;--line:#326f91}html,body,[class*=css]{font-family:Segoe UI,sans-serif}.stApp{background:radial-gradient(circle at 52% 3%,#164a67 0,#071827 30%,#020812 76%);color:#eefaff}.block-container{max-width:100%;padding:1rem 1.2rem 2rem}.brand{font-size:32px;font-weight:800}.sub{letter-spacing:.34em;color:#72dfff;font-size:11px}.glass{background:linear-gradient(145deg,#0c2437ed,#061421ed);border:1px solid var(--line);box-shadow:inset 0 0 24px #38d9ff12,0 10px 32px #0009}.head{padding:14px;border-color:#53dcff}.price{font-size:31px;font-weight:800;color:var(--mint)}.chip{display:inline-block;padding:4px 10px;border:1px solid var(--mint);border-radius:16px;color:#7af0d0;background:#10373b}.warn{border-color:#ffbf5d;color:#ffd58a;background:#3c3017}.agent{padding:13px;margin:9px 0;border:1px solid #49d9ff;border-radius:9px;background:#081d2eeb;box-shadow:0 0 14px #32d8ff42;transition:.25s}.agent:hover{transform:translateX(-4px);box-shadow:0 0 25px #39dcff88}.agent.running{animation:pulse 1.1s infinite}.agent.done{border-color:#51e2b8}.agent-title{font-size:17px;font-weight:800}.small{font-size:12px;color:#93adbd}.mint{color:var(--mint)}.cyan{color:var(--cyan)}.rose{color:var(--rose)}.report{padding:14px;border-left:3px solid var(--cyan);margin:8px 0}.conversation{padding:11px 13px;margin:7px 0;border-radius:8px;background:#0a2134;border:1px solid #274f69}.supervisor{border:1px solid #55e3ba;box-shadow:0 0 24px #3de0b94a;padding:16px}.signal{font-size:34px;font-weight:900}.metric{padding:11px;border:1px solid #2d6484;background:#071a2bcc}.metric b{font-size:20px}.stButton>button{width:100%;border:1px solid #5fe4ff;background:linear-gradient(90deg,#15577b,#217da7);color:white;font-weight:700}.scan{height:2px;background:linear-gradient(90deg,transparent,#61eaff,transparent);animation:scan 2s linear infinite}@keyframes pulse{50%{box-shadow:0 0 28px #3ad9ffbb;transform:translateY(-2px)}}@keyframes scan{from{transform:translateX(-50%)}to{transform:translateX(50%)}}
</style>""",unsafe_allow_html=True)
st_autorefresh(interval=60_000,key='refresh')

if 'reports' not in st.session_state: st.session_state.reports=None
if 'consensus' not in st.session_state: st.session_state.consensus=None
if 'selected_agent' not in st.session_state: st.session_state.selected_agent='Supervisor'

feed=get_gold_data('1min',220); data=enrich(feed.candles)
last=float(data.Close.iloc[-1]); prev=float(data.Close.iloc[-2]); change=last-prev; pct=change/prev*100
st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center'><div><div class='brand'><span class='cyan'>✦</span> AURA</div><div class='sub'>GOLD MULTI-AGENT INTELLIGENCE</div></div><div><span class='chip {'warn' if 'DEMO' in feed.mode else ''}'>{feed.mode}</span>&nbsp; <span class='small'>{feed.source} · {feed.updated_at.strftime('%H:%M:%S UTC')}</span></div></div>",unsafe_allow_html=True)

page=st.radio('Navigation',['Dashboard','Agents','Analysis','Settings'],horizontal=True,label_visibility='collapsed')

if page=='Dashboard':
 c1,c2=st.columns([6.6,3.4],gap='large')
 with c1:
  color='#55e3ba' if change>=0 else '#ff6f91'
  st.markdown(f"<div class='glass head'><div style='display:flex;justify-content:space-between'><div><h2 style='margin:0'>Live Gold Market Chart</h2><div class='small'>XAU/USD · 1 minute · EMA · RSI · MACD · ATR</div></div><div style='text-align:right'><div class='price'>{last:,.2f}</div><div style='color:{color}'>{change:+.2f} ({pct:+.2f}%)</div></div></div><div class='scan'></div></div>",unsafe_allow_html=True)
  st.plotly_chart(build_market_chart(data,st.session_state.consensus),use_container_width=True,config={'displaylogo':False,'scrollZoom':True})
 with c2:
  st.markdown('## Agent Hierarchy')
  if st.button('RUN FULL AGENT REVIEW',type='primary'):
   ph=st.empty(); names=['Momentum','Trend','Volatility','Pattern','News Context']
   for i,n in enumerate(names):
    ph.markdown(f"<div class='agent running'><div class='agent-title'>{n} Agent</div><div class='small'>Processing transparent market inputs...</div></div>",unsafe_allow_html=True); time.sleep(.35)
   st.session_state.reports=build_agent_reports(data)
   st.session_state.consensus=supervisor_consensus(data,st.session_state.reports)
   st.rerun()
  reports=st.session_state.reports
  if reports:
   for key,r in reports.items(): st.markdown(f"<div class='agent done'><div class='agent-title'>{r['name']}</div><div class='small'>Status: <span class='mint'>Completed</span></div><div>{r['summary']}</div></div>",unsafe_allow_html=True)
  else: st.info('Run the full agent review to generate reports and supervisor consensus.')
  if st.session_state.consensus:
   s=st.session_state.consensus
   st.markdown(f"<div class='glass supervisor'><div class='small'>ADRIAN COLE · SUPERVISOR CONSENSUS</div><div class='signal'>{s['label']}</div><div>{s['rationale']}</div><hr><div class='small'>Illustrative levels, not a trade instruction</div><b>Reference:</b> {s['entry']:.2f}<br><b>Risk boundary:</b> {s['stop']:.2f}<br><b>Objective:</b> {s['target']:.2f}<br><b>Confidence:</b> {s['confidence']}%</div>",unsafe_allow_html=True)

elif page=='Agents':
 st.markdown('## Agent Workspace')
 st.caption('Select an agent to inspect inputs, checks, evidence and the report delivered to the Supervisor. The app shows operational evidence, not hidden chain-of-thought.')
 reports=st.session_state.reports or build_agent_reports(data)
 options=['Supervisor']+list(reports.keys())
 selected=st.selectbox('Open agent',options,index=options.index(st.session_state.selected_agent) if st.session_state.selected_agent in options else 0)
 st.session_state.selected_agent=selected
 if selected=='Supervisor':
  st.markdown("<div class='glass supervisor'><h3>Mike · Supervisor / Team Lead</h3><p>Receives structured reports from every specialist, compares agreement and conflicts, applies risk constraints, and produces one consolidated analytical scenario.</p></div>",unsafe_allow_html=True)
  cols=st.columns(len(reports))
  for col,(k,r) in zip(cols,reports.items()):
   with col: st.markdown(f"<div class='metric'><div class='small'>{r['name']}</div><b>{r['stance']}</b><br><span class='small'>Score {r['score']:+.2f}</span></div>",unsafe_allow_html=True)
  st.markdown('### Internal report handoff')
  for k,r in reports.items(): st.markdown(f"<div class='conversation'><b class='cyan'>{r['name']} → Mike:</b> {r['handoff']}</div>",unsafe_allow_html=True)
  s=supervisor_consensus(data,reports)
  st.markdown(f"<div class='conversation'><b class='mint'>Mike:</b> {s['rationale']}</div>",unsafe_allow_html=True)
 else:
  r=reports[selected]
  st.markdown(f"<div class='glass report'><h2>{r['name']}</h2><div class='chip'>{r['stance']}</div><p>{r['purpose']}</p></div>",unsafe_allow_html=True)
  a,b=st.columns(2)
  with a:
   st.markdown('### Data checked')
   for x in r['checks']: st.markdown(f'- {x}')
  with b:
   st.markdown('### Evidence')
   for x in r['evidence']: st.markdown(f'- {x}')
  st.markdown('### Report to Supervisor')
  st.info(r['handoff'])
  st.markdown('### Limitations')
  st.warning(r['limitations'])

elif page=='Analysis':
 st.markdown('## Complete Analysis Report')
 reports=st.session_state.reports or build_agent_reports(data); s=st.session_state.consensus or supervisor_consensus(data,reports)
 st.plotly_chart(build_market_chart(data,s),use_container_width=True,config={'displaylogo':False,'scrollZoom':True})
 for r in reports.values():
  with st.expander(f"{r['name']} · {r['stance']}",expanded=False):
   st.write(r['summary']); st.write('Checks:',r['checks']); st.write('Evidence:',r['evidence']); st.write('Supervisor handoff:',r['handoff'])
 st.markdown(f"<div class='glass supervisor'><h3>Mike · Supervisor Decision Record</h3><p>{s['rationale']}</p><p><b>Scenario:</b> {s['label']} | <b>Reference:</b> {s['entry']:.2f} | <b>Risk boundary:</b> {s['stop']:.2f} | <b>Objective:</b> {s['target']:.2f} | <b>Confidence:</b> {s['confidence']}%</p></div>",unsafe_allow_html=True)
 st.download_button('DOWNLOAD JSON REPORT',json.dumps({'generated_at':datetime.now(timezone.utc).isoformat(),'feed':feed.mode,'agents':reports,'supervisor':s},indent=2),file_name='aura_gold_report.json',mime='application/json')

else:
 st.markdown('## Settings and Data Status')
 st.write({'market':'XAU/USD','interval':'1 minute','feed_mode':feed.mode,'source':feed.source,'updated_at':feed.updated_at.isoformat()})
 st.info('Add TWELVE_DATA_API_KEY in Streamlit Secrets. Add GEMINI_API_KEY only if a future optional narrative layer is enabled. The deterministic analytical engine remains the source of indicator calculations.')

st.caption('AURA is an educational market-analysis dashboard. Levels and scenarios are illustrative, not personalized financial advice, and no orders are executed.')
