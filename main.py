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

# --- Page config & styling ---
st.set_page_config(
    page_title="Mover - Empowering Logistics with Technology",
    page_icon=":rocket:",
    layout="wide"
)
st.markdown("""
    <style>
      /* your global CSS here */
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
    <div style="text-align:center; padding:20px;">
      <img src="https://raw.githubusercontent.com/FayssalRF/cs-automation-app/refs/heads/main/moverLogotype_blue.png" style="max-width:300px;">
      <h2>We are changing logistics for good</h2>
    </div>
""", unsafe_allow_html=True)

# --- Imports for each tab ---
from forside import forside_tab
from controlling import controlling_tab
from solar_weekly import solar_weekly_tab
from solar_co2 import solar_co2_tab
from revenue import revenue_tab

# --- Build the tab bar ---
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
st.markdown("""
    <div style="text-align:center; padding:20px; font-size:0.9em; color:#01293D;">
      © 2025 Mover. All rights reserved.
    </div>
""", unsafe_allow_html=True)
