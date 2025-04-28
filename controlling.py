import streamlit as st
import pandas as pd
import io
from datetime import date, timedelta
from ikea_nl_deviations import ikea_nl_deviations_tab

# Indlæs keywords til controlling-delen (NB: ikea_nl_deviations har sin egen indlæsning)
try:
    with open("keywords.txt", "r", encoding="utf-8") as file:
        all_keywords = [line.strip().lower() for line in file if line.strip()]
except Exception as e:
    st.error("Fejl ved indlæsning af keywords: " + str(e))
    all_keywords = []

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
    
    # Auto-beregn ISO uge
    today = date.today()
    last_week_date = today - timedelta(days=7)
    yearweek = last_week_date.strftime("%Y") + f"{last_week_date.isocalendar()[1]:02d}"
    link = (
        "https://moverdatawarehouse.azurewebsites.net/download/DurationControlling"
        f"?apikey=2d633b&Userid=74859&Yearweek={yearweek}"
    )
    st.markdown(f"[Download Controlling report for sidste uge (ISO {last_week_date.isocalendar()[1]:02d})]({link})")
    
    st.write(
        "Upload en Excel-fil med controlling data, der indeholder kolonnerne:\n"
        "`SessionId`, `Date`, `CustomerId`, `CustomerName`, "
        "`EstDuration`, `ActDuration`, `DurationDifference`, `SupportNote`"
    )
    
    uploaded_file = st.file_uploader("Vælg controlling Excel-fil", type=["xlsx", "xls"], key="controlling")
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        except Exception as e:
            st.error("Fejl ved indlæsning af fil: " + str(e))
            return
        
        required = ["SessionId", "Date", "CustomerId", "CustomerName",
                    "EstDuration", "ActDuration", "DurationDifference", "SupportNote"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            st.error("Manglende kolonner: " + ", ".join(missing))
            return
        
        # Ryd op i data
        before = len(df)
        df = df.dropna(subset=["SupportNote", "CustomerName"])
        dropped = before - len(df)
        if dropped:
            st.info(f"{dropped} rækker droppet (mangled SupportNote/CustomerName).")
        
        # Exkluder IKEA NL (håndteres separat)
        df = df[~df["CustomerName"].str.contains("IKEA NL", case=False, na=False)]
        
        # Keyword-analyse
        df["Keywords"] = df["SupportNote"].apply(lambda n: analyse_supportnote(n)[0])
        df["MatchingKeyword"] = df["SupportNote"].apply(lambda n: analyse_supportnote(n)[1])
        
        # Formatér dato
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%d-%m-%Y")
        
        cols = required + ["Keywords", "MatchingKeyword"]
        st.markdown("#### Overordnede analyseresultater")
        st.dataframe(df[cols])
        
        st.markdown("#### Resultater per kunde")
        for cust in sorted(df["CustomerName"].unique()):
            with st.expander(f"Kunde: {cust}"):
                df_c = df[(df["CustomerName"] == cust) & (df["Keywords"] == "Ja")]
                st.dataframe(df_c[cols])
        
        # Download
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Analyseret")
        buf.seek(0)
        st.download_button(
            "Download analyseret controlling rapport",
            data=buf,
            file_name="analyseret_controlling_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # --- IKEA NL Deviations under Controlling tab som dropdown ---
    with st.expander("IKEA NL Deviations"):
        ikea_nl_deviations_tab()
