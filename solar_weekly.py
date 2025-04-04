import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
from datetime import date

def solar_weekly_tab():
    st.title("Solar Weekly Report")

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

    # Generer download-linket baseret på brugerens input
    base_url = "https://moverdatawarehouse.azurewebsites.net/download/routestats"
    generated_url = (
        f"{base_url}?apikey=b48c55&Userid=6016"
        f"&FromDate={from_date.strftime('%Y-%m-%d')}"
        f"&ToDate={to_date.strftime('%Y-%m-%d')}"
    )

    st.markdown("### 2. Download link til rapport")
    st.markdown(f"[Download rapport]({generated_url})", unsafe_allow_html=True)
    st.info("Kopier linket og indsæt det i din browser for at hente Excel-filen manuelt.")

    st.markdown("### 3. Upload den hentede Excel-rapport")
    uploaded_file = st.file_uploader("Upload Solar Weekly Excel-fil", type=["xlsx"], key="sw_upload")

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            
            # Tjek for nødvendige kolonner
            required_columns = [
                "Booking ref.", "Date", "Route ID", "Pick up adress", "Vehicle type",
                "Delivery adress", "Delivery zipcode", "Booking to Mover", 
                "Pickup arrival", "Pickup completed", "Delivery completed"
            ]
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                st.error("Følgende kolonner mangler i uploadet fil: " + ", ".join(missing))
                return
            else:
                df_filtered = df[required_columns]
                st.success("✅ Filen er valid og indlæst korrekt.")
                st.dataframe(df_filtered)

                # Dataanalyse: Beskrivende statistik
                st.markdown("#### Data Analyse")
                st.write("Beskrivende statistik:")
                st.write(df_filtered.describe(include='all'))

                # Plot af antal bookinger per dag, hvis 'Date'-kolonnen findes
                if 'Date' in df_filtered.columns:
                    df_filtered['Date'] = pd.to_datetime(df_filtered['Date'], errors='coerce')
                    bookings_per_date = df_filtered.groupby('Date').size().reset_index(name='Antal Bookinger')
                    fig, ax = plt.subplots()
                    ax.plot(bookings_per_date['Date'], bookings_per_date['Antal Bookinger'], marker='o')
                    ax.set_title("Antal Bookinger per Dag")
                    ax.set_xlabel("Dato")
                    ax.set_ylabel("Antal Bookinger")
                    st.pyplot(fig)

                # Download-knap for den filtrerede rapport
                towrite = io.BytesIO()
                with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
                    df_filtered.to_excel(writer, index=False, sheet_name='SolarWeeklyReport')
                towrite.seek(0)
                st.download_button(
                    label="Download filtreret Solar Weekly Report",
                    data=towrite,
                    file_name="solar_weekly_report_filtered.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"Fejl under indlæsning af fil: {e}")
