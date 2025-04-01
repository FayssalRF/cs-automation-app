import streamlit as st
import pandas as pd
import io

# Konfigurer siden
st.set_page_config(
    page_title="Customer Success Automation site",
    page_icon=":bar_chart:",
    layout="wide"
)

# Tilføj brugerdefineret CSS med større tekst og knap-stil
st.markdown(
    """
    <style>
    body, .main, p, li, .stMarkdown {
        font-size: 18px !important;
    }
    h1 {
        font-size: 3em !important;
    }
    h2 {
        font-size: 2.5em !important;
    }
    h3 {
        font-size: 2em !important;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 18px;
        width: 100%;
    }
    .stFileUploader label {
        font-weight: bold;
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Definer funktioner for de forskellige sider

def controlling_report_analyzer():
    st.header("Controlling Report Analyse")
    st.markdown("### Velkommen til appen til analyse af controlling rapporter")
    st.write("Upload en Excel-fil med controlling data, og få automatisk analyserede resultater baseret på nøgleord. Filen skal indeholde følgende kolonner:")
    st.write("- SessionId, Date, CustomerId, CustomerName, EstDuration, ActDuration, DurationDifference, SupportNote")
    
    uploaded_file = st.file_uploader("Vælg Excel-fil", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error("Fejl ved indlæsning af fil: " + str(e))
            return
        
        # Tjek for nødvendige kolonner
        required_columns = [
            "SessionId", "Date", "CustomerId", "CustomerName", 
            "EstDuration", "ActDuration", "DurationDifference", "SupportNote"
        ]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            st.error("Følgende nødvendige kolonner mangler: " + ", ".join(missing))
            return
        
        # Fjern rækker med tomme celler i SupportNote eller CustomerName
        initial_rows = len(df)
        df = df.dropna(subset=["SupportNote", "CustomerName"])
        dropped_rows = initial_rows - len(df)
        if dropped_rows > 0:
            st.info(f"{dropped_rows} rækker blev droppet, da de manglede værdier i SupportNote eller CustomerName.")
        
        # Fjern rækker med "IKEA NL" i CustomerName
        before_filter = len(df)
        df = df[~df["CustomerName"].str.contains("IKEA NL", case=False, na=False)]
        filtered_rows = before_filter - len(df)
        if filtered_rows > 0:
            st.info(f"{filtered_rows} rækker blev droppet, da de indeholdt 'IKEA NL' i CustomerName.")
        
        st.success("Filen er uploadet korrekt, og alle nødvendige kolonner er til stede!")
        
        # Definer nøgleord (inkl. ekstra tid)
        all_keywords = [
            # Trafikproblemer / Traffic Problems
            "trafikale problemer", "kø på vejen", "vejen lukket", "lukket vej", "lukkede veje", "langsom trafik", "trafik langsom",
            "road closed", "closed road", "heavy traffic", "traffic jam", "detour", "roadwork", "trafikprop", "vejarbejde", "trafik",
            # Ventetid / Pickup Delay
            "ventetid ved afhentning", "forsinket lager", "lageret ikke klar", "afsender ikke klar", "florist åbnede senere", "florist forsinket",
            "forsinket florist", "butikken ikke åben", "ikke åben butik", "ventetid", "forsinkelse", "ikke klar", "åbnede senere", "forsinket",
            "waiting at location", "sender delayed", "florist not ready", "pickup delay", "no one at pickup", "delayed florist",
            "waiting", "delay", "not ready", "opened late", "delayed",
            # Ekstra stop / ændringer
            "tilføjet ekstra stop", "ekstra stop tilføjet", "ændret rækkefølge", "rækkefølge ændret", "stop fjernet", "fjernet stop",
            "ændret rute", "rute ændret", "stop omrokeret", "omrokeret stop", "ekstra leverance", "leverance tilføjet", "ændring",
            "ekstra stop", "ekstra leverance", "ruteændring", "omrokering",
            "changed route", "route changed", "extra stop", "stop added", "stop removed", "removed stop", "stop rearranged",
            "rearranged stop", "additional delivery", "delivery added", "change", "extra stop", "additional delivery", "route change", "rearrangement",
            # Modtager ikke til stede / Receiver Not Present
            "ingen svarer", "svarer ingen", "modtager ikke hjemme", "ikke hjemme modtager", "kunden ikke hjemme", "ikke hjemme kunde",
            "kunden tager ikke telefon", "tager ikke telefon kunde", "kunde ikke kontaktbar", "ikke kontaktbar kunde", "modtager",
            "ikke hjemme", "ingen svar", "ingen kontakt", "ikke kontaktbar",
            "receiver not present", "not present receiver", "no answer", "answer not received", "not home", "home not",
            "unanswered call", "call unanswered", "customer not reachable", "not reachable customer", "receiver", "not home", "no answer", "no contact", "unreachable",
            # Forkert adresse / Wrong Address
            "forkert vejnavn", "vejnavn forkert", "forkert husnummer", "husnummer forkert", "forkert postnummer", "postnummer forkert",
            "kunne ikke finde adressen", "adressen kunne ikke findes", "ikke på adressen", "adressen ikke fundet", "adressen findes ikke",
            "forkert adresse", "forkert placering", "ukendt adresse", "fejl i adresse", "adresseproblem",
            "wrong address", "address wrong", "wrong street", "street wrong", "wrong house number", "house number wrong",
            "wrong postal code", "postal code wrong", "could not find address", "address not found", "not at address",
            "location not found", "location mismatch", "mismatch location", "wrong address", "unknown location", "address error",
            "location mismatch", "address issue",
            # Ingen adgang til leveringssted / No Access to Delivery Location
            "porten lukket", "lukket port", "ingen adgang", "adgang nægtet", "nægtet adgang", "adgang kræver nøgle", "nøgle kræves for adgang",
            "adgang via alarm", "alarmstyret adgang", "kunne ikke komme ind", "kom ikke ind", "adgang", "ingen adgang",
            "adgang nægtet", "låst", "forhindret adgang", "port lukket",
            "no access", "access denied", "denied access", "locked gate", "gate locked", "restricted area",
            "entrance blocked", "blocked entrance", "could not enter", "entry failed", "no access", "locked", "denied",
            "blocked", "restricted", "access issue",
            # Udfordringer med kunden / Customer Issues
            "kunden sur", "sur kunde", "kunden klager", "klager kunde", "afsender afviser", "afviser afsender", "modtager uenig",
            "uening modtager", "problem med kunde", "kunde problem", "utilfreds kunde", "klage", "afvisning", "uenighed",
            "problem med kunde",
            "receiver refused", "refused receiver", "sender issue", "issue with sender", "customer complaint", "complaint from customer",
            "customer upset", "upset customer", "problem with customer", "complaint", "refusal", "issue", "disagreement", "unhappy customer",
            # Besværlig leveringsadresse / Difficult Delivery Location
            "hospital", "skole", "center", "gågade", "etageejendom", "manglende parkering", "parkering mangler", "svært at finde",
            "vanskelig at finde", "besværlig levering", "tricky adresse", "svær placering", "ingen parkering", "trafikeret område",
            "tæt trafik",
            "busy location", "location busy", "pedestrian zone", "no parking", "parking unavailable", "difficult to find",
            "hard to find", "delivery challenge", "hospital", "school", "mall", "apartment building", "no parking",
            "complicated delivery", "difficult address", "busy area",
            # Ekstra tid / Extra time nøgleord
            "ekstra tid", "ekstratid", "extra time", "extratime"
        ]
        # Sørg for case-insensitiv søgning
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

def solar_weekly_report():
    st.header("Solar Weekly Report")
    st.write("Denne fane er under udvikling.")

def solar_co2_report():
    st.header("Solar CO2 Report")
    st.write("Denne fane er under udvikling.")

def revenue_analyser():
    st.header("Revenue analyser")
    st.write("Denne fane er under udvikling.")

# Navigation med session_state
if "page" not in st.session_state:
    st.session_state.page = "Home"

if st.session_state.page == "Home":
    # Forside med titel og en vandret menu
    st.title("Customer Success Automation site")
    st.markdown("### Vælg et menupunkt:")
    # Brug kolonner for at centrere menu-knapperne
    cols = st.columns([1,2,2,2,2,1])
    with cols[1]:
        if st.button("Controlling Report Analyzer"):
            st.session_state.page = "Controlling Report Analyzer"
            st.experimental_rerun()
    with cols[2]:
        if st.button("Solar Weekly Report"):
            st.session_state.page = "Solar Weekly Report"
            st.experimental_rerun()
    with cols[3]:
        if st.button("Solar CO2 Report"):
            st.session_state.page = "Solar CO2 Report"
            st.experimental_rerun()
    with cols[4]:
        if st.button("Revenue analyser"):
            st.session_state.page = "Revenue analyser"
            st.experimental_rerun()
else:
    # Tilbage-knap
    if st.button("Tilbage til forside"):
        st.session_state.page = "Home"
        st.experimental_rerun()
    
    if st.session_state.page == "Controlling Report Analyzer":
        controlling_report_analyzer()
    elif st.session_state.page == "Solar Weekly Report":
        solar_weekly_report()
    elif st.session_state.page == "Solar CO2 Report":
        solar_co2_report()
    elif st.session_state.page == "Revenue analyser":
        revenue_analyser()
