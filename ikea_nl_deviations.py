import streamlit as st
import pandas as pd
import io

# Indlæs keywords
try:
    with open("keywords.txt", "r", encoding="utf-8") as f:
        all_keywords = [line.strip().lower() for line in f if line.strip()]
except Exception as e:
    st.error(f"Fejl ved indlæsning af keywords.txt: {e}")
    all_keywords = []

def analyse_supportnote(note):
    if pd.isna(note):
        return "Nej", ""
    text = str(note).lower()
    matched = [kw for kw in all_keywords if kw in text]
    if matched:
        matched = list(set(matched))
        return "Ja", ", ".join(matched)
    return "Nej", ""

def ikea_nl_deviations_tab():
    st.write(
        "Upload en Excel-fil med kolonnerne:\n"
        "`RouteId`, `DriverId`, `Date`, `Slug`, `ActualStartTime`, "
        "`REVISEDActualStartTime`, `ActualEndTime`, `ActualDuration (min)`, "
        "`REVISEDActualDuration (min)`, `EstimatedStartTime`, `EstimatedEndTime`, "
        "`EstimateDuration (min)`, `Deviation (min)`, `Realtime-tag`, "
        "`SupportNote`, `Assessment`, `ShortNote`"
    )
    
    uploaded = st.file_uploader("Vælg Deviations Excel-fil", type=["xlsx", "xls"], key="ikea_dev")
    if not uploaded:
        return

    try:
        df = pd.read_excel(uploaded, engine="openpyxl")
    except Exception as e:
        st.error(f"Kunne ikke læse filen: {e}")
        return

    required = [
        "RouteId", "DriverId", "Date", "Slug", "ActualStartTime", "REVISEDActualStartTime",
        "ActualEndTime", "ActualDuration (min)", "REVISEDActualDuration (min)", "EstimatedStartTime",
        "EstimatedEndTime", "EstimateDuration (min)", "Deviation (min)", "Realtime-tag",
        "SupportNote", "Assessment", "ShortNote"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error("Manglende kolonner: " + ", ".join(missing))
        return

    # Drop rækker uden supportnoter
    df = df.dropna(subset=["SupportNote"])
    if df.empty:
        st.error("Ingen rækker med SupportNote fundet.")
        return

    # Keyword-analyse
    df["Keywords"] = df["SupportNote"].apply(lambda n: analyse_supportnote(n)[0])
    df["MatchingKeyword"] = df["SupportNote"].apply(lambda n: analyse_supportnote(n)[1])

    # Formatér dato
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%d-%m-%Y")

    cols_out = required + ["Keywords", "MatchingKeyword"]
    st.dataframe(df[cols_out])

    # Download
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="IKEA_NL_Deviations")
    buf.seek(0)
    st.download_button(
        "Download analyseret Deviations",
        data=buf,
        file_name="ikea_nl_deviations.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
