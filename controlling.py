import streamlit as st
import pandas as pd
import io
from datetime import date, timedelta  # Husk at importere timedelta

# Indlæs keywords fra keywords.txt (dette kan også placeres i en fælles utils.py, hvis ønsket)
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
    
    # Udregn forrige uges Yearweek (år + to-cifret uge)
    today = date.today()
    last_week_date = today - timedelta(days=7)
    last_week_str = last_week_date.strftime("%Y") + f"{last_week_date.isocalendar()[1]:02d}"
    data_link = f"https://moverdatawarehouse.azurewebsites.net/download/DurationControlling?apikey=2d633b&Userid=74859&Yearweek={last_week_str}"
    
    # Indsæt linket med teksten for sidste uge, f.eks. "Download Controlling report for sidste uge (2025-35)"
    st.markdown(f"[Download Controlling report for sidste uge (2025-{last_week_date.isocalendar()[1]:02d})]({data_link})")
    
    st.write("Upload en Excel-fil med controlling data, og få automatisk analyserede resultater baseret på nøgleord. Filen skal indeholde følgende kolonner:")
    st.write("- SessionId, Date, CustomerId, CustomerName, EstDuration, ActDuration, DurationDifference, SupportNote")
    
    uploaded_file = st.file_uploader("Vælg Excel-fil", type=["xlsx", "xls"], key="controlling")
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        except Exception as e:
            st.error("Fejl ved indlæsning af fil: " + str(e))
            return
        required_columns = ["SessionId", "Date", "CustomerId", "CustomerName", "EstDuration", "ActDuration", "DurationDifference", "SupportNote"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            st.error("Følgende nødvendige kolonner mangler: " + ", ".join(missing))
        else:
            initial_rows = len(df)
            df = df.dropna(subset=["SupportNote", "CustomerName"])
            dropped_rows = initial_rows - len(df)
            if dropped_rows > 0:
                st.info(f"{dropped_rows} rækker blev droppet, da de manglede værdier i SupportNote eller CustomerName.")
            df = df[~df["CustomerName"].str.contains("IKEA NL", case=False, na=False)]
            st.success("Filen er uploadet korrekt, og alle nødvendige kolonner er til stede!")
            df["Keywords"] = df["SupportNote"].apply(lambda note: analyse_supportnote(note)[0])
            df["MatchingKeyword"] = df["SupportNote"].apply(lambda note: analyse_supportnote(note)[1])
            output_cols = ["SessionId", "Date", "CustomerId", "CustomerName", "EstDuration", "ActDuration", "DurationDifference", "SupportNote", "Keywords", "MatchingKeyword"]
            st.markdown("#### Analyserede Resultater - Med ekstra tid (Ja):")
            df_yes = df[df["Keywords"] == "Ja"]
            st.dataframe(df_yes[output_cols])
            st.markdown("#### Analyserede Resultater - Uden ekstra tid (Nej):")
            df_no = df[df["Keywords"] == "Nej"]
            st.dataframe(df_no[output_cols])
            unique_customers = sorted(df["CustomerName"].unique())
            customer_list = "\n".join(["- " + str(customer) for customer in unique_customers])
            st.markdown("#### Unikke Kunder:")
            st.markdown(customer_list)
            towrite = io.BytesIO()
            with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Analyseret')
            towrite.seek(0)
            st.download_button(label="Download analyseret Excel-fil", data=towrite, file_name="analyseret_controlling_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
