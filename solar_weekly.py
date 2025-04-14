import streamlit as st
import pandas as pd
import io
import openpyxl
from datetime import date, timedelta

def solar_weekly_tab():
    st.title("Solar Weekly Report (UNDER UDVIKLING)")
    
    # Beregn forrige uge – antag at ugen starter mandag og slutter søndag
    today = date.today()
    current_weekday = today.weekday()  # mandag=0, søndag=6
    this_monday = today - timedelta(days=current_weekday)
    last_monday = this_monday - timedelta(days=7)
    last_sunday = last_monday + timedelta(days=6)
    
    # Udregn ugenummer ud fra forrige uges mandag
    week_number = last_monday.isocalendar()[1]
    week_str = f"Uge {week_number:02d}"
    
    st.markdown(f"### Rapport for {week_str}")
    st.write(f"Valgt periode: {last_monday.strftime('%Y-%m-%d')} til {last_sunday.strftime('%Y-%m-%d')}")
    
    # Generer datawarehouse-linket baseret på den automatiske periode
    base_url = "https://moverdatawarehouse.azurewebsites.net/download/routestats"
    generated_url = (
        f"{base_url}?apikey=b48c55&Userid=6016"
        f"&FromDate={last_monday.strftime('%Y-%m-%d')}"
        f"&ToDate={last_sunday.strftime('%Y-%m-%d')}"
    )
    st.markdown("### Download link til rapport")
    st.markdown(f"[Download rapport]({generated_url})", unsafe_allow_html=True)
    st.info("Når du klikker på linket, downloades rapporten i .xlsx format.")
    
    # 3. Upload den hentede Excel-rapport
    st.markdown("### Upload den hentede Excel-rapport")
    uploaded_file = st.file_uploader("Upload Solar Weekly Excel-fil", type=["xlsx"], key="sw_upload")
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
            
            # Drop rækker hvor 'ADDRESS REFERENCE' er tom
            df = df.dropna(subset=["ADDRESS REFERENCE"])
            
            final_rows = []
            # Gruppér efter "ADDRESS REFERENCE" (Booking ref.) og udtræk data for Pickup og Delivery
            for ref, group in df.groupby("ADDRESS REFERENCE"):
                pickup = group[group["StopType"].str.strip().str.lower() == "pickup"]
                delivery = group[group["StopType"].str.strip().str.lower() == "delivery"]
                
                if pickup.empty or delivery.empty:
                    continue  # Spring over grupper uden begge typer data
                
                pickup_row = pickup.iloc[0]
                delivery_row = delivery.iloc[0]
                
                final_row = {
                    "Booking ref.": pickup_row["ADDRESS REFERENCE"],
                    "Date": pickup_row["Date"],
                    "Route ID": pickup_row["Route ID"],
                    "Driver ID": pickup_row["Driver ID"],
                    "Pick up adress": pickup_row["ADDRESS"],
                    "Vehicle type": pickup_row["Vehicle"],
                    "Delivery adress": delivery_row["ADDRESS"],
                    "Delivery zipcode": delivery_row["ZIPCODE"],
                    "Booking to Mover": pickup_row["BOOKING RECEIVED"],
                    "Pickup arrival": pickup_row["ARRIVED"],
                    "Pickup completed": pickup_row["COMPLETED"],
                    "Delivery completed": delivery_row["COMPLETED"]
                }
                final_rows.append(final_row)
            
            if not final_rows:
                st.error("Ingen gyldige rækker fundet med både Pickup og Delivery data.")
                return
            
            final_report = pd.DataFrame(final_rows)
            
            # Konverter Booking ref. til numerisk og sorter fra laveste til højeste
            final_report["Booking ref."] = pd.to_numeric(final_report["Booking ref."], errors="coerce")
            final_report = final_report.dropna(subset=["Booking ref."])
            final_report.sort_values("Booking ref.", inplace=True)
            
            st.success("✅ Filen er valid og analyseret korrekt.")
            st.dataframe(final_report)
            
            # Download-knap for den endelige rapport – her udarbejdes en separat rapportfaneblad
            towrite = io.BytesIO()
            with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
                final_report.to_excel(writer, index=False, sheet_name="SolarWeeklyReport")
            towrite.seek(0)
            st.download_button(
                label="Download filtreret Solar Weekly Report",
                data=towrite,
                file_name="solar_weekly_report_filtered.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Fejl under indlæsning og analyse af fil: {e}")
