import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    .stApp {background: radial-gradient(circle at 85% 10%, #142b52 0, #08111f 42%, #050b15 100%); color:#e8f0f7; font-family:'DM Sans',sans-serif;}
    h1,h2,h3 {font-family:'Space Grotesk',sans-serif;color:#edf6ff;}
    [data-testid="stSidebar"] {background:#091426;border-right:1px solid #1b3557;}
    .hero {padding:2.5rem 1rem 1rem 1rem;}
    .hero h1 {font-size:3.3rem;margin:.2rem 0;}
    .hero h1 span {color:#39d9ff;}
    .hero p,.eyebrow {color:#9ab5d1;}
    .eyebrow {letter-spacing:.18em;font-size:.75rem;}
    .glass {background:rgba(18,35,59,.82);border:1px solid rgba(68,164,220,.35);border-radius:18px;padding:1.5rem;box-shadow:0 18px 55px rgba(0,0,0,.25);}
    div.stButton > button {background:linear-gradient(90deg,#1678db,#18c8e8);color:white;border:0;border-radius:10px;font-weight:700;}
    [data-testid="stMetric"] {background:#10213a;border:1px solid #244568;padding:14px;border-radius:12px;}
    </style>
    """, unsafe_allow_html=True)
