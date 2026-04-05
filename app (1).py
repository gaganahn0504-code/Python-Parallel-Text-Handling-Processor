import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import sqlite3
import re
import time
from multiprocessing import Pool, cpu_count
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import io
import os
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from rules import PATTERN_RULES, WORD_SCORES, NEGATIONS, INTENSIFIERS

st.set_page_config(page_title="ParText — Sentiment Processor", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════
# CSS + PARTICLE ANIMATION via components.html
# ══════════════════════════════════════════════════════════
def inject_css():
    components.html("""<!DOCTYPE html><html><head><script>
const css = `
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Exo+2:wght@300;400;600;700&display=swap');

  :root {
    --cyan:   #00d4ff;
    --cyan2:  #0099cc;
    --green:  #00ff88;
    --red:    #ff3d6e;
    --yellow: #ffc94d;
    --bg:     #03080f;
    --card:   rgba(0,20,40,0.92);
    --border: rgba(0,212,255,0.18);
  }

  *, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }

  html, body { background:var(--bg) !important; }

  [data-testid="stAppViewContainer"] {
    background:
      radial-gradient(ellipse 60% 40% at 20% 20%, rgba(0,100,200,0.09) 0%, transparent 60%),
      radial-gradient(ellipse 50% 40% at 80% 80%, rgba(0,180,255,0.07) 0%, transparent 60%),
      radial-gradient(ellipse 80% 60% at 50% 0%,  rgba(0,212,255,0.06) 0%, transparent 55%),
      var(--bg) !important;
    font-family:'Exo 2',sans-serif !important;
    color:#cce8f8 !important;
  }

  [data-testid="stHeader"] { background:transparent !important; }
  #MainMenu, footer, header { visibility:hidden !important; }
  [data-testid="stToolbar"] { display:none !important; }
  .block-container { padding:1.5rem 2.5rem 4rem !important; max-width:100% !important; }

  /* ── Scanlines ── */
  [data-testid="stAppViewContainer"]::before {
    content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
    background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,212,255,0.012) 3px,rgba(0,212,255,0.012) 4px);
    animation:scan 12s linear infinite;
  }
  @keyframes scan { from{background-position:0 0} to{background-position:0 100px} }

  /* ── Corner vignette ── */
  [data-testid="stAppViewContainer"]::after {
    content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
    background:radial-gradient(ellipse 100% 100% at 50% 50%, transparent 50%, rgba(0,5,12,0.7) 100%);
  }

  /* ═══════════════════════════
     SIDEBAR
  ═══════════════════════════ */
  [data-testid="stSidebar"] {
    background:linear-gradient(160deg,#010a14 0%,#020d1a 60%,#010810 100%) !important;
    border-right:1px solid rgba(0,212,255,0.12) !important;
    width:250px !important; min-width:250px !important;
    box-shadow:4px 0 40px rgba(0,212,255,0.04) !important;
  }
  [data-testid="stSidebarContent"] { padding:0 !important; }
  [data-testid="stSidebarCollapseButton"] { display:none !important; }
  section[data-testid="stSidebar"] { transform:none !important; display:block !important; visibility:visible !important; }

  [data-testid="stSidebar"] .stButton > button {
    width:100% !important; background:transparent !important;
    border:none !important; border-left:2px solid transparent !important;
    color:rgba(0,180,220,0.4) !important;
    font-family:'Exo 2',sans-serif !important; font-size:12px !important;
    font-weight:600 !important; letter-spacing:2.5px !important;
    text-transform:uppercase !important; padding:13px 20px !important;
    text-align:left !important; border-radius:0 !important;
    box-shadow:none !important; transition:all 0.25s !important;
  }
  [data-testid="stSidebar"] .stButton > button:hover {
    background:rgba(0,212,255,0.06) !important;
    border-left-color:rgba(0,212,255,0.4) !important;
    color:var(--cyan) !important; box-shadow:none !important;
  }
  [data-testid="stSidebar"] .stButton > button:focus { box-shadow:none !important; outline:none !important; }

  /* ═══════════════════════════
     HEADER
  ═══════════════════════════ */
  .hdr-wrap { text-align:center; padding:2.8rem 0 2.2rem; position:relative; }
  .hdr-eyebrow {
    display:inline-flex; align-items:center; gap:8px;
    font-family:'Exo 2',sans-serif; font-size:10px; font-weight:700;
    letter-spacing:5px; color:var(--cyan); text-transform:uppercase;
    border:1px solid rgba(0,212,255,0.25); padding:5px 18px 5px 14px;
    border-radius:20px; margin-bottom:20px;
    background:rgba(0,212,255,0.04);
    box-shadow:0 0 20px rgba(0,212,255,0.08);
  }
  .hdr-eyebrow-dot {
    width:6px; height:6px; border-radius:50%; background:var(--cyan);
    box-shadow:0 0 8px var(--cyan); animation:blink 2s ease-in-out infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

  .hdr-title {
    font-family:'Orbitron',sans-serif;
    font-size:clamp(26px,4.5vw,52px); font-weight:900;
    line-height:1.05; letter-spacing:1px; color:#fff;
    text-shadow:0 0 40px rgba(0,212,255,0.5), 0 0 100px rgba(0,212,255,0.15);
    margin-bottom:14px;
  }
  .hdr-title .accent { color:var(--cyan); position:relative; }
  .hdr-title .accent::after {
    content:''; position:absolute; bottom:-3px; left:0; right:0; height:2px;
    background:linear-gradient(90deg,transparent,var(--cyan),transparent);
    box-shadow:0 0 10px var(--cyan);
  }
  .hdr-sub {
    font-size:13px; color:rgba(160,210,240,0.5);
    letter-spacing:2px; text-transform:uppercase; font-weight:300;
  }
  .hdr-sub span { color:rgba(0,212,255,0.5); margin:0 8px; }

  /* ═══════════════════════════
     SECTION HEADER
  ═══════════════════════════ */
  .sec-hdr {
    font-family:'Orbitron',sans-serif; font-size:10px; font-weight:700;
    letter-spacing:4px; color:rgba(0,212,255,0.6); text-transform:uppercase;
    margin:30px 0 16px; display:flex; align-items:center; gap:14px;
  }
  .sec-hdr::before { content:''; width:8px; height:8px; border:1.5px solid var(--cyan); transform:rotate(45deg); flex-shrink:0; box-shadow:0 0 6px rgba(0,212,255,0.5); }
  .sec-hdr::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,rgba(0,212,255,0.3),transparent); }

  /* ═══════════════════════════
     UPLOAD CARD
  ═══════════════════════════ */
  .upload-card {
    position:relative;
    background:linear-gradient(135deg,rgba(0,16,32,0.97) 0%,rgba(0,10,22,0.99) 100%);
    border:1px solid var(--border); border-radius:6px;
    padding:40px 48px 36px; margin-bottom:24px; overflow:hidden;
  }
  .upload-card::before {
    content:''; position:absolute; top:0; left:15%; right:15%; height:1px;
    background:linear-gradient(90deg,transparent,var(--cyan),rgba(0,212,255,0.3),transparent);
    box-shadow:0 0 25px 3px rgba(0,212,255,0.3);
  }
  .upload-card::after {
    content:''; position:absolute; bottom:0; right:0; width:80px; height:80px;
    border-bottom:1px solid rgba(0,212,255,0.2); border-right:1px solid rgba(0,212,255,0.2);
  }
  .corner-tr { position:absolute; top:0; right:0; width:80px; height:80px; border-top:1px solid rgba(0,212,255,0.2); border-right:1px solid rgba(0,212,255,0.2); }
  .corner-bl { position:absolute; bottom:0; left:0; width:80px; height:80px; border-bottom:1px solid rgba(0,212,255,0.2); border-left:1px solid rgba(0,212,255,0.2); }
  .corner-tl { position:absolute; top:0; left:0; width:80px; height:80px; border-top:1px solid rgba(0,212,255,0.2); border-left:1px solid rgba(0,212,255,0.2); }

  /* animated grid bg inside card */
  .upload-card-bg {
    position:absolute; inset:0; pointer-events:none; opacity:0.025;
    background-image:linear-gradient(rgba(0,212,255,1) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,255,1) 1px,transparent 1px);
    background-size:40px 40px;
  }

  .upload-label {
    font-family:'Orbitron',sans-serif; font-size:9px; font-weight:700;
    letter-spacing:4px; color:rgba(0,212,255,0.5); text-transform:uppercase;
    margin-bottom:20px; display:flex; align-items:center; gap:12px;
  }
  .upload-label::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,rgba(0,212,255,0.25),transparent); }

  .upload-icon-wrap { text-align:center; margin-bottom:10px; }
  .upload-icon-wrap svg { filter:drop-shadow(0 0 16px rgba(0,212,255,0.6)); animation:float 4s ease-in-out infinite; }
  @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }

  /* file uploader overrides */
  [data-testid="stFileUploader"] { background:transparent !important; }
  [data-testid="stFileUploader"] > div {
    background:rgba(0,212,255,0.025) !important;
    border:1.5px dashed rgba(0,212,255,0.25) !important;
    border-radius:6px !important; padding:28px !important; transition:all .3s !important;
  }
  [data-testid="stFileUploader"] > div:hover {
    border-color:rgba(0,212,255,0.6) !important;
    background:rgba(0,212,255,0.05) !important;
    box-shadow:0 0 40px rgba(0,212,255,0.08) inset, 0 0 40px rgba(0,212,255,0.05) !important;
  }
  [data-testid="stFileUploader"] section { background:transparent !important; border:none !important; }
  [data-testid="stFileUploaderDropzoneInstructions"] { color:rgba(160,210,240,0.45) !important; font-family:'Exo 2',sans-serif !important; font-size:14px !important; font-weight:300 !important; }
  [data-testid="stFileUploaderDropzoneInstructions"] span { color:var(--cyan) !important; font-weight:600 !important; }
  [data-testid="stBaseButton-secondary"] {
    background:rgba(0,212,255,0.08) !important; border:1px solid rgba(0,212,255,0.35) !important;
    color:var(--cyan) !important; font-family:'Exo 2',sans-serif !important;
    font-size:11px !important; font-weight:600 !important; letter-spacing:2px !important; border-radius:4px !important;
    transition:all .2s !important;
  }
  [data-testid="stBaseButton-secondary"]:hover { background:rgba(0,212,255,0.15) !important; box-shadow:0 0 20px rgba(0,212,255,0.2) !important; }

  /* ═══════════════════════════
     CHIPS
  ═══════════════════════════ */
  .chips-row { display:flex; gap:10px; justify-content:center; margin-top:20px; flex-wrap:wrap; }
  .chip {
    display:inline-flex; align-items:center; gap:7px;
    font-family:'Exo 2',sans-serif; font-size:10px; font-weight:600; letter-spacing:2px;
    color:rgba(0,200,240,0.55); border:1px solid rgba(0,212,255,0.12);
    background:rgba(0,212,255,0.03); padding:6px 16px; border-radius:20px; text-transform:uppercase;
  }
  .chip-dot { width:5px; height:5px; border-radius:50%; background:var(--cyan); box-shadow:0 0 8px var(--cyan); animation:blink 3s ease-in-out infinite; }

  /* ═══════════════════════════
     MAIN BUTTONS
  ═══════════════════════════ */
  [data-testid="stMain"] .stButton > button {
    width:100%;
    background:linear-gradient(135deg,rgba(0,212,255,0.12) 0%,rgba(0,120,200,0.08) 100%) !important;
    border:1px solid rgba(0,212,255,0.45) !important; color:var(--cyan) !important;
    font-family:'Orbitron',sans-serif !important; font-size:11px !important;
    font-weight:700 !important; letter-spacing:4px !important;
    padding:16px 0 !important; border-radius:4px !important;
    transition:all .3s !important; text-transform:uppercase !important;
    box-shadow:0 0 25px rgba(0,212,255,0.08), inset 0 0 25px rgba(0,212,255,0.03) !important;
    position:relative !important; overflow:hidden !important;
  }
  [data-testid="stMain"] .stButton > button:hover {
    background:linear-gradient(135deg,rgba(0,212,255,0.2) 0%,rgba(0,140,220,0.15) 100%) !important;
    box-shadow:0 0 50px rgba(0,212,255,0.25), inset 0 0 30px rgba(0,212,255,0.06) !important;
    border-color:var(--cyan) !important; transform:translateY(-1px) !important;
  }

  /* ═══════════════════════════
     SELECTBOX & INPUT
  ═══════════════════════════ */
  [data-testid="stSelectbox"] label, [data-testid="stTextInput"] label {
    font-family:'Exo 2',sans-serif !important; font-size:10px !important;
    letter-spacing:3px !important; color:rgba(0,212,255,0.5) !important;
    text-transform:uppercase !important; font-weight:700 !important;
  }
  [data-testid="stSelectbox"] > div > div {
    background:rgba(0,10,25,0.95) !important; border:1px solid rgba(0,212,255,0.2) !important;
    border-radius:4px !important; color:#cce8f8 !important; font-family:'Exo 2',sans-serif !important;
    transition:border-color .2s !important;
  }
  [data-testid="stSelectbox"] > div > div:focus-within { border-color:rgba(0,212,255,0.5) !important; box-shadow:0 0 15px rgba(0,212,255,0.08) !important; }
  [data-testid="stTextInput"] input {
    background:rgba(0,10,25,0.95) !important; border:1px solid rgba(0,212,255,0.2) !important;
    border-radius:4px !important; color:#cce8f8 !important; font-family:'Exo 2',sans-serif !important;
  }
  [data-testid="stTextInput"] input:focus { border-color:rgba(0,212,255,0.5) !important; box-shadow:0 0 15px rgba(0,212,255,0.08) !important; outline:none !important; }

  /* ═══════════════════════════
     METRICS
  ═══════════════════════════ */
  [data-testid="stMetric"] {
    background:linear-gradient(135deg,rgba(0,16,34,0.96),rgba(0,10,24,0.98)) !important;
    border:1px solid var(--border) !important; border-radius:5px !important;
    padding:20px 22px !important; position:relative; overflow:hidden;
    transition:transform .2s, box-shadow .2s !important;
  }
  [data-testid="stMetric"]:hover { transform:translateY(-2px) !important; box-shadow:0 8px 30px rgba(0,212,255,0.1) !important; }
  [data-testid="stMetric"]::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,var(--cyan),rgba(0,212,255,0.2),transparent); }
  [data-testid="stMetric"]::after { content:''; position:absolute; bottom:0; right:0; width:30px; height:30px; border-bottom:1px solid rgba(0,212,255,0.2); border-right:1px solid rgba(0,212,255,0.2); }
  [data-testid="stMetricLabel"] { font-family:'Exo 2',sans-serif !important; font-size:9px !important; font-weight:700 !important; letter-spacing:3px !important; color:rgba(0,212,255,0.45) !important; text-transform:uppercase !important; }
  [data-testid="stMetricValue"] { font-family:'Orbitron',sans-serif !important; font-size:28px !important; font-weight:700 !important; color:#fff !important; text-shadow:0 0 25px rgba(0,212,255,0.4) !important; }

  /* ═══════════════════════════
     BARS
  ═══════════════════════════ */
  .bar-section { background:linear-gradient(135deg,rgba(0,16,32,0.96),rgba(0,10,22,0.98)); border:1px solid var(--border); border-radius:5px; padding:24px 28px; margin-bottom:16px; position:relative; overflow:hidden; }
  .bar-section::before { content:''; position:absolute; top:0; left:15%; right:15%; height:1px; background:linear-gradient(90deg,transparent,rgba(0,212,255,0.2),transparent); }
  .bar-wrap { margin-bottom:18px; }
  .bar-wrap:last-child { margin-bottom:0; }
  .bar-label { font-family:'Exo 2',sans-serif; font-size:11px; font-weight:700; letter-spacing:2px; color:rgba(0,200,240,0.7); text-transform:uppercase; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; }
  .bar-label .bar-val { font-family:'Orbitron',sans-serif; font-size:13px; font-weight:700; }
  .bar-track { background:rgba(255,255,255,0.04); border-radius:3px; height:12px; overflow:hidden; position:relative; }
  .bar-track::before { content:''; position:absolute; inset:0; background:repeating-linear-gradient(90deg,transparent,transparent 20px,rgba(255,255,255,0.02) 20px,rgba(255,255,255,0.02) 21px); }
  .bar-fill { height:100%; border-radius:3px; position:relative; transition:width 1s ease; }
  .bar-fill::after { content:''; position:absolute; top:0; right:0; bottom:0; width:4px; background:rgba(255,255,255,0.4); border-radius:3px; }
  .bar-pos { background:linear-gradient(90deg,rgba(0,180,100,0.7),var(--green)); box-shadow:0 0 12px rgba(0,255,136,0.35); }
  .bar-neg { background:linear-gradient(90deg,rgba(180,30,60,0.7),var(--red));   box-shadow:0 0 12px rgba(255,61,110,0.35); }
  .bar-neu { background:linear-gradient(90deg,rgba(180,140,0,0.7),var(--yellow)); box-shadow:0 0 12px rgba(255,201,77,0.35); }

  /* ═══════════════════════════
     DB BADGE
  ═══════════════════════════ */
  .db-badge {
    display:inline-flex; align-items:center; gap:10px;
    background:linear-gradient(135deg,rgba(0,255,136,0.05),rgba(0,200,100,0.03));
    border:1px solid rgba(0,255,136,0.2); border-radius:4px;
    padding:12px 20px; margin-bottom:8px;
    font-family:'Exo 2',sans-serif; font-size:13px; font-weight:600;
    color:rgba(0,255,136,0.75); letter-spacing:1px;
  }
  .db-badge svg { flex-shrink:0; opacity:0.8; }

  /* ═══════════════════════════
     PROGRESS
  ═══════════════════════════ */
  [data-testid="stProgress"] > div { background:rgba(0,212,255,0.08) !important; border-radius:3px !important; height:6px !important; }
  [data-testid="stProgress"] > div > div { background:linear-gradient(90deg,var(--cyan2),var(--cyan)) !important; box-shadow:0 0 15px rgba(0,212,255,0.6) !important; border-radius:3px !important; }

  /* ═══════════════════════════
     DATAFRAME
  ═══════════════════════════ */
  [data-testid="stDataFrame"] { border:1px solid rgba(0,212,255,0.12) !important; border-radius:5px !important; overflow:hidden !important; }

  /* ═══════════════════════════
     ALERTS
  ═══════════════════════════ */
  [data-testid="stAlert"] { border-radius:4px !important; font-family:'Exo 2',sans-serif !important; font-size:14px !important; font-weight:600 !important; }

  /* ═══════════════════════════
     DOWNLOAD BUTTON
  ═══════════════════════════ */
  [data-testid="stDownloadButton"] > button {
    background:rgba(0,255,136,0.05) !important; border:1px solid rgba(0,255,136,0.25) !important;
    color:var(--green) !important; font-family:'Exo 2',sans-serif !important;
    font-size:11px !important; font-weight:700 !important; letter-spacing:2px !important;
    border-radius:4px !important; transition:all .2s !important;
  }
  [data-testid="stDownloadButton"] > button:hover { background:rgba(0,255,136,0.1) !important; box-shadow:0 0 20px rgba(0,255,136,0.15) !important; }

  /* ═══════════════════════════
     TIMING STAT
  ═══════════════════════════ */
  .time-stat {
    display:inline-flex; align-items:center; gap:8px; margin-top:16px;
    font-family:'Exo 2',sans-serif; font-size:11px; font-weight:600;
    letter-spacing:2px; color:rgba(0,212,255,0.35); text-transform:uppercase;
  }
  .time-stat::before { content:''; width:5px; height:5px; border-radius:50%; background:var(--cyan); box-shadow:0 0 8px var(--cyan); flex-shrink:0; }

  /* ═══════════════════════════
     FOOTER
  ═══════════════════════════ */
  .footer {
    text-align:center; color:rgba(0,180,220,0.2); margin-top:60px;
    font-family:'Exo 2',sans-serif; font-size:10px; letter-spacing:4px; text-transform:uppercase;
  }
  .footer b { color:rgba(0,212,255,0.3); font-weight:600; }
`;
const el = window.parent.document.createElement('style');
el.id = 'partext-theme';
if (!window.parent.document.getElementById('partext-theme')) {
  el.innerHTML = css;
  window.parent.document.head.appendChild(el);
} else {
  window.parent.document.getElementById('partext-theme').innerHTML = css;
}
</script></head><body style="background:transparent;margin:0;padding:0;height:0;overflow:hidden;"></body></html>""",
    height=0, scrolling=False)


# ══════════════════════════════════════════
# SCORING ENGINE
# ══════════════════════════════════════════
# Rules imported from rules.py

def calculate_score(text):
    original = str(text); low = original.lower(); score = 0
    for pattern, value in PATTERN_RULES:
        if re.search(pattern, low): score += value
    words = re.findall(r"\b\w+\b", low)
    negate, boost = False, 1
    for w in words:
        if w in NEGATIONS:    negate = True; continue
        if w in INTENSIFIERS: boost = 2;     continue
        ws = WORD_SCORES.get(w, 0)
        if negate: ws *= -1; negate = False
        score += ws * boost; boost = 1
    sentiment = "Positive" if score > 1 else ("Negative" if score < -1 else "Neutral")
    return (original, score, sentiment)


# ══════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════
DB_NAME = "flipkart_sentiment.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT,
        score INTEGER, sentiment TEXT, run_id TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit(); conn.close()

def store_results(rows, run_id):
    conn = sqlite3.connect(DB_NAME)
    conn.executemany(
        "INSERT INTO results (text, score, sentiment, run_id) VALUES (?, ?, ?, ?)",
        [(r[0], r[1], r[2], run_id) for r in rows])
    conn.commit(); conn.close()

init_db()

# ══════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════
for key, default in {
    "page":"upload","df":None,"selected_col":None,
    "results":None,"filename":"","elapsed":0,"run_id":""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ══════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown("""
<div style="padding:32px 22px 22px; border-bottom:1px solid rgba(0,212,255,0.1); margin-bottom:6px;">
  <div style="font-family:'Orbitron',sans-serif; font-size:18px; font-weight:900;
              letter-spacing:2px; color:#00d4ff;
              text-shadow:0 0 30px rgba(0,212,255,0.6),0 0 60px rgba(0,212,255,0.2);">
    PARTEXT
  </div>
  <div style="font-family:'Exo 2',sans-serif; font-size:9px; letter-spacing:3px;
              color:rgba(0,180,220,0.3); text-transform:uppercase; margin-top:6px; font-weight:600;">
    Sentiment Processor &nbsp;v2.0
  </div>
  <div style="margin-top:14px; display:flex; align-items:center; gap:8px;">
    <div style="width:5px;height:5px;border-radius:50%;background:#00ff88;
                box-shadow:0 0 8px #00ff88; animation:blink 2s infinite;"></div>
    <span style="font-family:'Exo 2',sans-serif; font-size:9px; letter-spacing:2px;
                 color:rgba(0,255,136,0.5); text-transform:uppercase; font-weight:600;">System Online</span>
  </div>
</div>
""", unsafe_allow_html=True)

        # Nav label
        st.markdown("""
<div style="font-family:'Exo 2',sans-serif; font-size:8px; font-weight:700;
            letter-spacing:4px; color:rgba(0,180,220,0.25); text-transform:uppercase;
            padding:14px 22px 6px;">Navigation</div>
""", unsafe_allow_html=True)

        # Upload button
        is_upload = st.session_state.page == "upload"
        if is_upload:
            st.markdown("""<style>[data-testid="stSidebar"] div[data-testid="stButton"]:nth-of-type(1) button
            { border-left:2px solid #00d4ff !important; background:rgba(0,212,255,0.07) !important; color:#00d4ff !important; }</style>""",
            unsafe_allow_html=True)
        if st.button("  Upload CSV", key="nav_upload", use_container_width=True):
            st.session_state.page = "upload"; st.session_state.results = None
            st.session_state.df = None; st.rerun()

        # Results button
        has_results = st.session_state.results is not None
        is_results  = st.session_state.page == "results"
        if is_results:
            st.markdown("""<style>[data-testid="stSidebar"] div[data-testid="stButton"]:nth-of-type(2) button
            { border-left:2px solid #00d4ff !important; background:rgba(0,212,255,0.07) !important; color:#00d4ff !important; }</style>""",
            unsafe_allow_html=True)
        if st.button("  Results", key="nav_results", use_container_width=True, disabled=not has_results):
            st.session_state.page = "results"; st.rerun()

        # Divider
        st.markdown("""
<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.12),transparent);margin:16px 0;"></div>
<div style="font-family:'Exo 2',sans-serif;font-size:8px;font-weight:700;
            letter-spacing:4px;color:rgba(0,180,220,0.25);text-transform:uppercase;padding:0 22px 8px;">Status</div>
""", unsafe_allow_html=True)

        # Status
        if st.session_state.df is not None:
            rows = len(st.session_state.df)
            st.markdown(f"""
<div style="padding:8px 22px;font-family:'Exo 2',sans-serif;font-size:11px;font-weight:600;
            letter-spacing:1px;color:rgba(0,255,136,0.6);display:flex;align-items:center;gap:8px;">
  <div style="width:5px;height:5px;border-radius:50%;background:#00ff88;box-shadow:0 0 6px #00ff88;flex-shrink:0;"></div>
  File loaded &middot; {rows:,} rows
</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div style="padding:8px 22px;font-family:'Exo 2',sans-serif;font-size:11px;font-weight:600;
            letter-spacing:1px;color:rgba(0,180,220,0.2);">No file loaded</div>""", unsafe_allow_html=True)

        if has_results:
            total = len(st.session_state.results)
            pos = sum(1 for r in st.session_state.results if r[2]=="Positive")
            neg = sum(1 for r in st.session_state.results if r[2]=="Negative")
            st.markdown(f"""
<div style="padding:6px 22px 4px;font-family:'Exo 2',sans-serif;font-size:11px;font-weight:600;
            letter-spacing:1px;color:rgba(0,255,136,0.6);display:flex;align-items:center;gap:8px;">
  <div style="width:5px;height:5px;border-radius:50%;background:#00ff88;box-shadow:0 0 6px #00ff88;flex-shrink:0;"></div>
  {total:,} records scored
</div>
<div style="padding:4px 22px 4px 35px;font-family:'Exo 2',sans-serif;font-size:10px;
            letter-spacing:1px;color:rgba(0,255,136,0.35);">
  +{pos:,} pos &nbsp; &minus;{neg:,} neg
</div>""", unsafe_allow_html=True)

        # Footer
        st.markdown("""
<div style="position:absolute;bottom:18px;left:0;right:0;text-align:center;
            font-family:'Exo 2',sans-serif;font-size:9px;letter-spacing:3px;
            color:rgba(0,180,220,0.15);text-transform:uppercase;">
  Internship Project
</div>""", unsafe_allow_html=True)



# ══════════════════════════════════════════
# EMAIL REPORT SENDER
# ══════════════════════════════════════════
# ── Hardcoded sender — users never need to enter credentials ──
SENDER_EMAIL    = "nikhilbaratam566@gmail.com"
SENDER_PASSWORD = "ghkpjwrglbnzsmos"   # app password without spaces

def send_email_report(to_email, res_df, filename, run_id, elapsed, pos_pct, neg_pct, neu_pct):
    """Send rich HTML report + CSV attachment via Gmail SMTP."""
    sender_email    = SENDER_EMAIL
    sender_password = SENDER_PASSWORD
    total     = len(res_df)
    pos_count = int((res_df["Sentiment"]=="Positive").sum())
    neg_count = int((res_df["Sentiment"]=="Negative").sum())
    neu_count = int((res_df["Sentiment"]=="Neutral").sum())
    avg_score = res_df["Score"].mean()
    max_score = int(res_df["Score"].max())
    min_score = int(res_df["Score"].min())
    high_pos  = int((res_df["Score"] >= 4).sum())
    high_neg  = int((res_df["Score"] <= -4).sum())

    # ── SVG Donut chart values ──
    # Circle circumference for r=52 is ~326.7
    circ = 326.73
    pos_dash = round(pos_pct / 100 * circ, 2)
    neg_dash = round(neg_pct / 100 * circ, 2)
    neu_dash = round(neu_pct / 100 * circ, 2)
    pos_off  = 0
    neg_off  = round(-pos_dash, 2)
    neu_off  = round(-(pos_dash + neg_dash), 2)

    # ── Score distribution buckets ──
    bins   = {"Very High (≥4)":0, "High (2-3)":0, "Neutral (-1 to 1)":0, "Low (-2 to -3)":0, "Very Low (≤-4)":0}
    for s in res_df["Score"]:
        if s >= 4:   bins["Very High (≥4)"] += 1
        elif s >= 2: bins["High (2-3)"] += 1
        elif s >= -1:bins["Neutral (-1 to 1)"] += 1
        elif s >= -3:bins["Low (-2 to -3)"] += 1
        else:        bins["Very Low (≤-4)"] += 1
    max_bin = max(bins.values()) or 1

    def bin_bar(count, color):
        pct = round(count / max_bin * 100)
        return f"""<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
          <div style="width:130px;font-size:10px;color:rgba(0,200,240,0.6);letter-spacing:1px;">{{}}</div>
          <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:3px;height:14px;overflow:hidden;">
            <div style="width:{pct}%;height:100%;background:{color};border-radius:3px;"></div>
          </div>
          <div style="width:55px;text-align:right;font-size:11px;font-weight:700;color:{color};">{{}}</div>
        </div>"""

    dist_html = ""
    colors = ["#00ff88","#00d4ff","#ffc94d","#ff8c42","#ff3d6e"]
    for (label, count), color in zip(bins.items(), colors):
        pct2 = round(count / max_bin * 100)
        dist_html += f"""<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
          <div style="width:140px;font-size:10px;color:rgba(0,200,240,0.55);letter-spacing:0.5px;">{label}</div>
          <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:3px;height:14px;overflow:hidden;">
            <div style="width:{pct2}%;height:100%;background:{color};border-radius:3px;"></div>
          </div>
          <div style="min-width:55px;text-align:right;font-size:11px;font-weight:700;color:{color};">{count:,}</div>
        </div>"""

    # ── Top 5 positive samples ──
    top_pos = res_df[res_df["Sentiment"]=="Positive"].nlargest(5,"Score")[["Text","Score"]]
    top_neg = res_df[res_df["Sentiment"]=="Negative"].nsmallest(5,"Score")[["Text","Score"]]

    def sample_rows(df, color):
        rows = ""
        for _, r in df.iterrows():
            txt = str(r["Text"])[:90] + ("…" if len(str(r["Text"])) > 90 else "")
            rows += f"""<tr>
              <td style="padding:10px 14px;font-size:12px;color:#cce8f8;border-bottom:1px solid rgba(0,212,255,0.07);">{txt}</td>
              <td style="padding:10px 14px;text-align:center;font-size:13px;font-weight:800;color:{color};border-bottom:1px solid rgba(0,212,255,0.07);">{int(r["Score"]):+d}</td>
            </tr>"""
        return rows

    # ── Insight sentence ──
    dominant = "Positive" if pos_count > neg_count and pos_count > neu_count                else ("Negative" if neg_count > pos_count and neg_count > neu_count else "Neutral")
    dom_color = "#00ff88" if dominant=="Positive" else ("#ff3d6e" if dominant=="Negative" else "#ffc94d")
    insight = (f"Overall sentiment is <b style='color:{dom_color}'>{dominant}</b>. "
               f"{pos_pct:.1f}% of reviews are positive and {neg_pct:.1f}% are negative. "
               f"Average score of <b style='color:#00d4ff'>{avg_score:+.2f}</b> indicates "
               + ("strong customer satisfaction." if avg_score >= 2
                  else "moderate satisfaction." if avg_score >= 0
                  else "customer dissatisfaction that needs attention."))

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#03080f;font-family:'Segoe UI',Arial,sans-serif;">
<div style="max-width:640px;margin:0 auto;background:#03080f;color:#cce8f8;">

  <!-- ══ HEADER ══ -->
  <div style="background:linear-gradient(135deg,#010d1f 0%,#021428 100%);padding:40px 40px 32px;border-bottom:2px solid rgba(0,212,255,0.15);position:relative;">
    <div style="font-size:9px;letter-spacing:6px;color:rgba(0,212,255,0.4);text-transform:uppercase;margin-bottom:12px;">
      ParText &nbsp;·&nbsp; Sentiment Processor v2.0
    </div>
    <div style="font-size:30px;font-weight:800;color:#ffffff;letter-spacing:0.5px;line-height:1.2;">
      Sentiment Analysis<br>Report
    </div>
    <div style="margin-top:14px;font-size:12px;color:rgba(0,180,220,0.4);letter-spacing:1px;">
      File: <b style="color:rgba(0,212,255,0.6);">{filename}</b> &nbsp;·&nbsp; Run: <b style="color:rgba(0,212,255,0.6);">{run_id}</b>
    </div>
    <div style="position:absolute;top:0;right:0;width:120px;height:120px;
      border-top:1px solid rgba(0,212,255,0.15);border-right:1px solid rgba(0,212,255,0.15);"></div>
  </div>

  <!-- ══ KPI CARDS ══ -->
  <div style="display:flex;border-bottom:1px solid rgba(0,212,255,0.1);">
    <div style="flex:1;padding:24px 20px;border-right:1px solid rgba(0,212,255,0.08);text-align:center;">
      <div style="font-size:8px;letter-spacing:3px;color:rgba(0,212,255,0.4);text-transform:uppercase;margin-bottom:8px;">Total</div>
      <div style="font-size:28px;font-weight:800;color:#fff;">{total:,}</div>
      <div style="font-size:9px;color:rgba(0,212,255,0.3);margin-top:4px;">reviews</div>
    </div>
    <div style="flex:1;padding:24px 20px;border-right:1px solid rgba(0,212,255,0.08);text-align:center;">
      <div style="font-size:8px;letter-spacing:3px;color:rgba(0,212,255,0.4);text-transform:uppercase;margin-bottom:8px;">Positive</div>
      <div style="font-size:28px;font-weight:800;color:#00ff88;">{pos_count:,}</div>
      <div style="font-size:9px;color:#00ff88;opacity:0.5;margin-top:4px;">{pos_pct:.1f}%</div>
    </div>
    <div style="flex:1;padding:24px 20px;border-right:1px solid rgba(0,212,255,0.08);text-align:center;">
      <div style="font-size:8px;letter-spacing:3px;color:rgba(0,212,255,0.4);text-transform:uppercase;margin-bottom:8px;">Negative</div>
      <div style="font-size:28px;font-weight:800;color:#ff3d6e;">{neg_count:,}</div>
      <div style="font-size:9px;color:#ff3d6e;opacity:0.5;margin-top:4px;">{neg_pct:.1f}%</div>
    </div>
    <div style="flex:1;padding:24px 20px;border-right:1px solid rgba(0,212,255,0.08);text-align:center;">
      <div style="font-size:8px;letter-spacing:3px;color:rgba(0,212,255,0.4);text-transform:uppercase;margin-bottom:8px;">Neutral</div>
      <div style="font-size:28px;font-weight:800;color:#ffc94d;">{neu_count:,}</div>
      <div style="font-size:9px;color:#ffc94d;opacity:0.5;margin-top:4px;">{neu_pct:.1f}%</div>
    </div>
    <div style="flex:1;padding:24px 20px;text-align:center;">
      <div style="font-size:8px;letter-spacing:3px;color:rgba(0,212,255,0.4);text-transform:uppercase;margin-bottom:8px;">Avg Score</div>
      <div style="font-size:28px;font-weight:800;color:#00d4ff;">{avg_score:+.2f}</div>
      <div style="font-size:9px;color:rgba(0,212,255,0.3);margin-top:4px;">out of ±10</div>
    </div>
  </div>

  <!-- ══ INSIGHT BANNER ══ -->
  <div style="background:rgba(0,212,255,0.04);border-left:3px solid rgba(0,212,255,0.4);
              padding:16px 24px;margin:24px 32px;border-radius:0 4px 4px 0;">
    <div style="font-size:9px;letter-spacing:3px;color:rgba(0,212,255,0.4);text-transform:uppercase;margin-bottom:6px;">AI Insight</div>
    <div style="font-size:13px;color:rgba(200,232,248,0.8);line-height:1.7;">{insight}</div>
  </div>

  <!-- ══ DONUT CHART + BREAKDOWN BARS ══ -->
  <div style="padding:8px 32px 28px;">
    <div style="font-size:9px;letter-spacing:4px;color:rgba(0,212,255,0.4);text-transform:uppercase;margin-bottom:20px;padding-top:16px;
      border-top:1px solid rgba(0,212,255,0.08);">Sentiment Distribution</div>

    <div style="display:flex;align-items:center;gap:32px;">

      <!-- SVG Donut -->
      <div style="flex-shrink:0;">
        <svg width="150" height="150" viewBox="0 0 150 150">
          <circle cx="75" cy="75" r="52" fill="none" stroke="rgba(255,255,255,0.04)" stroke-width="18"/>
          <!-- Positive arc -->
          <circle cx="75" cy="75" r="52" fill="none" stroke="#00ff88" stroke-width="18"
            stroke-dasharray="{pos_dash} {circ}" stroke-dashoffset="{pos_off}"
            stroke-linecap="butt" transform="rotate(-90 75 75)"/>
          <!-- Negative arc -->
          <circle cx="75" cy="75" r="52" fill="none" stroke="#ff3d6e" stroke-width="18"
            stroke-dasharray="{neg_dash} {circ}" stroke-dashoffset="{neg_off}"
            stroke-linecap="butt" transform="rotate(-90 75 75)"/>
          <!-- Neutral arc -->
          <circle cx="75" cy="75" r="52" fill="none" stroke="#ffc94d" stroke-width="18"
            stroke-dasharray="{neu_dash} {circ}" stroke-dashoffset="{neu_off}"
            stroke-linecap="butt" transform="rotate(-90 75 75)"/>
          <!-- Centre label -->
          <text x="75" y="69" text-anchor="middle" fill="#ffffff" font-size="18" font-weight="800"
            font-family="Arial">{total:,}</text>
          <text x="75" y="85" text-anchor="middle" fill="rgba(0,212,255,0.5)" font-size="8"
            letter-spacing="2" font-family="Arial">REVIEWS</text>
        </svg>
      </div>

      <!-- Legend + bars -->
      <div style="flex:1;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
          <div style="width:12px;height:12px;border-radius:50%;background:#00ff88;flex-shrink:0;"></div>
          <div style="flex:1;">
            <div style="display:flex;justify-content:space-between;font-size:10px;color:rgba(0,200,240,0.6);margin-bottom:4px;">
              <span>Positive</span><span style="color:#00ff88;font-weight:700;">{pos_count:,} · {pos_pct:.1f}%</span>
            </div>
            <div style="background:rgba(255,255,255,0.05);border-radius:2px;height:8px;">
              <div style="width:{pos_pct}%;height:100%;background:linear-gradient(90deg,#00cc66,#00ff88);border-radius:2px;"></div>
            </div>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
          <div style="width:12px;height:12px;border-radius:50%;background:#ff3d6e;flex-shrink:0;"></div>
          <div style="flex:1;">
            <div style="display:flex;justify-content:space-between;font-size:10px;color:rgba(0,200,240,0.6);margin-bottom:4px;">
              <span>Negative</span><span style="color:#ff3d6e;font-weight:700;">{neg_count:,} · {neg_pct:.1f}%</span>
            </div>
            <div style="background:rgba(255,255,255,0.05);border-radius:2px;height:8px;">
              <div style="width:{neg_pct}%;height:100%;background:linear-gradient(90deg,#cc2244,#ff3d6e);border-radius:2px;"></div>
            </div>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:10px;">
          <div style="width:12px;height:12px;border-radius:50%;background:#ffc94d;flex-shrink:0;"></div>
          <div style="flex:1;">
            <div style="display:flex;justify-content:space-between;font-size:10px;color:rgba(0,200,240,0.6);margin-bottom:4px;">
              <span>Neutral</span><span style="color:#ffc94d;font-weight:700;">{neu_count:,} · {neu_pct:.1f}%</span>
            </div>
            <div style="background:rgba(255,255,255,0.05);border-radius:2px;height:8px;">
              <div style="width:{neu_pct}%;height:100%;background:linear-gradient(90deg,#cc9900,#ffc94d);border-radius:2px;"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ══ SCORE DISTRIBUTION ══ -->
  <div style="padding:24px 32px 28px;border-top:1px solid rgba(0,212,255,0.08);">
    <div style="font-size:9px;letter-spacing:4px;color:rgba(0,212,255,0.4);text-transform:uppercase;margin-bottom:20px;">Score Distribution</div>
    {dist_html}
  </div>

  <!-- ══ QUICK STATS ROW ══ -->
  <div style="display:flex;gap:0;border-top:1px solid rgba(0,212,255,0.08);border-bottom:1px solid rgba(0,212,255,0.08);">
    <div style="flex:1;padding:18px 20px;text-align:center;border-right:1px solid rgba(0,212,255,0.08);">
      <div style="font-size:8px;letter-spacing:2px;color:rgba(0,212,255,0.35);text-transform:uppercase;margin-bottom:6px;">Highest Score</div>
      <div style="font-size:22px;font-weight:800;color:#00ff88;">+{max_score}</div>
    </div>
    <div style="flex:1;padding:18px 20px;text-align:center;border-right:1px solid rgba(0,212,255,0.08);">
      <div style="font-size:8px;letter-spacing:2px;color:rgba(0,212,255,0.35);text-transform:uppercase;margin-bottom:6px;">Lowest Score</div>
      <div style="font-size:22px;font-weight:800;color:#ff3d6e;">{min_score}</div>
    </div>
    <div style="flex:1;padding:18px 20px;text-align:center;border-right:1px solid rgba(0,212,255,0.08);">
      <div style="font-size:8px;letter-spacing:2px;color:rgba(0,212,255,0.35);text-transform:uppercase;margin-bottom:6px;">Strong Positives</div>
      <div style="font-size:22px;font-weight:800;color:#00ff88;">{high_pos:,}</div>
    </div>
    <div style="flex:1;padding:18px 20px;text-align:center;">
      <div style="font-size:8px;letter-spacing:2px;color:rgba(0,212,255,0.35);text-transform:uppercase;margin-bottom:6px;">Strong Negatives</div>
      <div style="font-size:22px;font-weight:800;color:#ff3d6e;">{high_neg:,}</div>
    </div>
  </div>

  <!-- ══ TOP POSITIVE REVIEWS ══ -->
  <div style="padding:24px 32px 8px;">
    <div style="font-size:9px;letter-spacing:4px;color:rgba(0,212,255,0.4);text-transform:uppercase;margin-bottom:16px;">Top Positive Reviews</div>
    <table style="width:100%;border-collapse:collapse;background:rgba(0,255,136,0.02);border:1px solid rgba(0,255,136,0.12);border-radius:4px;overflow:hidden;">
      <tr style="background:rgba(0,255,136,0.06);">
        <th style="padding:10px 14px;text-align:left;font-size:9px;letter-spacing:2px;color:rgba(0,255,136,0.5);text-transform:uppercase;">Review</th>
        <th style="padding:10px 14px;text-align:center;font-size:9px;letter-spacing:2px;color:rgba(0,255,136,0.5);text-transform:uppercase;">Score</th>
      </tr>
      {sample_rows(top_pos, "#00ff88")}
    </table>
  </div>

  <!-- ══ TOP NEGATIVE REVIEWS ══ -->
  <div style="padding:16px 32px 24px;">
    <div style="font-size:9px;letter-spacing:4px;color:rgba(0,212,255,0.4);text-transform:uppercase;margin-bottom:16px;">Top Negative Reviews</div>
    <table style="width:100%;border-collapse:collapse;background:rgba(255,61,110,0.02);border:1px solid rgba(255,61,110,0.12);border-radius:4px;overflow:hidden;">
      <tr style="background:rgba(255,61,110,0.06);">
        <th style="padding:10px 14px;text-align:left;font-size:9px;letter-spacing:2px;color:rgba(255,61,110,0.5);text-transform:uppercase;">Review</th>
        <th style="padding:10px 14px;text-align:center;font-size:9px;letter-spacing:2px;color:rgba(255,61,110,0.5);text-transform:uppercase;">Score</th>
      </tr>
      {sample_rows(top_neg, "#ff3d6e")}
    </table>
  </div>

  <!-- ══ FOOTER ══ -->
  <div style="background:rgba(0,5,15,0.9);border-top:1px solid rgba(0,212,255,0.1);padding:22px 32px;">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div>
        <div style="font-size:13px;font-weight:800;color:rgba(0,212,255,0.6);letter-spacing:2px;">PARTEXT</div>
        <div style="font-size:9px;color:rgba(0,180,220,0.25);letter-spacing:1px;margin-top:3px;">Sentiment Processor v2.0</div>
      </div>
      <div style="text-align:right;font-size:10px;color:rgba(0,180,220,0.25);letter-spacing:1px;line-height:1.8;">
        Processed {total:,} records in {elapsed:.3f}s<br>
        Internship Project &nbsp;·&nbsp; Python Parallel Processing
      </div>
    </div>
  </div>

</div>
</body></html>"""

    # ── Build email ──
    msg = MIMEMultipart("mixed")
    msg["Subject"] = f"Sentiment Report — {filename} ({total:,} records)"
    msg["From"]    = sender_email
    msg["To"]      = to_email

    msg.attach(MIMEText(html, "html"))

    # ── CSV attachment ──
    csv_bytes = res_df.to_csv(index=False).encode("utf-8")
    part = MIMEBase("application", "octet-stream")
    part.set_payload(csv_bytes)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="sentiment_{run_id}.csv"')
    msg.attach(part)

    # ── Send via Gmail SMTP ──
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())


# ══════════════════════════════════════════
# PAGE 1 — UPLOAD
# ══════════════════════════════════════════
def page_upload():
    inject_css()
    render_sidebar()

    st.markdown("""
<div class='hdr-wrap'>
  <div class='hdr-eyebrow'>
    <div class='hdr-eyebrow-dot'></div>
    Sentiment Analysis System
  </div>
  <div class='hdr-title'>Parallel <span class='accent'>Text</span> Processor</div>
  <div class='hdr-sub'>Upload <span>·</span> Select Column <span>·</span> Run Analysis</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class='upload-card'>
  <div class='upload-card-bg'></div>
  <div class='corner-tl'></div><div class='corner-tr'></div>
  <div class='corner-bl'></div>
  <div class='upload-label'>01 — File Input</div>
  <div class='upload-icon-wrap'>
    <svg width='52' height='52' viewBox='0 0 52 52' fill='none'>
      <rect x='6' y='12' width='40' height='30' rx='3' stroke='#00d4ff' stroke-width='1.5' stroke-dasharray='4 3' fill='none'/>
      <path d='M26 22 L26 38' stroke='#00d4ff' stroke-width='2' stroke-linecap='round'/>
      <path d='M19 29 L26 22 L33 29' stroke='#00d4ff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/>
      <circle cx='26' cy='15' r='4' fill='rgba(0,212,255,0.1)' stroke='#00d4ff' stroke-width='1.5'/>
      <circle cx='10' cy='38' r='2' fill='rgba(0,212,255,0.3)'/>
      <circle cx='42' cy='16' r='1.5' fill='rgba(0,212,255,0.2)'/>
    </svg>
  </div>
""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Drop CSV here", type=["csv"], label_visibility="collapsed")

    st.markdown("""
  <div class='chips-row'>
    <div class='chip'><div class='chip-dot'></div>CSV Format</div>
    <div class='chip'><div class='chip-dot'></div>Text Columns</div>
    <div class='chip'><div class='chip-dot'></div>Max 200 MB</div>
    <div class='chip'><div class='chip-dot'></div>UTF-8 / Latin-1</div>
  </div>
</div>
""", unsafe_allow_html=True)

    if uploaded_file is not None:
        df = None
        for enc in ["utf-8", "latin1"]:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding=enc, engine="python"); break
            except UnicodeDecodeError: continue
            except Exception as e: st.error(f"Error reading file: {e}"); break

        if df is None:
            st.error("Could not decode file. Please ensure it is a valid CSV."); return

        text_cols    = df.select_dtypes(exclude=["number"]).columns.tolist()
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

        st.success(f"**{uploaded_file.name}** loaded — {len(df):,} rows · {len(df.columns)} columns")
        if numeric_cols:
            st.info(f"{len(numeric_cols)} numeric column(s) excluded. Showing {len(text_cols)} text column(s).")
        if not text_cols:
            st.error("No text columns found in this file."); return

        st.markdown("<div class='sec-hdr'>02 — Select Text Column</div>", unsafe_allow_html=True)
        col_choice = st.selectbox("Choose the column to analyse", text_cols)

        st.markdown("<div class='sec-hdr'>03 — Launch Analysis</div>", unsafe_allow_html=True)
        if st.button("RUN SENTIMENT ANALYSIS"):
            st.session_state.df           = df
            st.session_state.selected_col = col_choice
            st.session_state.filename     = uploaded_file.name
            st.session_state.results      = None
            st.session_state.page         = "results"
            st.rerun()

    st.markdown("<div class='footer'>Built with <b>Streamlit</b> &nbsp;&middot;&nbsp; Internship Project &nbsp;&middot;&nbsp; ParText v2.0</div>",
                unsafe_allow_html=True)


# ══════════════════════════════════════════
# PAGE 2 — RESULTS
# ══════════════════════════════════════════
def page_results():
    inject_css()
    render_sidebar()

    df = st.session_state.df
    col = st.session_state.selected_col
    filename = st.session_state.filename

    st.markdown(f"""
<div class='hdr-wrap'>
  <div class='hdr-eyebrow'>
    <div class='hdr-eyebrow-dot'></div>
    Analysis Complete
  </div>
  <div class='hdr-title'><span class='accent'>Sentiment</span> Report</div>
  <div class='hdr-sub'>{filename} <span>·</span> Column: {col}</div>
</div>
""", unsafe_allow_html=True)

    # ── Process ──
    if st.session_state.results is None:
        texts = df[col].dropna().astype(str).str.strip().tolist()
        st.markdown("<div class='sec-hdr'>Processing Data</div>", unsafe_allow_html=True)
        prog = st.progress(0, text="Initialising parallel workers…")
        status = st.empty(); start = time.time()

        try:
            cores = cpu_count()
            status.markdown(f"<p style='font-family:Exo 2,sans-serif;color:rgba(0,212,255,0.5);font-size:13px;letter-spacing:1px;'>Running across {cores} CPU cores…</p>", unsafe_allow_html=True)
            with Pool(cores) as pool: results = pool.map(calculate_score, texts)
        except Exception:
            status.markdown("<p style='font-family:Exo 2,sans-serif;color:rgba(0,212,255,0.5);font-size:13px;letter-spacing:1px;'>Running in single-process mode…</p>", unsafe_allow_html=True)
            results = [calculate_score(t) for t in texts]

        elapsed = time.time() - start
        prog.progress(0.75, text="Storing to SQLite database…")
        run_id = f"run_{int(time.time())}"
        store_results(results, run_id)
        prog.progress(1.0, text="Complete!")
        time.sleep(0.4); prog.empty(); status.empty()
        st.session_state.results = results
        st.session_state.elapsed = elapsed
        st.session_state.run_id  = run_id

    results   = st.session_state.results
    elapsed   = st.session_state.elapsed
    run_id    = st.session_state.run_id
    res_df    = pd.DataFrame(results, columns=["Text","Score","Sentiment"])
    total     = len(res_df)
    pos_count = (res_df["Sentiment"]=="Positive").sum()
    neg_count = (res_df["Sentiment"]=="Negative").sum()
    neu_count = (res_df["Sentiment"]=="Neutral").sum()
    avg_score = res_df["Score"].mean()
    pos_pct   = (pos_count/total*100) if total else 0
    neg_pct   = (neg_count/total*100) if total else 0
    neu_pct   = (neu_count/total*100) if total else 0

    # DB badge
    st.markdown(f"""
<div class='db-badge'>
  <svg width='15' height='15' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'>
    <ellipse cx='12' cy='5' rx='9' ry='3'/><path d='M21 12c0 1.66-4 3-9 3s-9-1.34-9-3'/><path d='M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5'/>
  </svg>
  {total:,} records persisted &nbsp;&middot;&nbsp; SQLite &nbsp;&middot;&nbsp; Run: {run_id}
</div>
<div class='time-stat'>Processed {total:,} texts in {elapsed:.3f}s using parallel execution</div>
""", unsafe_allow_html=True)

    # KPIs
    st.markdown("<div class='sec-hdr'>01 — Summary Metrics</div>", unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total Records", f"{total:,}")
    c2.metric("Positive", f"{pos_count:,}")
    c3.metric("Negative", f"{neg_count:,}")
    c4.metric("Neutral",  f"{neu_count:,}")
    c5.metric("Avg Score", f"{avg_score:+.2f}")

    # Bars
    st.markdown("<div class='sec-hdr'>02 — Sentiment Breakdown</div>", unsafe_allow_html=True)
    st.markdown(f"""
<div class='bar-section'>
  <div class='bar-wrap'>
    <div class='bar-label'>
      <span>Positive</span>
      <span class='bar-val' style='color:#00ff88'>{pos_count:,} &nbsp; {pos_pct:.1f}%</span>
    </div>
    <div class='bar-track'><div class='bar-fill bar-pos' style='width:{pos_pct}%'></div></div>
  </div>
  <div class='bar-wrap'>
    <div class='bar-label'>
      <span>Negative</span>
      <span class='bar-val' style='color:#ff3d6e'>{neg_count:,} &nbsp; {neg_pct:.1f}%</span>
    </div>
    <div class='bar-track'><div class='bar-fill bar-neg' style='width:{neg_pct}%'></div></div>
  </div>
  <div class='bar-wrap'>
    <div class='bar-label'>
      <span>Neutral</span>
      <span class='bar-val' style='color:#ffc94d'>{neu_count:,} &nbsp; {neu_pct:.1f}%</span>
    </div>
    <div class='bar-track'><div class='bar-fill bar-neu' style='width:{neu_pct}%'></div></div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── CHARTS ──
    TRANSPARENT = "rgba(0,0,0,0)"
    GRID_COLOR  = "rgba(0,212,255,0.08)"
    FONT_COLOR  = "rgba(0,212,255,0.55)"
    PLOT_BG     = "rgba(0,8,18,0.6)"

    def base_layout(title="", height=340):
        return dict(
            title=dict(text=title, font=dict(family="Orbitron,sans-serif",
                       size=10, color="rgba(0,212,255,0.55)"), x=0.01, y=0.97),
            paper_bgcolor=TRANSPARENT,
            plot_bgcolor=PLOT_BG,
            font=dict(family="Exo 2,sans-serif", color=FONT_COLOR, size=11),
            height=height,
            margin=dict(l=40, r=20, t=48, b=40),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#cce8f8", size=11),
                        orientation="h", y=-0.18, x=0),
        )

    st.markdown("<div class='sec-hdr'>03 — Visual Analytics</div>", unsafe_allow_html=True)

    # ── ROW 1: Donut (left) + Horizontal bar (right) ──
    col_a, col_b = st.columns([1, 1], gap="large")

    with col_a:
        fig_donut = go.Figure(go.Pie(
            labels=["Positive", "Negative", "Neutral"],
            values=[pos_count, neg_count, neu_count],
            hole=0.60,
            marker=dict(
                colors=["#00ff88", "#ff3d6e", "#ffc94d"],
                line=dict(color="rgba(0,5,15,1)", width=2)
            ),
            textinfo="label+percent",
            textfont=dict(size=11, color="#ffffff"),
            insidetextorientation="radial",
            hovertemplate="<b>%{label}</b><br>%{value:,} reviews<br>%{percent}<extra></extra>",
        ))
        fig_donut.add_annotation(
            text=f"<b>{total:,}</b><br>REVIEWS",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#ffffff", family="Orbitron,sans-serif"),
            align="center"
        )
        lo = base_layout("SENTIMENT DISTRIBUTION", height=340)
        lo["showlegend"] = True
        lo["legend"]["y"] = -0.12
        fig_donut.update_layout(**lo)
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        fig_hbar = go.Figure()
        items = [
            ("Positive", int(pos_count), pos_pct, "#00ff88"),
            ("Neutral",  int(neu_count), neu_pct, "#ffc94d"),
            ("Negative", int(neg_count), neg_pct, "#ff3d6e"),
        ]
        for label, count, pct, color in items:
            fig_hbar.add_trace(go.Bar(
                name=label, y=[label], x=[count],
                orientation="h",
                marker=dict(color=color, opacity=0.85, line=dict(width=0)),
                text=f" {count:,}   {pct:.1f}%",
                textposition="inside",
                textfont=dict(color="#03080f", size=12, family="Exo 2,sans-serif"),
                hovertemplate=f"<b>{label}</b><br>%{{x:,}} reviews ({pct:.1f}%)<extra></extra>",
            ))
        lo2 = base_layout("REVIEWS BY SENTIMENT", height=340)
        lo2["showlegend"] = False
        lo2["xaxis"] = dict(showgrid=True, gridcolor=GRID_COLOR, color=FONT_COLOR,
                            tickformat=",", zeroline=False)
        lo2["yaxis"] = dict(showgrid=False, color="#cce8f8",
                            tickfont=dict(size=13, color="#cce8f8", family="Exo 2,sans-serif"))
        lo2["bargap"] = 0.4
        fig_hbar.update_layout(**lo2)
        st.plotly_chart(fig_hbar, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── ROW 2: Score histogram (left) + Box plot (right) ──
    col_c, col_d = st.columns([1, 1], gap="large")

    with col_c:
        score_counts = res_df["Score"].value_counts().sort_index()
        colors_hist  = ["#ff3d6e" if s < -1 else "#ffc94d" if s <= 1 else "#00ff88"
                        for s in score_counts.index]
        fig_hist = go.Figure(go.Bar(
            x=score_counts.index.tolist(),
            y=score_counts.values.tolist(),
            marker=dict(color=colors_hist, opacity=0.85, line=dict(width=0)),
            hovertemplate="Score <b>%{x}</b>: %{y:,} reviews<extra></extra>",
        ))
        lo3 = base_layout("SCORE DISTRIBUTION", height=320)
        lo3["xaxis"] = dict(title=dict(text="Score", font=dict(color=FONT_COLOR)),
                            showgrid=False, color=FONT_COLOR, dtick=1,
                            tickfont=dict(size=10))
        lo3["yaxis"] = dict(title=dict(text="Count", font=dict(color=FONT_COLOR)),
                            showgrid=True, gridcolor=GRID_COLOR, color=FONT_COLOR,
                            tickformat=",")
        lo3["showlegend"] = False
        fig_hist.update_layout(**lo3)
        st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

    with col_d:
        BOX_FILLS  = {"Positive":"rgba(0,255,136,0.12)",
                      "Negative":"rgba(255,61,110,0.12)",
                      "Neutral":"rgba(255,201,77,0.12)"}
        BOX_COLORS = {"Positive":"#00ff88","Negative":"#ff3d6e","Neutral":"#ffc94d"}
        fig_box = go.Figure()
        for sent in ["Positive", "Neutral", "Negative"]:
            subset = res_df[res_df["Sentiment"]==sent]["Score"]
            fig_box.add_trace(go.Box(
                y=subset, name=sent,
                marker=dict(color=BOX_COLORS[sent], size=3, opacity=0.6),
                line=dict(color=BOX_COLORS[sent], width=2),
                fillcolor=BOX_FILLS[sent],
                boxmean="sd",
                hovertemplate=f"<b>{sent}</b><br>Score: %{{y}}<extra></extra>",
            ))
        lo4 = base_layout("SCORE SPREAD BY SENTIMENT", height=320)
        lo4["showlegend"] = False
        lo4["yaxis"] = dict(title=dict(text="Score", font=dict(color=FONT_COLOR)),
                            showgrid=True, gridcolor=GRID_COLOR, color=FONT_COLOR,
                            zeroline=True, zerolinecolor="rgba(0,212,255,0.15)")
        lo4["xaxis"] = dict(showgrid=False, color="#cce8f8",
                            tickfont=dict(size=13, color="#cce8f8"))
        fig_box.update_layout(**lo4)
        st.plotly_chart(fig_box, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── ROW 3: Stacked score bucket bar (full width) ──
    b_labels = ["Very High (≥ 4)", "High (2 to 3)", "Neutral (−1 to 1)", "Low (−2 to −3)", "Very Low (≤ −4)"]
    b_values = [
        int((res_df["Score"] >= 4).sum()),
        int(((res_df["Score"] >= 2) & (res_df["Score"] < 4)).sum()),
        int(((res_df["Score"] >= -1) & (res_df["Score"] <= 1)).sum()),
        int(((res_df["Score"] >= -3) & (res_df["Score"] < -1)).sum()),
        int((res_df["Score"] <= -4).sum()),
    ]
    b_colors = ["#00ff88", "#00d4ff", "#ffc94d", "#ff8c42", "#ff3d6e"]
    fig_bucket = go.Figure()
    for lbl, val, col in zip(b_labels, b_values, b_colors):
        fig_bucket.add_trace(go.Bar(
            name=lbl, x=[val], y=[""],
            orientation="h",
            marker=dict(color=col, opacity=0.88, line=dict(width=0)),
            text=f"{val:,}",
            textposition="inside",
            textfont=dict(color="#03080f", size=12, family="Exo 2,sans-serif"),
            hovertemplate=f"<b>{lbl}</b>: %{{x:,}} reviews<extra></extra>",
        ))
    lo5 = base_layout("SCORE BUCKET BREAKDOWN", height=200)
    lo5["barmode"]    = "stack"
    lo5["showlegend"] = True
    lo5["legend"]     = dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#cce8f8", size=11),
                              orientation="h", y=-0.35, x=0)
    lo5["xaxis"]      = dict(showgrid=True, gridcolor=GRID_COLOR, color=FONT_COLOR, tickformat=",")
    lo5["yaxis"]      = dict(showgrid=False, showticklabels=False)
    lo5["margin"]     = dict(l=20, r=20, t=48, b=80)
    fig_bucket.update_layout(**lo5)
    st.plotly_chart(fig_bucket, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Table
    st.markdown("<div class='sec-hdr'>03 — Scored Records</div>", unsafe_allow_html=True)
    fc1, fc2 = st.columns([1, 3])
    with fc1: sentiment_filter = st.selectbox("Filter by sentiment", ["All","Positive","Negative","Neutral"])
    with fc2: search_term = st.text_input("Search text", placeholder="Type keywords to filter records…")

    display_df = res_df.copy()
    if sentiment_filter != "All":
        display_df = display_df[display_df["Sentiment"]==sentiment_filter]
    if search_term:
        display_df = display_df[display_df["Text"].str.contains(search_term, case=False, na=False)]

    def colour_sentiment(val):
        if val=="Positive": return "color:#00ff88;font-weight:700"
        if val=="Negative": return "color:#ff3d6e;font-weight:700"
        return "color:#ffc94d;font-weight:700"

    pd.set_option("styler.render.max_elements", len(display_df) * len(display_df.columns) + 1)
    st.dataframe(display_df.style.map(colour_sentiment, subset=["Sentiment"]),
                 use_container_width=True, height=440)

    # Export + Email
    st.markdown("<div class='sec-hdr'>04 — Export & Share</div>", unsafe_allow_html=True)

    dl_col, _ = st.columns([1, 2])
    with dl_col:
        st.download_button(
            label="  Download Full Results as CSV",
            data=res_df.to_csv(index=False).encode("utf-8"),
            file_name=f"sentiment_{run_id}.csv", mime="text/csv")

    # ── Email Report ──
    st.markdown("<div class='sec-hdr'>05 — Email Report</div>", unsafe_allow_html=True)
    st.markdown("""
<div class='email-card'>
  <div class='corner-tl'></div><div class='corner-tr'></div>
  <div style='font-family:"Orbitron",sans-serif;font-size:9px;font-weight:700;letter-spacing:4px;
              color:rgba(0,212,255,0.5);text-transform:uppercase;margin-bottom:14px;
              display:flex;align-items:center;gap:12px;'>
    Send Report
    <span style='flex:1;height:1px;background:linear-gradient(90deg,rgba(0,212,255,0.25),transparent);'></span>
  </div>
  <p style='font-family:"Exo 2",sans-serif;font-size:13px;color:rgba(160,210,240,0.45);
             letter-spacing:0.5px;margin-bottom:0;line-height:1.7;'>
    Enter the recipient's email address. A styled HTML report with the full CSV attached
    will be sent instantly — no login required.
  </p>
</div>
""", unsafe_allow_html=True)

    em_col, btn_col = st.columns([3, 1])
    with em_col:
        to_email = st.text_input(
            "Recipient Email Address",
            placeholder="Enter email to receive the report…",
            key="to_email"
        )
    with btn_col:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        send_clicked = st.button("SEND REPORT", use_container_width=True)

    if send_clicked:
        if not to_email or "@" not in to_email or "." not in to_email.split("@")[-1]:
            st.markdown("""
<div class='send-status-err'>
  Please enter a valid email address.
</div>""", unsafe_allow_html=True)
        else:
            with st.spinner("Composing and sending report…"):
                try:
                    send_email_report(
                        to_email=to_email,
                        res_df=res_df,
                        filename=filename,
                        run_id=run_id,
                        elapsed=elapsed,
                        pos_pct=pos_pct,
                        neg_pct=neg_pct,
                        neu_pct=neu_pct,
                    )
                    st.markdown(f"""
<div class='send-status-ok'>
  <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.5'>
    <polyline points='20 6 9 17 4 12'/>
  </svg>
  Report delivered to <b>{to_email}</b> &nbsp;&middot;&nbsp; CSV attached ({len(res_df):,} records)
</div>""", unsafe_allow_html=True)
                except smtplib.SMTPAuthenticationError:
                    st.markdown("""
<div class='send-status-err'>
  Sender authentication failed. Please contact the administrator to update SENDER credentials in app.py.
</div>""", unsafe_allow_html=True)
                except smtplib.SMTPException as e:
                    st.markdown(f"<div class='send-status-err'>SMTP error: {e}</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"<div class='send-status-err'>Error: {e}</div>", unsafe_allow_html=True)

    st.markdown("<div class='footer'>Built with <b>Streamlit</b> &nbsp;&middot;&nbsp; Internship Project &nbsp;&middot;&nbsp; ParText v2.0</div>",
                unsafe_allow_html=True)


# ══════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════
if st.session_state.page == "upload":
    page_upload()
else:
    page_results()