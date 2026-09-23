from __future__ import annotations
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def build_gold_chart(d: pd.DataFrame) -> go.Figure:
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.025,
        row_heights=[0.58, 0.14, 0.14, 0.14],
        specs=[[{'secondary_y': True}], [{}], [{}], [{}]],
    )
    fig.add_trace(go.Candlestick(
        x=d['Date'], open=d['Open'], high=d['High'], low=d['Low'], close=d['Close'],
        increasing_line_color='#70f2e5', increasing_fillcolor='#165f66',
        decreasing_line_color='#ff6f91', decreasing_fillcolor='#742c4e', name='XAU/USD'), row=1, col=1
    )
    fig.add_trace(go.Scatter(x=d['Date'], y=d['EMA20'], name='EMA 20', line=dict(color='#4bdcff', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=d['Date'], y=d['EMA50'], name='EMA 50', line=dict(color='#af91ff', width=1.4)), row=1, col=1)
    colors = ['#39d5b55a' if c >= o else '#ff64825a' for o, c in zip(d['Open'], d['Close'])]
    fig.add_trace(go.Bar(x=d['Date'], y=d['Volume'], marker_color=colors, name='Volume'), row=2, col=1)
    fig.add_trace(go.Scatter(x=d['Date'], y=d['RSI14'], name='RSI 14', line=dict(color='#c4a7ff', width=1.3)), row=3, col=1)
    fig.add_hline(y=70, line_dash='dot', line_color='#ffbd59', row=3, col=1)
    fig.add_hline(y=30, line_dash='dot', line_color='#4fd9bb', row=3, col=1)
    hist_colors = ['#45d9c0' if x >= 0 else '#ff667d' for x in d['MACD_HIST']]
    fig.add_trace(go.Bar(x=d['Date'], y=d['MACD_HIST'], marker_color=hist_colors, name='MACD histogram'), row=4, col=1)
    fig.add_trace(go.Scatter(x=d['Date'], y=d['MACD'], line=dict(color='#55dcff', width=1.2), name='MACD'), row=4, col=1)
    fig.add_trace(go.Scatter(x=d['Date'], y=d['MACD_SIGNAL'], line=dict(color='#ff9f7a', width=1.2), name='Signal'), row=4, col=1)
    fig.update_layout(
        height=760, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#061625',
        margin=dict(l=15, r=55, t=35, b=25), xaxis_rangeslider_visible=False, hovermode='x unified',
        legend=dict(orientation='h', y=1.03, x=0), font=dict(color='#dff7ff'),
    )
    fig.update_xaxes(gridcolor='rgba(84,153,183,.14)', showspikes=True, spikemode='across', spikesnap='cursor')
    fig.update_yaxes(gridcolor='rgba(84,153,183,.14)', side='right')
    fig.update_yaxes(range=[0, 100], row=3, col=1)
    return fig
