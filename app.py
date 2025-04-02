import streamlit as st
import pandas as pd
import io
import requests
from PIL import Image
from datetime import date

# Sikkerhed: Enkel login-godkendelse
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Login")
    password = st.text_input("Indtast adgangskode", type="password")
    if st.button("Login"):
        if password == "CSlikestomoveitmoveit123":  # Ændr denne kode til din ønskede adgangskode
            st.session_state.authenticated = True
            st.success("Adgangskode korrekt!")
        else:
            st.error("Forkert adgangskode!")
    st.stop()

# Konfigurer siden
st.set_page_config(
    page_title="Analyser",
    page_icon=":bar_chart:",
    layout="wide"
)

# Tilføj brugerdefineret CSS med opdaterede knap-stilarter
st.markdown(
    """
    <style>
    /* Importér Open Sans fra Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap');

    /* Generel typografi */
    body, .main, p, li, .stMarkdown {
        font-family: 'Open Sans', sans-serif;
        font-size: 16pt !important;
        font-weight: 400 !important;
        color: #000 !important;
    }
    
    /* Headings */
    h1 {
        font-family: 'Open Sans', sans-serif;
        font-size: 3em !important;
        font-weight: 400 !important;
        color: #333333 !important;
    }
    h2 {
        font-family: 'Open Sans', sans-serif;
        font-size: 2.5em !important;
        font-weight: 400 !important;
        color: #333333 !important;
    }
    h3 {
        font-family: 'Open Sans', sans-serif;
        font-size: 2em !important;
        font-weight: 400 !important;
        color: #333333 !important;
    }
    
    /* Primære knapper (standard) */
    .stButton>button {
        font-family: 'Open Sans', sans-serif;
        font-size: 16pt !important;
        font-weight: 700 !important;
        background-color: #191970;
        color: white !important;
        border: none;
        padding: 10px 24px;
        border-radius: 25px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    /* Labels fra file-uploader */
    .stFileUploader label {
        font-family: 'Open Sans', sans-serif;
        font-size: 16pt !important;
        font-weight: 400 !important;
        text-transform: lowercase;
        color: #008080 !important;
    }
    
    /* Margin mellem fanepunkterne */
    [data-baseweb="tab"] {
        margin-right: 30px !important;
    }
    
    /* Specifik styling for "Hent rapport" knappen */
    .hentRapportContainer .stButton > button {
        background-color: #ADD8E6 !important; /* lyseblå */
        color: white !important;
        font-weight: 700 !important;
    }
    .hentRapportContainer .stButton > button:active {
        background-color: white !important;
        color: #191970 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Forsøg at indlæse logoet med PIL og vis med st.image med en bredde på 300px (øverst til venstre)
try:
    logo = Image.open("moverLogotype_blue.png")
    st.image(logo, width=300)
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
except Exception as e:
    st.error("Fejl ved indlæsning af logo: " + str(e))

# Læs keywords fra den eksterne fil "keywords.txt"
try:
    with open("keywords.txt", "r", encoding="utf-8") as file:
        all_keywords = [line.strip() for line in file if line.strip()]
except Exception as e:
    st.error("Fejl ved indlæsning af keywords: " + str(e))
    all_keywords = []
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

# Opret fanebjælke med 5 faner: Forside, Controlling Report Analyzer, Solar Weekly Report, Solar CO2 Report, Revenue analyser
tabs = st.tabs(["Forside", "Controlling Report Analyzer", "Solar Weekly Report", "Solar CO2 Report", "Revenue analyser"])

# Fanen: Forside
with tabs[0]:
    st.markdown("<div style='text-align: center;'><h1>Customer Success Automation site</h1></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'><p>vælg et menupunkt i fanebjælken ovenfor for at komme videre.</p></div>", unsafe_allow_html=True)

# Fanen: Controlling Report Analyzer
with tabs[1]:
    st.title("Controlling Report Analyse")
    st.markdown("### Velkommen til appen til analyse af controlling rapporter")
    st.write("Upload en Excel-fil med controlling data, og få automatisk analyserede resultater baseret på nøgleord. Filen skal indeholde følgende kolonner:")
    st.write("- SessionId, Date, CustomerId, CustomerName, EstDuration, ActDuration, DurationDifference, SupportNote")
    
    uploaded_file = st.file_uploader("Vælg Excel-fil", type=["xlsx", "xls"], key="controlling")
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        except Exception as e:
            st.error("Fejl ved indlæsning af fil: " + str(e))
            df = None
        
        if df is not None:
            required_columns = [
                "SessionId", "Date", "CustomerId", "CustomerName", 
                "EstDuration", "ActDuration", "DurationDifference", "SupportNote"
            ]
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                st.error("Følgende nødvendige kolonner mangler: " + ", ".join(missing))
            else:
                initial_rows = len(df)
                df = df.dropna(subset=["SupportNote", "CustomerName"])
                dropped_rows = initial_rows - len(df)
                if dropped_rows > 0:
                    st.info(f"{dropped_rows} rækker blev droppet, da de manglede værdier i SupportNote eller CustomerName.")
                
                before_filter = len(df)
                df = df[~df["CustomerName"].str.contains("IKEA NL", case=False, na=False)]
                filtered_rows = before_filter - len(df)
                if filtered_rows > 0:
                    st.info(f"{filtered_rows} rækker blev droppet, da de indeholdt 'IKEA NL' i CustomerName.")
                
                st.success("Filen er uploadet korrekt, og alle nødvendige kolonner er til stede!")
                
                df["Keywords"] = df["SupportNote"].apply(lambda note: analyse_supportnote(note)[0])
                df["MatchingKeyword"] = df["SupportNote"].apply(lambda note: analyse_supportnote(note)[1])
                
                output_cols = [
                    "SessionId", "Date", "CustomerId", "CustomerName", 
                    "EstDuration", "ActDuration", "DurationDifference", "SupportNote", 
                    "Keywords", "MatchingKeyword"
                ]
                
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
                
                st.download_button(
                    label="Download analyseret Excel-fil",
                    data=towrite,
                    file_name="analyseret_controlling_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# Fanen: Solar Weekly Report – hent data fra datawarehouse-linket med bekræftelsesknap
with tabs[2]:
    st.title("Solar Weekly Report")
    st.markdown("Vælg en periode (maks 7 dage) for rapporten:")
    from_date = st.date_input("Fra dato", value=date(2025, 1, 1), key="from_date")
    to_date = st.date_input("Til dato", value=date(2025, 1, 7), key="to_date")
    
    # Pak knappen ind i en container med en særskilt CSS-klasse for "Hent rapport" knappen
    with st.container():
        st.markdown('<div class="hentRapportContainer">', unsafe_allow_html=True)
        hent_rapport_clicked = st.button("Hent rapport")
        st.markdown('</div>', unsafe_allow_html=True)
    
    if hent_rapport_clicked:
        if to_date < from_date:
            st.error("Til dato skal være efter fra dato!")
        elif (to_date - from_date).days > 7:
            st.error("Perioden må ikke være mere end 7 dage!")
        else:
            url = f"https://moverdatawarehouse.azurewebsites.net/download/routestats?apikey=b48c55&Userid=6016&FromDate={from_date.strftime('%Y-%m-%d')}&ToDate={to_date.strftime('%Y-%m-%d')}"
            st.info("Henter rapport fra: " + url)
            try:
                response = requests.get(url)
                response.raise_for_status()
                df_sw = pd.read_excel(io.BytesIO(response.content), engine='openpyxl')
                required_columns_sw = ["Booking ref.", "Date", "Route ID", "Pick up adress", "Vehicle type", "Delivery adress", "Delivery zipcode", "Booking to Mover", "Pickup arrival", "Pickup completed", "Delivery completed"]
                missing_sw = [col for col in required_columns_sw if col not in df_sw.columns]
                if missing_sw:
                    st.error("Følgende nødvendige kolonner mangler i rapporten: " + ", ".join(missing_sw))
                else:
                    df_final_sw = df_sw[required_columns_sw]
                    st.success("Rapporten er hentet!")
                    st.dataframe(df_final_sw)
                    
                    towrite_sw = io.BytesIO()
                    with pd.ExcelWriter(towrite_sw, engine='xlsxwriter') as writer:
                        df_final_sw.to_excel(writer, index=False, sheet_name='SolarWeeklyReport')
                    towrite_sw.seek(0)
                    
                    st.download_button(
                        label="Download Solar Weekly Report",
                        data=towrite_sw,
                        file_name="solar_weekly_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error("Fejl ved hentning af rapport: " + str(e))

# Fanen: Solar CO2 Report
with tabs[3]:
    st.title("Solar CO2 Report")
    st.write("Denne fane er under udvikling.")

# Fanen: Revenue analyser
with tabs[4]:
    st.title("Revenue analyser")
    st.write("Denne fane er under udvikling.")
