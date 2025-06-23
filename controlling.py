import io
import re
from datetime import date, timedelta

import pandas as pd
import streamlit as st

# --- Hjælpefunktioner -------------------------------------------------------

@st.cache_data
def load_keywords(path: str = "keywords.txt") -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def download_df(df: pd.DataFrame, label: str, file_name: str) -> None:
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="xlsxwriter")
    st.download_button(
        label=label,
        data=buf.getvalue(),
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# --- Analysefunktioner -----------------------------------------------------

def analyze_quicknotes(df: pd.DataFrame) -> pd.DataFrame:
    patterns = [
        "Solutions - Delay",
        "Solutions - Customer deviation",
        "Courier - Extra loading time"
    ]
    out = df.copy()
    # Tving altid til str før vi søger
    series = out["QuickNotes"].fillna("").astype(str).str.lower()
    out["QuickNotesMatch"] = series.apply(
        lambda txt: any(p.lower() in txt for p in patterns)
    )
    return out[out["QuickNotesMatch"]][
        ["SessionId", "Date", "CustomerId", "CustomerName", "QuickNotes"]
    ]

def analyze_notes(df: pd.DataFrame, keywords: list[str]) -> pd.DataFrame:
    pattern = "|".join(re.escape(kw) for kw in keywords)
    out = df.copy()
    notes_str = out["Notes"].fillna("").astype(str)
    out["NotesMatch"]    = notes_str.str.contains(pattern, case=False, regex=True)
    out["NotesKeywords"] = notes_str.apply(
        lambda txt: [kw for kw in keywords if kw.lower() in txt.lower()]
    )
    return out[
        ["SessionId", "Date", "CustomerId", "CustomerName", "Notes", "NotesMatch", "NotesKeywords"]
    ]

def analyze_supportnote(df: pd.DataFrame, keywords: list[str]) -> pd.DataFrame:
    pattern = "|".join(re.escape(kw) for kw in keywords)
    out = df.copy()
    sup_str = out["SupportNote"].fillna("").astype(str)
    out["SupportNoteMatch"]    = sup_str.str.contains(pattern, case=False, regex=True)
    out["SupportNoteKeywords"] = sup_str.apply(
        lambda txt: [kw for kw in keywords if kw.lower() in txt.lower()]
    )
    return out[
        [
            "SessionId", "Date", "CustomerId", "CustomerName",
            "SupportNote", "SupportNoteMatch", "SupportNoteKeywords"
        ]
    ]

# --- Streamlit-faneblad -----------------------------------------------------

def controlling_tab():
    st.header("Controlling-analyse")

    # Auto-beregn sidste ISO-uge
    today = date.today()
    last_week = today - timedelta(days=7)
    iso_week = last_week.isocalendar()[1]
    yearweek = last_week.strftime("%Y") + f"{iso_week:02d}"
    link = (
        "https://moverdatawarehouse.azurewebsites.net/download/DurationControlling"
        f"?apikey=2d633b&Userid=74859&Yearweek={yearweek}"
    )
    st.markdown(
        f"[Download controlling-rapport for sidste uge (ISO uge {iso_week})]({link})"
    )

    # Upload
    uploaded = st.file_uploader("Upload din controlling-rapport (.xlsx)", type=["xlsx"])
    if not uploaded:
        return
    df = pd.read_excel(uploaded)

    # Ekskluder IKEA NL
    df = df[df["CustomerName"].fillna("") != "IKEA NL"].copy()

    # Fjern rækker uden tekst i alle tre felter
    sup_blank  = df["SupportNote"].fillna("").astype(str).str.strip() == ""
    notes_blank= df["Notes"].fillna("").astype(str).str.strip() == ""
    quick_blank= df["QuickNotes"].fillna("").astype(str).str.strip() == ""
    df = df[~(sup_blank & notes_blank & quick_blank)].copy()

    # Load keywords
    keywords = load_keywords()

    # 1) QuickNotes-analyse
    st.subheader("1) QuickNotes-analyse")
    df_q = analyze_quicknotes(df)
    if not df_q.empty:
        for cust, grp in df_q.groupby("CustomerName"):
            with st.expander(cust):
                st.dataframe(grp)
    else:
        st.write("Ingen relevante QuickNotes fundet.")

    # 2) Notes-analyse
    st.subheader("2) Notes-analyse")
    df_no_q = df.loc[~df.index.isin(df_q.index)]
    df_n    = analyze_notes(df_no_q, keywords)
    if not df_n.empty:
        for cust, grp in df_n.groupby("CustomerName"):
            with st.expander(cust):
                df_yes = grp[grp["NotesMatch"]]
                df_no  = grp[~grp["NotesMatch"]]
                if not df_yes.empty:
                    st.markdown("**Matches (Ja)**")
                    st.dataframe(df_yes)
                if not df_no.empty:
                    st.markdown("**No Matches (Nej)**")
                    st.dataframe(df_no)
    else:
        st.write("Ingen Notes-matches fundet.")

    # Download hovedanalyse
    main_df = pd.concat([df_q, df_n], ignore_index=True)
    download_df(main_df, "Download hovedanalyse (QuickNotes + Notes)", "controlling_hovedanalyse.xlsx")

    # SupportNote-analyse i separat expander
    with st.expander("SupportNote-analyse"):
        df_s = analyze_supportnote(df, keywords)
        for cust, grp in df_s.groupby("CustomerName"):
            with st.expander(cust):
                st.dataframe(grp)
        download_df(df_s, "Download SupportNote-analyse", "supportnote_analyse.xlsx")

if __name__ == "__main__":
    st.set_page_config(page_title="CS Automation – Controlling")
    controlling_tab()
