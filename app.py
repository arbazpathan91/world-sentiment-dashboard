import streamlit as st
import plotly.express as px
import pandas as pd
import time
from data_engine import fetch_live_sentiment_data

st.set_page_config(page_title="World Sentiment Index", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #00FFA6; font-family: monospace; font-size: 1.8rem !important; }
    div[data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
    .stDataFrame div { font-size: 11px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 PLANETARY MOOD MONITOR")
st.caption("Live global news vectors parsed via NLP sentiment scoring.")

if "master_stream" not in st.session_state:
    st.session_state.master_stream = fetch_live_sentiment_data()
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

current_time = time.time()
if current_time - st.session_state.last_refresh > 300:
    st.session_state.master_stream = pd.concat([st.session_state.master_stream, fetch_live_sentiment_data()]).tail(100)
    st.session_state.last_refresh = current_time

df = st.session_state.master_stream

if not df.empty:
    geo_df = df.groupby('ISO_Alpha').agg({'Sentiment': 'mean', 'Headline': 'count'}).reset_index().rename(columns={'Headline': 'Volume'})
    global_mean = df['Sentiment'].mean()
    mood_string = "OPTIMISTIC" if global_mean > 0.02 else ("PANIC" if global_mean < -0.02 else "NEUTRAL")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("SEN-INDEX", f"{global_mean:.3f}")
    m2.metric("MOOD AXIS", mood_string)
    m3.metric("VECTORS", f"{len(df)}")

    st.subheader("🗺️ Live Sentiment Topography")
    fig = px.choropleth(
        geo_df, locations="ISO_Alpha", color="Sentiment", hover_name="ISO_Alpha",
        color_continuous_scale=px.colors.diverging.RdYlGn, range_color=[-0.4, 0.4]
    )
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth', bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False})

    st.subheader("📰 Live Streaming Vector Ledger")
    st.dataframe(
        df.sort_values(by="Timestamp", ascending=False)[["CountryName", "Sentiment", "Headline"]],
        use_container_width=True, hide_index=True
    )
    
    time_left = int(300 - (current_time - st.session_state.last_refresh))
    st.caption(f"⏱️ Next automated data sync in {max(0, time_left)} seconds...")
else:
    st.warning("Connecting to global API endpoints...")

time.sleep(10)
st.rerun()
