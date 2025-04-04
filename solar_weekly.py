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
        
        url = f"https://moverdatawarehouse.azurewebsites.net/download/routestats?apikey=b48c55&Userid=6016&FromDate={from_date.strftime('%Y-%m-%d')}&ToDate={to_date.strftime('%Y-%m-%d')}"
        st.info("Henter rapport fra: " + url)
        try:
            max_tries = 10
            success = False
            df_sw = None
            for i in range(max_tries):
                time.sleep(10)  # 10 sekunders pause mellem forsøg
                try:
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    st.write("HTTP Status Code:", response.status_code)
                    st.write("Response Headers:", response.headers)
                    # Tjek om Content-Type indikerer HTML
                    content_type = response.headers.get("Content-Type", "").lower()
                    if "html" in content_type:
                        st.info(f"Forsøg {i+1} af {max_tries}: Modtaget indhold er HTML, rapporten er endnu ikke klar...")
                        continue
                    # Forsøg at læse Excel-data
                    df_sw = pd.read_excel(io.BytesIO(response.content), engine='openpyxl')
                    success = True
                    break
                except Exception as e:
                    st.info(f"Forsøg {i+1} af {max_tries}: Rapporten er endnu ikke klar...")
            if not success:
                st.error("Rapporten kunne ikke hentes inden for tidsgrænsen. Prøv igen senere.")
                return

            required_columns_sw = [
                "Booking ref.", "Date", "Route ID", "Pick up adress", "Vehicle type",
                "Delivery adress", "Delivery zipcode", "Booking to Mover", 
                "Pickup arrival", "Pickup completed", "Delivery completed"
            ]
            missing_sw = [col for col in required_columns_sw if col not in df_sw.columns]
            if missing_sw:
                st.error("Følgende nødvendige kolonner mangler i rapporten: " + ", ".join(missing_sw))
            else:
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
