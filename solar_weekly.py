# solar_weekly.py

import streamlit as st
import pandas as pd
import io
from datetime import date, timedelta

def solar_weekly_tab():
    st.title("Solar Weekly RouteStat-Report")

    # 1. Automatisk beregning af sidste uges periode (mandag–søndag)
    today = date.today()
    current_weekday = today.weekday()      # mandag=0 … søndag=6
    this_monday = today - timedelta(days=current_weekday)
    last_monday = this_monday - timedelta(days=7)
    last_sunday = last_monday + timedelta(days=6)
    week_number = last_monday.isocalendar()[1]
    week_str = f"Uge {week_number:02d}"
    
    st.markdown(f"### Rapport for {week_str}")
    st.write(f"Periode: {last_monday:%Y-%m-%d} til {last_sunday:%Y-%m-%d}")
    
    # 2. Link til download af rå rutedata
    base_url = "https://moverdatawarehouse.azurewebsites.net/download/routestats"
    url = (
        f"{base_url}?apikey=b48c55&Userid=6016"
        f"&FromDate={last_monday:%Y-%m-%d}"
        f"&ToDate={last_sunday:%Y-%m-%d}"
    )
    st.markdown(f"[Download rå rapport]({url})", unsafe_allow_html=True)
    st.info("Klik for at hente Solar RouteStat rapport for sidste uge")
    
