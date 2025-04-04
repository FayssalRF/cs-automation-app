import streamlit as st
import pandas as pd
import io
from datetime import date

def solar_weekly_tab():
    st.title("Solar Weekly Report")
    
    # 1. Vælg en periode (maks 7 dage)
    st.markdown("### 1. Vælg en periode (maks 7 dage)")
    col1, col2 = st.columns(2)
    with col1:
        from_date = st.date_input("Fra dato", value=date(2025, 1, 1), key="sw_from")
    with col2:
        to_date = st.date_input("Til dato", value=date(2025, 1, 7), key="sw_to")
    
    if to_date < from_date:
        st.error("❌ Til dato skal være efter fra dato!")
        return
    if (to_date - from_date).days > 7:
        st.error("❌ Perioden må ikke være mere end 7 dage!")
        return

    # 2. Generer datawarehouse-linket baseret på de valgte datoer
    base_url = "https://moverdatawarehouse.azurewebsites.net/download/routestats"
    generated_url = (
        f"{base_url}?apikey=b48c55&Userid=6016"
        f"&FromDate={from_date.strftime('%Y-%m-%d')}"
        f"&ToDate={to_date.strftime('%Y-%m-%d')}"
    )
    st.markdown("### 2. Download link til rapport")
    st.markdown(f"[Download rapport]({generated_url})", unsafe_allow_html=True)
    st.info("Når du klikker på linket, downloades rapporten i .xlsx format.")
    
    # 3. Upload den hentede Excel-rapport
    st.markdown("### 3. Upload den hentede Excel-rapport")
    uploaded_file = st.file_uploader("Upload Solar Weekly Excel-fil", type=["xlsx"], key="sw_upload")
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
            
            # Drop rækker hvor 'ADDRESS REFERENCE' (kolonne B) er tom
            df = df.dropna(subset=["ADDRESS REFERENCE"])
            
            final_rows = []
            # Gruppér efter "ADDRESS REFERENCE" (Booking ref.)
            for ref, group in df.groupby("ADDRESS REFERENCE"):
                # Find rækken med Pickup og rækken med Delivery
                pickup = group[group["StopType"].str.strip().str.lower() == "pickup"]
                delivery = group[group["StopType"].str.strip().str.lower() == "delivery"]
                
                if pickup.empty or delivery.empty:
                    continue  # Spring over, hvis enten pickup eller delivery mangler
                
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
            
            # Download-knap for den endelige rapport
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
