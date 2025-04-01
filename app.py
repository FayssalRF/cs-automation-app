import streamlit as st
import pandas as pd
import io

# Konfigurer siden
st.set_page_config(
    page_title="Analyser",
    page_icon=":bar_chart:",
    layout="wide"
)

# Tilføj brugerdefineret CSS med Open Sans, øget tekststørrelse og ekstra margin mellem fanepunkterne
st.markdown(
    """
    <style>
    /* Importér Open Sans fra Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400&display=swap');

    /* Anvend Open Sans, Regular, minimum 16pt for alle paragraffer, lister og markdown-elementer */
    body, .main, p, li, .stMarkdown {
        font-family: 'Open Sans', sans-serif;
        font-size: 16pt !important;
        font-weight: 400 !important;
        color: #000 !important;
    }
    
    /* Headings: Brug Open Sans, Regular med større skriftstørrelser og primær farve (#333333) */
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
    
    /* Knapper */
    .stButton>button {
        font-family: 'Open Sans', sans-serif;
        font-size: 16pt !important;
        font-weight: 400 !important;
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 5px;
        cursor: pointer;
    }
    
    /* Labels (fx. fra file-uploader) - vises i lower case med teal farve */
    .stFileUploader label {
        font-family: 'Open Sans', sans-serif;
        font-size: 16pt !important;
        font-weight: 400 !important;
        text-transform: lowercase;
        color: #008080 !important;
    }
    
    /* Øg afstanden mellem fanepunkterne til 30px */
    [data-baseweb="tab"] {
        margin-right: 30px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Læs keywords fra den eksterne fil "keywords.txt"
try:
    with open("keywords.txt", "r", encoding="utf-8") as file:
        all_keywords = [line.strip() for line in file if line.strip()]
except Exception as e:
    st.error("Fejl ved indlæsning af keywords: " + str(e))
    all_keywords = []

# Sørg for, at alle keywords er i små bogstaver for case-insensitiv søgning
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

# Vis logo øverst i midten
st.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <img src='moverLogotype_blue.png' style='max-width: 150px;' alt='Mover logo'>
    </div>
    """,
    unsafe_allow_html=True
)

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
    
    # Filupload
    uploaded_file = st.file_uploader("Vælg Excel-fil", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
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
                # Fjern rækker med tomme celler i SupportNote eller CustomerName
                initial_rows = len(df)
                df = df.dropna(subset=["SupportNote", "CustomerName"])
                dropped_rows = initial_rows - len(df)
                if dropped_rows > 0:
                    st.info(f"{dropped_rows} rækker blev droppet, da de manglede værdier i SupportNote eller CustomerName.")
                
                # Fjern rækker, hvor CustomerName indeholder "IKEA NL"
                before_filter = len(df)
                df = df[~df["CustomerName"].str.contains("IKEA NL", case=False, na=False)]
                filtered_rows = before_filter - len(df)
                if filtered_rows > 0:
                    st.info(f"{filtered_rows} rækker blev droppet, da de indeholdt 'IKEA NL' i CustomerName.")
                
                st.success("Filen er uploadet korrekt, og alle nødvendige kolonner er til stede!")
                
                # Anvend analysen på SupportNote
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

# Fanen: Solar Weekly Report
with tabs[2]:
    st.title("Solar Weekly Report")
    st.write("Denne fane er under udvikling.")

# Fanen: Solar CO2 Report
with tabs[3]:
    st.title("Solar CO2 Report")
    st.write("Denne fane er under udvikling.")

# Fanen: Revenue analyser
with tabs[4]:
    st.title("Revenue analyser")
    st.write("Denne fane er under udvikling.")
