# solar_weekly.py

import streamlit as st
import pandas as pd
import io
from datetime import date, timedelta

def solar_weekly_tab():
    st.title("Solar Weekly Report **(stadig under udvikling)**")

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
    st.info("Klik for at hente rå .xlsx med alle ruter.")
    
    # 3. Upload af den hentede fil
    st.markdown("### Upload den hentede Excel-rapport")
    uploaded_file = st.file_uploader("Vælg Excel-fil", type=["xlsx"], key="sw_upload")
    if not uploaded_file:
        return

    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception as e:
        st.error(f"Fejl under indlæsning af fil: {e}")
        return

    # 4. Filtrér kun rækker hvor STATUS == "Completed"
    if "STATUS" not in df.columns:
        st.error("Kolonnen 'STATUS' findes ikke i filen.")
        return
    df = df[df["STATUS"].astype(str).str.strip().str.lower() == "completed"]

    # 5. Konverter kolonner B, C og D til tal
    try:
        col_b, col_c, col_d = df.columns[1], df.columns[2], df.columns[3]
    except IndexError:
        st.error("Filen har ikke nok kolonner til B, C og D.")
        return

    df[col_b] = pd.to_numeric(df[col_b], errors="coerce")
    df[col_c] = pd.to_numeric(df[col_c], errors="coerce")
    df[col_d] = pd.to_numeric(df[col_d], errors="coerce")

    # 6. Frasortér tomme og ikke-numeriske i kolonne D
    df = df.dropna(subset=[col_d])

    # 7. Sortér efter kolonne D (mindst→størst)
    df = df.sort_values(by=col_d)

    st.success("✅ Data filtreret og sorteret korrekt.")
    st.dataframe(df)

    # 8. Download-knap med Excel-formattering
    towrite = io.BytesIO()
    with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Filtered")
        workbook  = writer.book
        worksheet = writer.sheets["Filtered"]

        # Format kolonne H som kort dato (dd-mm-yyyy)
        date_fmt = workbook.add_format({'num_format': 'dd-mm-yyyy'})
        worksheet.set_column('H:H', None, date_fmt)

        # Format kolonnerne E, L, M, N, O og P som tid (hh:mm:ss)
        time_fmt = workbook.add_format({'num_format': 'hh:mm:ss'})
        for col in ['E', 'L', 'M', 'N', 'O', 'P']:
            worksheet.set_column(f'{col}:{col}', None, time_fmt)

    towrite.seek(0)
    st.download_button(
        label="Download filtreret rapport",
        data=towrite,
        file_name=f"solar_weekly_filtered_{week_str}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
