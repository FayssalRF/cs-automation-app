import streamlit as st
import pandas as pd
import io

st.set_page_config(
    page_title="Analyser",
    page_icon=":bar_chart:",
    layout="wide"
)

# Læs keywords fra den eksterne tekstfil "keywords.txt"
try:
    with open("keywords.txt", "r", encoding="utf-8") as file:
        all_keywords = [line.strip() for line in file if line.strip()]
except Exception as e:
    st.error("Fejl ved indlæsning af keywords: " + str(e))
    all_keywords = []

# Sørg for, at alle keywords er i små bogstaver (for case-insensitiv søgning)
all_keywords = [kw.lower() for kw in all_keywords]

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

# Eksempel: Brug keywords i din "Controlling Report Analyzer" app
uploaded_file = st.file_uploader("Vælg Excel-fil", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error("Fejl ved indlæsning af fil: " + str(e))
        df = None

    if df is not None:
        # Tjek for de nødvendige kolonner
        required_columns = [
            "SessionId", "Date", "CustomerId", "CustomerName", 
            "EstDuration", "ActDuration", "DurationDifference", "SupportNote"
        ]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            st.error("Følgende nødvendige kolonner mangler: " + ", ".join(missing))
        else:
            # Fjern rækker med tomme celler i SupportNote eller CustomerName
            initial_rows = len(df)
            df = df.dropna(subset=["SupportNote", "CustomerName"])
            dropped_rows = initial_rows - len(df)
            if dropped_rows > 0:
                st.info(f"{dropped_rows} rækker blev droppet, da de manglede værdier i SupportNote eller CustomerName.")
            
            # Eksempel: Tilføj en kolonne med analysedata baseret på keywords
            df["Keywords"] = df["SupportNote"].apply(lambda note: analyse_supportnote(note)[0])
            df["MatchingKeyword"] = df["SupportNote"].apply(lambda note: analyse_supportnote(note)[1])
            
            st.dataframe(df)
            
            # Konverter data til en Excel-fil, som brugeren kan downloade
            towrite = io.BytesIO()
            with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Analyseret')
            towrite.seek(0)
            
            st.download_button(
                label="Download analyseret Excel-fil",
                data=towrite,
                file_name="analyseret_controlling_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
