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
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons:outlined" rel="stylesheet">

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

        /* Primære knapper (lyseblå Apple-style) */
        .stButton > button {
        border-radius: 999px;
        font-size: 14px;
        font-weight: 600;
        background-color: #D7F3F9 !important;   /* Lyseblå */
        color: #FFFFFF !important;
        border: none;
        padding: 8px 22px;
        cursor: pointer;
        box-shadow: 0 10px 20px rgba(0,0,0,0.08);
        transition: background-color 0.2s ease;
        }
        
        .stButton > button:hover {
            background-color: #2496FF !important;   /* Lidt mørkere lyseblå */
        }


      /* Sekundær knap (tilbage) */
      .secondary-btn > button {
        background-color: #FFFFFF !important;
        color: #01293D !important;
        border: 1px solid #D0D7DE !important;
        box-shadow: none !important;
      }

      /* Dashboard cards */
      .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 24px;
        margin-top: 10px;
      }
      .card {
        background: #FFFFFF;
        border-radius: 22px;
        padding: 20px 20px 16px 20px;
        box-shadow: 0 18px 40px rgba(1,41,61,0.06);
        border: 1px solid #E5E9F0;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
      }
      .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 24px 60px rgba(1,41,61,0.09);
        border-color: #D0D7DE;
      }
      .card-icon {
        font-family: 'Material Icons', 'Material Icons Outlined';
        font-size: 26px;
        color: #01293D;
        margin-bottom: 8px;
      }
      .card-title {
        font-size: 1.1em;
        font-weight: 600;
        margin-bottom: 4px;
      }
      .card-body {
        font-size: 0.95em;
        color: #355067;
        margin-bottom: 12px;
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
    st.rerun()

# --- Layout: Dashboard + sider ----------------------------------------------

if st.session_state.page == "dashboard":
    # Apple-agtigt dashboard med cards
    st.markdown("### Dashboard")

    st.markdown(
        """
        <p style="color:#4A6275; font-size:0.95em; margin-bottom: 20px;">
          Vælg et værktøj nedenfor for at komme hurtigt i gang.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)

    # Card 1 – Controlling
    st.markdown(
        """
        <div class="card">
          <div class="card-icon">insights</div>
          <div class="card-title">Controlling Report Analyzer</div>
          <div class="card-body">
            Få automatisk overblik over ruter med ekstra tid og kundedeviation
            baseret på QuickNotes.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Åbn Controlling", key="open_controlling"):
        go("controlling")

    # Card 2 – Solar Weekly
    st.markdown(
        """
        <div class="card">
          <div class="card-icon">calendar_month</div>
          <div class="card-title">Solar Weekly Report</div>
          <div class="card-body">
            Upload ugens Solar-rapport og få et hurtigt overblik over performance
            og nøgletal.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Åbn Solar Weekly", key="open_solar_weekly"):
        go("solar_weekly")

    # Card 3 – Forside / overblik
    st.markdown(
        """
        <div class="card">
          <div class="card-icon">dashboard</div>
          <div class="card-title">Overblik &amp; noter</div>
          <div class="card-body">
            Se forside-visningen med generelt overblik, noter eller andre
            værktøjer du har lagt her.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Åbn overblik", key="open_forside"):
        go("forside")

    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "controlling":
    # Tilbage-knap
    col_back, _ = st.columns([1, 4])
    with col_back:
        back = st.button("← Tilbage til dashboard", key="back_from_controlling")
        if back:
            go("dashboard")

    st.markdown("---")
    controlling_tab()

elif st.session_state.page == "solar_weekly":
    col_back, _ = st.columns([1, 4])
    with col_back:
        back = st.button("← Tilbage til dashboard", key="back_from_solar")
        if back:
            go("dashboard")

    st.markdown("---")
    solar_weekly_tab()

elif st.session_state.page == "forside":
    col_back, _ = st.columns([1, 4])
    with col_back:
        back = st.button("← Tilbage til dashboard", key="back_from_forside")
        if back:
            go("dashboard")

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



