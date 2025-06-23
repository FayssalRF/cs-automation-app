import io

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from openpyxl import load_workbook

# --- Hjælpefunktioner -------------------------------------------------------

@st.cache_data
def load_revenue_df(uploaded_file) -> pd.DataFrame:
    """Loader den uploadede Excel-rapport, og unhider alle skjulte kolonner."""
    # Sørg for at læse fra starten
    uploaded_file.seek(0)
    wb = load_workbook(uploaded_file, data_only=True)

    # Unhide alle kolonner i alle ark
    for ws in wb.worksheets:
        for col_dim in ws.column_dimensions.values():
            col_dim.hidden = False

    # Gem det midlertidigt og læs med pandas
    tmp = io.BytesIO()
    wb.save(tmp)
    tmp.seek(0)
    df = pd.read_excel(tmp, engine="openpyxl")
    return df

def download_df(df: pd.DataFrame, label: str, file_name: str) -> None:
    """Pak en DataFrame til en Streamlit-download-knap."""
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
    st.header("Onboarding-tracker: Nye 2025-kunder")

    # Trin 1: Upload og identificer nye kunder
    uploaded = st.file_uploader("1) Upload din Revenue-rapport (.xlsx)", type=["xlsx"])
    if not uploaded:
        return

    df = load_revenue_df(uploaded)

    # Find årskolonner 2016–2024 og total-2025
    year_cols = [str(y) for y in range(2016, 2025) if str(y) in df.columns]
    total_2025 = "2025"
    if total_2025 not in df.columns:
        st.error(f"Kolonnen '{total_2025}' (2025-total) mangler i din fil.")
        return

    # Filter: 2016–2024 SKAL være 0, 2025 > 0
    mask_zero_years     = (df[year_cols] == 0).all(axis=1)
    mask_positive_2025  = pd.to_numeric(df[total_2025], errors="coerce").fillna(0) > 0
    df_new = df[mask_zero_years & mask_positive_2025].copy()

    st.subheader(f"Fundet {len(df_new)} nye kunder (kun omsætning i 2025)")
    if df_new.empty:
        st.info("Ingen nye kunder efter kriteriet.")
        return

    # Kort preview
    preview = ["Company Name", "Name", "ID", total_2025]
    preview = [c for c in preview if c in df_new.columns]
    st.dataframe(df_new[preview])

    # Trin 2: Angiv estimeret årlig omsætning
    st.subheader("2) Angiv estimeret årlig omsætning")
    with st.form("estimation_form"):
        potentials = {}
        for idx, row in df_new.iterrows():
            label = f"{row.get('Company Name','')} ({row.get('ID','')})"
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

    # Beregn onboard-success
    df_new["EstPotential"]   = df_new.index.to_series().map(potentials)
    df_new["OnboardSuccess"] = df_new[total_2025] >= 0.1 * df_new["EstPotential"]

    # Dashboard-metrics
    total   = len(df_new)
    success = int(df_new["OnboardSuccess"].sum())
    fail    = total - success

    c1, c2, c3 = st.columns(3)
    c1.metric("Nye kunder 2025",              total)
    c2.metric("Succesfuld onboarding (≥10%)", success)
    c3.metric("Under 10% omsætning",          fail)

    # Produkt-fordeling
    if "Product" in df_new.columns:
        st.subheader("Produkt-fordeling")
        counts = df_new["Product"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

    # Endelig rapport: kun de ønskede kolonner
    out_cols = ["Company Name", "Name", "ID", "Category", "Sales", "SDM", "Product"]
    out_cols = [c for c in out_cols if c in df_new.columns]

    st.subheader("Detaljer for nye kunder")
    st.dataframe(df_new[out_cols])

    download_df(
        df_new[out_cols],
        label="Download onboarding-rapport for nye 2025-kunder",
        file_name="new_customers_onboarding_2025.xlsx"
    )

if __name__ == "__main__":
    st.set_page_config(page_title="CS Automation – Revenue")
    revenue_tab()
