from __future__ import annotations
import time
from datetime import datetime
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from charts import build_gold_chart
from indicators import enrich, market_snapshot
from market_data import get_gold_data

st.set_page_config(page_title='AURA Gold Market', page_icon='✦', layout='wide', initial_sidebar_state='collapsed')

st.markdown(r"""<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&display=swap');
:root{--cyan:#5ee6ff;--mint:#55e3ba;--violet:#9e82ff;--panel:rgba(7,24,39,.88);--line:#326f91}
html,body,[class*="css"]{font-family:Rajdhani,Segoe UI,sans-serif}.stApp{background:radial-gradient(circle at 53% 5%,#174c6d 0,#071827 31%,#020812 76%);color:#effbff}.block-container{max-width:100%;padding:1rem 1.1rem 2rem}.aura-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}.brand{font-size:30px;font-weight:700;letter-spacing:.05em;color:white}.brand span{color:var(--cyan);text-shadow:0 0 18px #46dcff}.sub{font-size:11px;letter-spacing:.35em;color:#75dfff}.glass{background:linear-gradient(145deg,rgba(12,36,55,.94),rgba(5,18,31,.94));border:1px solid var(--line);box-shadow:inset 0 0 24px rgba(56,217,255,.08),0 10px 35px rgba(0,0,0,.55);backdrop-filter:blur(14px)}.nav{padding:12px;margin:8px 0;border:1px solid #6388e7;border-radius:7px;background:linear-gradient(90deg,#282e59,#1d5071);box-shadow:0 0 15px #44dbff44;transition:.25s}.nav:hover,.nav.active{transform:translateX(5px);background:linear-gradient(90deg,#1374a8,#38d7ff77);box-shadow:0 0 24px #3cddff88}.market-head{padding:12px 15px;border:1px solid #4edfff;box-shadow:0 0 20px #35d7ff55}.price{font-size:28px;font-weight:700;color:var(--mint)}.tag{display:inline-block;padding:4px 9px;border-radius:12px;border:1px solid #4de3bd;color:#7cf4d0;background:#113b40;font-size:12px}.warn{border-color:#ffbd59;color:#ffd98c;background:#3f3114}.agent{position:relative;overflow:hidden;padding:12px 13px;margin:8px 0;border:1px solid #4ad9ff;border-radius:9px;background:linear-gradient(145deg,rgba(12,37,56,.95),rgba(7,22,36,.95));box-shadow:inset 0 0 18px #32d6ff14,0 0 13px #2cd2ff44;transition:.25s}.agent:hover{transform:translateX(-4px);box-shadow:0 0 25px #39dcff88}.agent.running{animation:pulse 1.15s infinite}.agent.running:after{content:'';position:absolute;inset:-60%;background:conic-gradient(transparent 78%,#59eaff66);animation:spin 1.4s linear infinite;pointer-events:none}.agent.done{border-color:#4ee1b6}.agent.error{border-color:#ff5f78}.agent-title{font-size:17px;font-weight:700}.agent-grid{display:grid;grid-template-columns:1fr 1fr 1fr;font-size:12px;color:#b9d4e4}.mint{color:var(--mint)}.cyan{color:var(--cyan)}.gold{color:#f5c759}.metric-card{padding:12px;border:1px solid #2f6686;background:#081b2ccc}.metric-label{font-size:12px;color:#8faec1}.metric-value{font-size:21px;font-weight:700;color:#eaf9ff}.trade{padding:15px;border:1px solid #62e1ff;box-shadow:inset 0 0 25px #42d9ff17,0 0 20px #38d9ff44}.scan{height:2px;background:linear-gradient(90deg,transparent,#61eaff,transparent);animation:scan 2s linear infinite}.stButton>button{width:100%;border:1px solid #5fe4ff;background:linear-gradient(90deg,#15577b,#217da7);color:white;font-weight:700}.disclaimer{font-size:11px;color:#7894a7;padding-top:9px}@keyframes pulse{50%{box-shadow:0 0 30px #3ad9ffbb;transform:translateY(-2px)}}@keyframes spin{to{transform:rotate(360deg)}}@keyframes scan{from{transform:translateX(-55%)}to{transform:translateX(55%)}}
</style>""", unsafe_allow_html=True)

st_autorefresh(interval=60_000, key='gold-auto-refresh')

if 'agent_stage' not in st.session_state:
    st.session_state.agent_stage = -1
if 'run_agents' not in st.session_state:
    st.session_state.run_agents = False

result = get_gold_data('1min', 180)
data = enrich(result.candles)
snap = market_snapshot(data)

st.markdown(f"""<div class='aura-top'><div><div class='brand'><span>✦</span> AURA</div><div class='sub'>GOLD MARKET INTELLIGENCE</div></div><div><span class='tag {'warn' if 'DEMO' in result.mode else ''}'>{result.mode}</span>&nbsp;&nbsp;<span style='color:#9ab5c5;font-size:12px'>{result.source} · {result.updated_at.strftime('%H:%M:%S UTC')}</span></div></div>""", unsafe_allow_html=True)

left, center, right = st.columns([1.15, 5.7, 2.55], gap='medium')

with left:
    st.markdown("<div class='nav active'>▦ &nbsp; Dashboard</div><div class='nav'>♟ &nbsp; Agents</div><div class='nav'>⌁ &nbsp; Analysis</div><div class='nav'>⚙ &nbsp; Settings</div><div class='nav'>◫ &nbsp; Data Feed</div>", unsafe_allow_html=True)
    st.markdown("<br><div class='glass' style='padding:12px'><div class='metric-label'>INSTRUMENT</div><div class='metric-value'>XAU/USD</div><div class='metric-label'>INTERVAL</div><div class='metric-value'>1 minute</div><div class='metric-label'>AUTO REFRESH</div><div class='metric-value mint'>60 seconds</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='disclaimer'>Market information and technical indicators are for educational and monitoring purposes only. This app does not place orders or provide personalized financial advice.</div>", unsafe_allow_html=True)

with center:
    delta_color = '#55e3ba' if snap['change'] >= 0 else '#ff6f91'
    st.markdown(f"""<div class='glass market-head'><div style='display:flex;justify-content:space-between;align-items:center'><div><div style='font-size:20px;font-weight:700'>Live Gold Market Chart</div><div style='color:#91adbf'>XAU/USD · 1 minute · EMA 20/50 · RSI 14 · MACD</div></div><div style='text-align:right'><div class='price'>{snap['last']:,.2f}</div><div style='color:{delta_color}'>{snap['change']:+.2f} ({snap['pct']:+.2f}%)</div></div></div><div class='scan'></div></div>""", unsafe_allow_html=True)
    st.plotly_chart(build_gold_chart(data), use_container_width=True, config={'displaylogo': False, 'scrollZoom': True, 'responsive': True})
    m1, m2, m3, m4 = st.columns(4)
    metrics = [('RSI 14', f"{snap['rsi']:.1f}"), ('MACD', f"{snap['macd']:.2f}"), ('TREND', snap['trend']), ('VOLATILITY', f"{snap['volatility']:.1f}%")]
    for col, (label, value) in zip([m1,m2,m3,m4], metrics):
        with col:
            st.markdown(f"<div class='glass metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div></div>", unsafe_allow_html=True)
    if result.message:
        st.caption(result.message)

with right:
    st.markdown("<div style='font-size:20px;font-weight:700'>AGENT HIERARCHY</div>", unsafe_allow_html=True)
    if st.button('RUN MULTI-AGENT ANALYSIS', type='primary'):
        st.session_state.run_agents = True
        st.session_state.agent_stage = 0

    agent_specs = [
        ('SUPERVISOR AGENT', 'Market Coordinator', 'S-001', 'Combines indicator summaries'),
        ('ALPHA AGENT', 'Momentum', 'A-002', f"RSI {snap['rsi']:.1f} · {snap['momentum']}"),
        ('BETA AGENT', 'Trend', 'B-003', snap['trend']),
        ('GAMMA AGENT', 'Volatility', 'G-004', f"Volatility {snap['volatility']:.1f}%"),
        ('DELTA AGENT', 'Data Quality', 'D-005', f"Feed mode: {result.mode}"),
    ]

    def agents_html(stage: int) -> str:
        blocks = []
        for i, (name, role, aid, detail) in enumerate(agent_specs):
            state = 'done' if i < stage else 'running' if i == stage else ''
            status = 'Completed' if i < stage else 'Working' if i == stage else 'Waiting'
            blocks.append(f"""<div class='agent {state}'><div class='agent-title'>{name} <span style='font-weight:400'>({role})</span></div><div class='agent-grid'><span>ID: {aid}</span><span>Status: <b class='mint'>{status}</b></span><span>XAU/USD</span></div><div style='font-size:12px;color:#92adbf;margin-top:5px'>{detail}</div></div>""")
        return ''.join(blocks)

    agent_placeholder = st.empty()
    if st.session_state.run_agents:
        for stage in range(st.session_state.agent_stage, len(agent_specs)):
            agent_placeholder.markdown(agents_html(stage), unsafe_allow_html=True)
            time.sleep(0.55)
        st.session_state.agent_stage = len(agent_specs)
        st.session_state.run_agents = False
        agent_placeholder.markdown(agents_html(len(agent_specs)), unsafe_allow_html=True)
        st.toast('Agent review completed')
    else:
        agent_placeholder.markdown(agents_html(st.session_state.agent_stage), unsafe_allow_html=True)

    st.markdown("<div style='font-size:20px;font-weight:700;margin-top:10px'>MARKET SNAPSHOT</div>", unsafe_allow_html=True)
    st.markdown(f"""<div class='glass trade'><div style='display:flex;justify-content:space-between'><div><b style='font-size:19px'>◉ XAU/USD</b><div class='metric-label'>Gold spot reference</div></div><span class='tag'>ANALYSIS ONLY</span></div><hr style='border-color:#275470'><div class='agent-grid' style='font-size:14px;line-height:2'><span>Last</span><span>EMA 20</span><span>EMA 50</span><b>{snap['last']:,.2f}</b><b>{snap['ema20']:,.2f}</b><b>{snap['ema50']:,.2f}</b></div><div style='margin-top:8px;color:#9eb7c6'>Momentum: <b class='mint'>{snap['momentum']}</b><br>Structure: <b class='cyan'>{snap['trend']}</b></div></div>""", unsafe_allow_html=True)
    st.markdown("<div class='disclaimer'>No buy/sell recommendation or trade execution is produced. Confirm provider licensing and latency before any production use.</div>", unsafe_allow_html=True)
