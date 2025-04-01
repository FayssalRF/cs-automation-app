import streamlit as st
import pandas as pd
import io

st.title("Controlling Report Analyse")

st.write(
    """
    Upload din Excel-fil med controlling report. Filen skal indeholde følgende kolonner:
    - SessionId
    - Date
    - CustomerId
    - CustomerName
    - EstDuration
    - ActDuration
    - DurationDifference
    - SupportNote

    Applikationen analyserer "SupportNote" for nøgleord, der indikerer ekstra tid.
    """
)

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
            # Definer alle nøgleord for at identificere ekstra tid (Dansk og Engelsk)
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
                "complicated delivery", "difficult address", "busy area"
            ]
            # Gør alle nøgleord små bogstaver for at sikre case-insensitiv søgning
            all_keywords = [kw.lower() for kw in all_keywords]

            # Funktion til at analysere supportnote
            def analyse_supportnote(note):
                if pd.isna(note):
                    return "Nej", ""
                note_lower = str(note).lower()
                # Find alle nøgleord, der optræder i supportnoten
                matched = [kw for kw in all_keywords if kw in note_lower]
                if matched:
                    # Fjern eventuelle dubletter
                    matched = list(set(matched))
                    return "Ja", ", ".join(matched)
                else:
                    return "Nej", ""

            # Anvend analysen på hver række i dataframen
            df["Keywords"] = df["SupportNote"].apply(lambda note: analyse_supportnote(note)[0])
            df["MatchingKeyword"] = df["SupportNote"].apply(lambda note: analyse_supportnote(note)[1])

            # Udvælg de ønskede kolonner til output
            output_cols = [
                "SessionId", "Date", "CustomerId", "CustomerName", 
                "EstDuration", "ActDuration", "DurationDifference", "SupportNote", 
                "Keywords", "MatchingKeyword"
            ]

            st.write("Resultater:")
            st.dataframe(df[output_cols])

            # Konverter dataframen til en Excel-fil i hukommelsen
            towrite = io.BytesIO()
            with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Analyseret')
                writer.save()
            towrite.seek(0)

            st.download_button(
                label="Download analyseret Excel-fil",
                data=towrite,
                file_name="analyseret_controlling_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("Upload venligst en Excel-fil for at starte analysen.")
