import io
from datetime import date, timedelta

import pandas as pd
import streamlit as st

# --- Hjælpefunktioner -------------------------------------------------------

def download_df(df: pd.DataFrame, label: str, file_name: str) -> None:
    """Download en DataFrame som Excel-fil via Streamlit."""
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="xlsxwriter")
    st.download_button(
        label=label,
        data=buf.getvalue(),
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

def filter_by_realized_time(df: pd.DataFrame) -> pd.DataFrame:
    """
    Frasortér alle ruter med realiseret tid (ActDuration) under:
      - 180 minutter (3 timer) for alle kunder
      - 150 minutter (2,5 time) for 'Brød Cooperativet'
    """

    duration_col = "ActDuration"

    if duration_col not in df.columns:
        st.error(
            f"Kolonnen '{duration_col}' blev ikke fundet i data. "
            "Tjek at du har uploadet en DurationControlling-rapport."
        )
        return df

    out = df.copy()
    out[duration_col] = pd.to_numeric(out[duration_col], errors="coerce")

    # Sikre CustomerName som str
    cust_name = out["CustomerName"].fillna("").astype(str)

    # Mask for Brød Cooperativet
    is_brod = cust_name == "Brød Cooperativet"

    # Krav:
    brod_ok = is_brod & (out[duration_col] >= 150)
    other_ok = ~is_brod & (out[duration_col] >= 180)

    return out[brod_ok | other_ok].copy()

# --- Analysefunktion --------------------------------------------------------

def analyze_quicknotes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtrér kun ruter hvor QuickNotes indeholder én af:
      - "Solutions - Delay - Extra time spent (S)"
      - "Solutions - Customer deviation"
    """
    patterns = [
        "Solutions - Delay - Extra time spent (S)",
        "Solutions - Customer deviation",
    ]

    out = df.copy()
    series = out["QuickNotes"].fillna("").astype(str).str.lower()

    out["QuickNotesMatch"] = series.apply(
        lambda txt: any(p.lower() in txt for p in patterns)
    )

    return out[out["QuickNotesMatch"]][
        ["SessionId", "Date", "CustomerId", "CustomerName", "ActDuration", "QuickNotes"]
    ]

# --- Streamlit-faneblad -----------------------------------------------------

def controlling_tab():
    st.header("Controlling-analyse – QuickNotes (Solutions)")

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

    # --- ROBUST FRASORTERING AF IKEA-KUNDER ----------------------------------
    exclude_customers_raw = ["IKEA Norway", "IKEA BE", "IKEA NL"]

    # Normaliser CustomerName → fjern whitespace & gør lowercase
    df["CustomerName_clean"] = (
        df["CustomerName"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    exclude_customers = [name.lower() for name in exclude_customers_raw]

    df = df[~df["CustomerName_clean"].isin(exclude_customers)].copy()

    # Fjern hjælpekolonnen
    df.drop(columns=["CustomerName_clean"], inplace=True)

    # -------------------------------------------------------------------------

    # Frasortér ruter ud fra realiseret tid (ActDuration)
    df = filter_by_realized_time(df)

    if df.empty:
        st.warning("Ingen ruter opfylder kravet til minimum realiseret tid efter filtrering.")
        return

    # Fjern rækker uden QuickNotes-tekst
    quick_str = df["QuickNotes"].fillna("").astype(str)
    df = df[quick_str.str.strip() != ""].copy()

    if df.empty:
        st.warning("Ingen ruter med QuickNotes-tekst tilbage efter filtrering.")
        return

    # --- QuickNotes-analyse --------------------------------------------------
    st.subheader("QuickNotes-analyse – Solutions deviations")
    df_q = analyze_quicknotes(df)

    if df_q.empty:
        st.write("Ingen ruter med de valgte QuickNotes efter alle filtreringer.")
    else:
        st.write(f"Antal ruter efter tids- og QuickNotes-filtrering: **{len(df_q)}**")

        # Vis pr. kunde
        for cust, grp in df_q.groupby("CustomerName"):
            with st.expander(cust):
                st.dataframe(grp)

        # Download-knap
        download_df(
            df_q,
            "Download QuickNotes-analyse",
            "quicknotes_solutions_analyse.xlsx",
        )

if __name__ == "__main__":
    st.set_page_config(page_title="CS Automation – Controlling")
    controlling_tab()
