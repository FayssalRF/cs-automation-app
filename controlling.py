import io
import pandas as pd
import streamlit as st

# --- Hjælpefunktioner -------------------------------------------------------

@st.cache_data
def load_keywords(path="keywords.txt"):
    """Loader liste af keywords fra fil."""
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def find_keywords(text, keywords):
    """Finder alle keywords i en tekst."""
    txt = str(text).lower()
    return [kw for kw in keywords if kw.lower() in txt]

def analyze_supportnote(df: pd.DataFrame) -> pd.DataFrame:
    """Analyserer SupportNote som før."""
    kws = load_keywords()
    out = df.copy()
    out["SupportNoteKeywords"] = out["SupportNote"].apply(lambda x: find_keywords(x, kws))
    out["SupportNoteMatch"]    = out["SupportNoteKeywords"].apply(lambda lst: "Ja" if lst else "Nej")
    return out[[
        "SessionId","Date","CustomerId","CustomerName",
        "SupportNote","SupportNoteMatch","SupportNoteKeywords"
    ]]

def analyze_notes(df: pd.DataFrame) -> pd.DataFrame:
    """Analyserer Notes med samme keyword-logik."""
    kws = load_keywords()
    out = df.copy()
    out["NotesKeywords"] = out["Notes"].apply(lambda x: find_keywords(x, kws))
    out["NotesMatch"]    = out["NotesKeywords"].apply(lambda lst: "Ja" if lst else "Nej")
    return out[[
        "SessionId","Date","CustomerId","CustomerName",
        "Notes","NotesMatch","NotesKeywords"
    ]]

def analyze_quicknotes(df: pd.DataFrame) -> pd.DataFrame:
    """Finder kun de rækker i QuickNotes, der matcher de 3 mønstre."""
    patterns = [
        "Solutions - Delay",
        "Solutions - Customer deviation",
        "Courier - Extra loading time"
    ]
    out = df.copy()
    out["QuickNotesMatch"] = out["QuickNotes"].apply(
        lambda x: any(p.lower() in str(x).lower() for p in patterns)
    )
    return out[out["QuickNotesMatch"]][[
        "SessionId","Date","CustomerId","CustomerName","QuickNotes"
    ]]

# --- Streamlit faneblad -----------------------------------------------------

def controlling_tab():
    st.header("Controlling-analyse")

    # 1) Link til ISO-uge-rapport
    st.markdown("### Download seneste ISO-uge-rapport")
    iso_link = "https://moverdatawarehouse.../latest_iso_week_report.xlsx"
    st.markdown(f"[Hent ISO-rapport her ↗]({iso_link})")

    # 2) Upload bruger-fil
    uploaded = st.file_uploader("Upload din controlling-rapport (.xlsx)", type=["xlsx"])
    if not uploaded:
        return
    df = pd.read_excel(uploaded)

    # 3) Ekskluder IKEA NL
    df = df[df["CustomerName"] != "IKEA NL"]

    # 4) Fjern rækker uden tekst i SupportNote, Notes & QuickNotes
    mask_blank = (
        df["SupportNote"].fillna("").astype(str).str.strip() == "" &
        df["Notes"].fillna("").astype(str).str.strip() == "" &
        df["QuickNotes"].fillna("").astype(str).str.strip() == ""
    )
    df = df[~mask_blank]

    # --- Hovedanalyse --------------------------------------------------------

    st.subheader("1) QuickNotes-analyse")
    df_q = analyze_quicknotes(df)
    if not df_q.empty:
        for cust, grp in df_q.groupby("CustomerName"):
            with st.expander(cust):
                st.dataframe(grp)
    else:
        st.write("Ingen relevante QuickNotes fundet.")

    st.subheader("2) Notes-analyse (hvor QuickNotes er tomme eller uden match)")
    # Tag kun rækker uden QuickNotes-match
    df_no_q = df[~df.index.isin(df_q.index)]
    df_n    = analyze_notes(df_no_q)

    if not df_n.empty:
        for cust, grp in df_n.groupby("CustomerName"):
            with st.expander(cust):
                # Sektion for Matches = Ja
                df_yes = grp[grp["NotesMatch"] == "Ja"]
                if not df_yes.empty:
                    st.markdown("**Matches (Ja)**")
                    st.dataframe(df_yes)
                # Sektion for Matches = Nej
                df_no = grp[grp["NotesMatch"] == "Nej"]
                if not df_no.empty:
                    st.markdown("**No Matches (Nej)**")
                    st.dataframe(df_no)
    else:
        st.write("Ingen Notes-matches fundet.")

    # Download af samlet hovedanalyse
    main_df = pd.concat([df_q, df_n], ignore_index=True)
    buf = io.BytesIO()
    main_df.to_excel(buf, index=False, engine="xlsxwriter")
    st.download_button(
        label="Download Hovedanalyse (QuickNotes + Notes)",
        data=buf.getvalue(),
        file_name="controlling_hovedanalyse.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # --- SupportNote-analyse i separat dropdown -----------------------------

    with st.expander("SupportNote-analyse"):
        df_s = analyze_supportnote(df)
        for cust, grp in df_s.groupby("CustomerName"):
            with st.expander(cust):
                st.dataframe(grp)

        buf2 = io.BytesIO()
        df_s.to_excel(buf2, index=False, engine="xlsxwriter")
        st.download_button(
            label="Download SupportNote-analyse",
            data=buf2.getvalue(),
            file_name="supportnote_analyse.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    st.set_page_config(page_title="CS Automation – Controlling")
    controlling_tab()
