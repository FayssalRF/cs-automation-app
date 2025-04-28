import streamlit as st
import pandas as pd
import io
from datetime import date, timedelta

# Indlæs keywords fra keywords.txt
try:
    with open("keywords.txt", "r", encoding="utf-8") as file:
        all_keywords = [line.strip().lower() for line in file if line.strip()]
except Exception as e:
    st.error("Fejl ved indlæsning af keywords: " + str(e))
    all_keywords = []

from ikea_nl_deviations import ikea_nl_deviations_tab

def analyse_supportnote(note):
    if pd.isna(note):
        return "Nej", ""
    note_lower = str(note).lower()
    matched = [kw for kw in all_keywords if kw in note_lower]
    if matched:
        matched = list(set(matched))
        return "Ja", ", ".join(matched)
    else:
        return "Nej", ""


def controlling_tab():
    st.title("Controlling Report Analyse")
    st.markdown("### Velkommen til appen til analyse af controlling rapporter")
    
    # Auto–calculate last ISO week
    today = date.today()
    last_week_date = today - timedelta(days=7)
    yearweek = last_week_date.strftime("%Y") + f"{last_week_date.isocalendar()[1]:02d}"
    data_link = (
        f"https://moverdatawarehouse.azurewebsites.net/download/DurationControlling"
        f"?apikey=2d633b&Userid=74859&Yearweek={yearweek}"
    )
    st.markdown(f"[Download Controlling report for sidste uge (ISO {last_week_date.isocalendar()[1]:02d})]({data_link})")
    
    st.write("Upload en Excel-fil med controlling data med kolonnerne: SessionId, Date, CustomerId, CustomerName, EstDuration, ActDuration, DurationDifference, SupportNote")
    uploaded_file = st.file_uploader("Vælg controlling Excel-fil", type=["xlsx", "xls"], key="controlling")
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        except Exception as e:
            st.error("Fejl ved indlæsning af fil: " + str(e))
            return
        
        required_cols = ["SessionId", "Date", "CustomerId", "CustomerName", "EstDuration", "ActDuration", "DurationDifference", "SupportNote"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error("Manglende kolonner: " + ", ".join(missing))
            return

        # Drop rows without SupportNote or CustomerName
        initial = len(df)
        df = df.dropna(subset=["SupportNote", "CustomerName"])
        dropped = initial - len(df)
        if dropped > 0:
            st.info(f"{dropped} rækker blev droppet pga. manglende SupportNote/CustomerName.")
        
        # Exclude IKEA NL deviations for later
        df = df[~df["CustomerName"].str.contains("IKEA NL", case=False, na=False)]
        
        # Analyse af support notes
        df["Keywords"] = df["SupportNote"].apply(lambda n: analyse_supportnote(n)[0])
        df["MatchingKeyword"] = df["SupportNote"].apply(lambda n: analyse_supportnote(n)[1])
        
        # Formatter Date
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%d-%m-%Y")

        output_cols = required_cols + ["Keywords", "MatchingKeyword"]
        st.markdown("#### Overordnede analyserede controlling resultater:")
        st.dataframe(df[output_cols])
        
        st.markdown("#### Resultater per kunde:")
        for cust in sorted(df["CustomerName"].unique()):
            with st.expander(f"Kunde: {cust}"):
                df_c = df[(df["CustomerName"] == cust) & (df["Keywords"] == "Ja")]
                st.dataframe(df_c[output_cols])

        # Download analyseret controlling rapport
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Analyseret")
        buf.seek(0)
        st.download_button(
            label="Download analyseret controlling rapport",
            data=buf,
            file_name="analyseret_controlling_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # -----------------------------------------------------------------------
    # IKEA NL Deviations under Controlling tab
    st.markdown("### IKEA NL Deviations")
    ikea_nl_deviations_tab()
