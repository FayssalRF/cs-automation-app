import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
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

    # 2. Producer datawarehouse-linket
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
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            
            # Krævede kolonner – her antages at "Booking ref." fungerer som delivery reference
            required_columns = [
                "Booking ref.", "Date", "Route ID", "Driver ID", "Pick up adress",
                "Vehicle type", "Delivery adress", "Delivery zipcode", "Booking to Mover",
                "Pickup arrival", "Pickup completed", "Delivery completed"
            ]
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                st.error("Følgende kolonner mangler i uploadet fil: " + ", ".join(missing))
                return
            
            # Filtrer til de nødvendige kolonner
            df_filtered = df[required_columns].copy()
            
            # Sorter efter delivery reference (Booking ref.) i stigende rækkefølge
            df_filtered.sort_values("Booking ref.", inplace=True, ascending=True)
            
            # Fjern "Booking ref." fra output – den endelige rapport skal kun indeholde:
            # Date, Route ID, Driver ID, Pick up adress, Vehicle type, Delivery adress,
            # Delivery zipcode, Booking to Mover, Pickup arrival, Pickup completed, Delivery completed
            final_report = df_filtered.drop(columns=["Booking ref."])
            
            st.success("✅ Filen er valid og indlæst korrekt.")
            st.dataframe(final_report)
            
            # Dataanalyse: Beskrivende statistik
            st.markdown("#### Data Analyse")
            st.write("Beskrivende statistik:")
            st.write(final_report.describe(include='all'))
            
            # Plot af antal bookinger per dag (baseret på 'Date')
            if 'Date' in final_report.columns:
                final_report['Date'] = pd.to_datetime(final_report['Date'], errors='coerce')
                bookings_per_date = final_report.groupby('Date').size().reset_index(name='Antal Bookinger')
                fig, ax = plt.subplots()
                ax.plot(bookings_per_date['Date'], bookings_per_date['Antal Bookinger'], marker='o')
                ax.set_title("Antal Bookinger per Dag")
                ax.set_xlabel("Dato")
                ax.set_ylabel("Antal Bookinger")
                st.pyplot(fig)
            
            # Download-knap for den filtrerede rapport med de ønskede kolonner
            towrite = io.BytesIO()
            with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
                final_report.to_excel(writer, index=False, sheet_name='SolarWeeklyReport')
            towrite.seek(0)
            st.download_button(
                label="Download filtreret Solar Weekly Report",
                data=towrite,
                file_name="solar_weekly_report_filtered.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Fejl under indlæsning af fil: {e}")
