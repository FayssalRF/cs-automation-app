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
    st.title("Login Form")
    password = st.text_input("Indtast adgangskode", type="password")
    if st.button("Login"):
        if password == "CSlikestomoveitmoveit123":  # Ændr denne kode til din ønskede adgangskode
            st.session_state.authenticated = True
            st.success("Adgangskode korrekt!")
        else:
            st.error("Forkert adgangskode!")
    st.stop()
import streamlit as st
from PIL import Image
from datetime import date

# Konfigurer siden
st.set_page_config(
    page_title="Analyser",
    page_icon=":bar_chart:",
    layout="wide"
)

# Tilføj fælles CSS
st.markdown(
    """
    <style>
    /* Importér Open Sans */
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap');

    body, .main, p, li, .stMarkdown {
        font-family: 'Open Sans', sans-serif;
        font-size: 16pt !important;
        font-weight: 400 !important;
        color: #000 !important;
    }
    h1 {
        font-size: 3em !important;
        font-weight: 400 !important;
        color: #333333 !important;
    }
    h2 {
        font-size: 2.5em !important;
        font-weight: 400 !important;
        color: #333333 !important;
    }
    h3 {
        font-size: 2em !important;
        font-weight: 400 !important;
        color: #333333 !important;
    }
    /* Primære knapper */
    .stButton>button {
        font-size: 16pt !important;
        font-weight: 700 !important;
        background-color: #D7F3F9;
        color: white !important;
        border: none;
        padding: 10px 24px;
        border-radius: 25px;
        cursor: pointer;
        transition: background-color 0.3s, color 0.3s;
    }
    /* Labels fra file-uploader */
    .stFileUploader label {
        text-transform: lowercase;
        color: #008080 !important;
    }
    /* Margin mellem faner */
    [data-baseweb="tab"] {
        margin-right: 30px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Indlæs logo
try:
    logo = Image.open("moverLogotype_blue.png")
    st.image(logo, width=300)
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
except Exception as e:
    st.error("Fejl ved indlæsning af logo: " + str(e))

# Importer de enkelte menupunktsmoduler
from forside import forside_tab
from controlling import controlling_tab
from solar_weekly import solar_weekly_tab
from solar_co2 import solar_co2_tab
from revenue import revenue_tab

# Opret fanebjælken med 5 faner
tabs = st.tabs(["Forside", "Controlling Report Analyzer", "Solar Weekly Report", "Solar CO2 Report", "Revenue analyser"])

with tabs[0]:
    forside_tab()
with tabs[1]:
    # Send all_keywords til controlling-tabben
    controlling_tab()
with tabs[2]:
    solar_weekly_tab()
with tabs[3]:
    solar_co2_tab()
with tabs[4]:
    revenue_tab()
