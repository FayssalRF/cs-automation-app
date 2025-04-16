import streamlit as st
import pandas as pd
import io
from datetime import date, timedelta

# Forudsætter, at funktionen analyse_supportnote() er defineret et sted, fx i samme modul eller i en delt utils-fil.
def analyse_supportnote(note):
    # Dummy-funktion – erstat med din egen logik
    if pd.isna(note):
        return "Nej", ""
    note_lower = str(note).lower()
    # Eksempel: Returner "Ja" hvis note indeholder et nøgleord, ellers "Nej"
    keywords = ["eksempel", "fejl", "forsinket"]
    found = [kw for kw in keywords if kw in note_lower]
    if found:
        return "Ja", ", ".join(found)
    return "Nej", ""

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
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        except Exception as e:
            st.error("Fejl ved indlæsning af fil: " + str(e))
            return
        
        required_columns = [
            "SessionId", "Date", "CustomerId", "CustomerName", 
            "EstDuration", "ActDuration", "DurationDifference", "SupportNote"
        ]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            st.error("Følgende nødvendige kolonner mangler: " + ", ".join(missing))
        else:
            # Ryd op i data: Drop rækker uden SupportNote eller CustomerName
            initial_rows = len(df)
            df = df.dropna(subset=["SupportNote", "CustomerName"])
            dropped_rows = initial_rows - len(df)
            if dropped_rows > 0:
                st.info(f"{dropped_rows} rækker blev droppet, da de manglede værdier i SupportNote eller CustomerName.")
            # Fjern rækker for "IKEA NL", så disse bliver håndteret separat
            df = df[~df["CustomerName"].str.contains("IKEA NL", case=False, na=False)]
            st.success("Filen er uploadet korrekt, og alle nødvendige kolonner er til stede!")
            
            # Anvend analyse på SupportNote og tilføj resultater i nye kolonner
            df["Keywords"] = df["SupportNote"].apply(lambda note: analyse_supportnote(note)[0])
            df["MatchingKeyword"] = df["SupportNote"].apply(lambda note: analyse_supportnote(note)[1])
            
            # Formatter "Date"-kolonnen til kort datoformat "DD-MM-ÅÅÅÅ"
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%d-%m-%Y")
            
            output_cols = [
                "SessionId", "Date", "CustomerId", "CustomerName", 
                "EstDuration", "ActDuration", "DurationDifference", 
                "SupportNote", "Keywords", "MatchingKeyword"
            ]
            
            # Vis samlet overordnet tabel med alle resultater
            st.markdown("#### Overordnede analyserede resultater:")
            st.dataframe(df[output_cols])
            
            # Kollapsibel sektion for "Resultater per kunde:" hvor kun de rækker med Keywords=="Ja" vises
            st.markdown("#### Resultater per kunde:")
            unique_customers = sorted(df["CustomerName"].unique())
            for customer in unique_customers:
                with st.expander(f"Kunde: {customer}"):
                    st.markdown(f'<h4 style="font-size:14px;">Kunde: {customer}</h4>', unsafe_allow_html=True)
                    df_customer = df[(df["CustomerName"] == customer) & (df["Keywords"] == "Ja")]
                    st.dataframe(df_customer[output_cols])
            
            # Gem samlet analyseret fil til download
            towrite = io.BytesIO()
            with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Analyseret")
            towrite.seek(0)
            st.download_button(
                label="Download analyseret Excel-fil", 
                data=towrite, 
                file_name="analyseret_controlling_report.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    # -------------------------------------------------------------------------
    # Ny sektion: IKEA NL Deviations
    st.markdown("### IKEA NL Deviations")
    st.write("Upload en Excel-fil med følgende kolonner:")
    st.write("RouteId, DriverId, Date, Slug, ActualStartTime, REVISEDActualStartTime, ActualEndTime, ActualDuration (min), REVISEDActualDuration (min), EstimatedStartTime, EstimatedEndTime, EstimateDuration (min), Deviation (min), Realtime-tag, SupportNote, Assessment, ShortNote")
    
    uploaded_dev_file = st.file_uploader("Upload Deviations Excel-fil", type=["xlsx", "xls"], key="deviations")
    if uploaded_dev_file is not None:
        try:
            df_dev = pd.read_excel(uploaded_dev_file, engine="openpyxl")
        except Exception as e:
            st.error("Fejl ved indlæsning af deviations fil: " + str(e))
            return
        
        required_columns_dev = [
            "RouteId", "DriverId", "Date", "Slug", "ActualStartTime", "REVISEDActualStartTime",
            "ActualEndTime", "ActualDuration (min)", "REVISEDActualDuration (min)", "EstimatedStartTime", 
            "EstimatedEndTime", "EstimateDuration (min)", "Deviation (min)", "Realtime-tag", 
            "SupportNote", "Assessment", "ShortNote"
        ]
        missing_dev = [col for col in required_columns_dev if col not in df_dev.columns]
        if missing_dev:
            st.error("Følgende nødvendige kolonner mangler i deviations filen: " + ", ".join(missing_dev))
        else:
            # Anvend analyse på SupportNote (kolonne "SupportNote")
            df_dev["Keywords"] = df_dev["SupportNote"].apply(lambda note: analyse_supportnote(note)[0])
            df_dev["MatchingKeyword"] = df_dev["SupportNote"].apply(lambda note: analyse_supportnote(note)[1])
            # Formatter "Date"-kolonnen til kort datoformat
            df_dev["Date"] = pd.to_datetime(df_dev["Date"], errors="coerce").dt.strftime("%d-%m-%Y")
            
            output_cols_dev = [
                "RouteId", "DriverId", "Date", "Slug", "ActualStartTime", "REVISEDActualStartTime",
                "ActualEndTime", "ActualDuration (min)", "REVISEDActualDuration (min)", "EstimatedStartTime", 
                "EstimatedEndTime", "EstimateDuration (min)", "Deviation (min)", "Realtime-tag", 
                "SupportNote", "Assessment", "ShortNote", "Keywords", "MatchingKeyword"
            ]
            
            st.markdown("#### Analyserede IKEA NL Deviations:")
            st.dataframe(df_dev[output_cols_dev])
            
            towrite_dev = io.BytesIO()
            with pd.ExcelWriter(towrite_dev, engine="xlsxwriter") as writer:
                df_dev.to_excel(writer, index=False, sheet_name="IKEA_NL_Deviations")
            towrite_dev.seek(0)
            st.download_button(
                label="Download analyseret Deviations rapport", 
                data=towrite_dev, 
                file_name="analyseret_IKEA_NL_Deviations.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
