# main.py

import streamlit as st
import pandas as pd
import io
import requests
from PIL import Image
from datetime import date

# --- Authentication ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Login")
    password = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if password == "CSmover123":
            st.session_state.authenticated = True
            st.success("Password correct!")
        else:
            st.error("Incorrect password!")
    st.stop()

# --- Page config & global CSS styling ---
st.set_page_config(
    page_title="Mover - Empowering Logistics with Technology",
    page_icon=":rocket:",
    layout="wide"
)
st.markdown(
    """
    <!-- Import Open Sans and Material Icons from Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons:outlined" rel="stylesheet">
    <style>
      body, .main, p, li, .stMarkdown {
        font-family: 'Open Sans', sans-serif;
        font-size: 16pt;
        font-weight: 400;
        color: #01293D; /* Primary text color */
      }
      h1, h2, h3, h4 {
        font-family: 'Open Sans', sans-serif;
        font-weight: 400;
        margin-bottom: 10px;
      }
      h1 { font-size: 2.5em; color: #01293D; }
      h2 { font-size: 2em; color: #003F63; }
      h3 { font-size: 1.75em; color: #01293D; }
      .header { text-align: center; padding: 20px; }
      .stButton > button {
        border-radius: 25px;
        font-size: 14pt;
        font-weight: 700;
        background-color: #01293D;
        color: #FFFFFF;
        border: none;
        padding: 10px 24px;
        cursor: pointer;
      }
      .stButton > button.secondary {
        background-color: transparent;
        color: #01293D;
        border: 2px solid #01293D;
      }
      /* Doubled spacing between tabs */
      [data-baseweb="tab"] {
        margin-right: 60px;  /* was 30px */
      }
      .stTabs [data-baseweb="tab"] button {
        font-size: 14pt;
        font-weight: 700;
        color: #01293D;
      }
      .stTabs [data-baseweb="tab"] button:focus,
      .stTabs [data-baseweb="tab"] button:hover {
        color: #003F63;
      }
      .footer {
        text-align: center;
        padding: 20px;
        font-size: 0.9em;
        color: #01293D;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Header ---
st.markdown(
    """
    <div class="header">
      <img src="https://raw.githubusercontent.com/FayssalRF/cs-automation-app/refs/heads/main/moverLogotype_blue.png"
           alt="Mover Logo" style="max-width:300px;">
      <h2>We are changing logistics for good</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Import tabs ---
from forside import forside_tab
from controlling import controlling_tab
from solar_weekly import solar_weekly_tab
from solar_co2 import solar_co2_tab
from revenue import revenue_tab

# --- Create tab bar ---
tabs = st.tabs([
    "Forside",
    "Controlling Report Analyzer",
    "Solar Weekly Report",
    "Solar CO₂ Report",
    "Revenue analyzer"
])

with tabs[0]:
    forside_tab()
with tabs[1]:
    controlling_tab()
with tabs[2]:
    solar_weekly_tab()
with tabs[3]:
    solar_co2_tab()
with tabs[4]:
    revenue_tab()

# --- Footer ---
st.markdown(
    """
    <div class="footer">
      &copy; 2025 Mover. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)
