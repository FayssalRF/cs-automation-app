# main.py

import streamlit as st

# --- Authentication ---------------------------------------------------------

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Login")
    password = st.text_input("Enter password", type="password")
    if st.button("Login"):
        # Sikker sammenligning med adgangskoden fra Streamlit Secrets
        if "APP_PASSWORD" in st.secrets and password == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.session_state.page = "dashboard"
            st.success("Password correct!")
            st.rerun()
        else:
            st.error("Incorrect password!")
    # Stop med at køre resten af app'en, indtil man er logget ind
    st.stop()

# --- Page config & global CSS styling ---------------------------------------

st.set_page_config(
    page_title="Mover - Empowering Logistics with Technology",
    page_icon=":rocket:",
    layout="wide"
)

st.markdown(
    """
    <!-- Import Open Sans and Material Icons from Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap" rel="stylesheet">

    <style>
      body, .main, p, li, .stMarkdown {
        font-family: 'Open Sans', sans-serif;
        font-size: 15px;
        font-weight: 400;
        color: #01293D;
      }
      h1, h2, h3, h4 {
        font-family: 'Open Sans', sans-serif;
        font-weight: 400;
        margin-bottom: 10px;
      }
      h1 { font-size: 2.4em; color: #01293D; }
      h2 { font-size: 2em; color: #003F63; }
      h3 { font-size: 1.5em; color: #01293D; }

      .header {
        text-align: center;
        padding: 10px 0 30px 0;
      }
      .header img {
        max-width: 260px;
      }
      .header-subtitle {
        margin-top: 4px;
        font-size: 1.1em;
        color: #33566C;
      }

      /* Standard knapper (tilbage, mv.) */
      .stButton > button {
        border-radius: 999px;
        font-size: 14px;
        font-weight: 600;
        background-color: #01293D;
        color: #FFFFFF;
        border: none;
        padding: 8px 22px;
        cursor: pointer;
        box-shadow: 0 10px 20px rgba(0,0,0,0.08);
      }
      .stButton > button:hover {
        background-color: #003F63;
      }

      /* Tilbage-knap / sekundær knap */
      .secondary-btn .stButton > button {
        background-color: #FFFFFF !important;
        color: #01293D !important;
        border: 1px solid #D0D7DE !important;
        box-shadow: none !important;
      }

      /* Dashboard layout */
      .dashboard-wrapper {
        max-width: 1100px;
        margin: 0 auto;
      }

      /* Card-knapper */
      .card-list {
        margin-top: 10px;
      }
      .card-btn .stButton > button {
        width: 100%;
        text-align: left;
        border-radius: 24px;
        padding: 18px 24px;
        background: #FFFFFF;
        border: 1px solid #E5E9F0;
        box-shadow: 0 18px 40px rgba(1,41,61,0.06);
        color: #01293D;
        font-weight: 500;
        font-size: 15px;
        white-space: pre-wrap; /* bevar linjeskift i label */
      }
      .card-btn .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 24px 60px rgba(1,41,61,0.10);
        border-color: #D0D7DE;
        background: #FDFEFE;
      }

      .card-spacer {
        height: 14px;
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

# --- Header -----------------------------------------------------------------

st.markdown(
    """
    <div class="header">
      <img src="https://raw.githubusercontent.com/FayssalRF/cs-automation-app/refs/heads/main/moverLogotype_blue.png"
           alt="Mover Logo">
      <div class="header-subtitle">We are changing logistics for good</div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Import pages -----------------------------------------------------------

from forside import forside_tab
from controlling import controlling_tab
from solar_weekly import solar_weekly_tab

# --- Simple router state ----------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

def go(page_key: str):
    st.session_state.page = page_key
    st.experimental_rerun()

# --- Layout: Dashboard + sider ----------------------------------------------

if st.session_state.page == "dashboard":
    st.markdown('<div class="dashboard-wrapper">', unsafe_allow_html=True)

    st.markdown("### Dashboard")
    st.markdown(
        """
        <p style="color:#4A6275; font-size:0.95em; margin-bottom: 18px;">
          Vælg et værktøj nedenfor for at komme hurtigt i gang.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card-list">', unsafe_allow_html=True)

    # Card 1 – Controlling
    with st.container():
        st.markdown('<div class="card-btn">', unsafe_allow_html=True)
        label = (
            "📊  Controlling Report Analyzer\n"
            "Få automatisk overblik over ruter med ekstra tid og kundedeviation baseret på QuickNotes."
        )
        if st.button(label, key="card_controlling", use_container_width=True):
            go("controlling")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-spacer"></div>', unsafe_allow_html=True)

    # Card 2 – Solar Weekly
    with st.container():
        st.markdown('<div class="card-btn">', unsafe_allow_html=True)
        label = (
            "📅  Solar Weekly Report\n"
            "Upload ugens Solar-rapport og få et hurtigt overblik over performance og nøgletal."
        )
        if st.button(label, key="card_solar_weekly", use_container_width=True):
            go("solar_weekly")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-spacer"></div>', unsafe_allow_html=True)

    # Card 3 – Forside / overblik
    with st.container():
        st.markdown('<div class="card-btn">', unsafe_allow_html=True)
        label = (
            "📋  Overblik & noter\n"
            "Se forside-visningen med generelt overblik, noter eller andre værktøjer du har lagt her."
        )
        if st.button(label, key="card_forside", use_container_width=True):
            go("forside")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # card-list
    st.markdown('</div>', unsafe_allow_html=True)  # dashboard-wrapper

elif st.session_state.page == "controlling":
    col_back, _ = st.columns([1, 4])
    with col_back:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("← Tilbage til dashboard", key="back_from_controlling"):
            go("dashboard")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    controlling_tab()

elif st.session_state.page == "solar_weekly":
    col_back, _ = st.columns([1, 4])
    with col_back:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("← Tilbage til dashboard", key="back_from_solar"):
            go("dashboard")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    solar_weekly_tab()

elif st.session_state.page == "forside":
    col_back, _ = st.columns([1, 4])
    with col_back:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("← Tilbage til dashboard", key="back_from_forside"):
            go("dashboard")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    forside_tab()

# --- Footer -----------------------------------------------------------------

st.markdown(
    """
    <div class="footer">
      &copy; 2025 Mover. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)
