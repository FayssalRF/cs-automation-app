import re
import io

import pandas as pd
import streamlit as st

# --- Hjælpefunktioner -------------------------------------------------------

@st.cache_data
def load_keywords(path: str = "keywords.txt") -> list[str]:
    """Loader liste af keywords fra fil."""
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def download_df(df: pd.DataFrame, label: str, file_name: str) -> None:
    """Pakker en DataFrame til en Streamlit-download-knap."""
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="xlsxwriter")
    st.download_button(
        label=label,
        data=buf.getvalue(),
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

def analyze_supportnote(df: pd.DataFrame, keywords: list[str]) -> pd.DataFrame:
    """Analyserer SupportNote med keyword-match."""
    pattern = "|".join(re.escape(kw) for kw in keywords)
    out = df.copy()
    out["SupportNoteMatch"]    = out["SupportNote"].fillna("").str.contains(pattern, case=False, regex=True)
    out["SupportNoteKeywords"] = out["SupportNote"].apply(
        lambda txt: [kw for kw in keywords if kw.lower() in str(txt).lower()]
    )
    return out[
        [
            "SessionId",
            "Date",
            "CustomerId",
            "CustomerName",
            "SupportNote",
            "SupportNoteMatch",
            "SupportNoteKeywords",
        ]
    ]

# --- Streamlit-faneblad -----------------------------------------------------

def controlling_tab():
    st.header("Controlling-analyse")

# Auto-beregn sidste ISO-uge
    today = date.today()
    last_week_date = today - timedelta(days=7)
    yearweek = last_week_date.strftime("%Y") + f"{last_week_date.isocalendar()[1]:02d}"
    link = (
        "https://moverdatawarehouse.azurewebsites.net/download/DurationControlling"
        f"?apikey=2d633b&Userid=74859&Yearweek={yearweek}"
    )
    st.markdown(f"[Download Controlling report for sidste uge (ISO {last_week_date.isocalendar()[1]:02d})]({link})")

    # Upload
    uploaded = st.file_uploader("Upload din controlling-rapport (.xlsx)", type=["xlsx"])
    if not uploaded:
        return

    df = pd.read_excel(uploaded)
    df = df[df["CustomerName"] != "IKEA NL"]  # ekskluder IKEA NL

    # Fjern rækker uden nogen noter eller QuickNotes
    blank_support = df["SupportNote"].fillna("").str.strip() == ""
    blank_notes   = df["Notes"].fillna("").str.strip() == ""
    blank_quick   = df["QuickNotes"].fillna("").str.strip() == ""
    mask_blank    = blank_support & blank_notes & blank_quick
    df = df[~mask_blank]

    # QuickNotes-analyse (vektoriseret)
    PAT_QN = r"(Solutions - Delay|Solutions - Customer deviation|Courier - Extra loading time)"
    df["QuickNotesMatch"] = df["QuickNotes"].fillna("").str.contains(PAT_QN, case=False, regex=True)
    df_q = df[df["QuickNotesMatch"]].copy()

    # Notes-analyse for de rækker uden QuickNotes-match
    df_no_q = df[~df.index.isin(df_q.index)].copy()
    keywords = load_keywords()
    PAT_NOTES = "|".join(re.escape(kw) for kw in keywords)
    df_no_q["NotesMatch"] = df_no_q["Notes"].fillna("").str.contains(PAT_NOTES, case=False, regex=True)

    # KPI-metrics
    total_rows = len(df)
    qn_count   = df_q.shape[0]
    notes_yes  = int(df_no_q["NotesMatch"].sum())
    c1, c2, c3 = st.columns(3)
    c1.metric("Total rækker",           f"{total_rows}")
    c2.metric("QuickNotes-matches",     f"{qn_count}")
    c3.metric("Notes-matches (Ja)",     f"{notes_yes}")

    # Tabs til detalje-analyse og SupportNote-analyse
    tab1, tab2 = st.tabs(["🔍 QuickNotes/Note - analyse", "📝 SupportNote - analyse"])

    # --- Detail-analyse ------------------------------------------------------
    with tab1:
        st.subheader("1) QuickNotes-analyse")
        if not df_q.empty:
            for cust, grp in df_q.groupby("CustomerName"):
                with st.expander(cust):
                    st.dataframe(grp[["SessionId", "Date", "CustomerId", "CustomerName", "QuickNotes"]])
        else:
            st.write("Ingen relevante QuickNotes fundet.")

        st.subheader("2) Notes-analyse")
        if not df_no_q.empty:
            for cust, grp in df_no_q.groupby("CustomerName"):
                with st.expander(cust):
                    df_yes = grp[grp["NotesMatch"]]
                    df_no  = grp[~grp["NotesMatch"]]
                    if not df_yes.empty:
                        st.markdown("**Matches (Ja)**")
                        st.dataframe(df_yes[["SessionId", "Date", "CustomerId", "CustomerName", "Notes", "NotesMatch"]])
                    if not df_no.empty:
                        st.markdown("**No Matches (Nej)**")
                        st.dataframe(df_no[["SessionId", "Date", "CustomerId", "CustomerName", "Notes", "NotesMatch"]])
        else:
            st.write("Ingen Notes-matches fundet.")

        # Download hovedanalyse
        main_df = pd.concat(
            [
                df_q[["SessionId", "Date", "CustomerId", "CustomerName", "QuickNotes"]],
                df_no_q[["SessionId", "Date", "CustomerId", "CustomerName", "Notes", "NotesMatch"]],
            ],
            ignore_index=True,
        )
        download_df(main_df, "Download Hovedanalyse (QuickNotes + Notes)", "controlling_hovedanalyse.xlsx")

    # --- SupportNote-analyse --------------------------------------------------
    with tab2:
        st.subheader("SupportNote-analyse")
        df_s = analyze_supportnote(df, keywords)
        if not df_s.empty:
            for cust, grp in df_s.groupby("CustomerName"):
                with st.expander(cust):
                    st.dataframe(grp)
        else:
            st.write("Ingen SupportNote-matches fundet.")

        download_df(df_s, "Download SupportNote-analyse", "supportnote_analyse.xlsx")


if __name__ == "__main__":
    st.set_page_config(page_title="CS Automation – Controlling")
    controlling_tab()
