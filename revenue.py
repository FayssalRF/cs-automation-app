import io
import re

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- Hjælpefunktioner -------------------------------------------------------

@st.cache_data
def load_revenue_df(uploaded_file) -> pd.DataFrame:
    """Loader den uploadede Excel-rapport."""
    return pd.read_excel(uploaded_file, engine="openpyxl")

def download_df(df: pd.DataFrame, label: str, file_name: str) -> None:
    """Gør en DataFrame til en Streamlit-download-knap."""
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

    # 1) Upload
    uploaded = st.file_uploader("Upload din Revenue-rapport (.xlsx)", type=["xlsx"])
    if not uploaded:
        return
    df = load_revenue_df(uploaded)

    # 2) Identificér 2025-kolonner og beregn realiseret 2025
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    cols_2025 = [f"{m}-25" for m in months] + ["2025"]
    # Bevar kun de kolonner som findes i filen
    cols_2025 = [c for c in cols_2025 if c in df.columns]
    df["Realized2025"] = df[cols_2025].sum(axis=1)

    # 3) Filter: kun nye kunder med Realized2025 > 0
    df_new = df[df["Realized2025"] > 0].copy()

    # 4) Lad brugeren taste potentiel årlig omsætning
    est_potential = st.number_input(
        "Estimeret årlig omsætning (potentiel) pr. kunde",
        min_value=0.0,
        value=100_000.0,
        step=1_000.0,
        format="%.2f"
    )

    # 5) Beregn onboarding-success (>=10%)
    df_new["OnboardSuccess"] = df_new["Realized2025"] >= 0.1 * est_potential

    # 6) KPI-metrics
    total_new     = len(df_new)
    success_count = int(df_new["OnboardSuccess"].sum())
    fail_count    = total_new - success_count

    c1, c2, c3 = st.columns(3)
    c1.metric("Nye kunder 2025",           total_new)
    c2.metric("Succesfuld onboarding (≥10%)", success_count)
    c3.metric("Under 10% omsætning",       fail_count)

    # 7) Produkt-fordeling i kagediagram
    st.subheader("Produkt-fordeling")
    prod_counts = df_new["Product"].value_counts()
    fig, ax = plt.subplots()
    ax.pie(
        prod_counts.values,
        labels=prod_counts.index,
        autopct="%1.1f%%",
        startangle=90
    )
    ax.axis("equal")
    st.pyplot(fig)

    # 8) Detalje-tabel
    st.subheader("Detaljer for nye kunder")
    display_cols = [
        "Company Reference",
        "Company Name",
        "Name",
        "ID",
        "CompanyName",
        "cvr",
        "YearCreated",
        "Status",
        "Product",
        "Realized2025",
        "OnboardSuccess"
    ]
    # Filtrér kun de kolonner vi vil vise, og undgå KeyError hvis nogen mangler
    display_cols = [c for c in display_cols if c in df_new.columns]
    st.dataframe(df_new[display_cols])

    # 9) Download-knap
    download_df(
        df_new[display_cols],
        label="Download nye kunder (onboarding-rapport)",
        file_name="new_customers_onboarding_2025.xlsx"
    )

# --- Kør som standalone -----------------------------------------------------

if __name__ == "__main__":
    st.set_page_config(page_title="CS Automation – Revenue")
    revenue_tab()
