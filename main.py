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
    password = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if password == "CSmover123":  # Change this to your desired password.
            st.session_state.authenticated = True
            st.success("Password correct!")
        else:
            st.error("Incorrect password!")
    st.stop()

# Konfigurer siden med professionelt titel, ikon og bredt layout
st.set_page_config(
    page_title="Mover - Empowering Logistics with Technology",
    page_icon=":rocket:",
    layout="wide"
)

# Global CSS-styling baseret på Mover Brand Guidelines
st.markdown(
    """
    <!-- Import Open Sans and Material Icons from Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons:outlined" rel="stylesheet">
    <style>
    /* Basic typography and color settings */
    body, .main, p, li, .stMarkdown {
        font-family: 'Open Sans', sans-serif;
        font-weight: 400;
        font-size: 16pt;
        color: #01293D; /* Primary text color (Midnight Blue) */
        background-color: #FFFFFF; /* White background for text */
    }
    h1, h2, h3, h4 {
        font-family: 'Open Sans', sans-serif;
        font-weight: 400;
        margin-bottom: 10px;
    }
    h1 {
        font-size: 2.5em;
        color: #01293D; /* Midnight Blue */
    }
    h2 {
        font-size: 2em;
        color: #003F63; /* Daylight Blue */
    }
    h3 {
        font-size: 1.75em;
        color: #01293D;
    }
    /* Header styling */
    .header {
        text-align: center;
        padding: 20px;
    }
    /* Primary buttons: rounded with solid fill */
    .stButton>button {
        border-radius: 25px;
        font-size: 14pt;
        font-weight: 700;
        background-color: #01293D; /* Midnight Blue */
        color: #FFFFFF;
        border: none;
        padding: 10px 24px;
        cursor: pointer;
    }
    /* Secondary buttons: outlined style */
    .stButton>button.secondary {
        background-color: transparent;
        color: #01293D;
        border: 2px solid #01293D;
    }
    /* Tab styling */
    [data-baseweb="tab"] {
        margin-right: 30px;
    }
    .stTabs [data-baseweb="tab"] button {
        font-size: 14pt;
        font-weight: 700;
        color: #01293D;
    }
    .stTabs [data-baseweb="tab"] button:focus, .stTabs [data-baseweb="tab"] button:hover {
        color: #003F63;
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

# Header: Vis logo centreret med tagline under
try:
    logo = Image.open("moverLogotype_blue.png")
    # Brug kolonner til at centrere logoet og tagline
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(logo, width=200)
        st.markdown(
            "<h1 style='font-size:2.5em; color:#01293D;'>We are changing logistics for good</h1>",
            unsafe_allow_html=True,
        )
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
except Exception as e:
    st.error("Error loading logo: " + str(e))

# Importer de enkelte moduler for fanerne
from forside import forside_tab
from controlling import controlling_tab
from solar_weekly import solar_weekly_tab
from solar_co2 import solar_co2_tab
from revenue import revenue_tab

# Opret fanebjælken med de forskellige sektioner
tabs = st.tabs([
    "Forside",
    "Controlling Report Analyzer",
    "Solar Weekly Report",
    "Solar CO2 Report",
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

# Footer-sektion
st.markdown(
    """
    <div class="footer">
        &copy; 2025 Mover. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)
