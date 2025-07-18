import io
import re

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- Hjælpefunktioner -------------------------------------------------------

@st.cache_data
def load_revenue_df(uploaded_file) -> pd.DataFrame:
    """Loader den uploadede Excel-rapport med header i række 5 og strip’er alle kolonnenavne."""
    uploaded_file.seek(0)
    df = pd.read_excel(uploaded_file, engine="openpyxl", header=4)
    df.columns = df.columns.str.strip()
    return df

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

# --- Streamlit-faneblad -----------------------------------------------------

def revenue_tab():
    st.header("Onboarding-tracker for nye 2025-kunder")

    # Trin 1: Upload
    uploaded = st.file_uploader("1) Upload din Revenue-rapport (.xlsx)", type=["xlsx"])
    if not uploaded:
        return
    df = load_revenue_df(uploaded)

    # Trin 2: Find YTD 2025-kolonnen
    total_candidates = [
        c for c in df.columns
        if re.fullmatch(r"(?i)(2025|YTD\s*2025)", c)
    ]
    if not total_candidates:
        st.error("Kolonnen for YTD 2025 mangler: kig efter header '2025' eller 'YTD 2025'")
        return
    total_col = total_candidates[0]

    # Trin 3: Find 2016–2024-årskolonner
    prev_years = [str(y) for y in range(2016, 2025)]
    prev_cols = [c for c in prev_years if c in df.columns]

    # Trin 4: Filtrer nye kunder
    mask_prev_zero = (df[prev_cols] == 0).all(axis=1) if prev_cols else pd.Series(True, index=df.index)
    mask_new       = pd.to_numeric(df[total_col], errors="coerce").fillna(0) > 0
    df_new = df[mask_prev_zero & mask_new].copy()

    # Trin 4b: Frasortér <1.000 kr.
    df_new = df_new[pd.to_numeric(df_new[total_col], errors="coerce") > 1000]

    st.subheader(f"Fundet {len(df_new)} nye kunder med ≥1.000 kr. i 2025-omsætning")
    if df_new.empty:
        st.info("Ingen nye kunder efter kriteriet.")
        return

    # Kort preview
    preview_cols = [c for c in ["Name", "ID", total_col] if c in df_new.columns]
    st.dataframe(df_new[preview_cols])

    # Trin 5: Formular til estimeret omsætning
    st.subheader("2) Angiv estimeret årlig omsætning")
    with st.form("estimation_form"):
        potentials: dict[int, float] = {}
        for idx, row in df_new.iterrows():
            profile = row.get("Name", "")
            cid     = row.get("ID", "")
            label   = f"{profile} ({cid})"
            potentials[idx] = st.number_input(
                label,
                min_value=0.0,
                value=0.0,
                step=1_000.0,
                format="%.2f",
                key=f"est_{idx}"
            )
        do_analyze = st.form_submit_button("Analyser")

    if not do_analyze:
        return

    # Trin 6: Beregn succes‐flag
    df_new["EstPotential"]   = df_new.index.to_series().map(potentials)
    df_new["OnboardSuccess"] = pd.to_numeric(df_new[total_col], errors="coerce") >= 0.1 * df_new["EstPotential"]

    # Trin 7: KPI‐metrics
    total   = len(df_new)
    success = int(df_new["OnboardSuccess"].sum())
    fail    = total - success

    c1, c2, c3 = st.columns(3)
    c1.metric("Nye kunder 2025",              total)
    c2.metric("Succesfuld onboarding (≥10%)", success)
    c3.metric("Under 10% omsætning",          fail)

    # Trin 8: Produkt‐fordeling
    if "Product" in df_new.columns:
        st.subheader("Produkt-fordeling")
        counts = df_new["Product"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

    # Trin 9: Slutrapport – kun ønskede kolonner
    out_cols = ["Name", "ID", "Category", "Sales", "SDM", "Product"]
    out_cols = [c for c in out_cols if c in df_new.columns]

    st.subheader("Detaljer for nye kunder")
    st.dataframe(df_new[out_cols])

    # Trin 10: Download
    download_df(
        df_new[out_cols],
        label="Download onboarding-rapport for nye 2025-kunder",
        file_name="new_customers_onboarding_2025.xlsx"
    )

if __name__ == "__main__":
    st.set_page_config(page_title="CS Automation – Revenue")
    revenue_tab()
