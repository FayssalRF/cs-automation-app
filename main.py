# main.py

import streamlit as st

# --- Helpers ---------------------------------------------------------------

def load_css(path: str = "styles.css") -> None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Kunne ikke finde {path}. Læg styles.css i samme mappe som main.py")

def svg_icon(name: str) -> str:
    # Simple, clean SVGs (24x24) using currentColor
    icons = {
        "insights": """
        <svg class="card-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 19V5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M8 19V11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 19V7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M16 19V13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M20 19V9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        """,
        "calendar": """
        <svg class="card-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M7 3V5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M17 3V5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M4 8H20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M6 5H18C19.1046 5 20 5.89543 20 7V19C20 20.1046 19.1046 21 18 21H6C4.89543 21 4 20.1046 4 19V7C4 5.89543 4.89543 5 6 5Z"
                stroke="currentColor" stroke-width="2" />
        </svg>
        """,
        "note": """
        <svg class="card-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M7 3H15L19 7V21H7V3Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
          <path d="M15 3V7H19" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
          <path d="M9 11H17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M9 15H17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        """
    }
    return icons.get(name, "")

def card(title: str, body: str, icon_svg: str) -> None:
    st.markdown(
        f"""
        <div class="card">
          {icon_svg}
          <div class="card-title">{title}</div>
          <div class="card-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Authentication ---------------------------------------------------------

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Login")
    password = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if "APP_PASSWORD" in st.secrets and password == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.session_state.page = "dashboard"
            st.success("Password correct!")
            st.rerun()
        else:
            st.error("Incorrect password!")
    st.stop()

# --- Page config & CSS ------------------------------------------------------

st.set_page_config(
    page_title="Mover - Empowering Logistics with Technology",
    page_icon=":rocket:",
    layout="wide"
)

# Load fonts + CSS
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap" rel="stylesheet">
    """,
    unsafe_allow_html=True
)
load_css("styles.css")

# --- Header ----------------------------------------------------------------

st.markdown(
    """
    <div class="header">
      <img src="https://raw.githubusercontent.com/FayssalRF/cs-automation-app/refs/heads/main/moverLogotype_blue.png"
           alt="Mover Logo" style="max-width:300px;">
      <div class="header-subtitle">We are changing logistics for good</div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Import pages -----------------------------------------------------------

from controlling import controlling_tab
from solar_weekly import solar_weekly_tab
from overviewnotes import overviewnotes_tab

# --- Router ----------------------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

def go(page_key: str):
    st.session_state.page = page_key
    st.rerun()

# --- Views -----------------------------------------------------------------

if st.session_state.page == "dashboard":
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

    # 1) Controlling
    card(
        "Controlling Report Analyzer",
        "Overblik over ruter med ekstra tid og kundedeviation baseret på QuickNotes.",
        svg_icon("insights"),
    )
    if st.button("Åbn Controlling", key="open_controlling"):
        go("controlling")

    # 2) Solar Weekly
    card(
        "Solar Weekly Report",
        "Upload ugens Solar-rapport og få et hurtigt overblik over performance og nøgletal.",
        svg_icon("calendar"),
    )
    if st.button("Åbn Solar Weekly", key="open_solar_weekly"):
        go("solar_weekly")

    # 3) Overblik & noter
    card(
        "Overblik &amp; noter",
        "Skriv noter, instrukser og hjælpeartikler til teamet. Kan eksporteres/importeres som JSON.",
        svg_icon("note"),
    )
    if st.button("Åbn Overblik & noter", key="open_overviewnotes"):
        go("overviewnotes")

    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "controlling":
    col_back, _ = st.columns([1, 4])
    with col_back:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("← Tilbage til dashboard", key="back_from_controlling"):
            go("dashboard")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    controlling_tab()

elif st.session_state.page == "solar_weekly":
    col_back, _ = st.columns([1, 4])
    with col_back:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("← Tilbage til dashboard", key="back_from_solar"):
            go("dashboard")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    solar_weekly_tab()

elif st.session_state.page == "overviewnotes":
    col_back, _ = st.columns([1, 4])
    with col_back:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("← Tilbage til dashboard", key="back_from_overviewnotes"):
            go("dashboard")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    overviewnotes_tab()

# --- Footer -----------------------------------------------------------------

st.markdown(
    """
    <div class="footer">
      &copy; 2025 Mover. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)
