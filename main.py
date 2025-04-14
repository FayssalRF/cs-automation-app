import streamlit as st
import pandas as pd
import io
import requests
from PIL import Image
from datetime import date

# Sikkerhed: Enkel login-godkendelse
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Login")
    password = st.text_input("Indtast adgangskode", type="password")
    if st.button("Login"):
        if password == "CSmover123":  # Ændr denne kode til din ønskede adgangskode
            st.session_state.authenticated = True
            st.success("Adgangskode korrekt!")
        else:
            st.error("Forkert adgangskode!")
    st.stop()

# Konfigurer siden med passende titel, ikon og bred layout.
st.set_page_config(
    page_title="Mover - Tech & Logistics Solutions",
    page_icon=":rocket:",
    layout="wide"
)

# Global CSS-styling baseret på Mover Brand Guidelines
st.markdown(
    """
    <style>
    /* Import Open Sans fra Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap');

    /* Grundlæggende styling */
    body, .main, p, li, .stMarkdown {
        font-family: 'Open Sans', sans-serif;
        font-size: 16pt !important;
        font-weight: 400 !important;
        color: #01293D !important;  /* Midnight Blue */
        background-color: #f7f9fc;
    }
    h1 {
        font-size: 2.5em !important;
        color: #01293D !important;
        margin-bottom: 10px;
    }
    h2 {
        font-size: 2em !important;
        color: #003F63 !important;  /* Daylight Blue */
        margin-bottom: 10px;
    }
    h3 {
        font-size: 1.75em !important;
        color: #01293D !important;
        margin-bottom: 10px;
    }
    /* Styling til primære knapper: afrundede hjørner og solid fyld */
    .stButton>button {
        border-radius: 25px;
        font-size: 14pt !important;
        font-weight: 700 !important;
        background-color: #01293D; 
        color: white !important;
        border: none;
        padding: 10px 24px;
        cursor: pointer;
    }
    /* Styling til file uploader label */
    .stFileUploader label {
        text-transform: lowercase;
        color: #003F63 !important;
    }
    [data-baseweb="tab"] {
        margin-right: 30px !important;
    }
    /* Header styling */
    .header {
        text-align: center;
        padding: 20px;
    }
    /* Footer styling */
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

# Header-sektion med virksomhedsnavn, slogan og værdiforslag
st.markdown(
    """
    <div class="header">
        <h1>Mover - Empowering your logistics</h1>
        <p>We help you save time, reduce costs, and drive sustainability with advanced technology.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Indlæs logo (sørg for at billedfilen er tilgængelig i rodmappen)
try:
    logo = Image.open("moverLogotype_blue.png")
    st.image(logo, width=200)
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
except Exception as e:
    st.error("Fejl ved indlæsning af logo: " + str(e))

# Importer de enkelte menupunktsmoduler
from forside import forside_tab
from controlling import controlling_tab
from solar_weekly import solar_weekly_tab
from solar_co2 import solar_co2_tab
from revenue import revenue_tab  # Aktiverer Revenue-fanen

# Opret fanebjælken med de forskellige sektioner
tabs = st.tabs([
    "Forside",
    "Controlling Report Analyzer",
    "Solar Weekly Report",
    "Solar CO2 Report",
    "Revenue analyser"
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

# Footer-sektion
st.markdown(
    """
    <div class="footer">
        &copy; 2025 Mover. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)
