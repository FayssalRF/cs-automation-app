import streamlit as st
import pandas as pd
import io
import requests
from datetime import date
import time

def solar_weekly_tab():
    st.title("Solar Weekly Report")
    st.markdown("Vælg en periode (maks 7 dage) for rapporten:")
    from_date = st.date_input("Fra dato", value=date(2025, 1, 1), key="from_date")
    to_date = st.date_input("Til dato", value=date(2025, 1, 7), key="to_date")
    
    if st.button("Hent rapport"):
        if to_date < from_date:
            st.error("Til dato skal være efter fra dato!")
            return
        if (to_date - from_date).days > 7:
            st.error("Perioden må ikke være mere end 7 dage!")
            return
        
        # Konstruer URL'en med de valgte datoer
        url = f"https://moverdatawarehouse.azurewebsites.net/download/routestats?apikey=b48c55&Userid=6016&FromDate={from_date.strftime('%Y-%m-%d')}&ToDate={to_date.strftime('%Y-%m-%d')}"
        st.info("Henter rapport fra: " + url)
        
        try:
            # Øg timeout til 30 sekunder
            response = requests.get(url, timeout=30)
            
            # Log HTTP statuskode og headers
            st.write("HTTP Status Code:", response.status_code)
            st.write("Response Headers:", response.headers)
            
            if not response.ok:
                st.error("Forespørgslen mislykkedes. Status kode: " + str(response.status_code))
                return
            
            # Tjek om responsen indeholder data
            if len(response.content) == 0:
                st.error("Responsen er tom, filen kunne ikke hentes.")
                return
            
            # Forsøg at læse Excel-data med openpyxl
            try:
                df_sw = pd.read_excel(io.BytesIO(response.content), engine='openpyxl')
            except Exception as e:
                st.error("Fejl ved læsning af Excel-fil: " + str(e))
                return
            
            required_columns_sw = [
                "Booking ref.", "Date", "Route ID", "Pick up adress", "Vehicle type",
                "Delivery adress", "Delivery zipcode", "Booking to Mover", 
                "Pickup arrival", "Pickup completed", "Delivery completed"
            ]
            missing_sw = [col for col in required_columns_sw if col not in df_sw.columns]
            if missing_sw:
                st.error("Følgende nødvendige kolonner mangler i rapporten: " + ", ".join(missing_sw))
                return
            
            df_final_sw = df_sw[required_columns_sw]
            st.success("Rapporten er hentet!")
            st.dataframe(df_final_sw)
            
            towrite_sw = io.BytesIO()
            with pd.ExcelWriter(towrite_sw, engine='xlsxwriter') as writer:
                df_final_sw.to_excel(writer, index=False, sheet_name='SolarWeeklyReport')
            towrite_sw.seek(0)
            
            st.download_button(
                label="Download Solar Weekly Report",
                data=towrite_sw,
                file_name="solar_weekly_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error("Fejl ved hentning af rapport: " + str(e))
