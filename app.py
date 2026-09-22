import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from agents.analysts import (
    create_chief_officer,
    create_fundamental_agent,
    create_liquidity_agent,
    create_sentiment_agent,
    create_technical_agent,
)
from market_data import get_gold_data

st.set_page_config(page_title="Gold Command Center", page_icon="🥇", layout="wide")
load_dotenv()

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
HISTORY_FILE = LOG_DIR / "agent_history.json"

if "agents" not in st.session_state:
    st.session_state.agents = {
        "technical": create_technical_agent(),
        "fundamental": create_fundamental_agent(),
        "sentiment": create_sentiment_agent(),
        "liquidity": create_liquidity_agent(),
        "chief": create_chief_officer(),
    }
if "market_data" not in st.session_state:
    st.session_state.market_data = None
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None


def save_history(reports):
    history = []
    if HISTORY_FILE.exists():
        try:
            history = json.loads(HISTORY_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            history = []
    history.append({"run_time": datetime.now().isoformat(), "reports": reports})
    HISTORY_FILE.write_text(json.dumps(history[-50:], indent=2))


def load_today_history():
    if not HISTORY_FILE.exists():
        return []
    try:
        today = datetime.now().date().isoformat()
        return [item for item in json.loads(HISTORY_FILE.read_text()) if item.get("run_time", "").startswith(today)]
    except (json.JSONDecodeError, OSError):
        return []


def validate_chief_signal(report):
    """Fail safely when Gemini returns an invalid or low-confidence trade setup."""
    action = report.get("suggested_action", "Hold")
    confidence = int(report.get("confidence", 0) or 0)
    entry = report.get("entry")
    stop_loss = report.get("stop_loss")
    take_profit = report.get("take_profit")
    numeric = all(isinstance(value, (int, float)) for value in (entry, stop_loss, take_profit))
    valid_buy = action == "Buy" and numeric and stop_loss < entry < take_profit
    valid_sell = action == "Sell" and numeric and take_profit < entry < stop_loss

    if action == "Hold":
        report.update({"entry": None, "stop_loss": None, "take_profit": None})
    elif confidence < 60 or not (valid_buy or valid_sell):
        report.update({
            "suggested_action": "Hold",
            "bias": "Neutral",
            "entry": None,
            "stop_loss": None,
            "take_profit": None,
            "summary": "HOLD: the proposed trade did not pass confidence and risk validation.",
        })
    return report


def run_full_analysis():
    market = get_gold_data()
    st.session_state.market_data = market
    reports = []
    specialist_reports = []

    for key in ("technical", "fundamental", "sentiment", "liquidity"):
        report = st.session_state.agents[key].analyze(market)
        reports.append(report)
        specialist_reports.append(report)

    context = "FOUR SPECIALIST REPORTS:\n" + json.dumps(specialist_reports, indent=2)
    chief_report = st.session_state.agents["chief"].analyze(market, context)
    chief_report = validate_chief_signal(chief_report)
    st.session_state.agents["chief"].last_report = chief_report
    reports.append(chief_report)
    save_history(reports)


st.markdown("""
<style>
:root { --panel:#0d1a2b; --line:#263b58; --gold:#f4b942; --muted:#91a3bb; }
.stApp { background:radial-gradient(circle at 80% 0%,#172842 0%,#081321 35%,#050b13 75%); color:#f8fafc; }
.block-container { max-width:1480px; padding-top:1.4rem; padding-bottom:2rem; }
#MainMenu, footer { visibility:hidden; }
h1,h2,h3,p,span,label,div { font-family:Inter,ui-sans-serif,system-ui,sans-serif; }
.hero { display:flex; justify-content:space-between; align-items:center; gap:20px; padding:22px; border:1px solid var(--line); border-radius:20px; background:linear-gradient(135deg,#101f33,#081321); box-shadow:0 18px 55px rgba(0,0,0,.3); }
.eyebrow { color:var(--gold); font-size:.78rem; font-weight:800; letter-spacing:.16em; }
.hero-title { color:#fff; font-size:2rem; font-weight:900; margin:4px 0; }
.muted { color:var(--muted); }
.live { color:#72e2b2; background:#0a2b23; border:1px solid #1f8f61; padding:8px 12px; border-radius:999px; font-weight:800; white-space:nowrap; }
.kpi,.level,.agent { background:linear-gradient(145deg,#101f33,#0a1626); border:1px solid var(--line); border-radius:17px; padding:19px; box-shadow:0 12px 31px rgba(0,0,0,.22); }
.kpi { min-height:125px; }
.label { color:var(--muted); font-size:.74rem; font-weight:800; letter-spacing:.12em; }
.value { color:#fff; font-size:1.75rem; font-weight:900; margin-top:11px; }
.note { color:var(--muted); font-size:.82rem; margin-top:5px; }
.signal { padding:26px; border:1px solid #6d5720; border-radius:22px; background:linear-gradient(135deg,#101a2a,#28200f); box-shadow:0 20px 55px rgba(0,0,0,.3); }
.signal-action { color:#fff; font-size:3rem; font-weight:950; line-height:1; margin:12px 0; }
.signal-copy { color:#b9c5d5; }
.level { min-height:105px; }
.agent { min-height:220px; }
.agent-name { color:#fff; font-size:1.12rem; font-weight:900; }
.badge { display:inline-block; margin-top:14px; padding:6px 10px; border-radius:999px; font-size:.76rem; font-weight:850; }
.bull { color:#6ce6a9; background:#0b3227; border:1px solid #176947; }
.bear { color:#ff8b92; background:#38151c; border:1px solid #7b2837; }
.neutral { color:#ffd778; background:#352a0f; border:1px solid #755c19; }
.agent-copy { color:#aab8c9; font-size:.87rem; margin-top:13px; min-height:64px; }
.warning { padding:14px 18px; border:1px solid #7a5f1b; border-radius:14px; background:#2f260e; color:#ffe08a; margin-top:12px; }
.stButton>button { min-height:46px; border-radius:12px; font-weight:800; border:1px solid #3c516e; }
.stButton>button[kind="primary"] { background:linear-gradient(135deg,#d99618,#f4b942); color:#111827; border:0; }
[data-testid="stMetric"],[data-testid="stExpander"] { background:#0d1a2b; border:1px solid var(--line); border-radius:14px; }
.disclaimer { margin-top:24px; padding:13px 16px; border:1px solid var(--line); border-radius:12px; background:#091422; color:#93a4b9; font-size:.82rem; }
@media(max-width:700px){.hero{display:block}.live{display:inline-block;margin-top:14px}.hero-title{font-size:1.55rem}.signal-action{font-size:2.2rem}}
</style>
""", unsafe_allow_html=True)

market = st.session_state.market_data or get_gold_data()
st.session_state.market_data = market
api_ready = bool(os.getenv("GEMINI_API_KEY"))
price = market.get("current_price", 0) or 0
change = market.get("change_1d_pct", 0) or 0

st.markdown(f"""
<div class="hero">
  <div><div class="eyebrow">AI-POWERED GOLD INTELLIGENCE</div><div class="hero-title">🥇 Gold Command Center</div><div class="muted">Four specialist agents. One validated Chief Officer signal.</div></div>
  <div class="live">● LIVE &nbsp; {datetime.now().strftime('%d %b %Y, %H:%M')}</div>
</div>
""", unsafe_allow_html=True)

if not api_ready:
    st.markdown('<div class="warning"><b>Gemini is not configured.</b> Add GEMINI_API_KEY in Streamlit Secrets, save, and reboot the app.</div>', unsafe_allow_html=True)

left, right = st.columns([3, 1])
with left:
    run_clicked = st.button("⚡ Run Four-Agent Analysis", type="primary", use_container_width=True, disabled=not api_ready)
with right:
    if st.button("Refresh Market Data", use_container_width=True):
        st.session_state.market_data = get_gold_data()
        st.rerun()

if run_clicked:
    with st.spinner("Four specialists are analyzing and the Chief Officer is validating the final setup..."):
        run_full_analysis()
    st.rerun()

kpi_data = [
    ("XAUUSD", f"${price:,.2f}", f"{change:+.2f}% latest move"),
    ("RSI 14", str(market.get("rsi_14", "N/A")), "Momentum gauge"),
    ("SMA 20", f"${market.get('sma_20'):,.2f}" if market.get("sma_20") else "N/A", "Short-term reference"),
    ("24H RANGE", f"${market.get('low_24h', 0):,.0f} to ${market.get('high_24h', 0):,.0f}", "Observed range"),
]
for col, item in zip(st.columns(4), kpi_data):
    label, value, note = item
    col.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div><div class="note">{note}</div></div>', unsafe_allow_html=True)

st.markdown("### Chief Officer Signal")
chief = st.session_state.agents["chief"].last_report
if chief and chief.get("confidence", 0) > 0:
    action = chief.get("suggested_action", "Hold").upper()
    confidence = chief.get("confidence", 0)
    def format_level(value):
        return f"${value:,.2f}" if isinstance(value, (int, float)) else "NO TRADE"
    st.markdown(f'<div class="signal"><div class="eyebrow">FINAL VALIDATED SIGNAL</div><div class="signal-action">{action}</div><div class="signal-copy">{chief.get("summary", "")}</div></div>', unsafe_allow_html=True)
    levels = [
        ("CONFIDENCE", f"{confidence}%"),
        ("ENTRY", format_level(chief.get("entry"))),
        ("STOP LOSS", format_level(chief.get("stop_loss"))),
        ("TAKE PROFIT", format_level(chief.get("take_profit"))),
    ]
    for col, (label, value) in zip(st.columns(4), levels):
        col.markdown(f'<div class="level"><div class="label">{label}</div><div class="value">{value}</div></div>', unsafe_allow_html=True)
    with st.expander("Why the Chief Officer selected this signal"):
        st.write(chief.get("reasoning", "No reasoning available."))
        for point in chief.get("key_points", []):
            st.write(f"• {point}")
else:
    st.markdown('<div class="signal"><div class="eyebrow">AWAITING ANALYSIS</div><div class="signal-action">NO SIGNAL</div><div class="signal-copy">Run the analysis to generate one Chief Officer decision with Entry, Stop Loss and Take Profit. Weak or conflicting evidence produces HOLD with no trade levels.</div></div>', unsafe_allow_html=True)

st.markdown("### Specialist Desk")
meta = {
    "technical": ("Technical Analyst", "Trend, momentum and levels"),
    "fundamental": ("Fundamental Analyst", "Macro and economic drivers"),
    "sentiment": ("Sentiment Analyst", "Positioning and psychology"),
    "liquidity": ("Liquidity Analyst", "Liquidity and invalidation"),
}
for col, (key, details) in zip(st.columns(4), meta.items()):
    name, role = details
    report = st.session_state.agents[key].last_report
    bias = report.get("bias", "Waiting") if report else "Waiting"
    confidence = report.get("confidence", 0) if report else 0
    summary = report.get("summary", "Run analysis to generate this specialist report.") if report else "Run analysis to generate this specialist report."
    badge = "bull" if bias == "Bullish" else "bear" if bias == "Bearish" else "neutral"
    col.markdown(f'<div class="agent"><div class="agent-name">{name}</div><div class="note">{role}</div><span class="badge {badge}">{bias} · {confidence}%</span><div class="agent-copy">{summary}</div></div>', unsafe_allow_html=True)
    if col.button("View full report", key=f"view_{key}", use_container_width=True, disabled=not bool(report)):
        st.session_state.selected_agent = key

if st.session_state.selected_agent:
    report = st.session_state.agents[st.session_state.selected_agent].last_report
    if report:
        st.markdown(f"### {report.get('agent')} Details")
        overview, points, reasoning = st.tabs(["Overview", "Key Points", "Full Reasoning"])
        with overview:
            a, b, c = st.columns(3)
            a.metric("Bias", report.get("bias", "N/A"))
            b.metric("Confidence", f"{report.get('confidence', 0)}%")
            c.metric("Action", report.get("suggested_action", "Hold"))
        with points:
            for point in report.get("key_points", []):
                st.write(f"• {point}")
        with reasoning:
            st.write(report.get("reasoning", "No reasoning available."))

st.markdown("### Recent Analysis")
runs = load_today_history()
if runs:
    for run in reversed(runs[-3:]):
        final = run.get("reports", [])[-1] if run.get("reports") else {}
        with st.expander(f"{run['run_time'][11:19]} · {final.get('suggested_action', 'Hold')} · {final.get('confidence', 0)}% confidence"):
            st.write(final.get("summary", ""))
else:
    st.caption("No completed analysis yet today.")

st.markdown('<div class="disclaimer"><b>Risk notice:</b> This dashboard provides AI-assisted educational research and paper-trading support only. It does not guarantee outcomes and is not financial advice. Verify market data and levels independently.</div>', unsafe_allow_html=True)
