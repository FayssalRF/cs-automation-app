import streamlit as st
import pandas as pd
import io

# Konfigurer siden
st.set_page_config(
    page_title="Analyser",
    page_icon=":bar_chart:",
    layout="wide"
)

# Tilføj brugerdefineret CSS med opdateret typography
st.markdown(
    """
    <style>
    /* Importér Open Sans fra Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400&display=swap');
    
    /* Anvend Open Sans, Regular, minimum 16pt for alle paragraffer og lister */
    body, .main, p, li, .stMarkdown {
        font-family: 'Open Sans', sans-serif;
        font-size: 16pt !important;
        font-weight: 400 !important;
        color: #000 !important;
    }
    
    /* Headings: Brug Open Sans, Regular, med lidt større fontstørrelser og en primær farve (#333333) */
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
    
    /* Labels (fx fra fil-uploader) - skal vises i lower case og med en teal farve */
    .stFileUploader label {
        font-family: 'Open Sans', sans-serif;
        font-size: 16pt !important;
        font-weight: 400 !important;
        text-transform: lowercase;
        color: #008080 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Opret fanebjælke med 5 faner, hvor den første er Forside
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
            # Tjek om alle nødvendige kolonner er til stede
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
                
                # Definer alle nøgleord for at identificere ekstra tid (både dansk og engelsk)
                all_keywords = [
                    "trafikale problemer", "kø på vejen", "vejen lukket", "lukket vej", "lukkede veje", "langsom trafik", "trafik langsom",
                    "road closed", "closed road", "heavy traffic", "traffic jam", "detour", "roadwork", "trafikprop", "vejarbejde", "trafik",
                    "ventetid ved afhentning", "forsinket lager", "lageret ikke klar", "afsender ikke klar", "florist åbnede senere", "florist forsinket",
                    "forsinket florist", "butikken ikke åben", "ikke åben butik", "ventetid", "forsinkelse", "ikke klar", "åbnede senere", "forsinket",
                    "waiting at location", "sender delayed", "florist not ready", "pickup delay", "no one at pickup", "delayed florist",
                    "waiting", "delay", "not ready", "opened late", "delayed",
                    "tilføjet ekstra stop", "ekstra stop tilføjet", "ændret rækkefølge", "rækkefølge ændret", "stop fjernet", "fjernet stop",
                    "ændret rute", "rute ændret", "stop omrokeret", "omrokeret stop", "ekstra leverance", "leverance tilføjet", "ændring",
                    "ekstra stop", "ekstra leverance", "ruteændring", "omrokering",
                    "changed route", "route changed", "extra stop", "stop added", "stop removed", "removed stop", "stop rearranged",
                    "rearranged stop", "additional delivery", "delivery added", "change", "extra stop", "additional delivery", "route change", "rearrangement",
                    "ingen svarer", "svarer ingen", "modtager ikke hjemme", "ikke hjemme modtager", "kunden ikke hjemme", "ikke hjemme kunde",
                    "kunden tager ikke telefon", "tager ikke telefon kunde", "kunde ikke kontaktbar", "ikke kontaktbar kunde", "modtager",
                    "ikke hjemme", "ingen svar", "ingen kontakt", "ikke kontaktbar",
                    "receiver not present", "not present receiver", "no answer", "answer not received", "not home", "home not",
                    "unanswered call", "call unanswered", "customer not reachable", "not reachable customer", "receiver", "not home", "no answer", "no contact", "unreachable",
                    "forkert vejnavn", "vejnavn forkert", "forkert husnummer", "husnummer forkert", "forkert postnummer", "postnummer forkert",
                    "kunne ikke finde adressen", "adressen kunne ikke findes", "ikke på adressen", "adressen ikke fundet", "adressen findes ikke",
                    "forkert adresse", "forkert placering", "ukendt adresse", "fejl i adresse", "adresseproblem",
                    "wrong address", "address wrong", "wrong street", "street wrong", "wrong house number", "house number wrong",
                    "wrong postal code", "postal code wrong", "could not find address", "address not found", "not at address",
                    "location not found", "location mismatch", "mismatch location", "wrong address", "unknown location", "address error",
                    "location mismatch", "address issue",
                    "porten lukket", "lukket port", "ingen adgang", "adgang nægtet", "nægtet adgang", "adgang kræver nøgle", "nøgle kræves for adgang",
                    "adgang via alarm", "alarmstyret adgang", "kunne ikke komme ind", "kom ikke ind", "adgang", "ingen adgang",
                    "adgang nægtet", "låst", "forhindret adgang", "port lukket",
                    "no access", "access denied", "denied access", "locked gate", "gate locked", "restricted area",
                    "entrance blocked", "blocked entrance", "could not enter", "entry failed", "no access", "locked", "denied",
                    "blocked", "restricted", "access issue",
                    "kunden sur", "sur kunde", "kunden klager", "klager kunde", "afsender afviser", "afviser afsender", "modtager uenig",
                    "uening modtager", "problem med kunde", "kunde problem", "utilfreds kunde", "klage", "afvisning", "uenighed",
                    "problem med kunde",
                    "receiver refused", "refused receiver", "sender issue", "issue with sender", "customer complaint", "complaint from customer",
                    "customer upset", "upset customer", "problem with customer", "complaint", "refusal", "issue", "disagreement", "unhappy customer",
                    "hospital", "skole", "center", "gågade", "etageejendom", "manglende parkering", "parkering mangler", "svært at finde",
                    "vanskelig at finde", "besværlig levering", "tricky adresse", "svær placering", "ingen parkering", "trafikeret område",
                    "tæt trafik",
                    "busy location", "location busy", "pedestrian zone", "no parking", "parking unavailable", "difficult to find",
                    "hard to find", "delivery challenge", "hospital", "school", "mall", "apartment building", "no parking",
                    "complicated delivery", "difficult address", "busy area",
                    "ekstra tid", "ekstratid", "extra time", "extratime"
                ]
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
