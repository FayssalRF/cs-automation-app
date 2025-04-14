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

def create_session_link(sid):
    """Laver et hyperlink for en given SessionId.
       Når man klikker, åbnes linket i en ny fane."""
    return f'<a href="https://admin.mover.dk/dk/da/user-area/trips/session/{sid}/" target="_blank">{sid}</a>'

def controlling_tab():
    st.title("Controlling Report Analyse")
    st.markdown("### Velkommen til appen til analyse af controlling rapporter")
    
    # Udregn forrige uges Yearweek (år + to-cifret uge)
    today = date.today()
    last_week_date = today - timedelta(days=7)
    last_week_str = last_week_date.strftime("%Y") + f"{last_week_date.isocalendar()[1]:02d}"
    data_link = f"https://moverdatawarehouse.azurewebsites.net/download/DurationControlling?apikey=2d633b&Userid=74859&Yearweek={last_week_str}"
    
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
            # Dataoprydning
            initial_rows = len(df)
            df = df.dropna(subset=["SupportNote", "CustomerName"])
            dropped_rows = initial_rows - len(df)
            if dropped_rows > 0:
                st.info(f"{dropped_rows} rækker blev droppet, da de manglede værdier i SupportNote eller CustomerName.")
            df = df[~df["CustomerName"].str.contains("IKEA NL", case=False, na=False)]
            st.success("Filen er uploadet korrekt, og alle nødvendige kolonner er til stede!")
            
            # Anvend analysen og tilføj kolonner for keywords
            df["Keywords"] = df["SupportNote"].apply(lambda note: analyse_supportnote(note)[0])
            df["MatchingKeyword"] = df["SupportNote"].apply(lambda note: analyse_supportnote(note)[1])
            
            # Formatter "Date"-kolonnen til formatet "DD-MM-ÅÅÅÅ"
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%d-%m-%Y")
            
            # Opdater SessionId-kolonnen, så den bliver til et hyperlink
            df["SessionId"] = df["SessionId"].apply(create_session_link)
            
            output_cols = ["SessionId", "Date", "CustomerId", "CustomerName", "EstDuration", "ActDuration", "DurationDifference", "SupportNote", "Keywords", "MatchingKeyword"]
            
            # Vis den overordnede analyse som en HTML-tabel
            st.markdown("#### Overordnede analyserede resultater:")
            st.markdown(df[output_cols].to_html(escape=False), unsafe_allow_html=True)
            
            # Vis resultater per kunde (kun med ekstra tid) i kollapsible sektioner
            unique_customers = sorted(df["CustomerName"].unique())
            st.markdown("#### Resultater per kunde (kun med ekstra tid):")
            for customer in unique_customers:
                with st.expander(f"Kunde: {customer}"):
                    # Overskrift med fast fontstørrelse 14px
                    st.markdown(f'<h4 style="font-size:14px;">Kunde: {customer}</h4>', unsafe_allow_html=True)
                    df_customer = df[(df["CustomerName"] == customer) & (df["Keywords"] == "Ja")]
                    st.markdown(df_customer[output_cols].to_html(escape=False), unsafe_allow_html=True)
            
            # Til download af Excel-fil – her fjernes HTML-tagget i SessionId
            df_download = df.copy()
            df_download["SessionId"] = df_download["SessionId"].str.extract(r'>(.*?)<')
            towrite = io.BytesIO()
            with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
                df_download.to_excel(writer, index=False, sheet_name='Analyseret')
            towrite.seek(0)
            st.download_button(
                label="Download analyseret Excel-fil", 
                data=towrite, 
                file_name="analyseret_controlling_report.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
