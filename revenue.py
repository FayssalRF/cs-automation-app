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

    # --- Trin 1: Upload og identifikation af nye kunder ---------------------
    uploaded = st.file_uploader("1. Upload din Revenue-rapport (.xlsx)", type=["xlsx"])
    if not uploaded:
        return

    df = load_revenue_df(uploaded)

    # Find alle 2025-kolonner
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    candidate_cols = [f"{m}-25" for m in months] + ["2025"]
    cols_2025 = [c for c in candidate_cols if c in df.columns]

    # Summer kun numeriske kolonner
    df["Realized2025"] = df[cols_2025].sum(axis=1, numeric_only=True)
    # Tving float for at undgå object-dtype
    df["Realized2025"] = pd.to_numeric(df["Realized2025"], errors="coerce").fillna(0.0)

    # Filtrer kunder der har omsætning (>0) i 2025
    df_new = df[df["Realized2025"] > 0].copy()

    st.subheader(f"Fundet {len(df_new)} nye kunder med omsætning i 2025")
    if df_new.empty:
        st.info("Ingen nye kunder med omsætning i 2025 fundet.")
        return

    # Vis hurtigt nøgle-kolonner
    overview_cols = [
        "Company Reference", "Company Name", "Name", "ID",
        "CompanyName", "cvr", "YearCreated", "Status", "Product", "Realized2025"
    ]
    overview_cols = [c for c in overview_cols if c in df_new.columns]
    st.dataframe(df_new[overview_cols])

    # --- Trin 2: Estimeret årlig omsætning per kunde -----------------------
    st.subheader("2. Estimeret årlig omsætning")
    st.write("Angiv forventet årlig omsætning for hver ny kunde.")

    with st.form("estimation_form"):
        potentials: dict = {}
        for idx, row in df_new.iterrows():
            name = row.get("Company Name") or row.get("CompanyName", "")
            cust_id = row.get("ID", "")
            label = f"{name} ({cust_id})"
            potentials[idx] = st.number_input(
                label=label,
                min_value=0.0,
                value=0.0,
                step=1_000.0,
                format="%.2f",
                key=f"est_{idx}"
            )
        analyze = st.form_submit_button("Analyser")

    if not analyze:
        return

    # Put estimater ind i df
    df_new["EstPotential"] = df_new.index.to_series().map(lambda i: potentials.get(i, 0.0))
    df_new["EstPotential"] = pd.to_numeric(df_new["EstPotential"], errors="coerce").fillna(0.0)

    # Beregn onboarding succes
    df_new["OnboardSuccess"] = df_new["Realized2025"] >= 0.1 * df_new["EstPotential"]

    # --- Dashboard ----------------------------------------------------------
    total_new     = len(df_new)
    success_count = int(df_new["OnboardSuccess"].sum())
    fail_count    = total_new - success_count

    c1, c2, c3 = st.columns(3)
    c1.metric("Nye kunder 2025",               total_new)
    c2.metric("Succesfuld onboarding (≥10%)",  success_count)
    c3.metric("Under 10% omsætning",           fail_count)

    # Produkt-fordeling
    if "Product" in df_new.columns:
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
    else:
        st.warning("Kolonnen 'Product' findes ikke; kan ikke vise fordeling.")

    # --- Detaljeret tabel ---------------------------------------------------
    st.subheader("Detaljer for nye kunder")
    detail_cols = [
        "Company Reference", "Company Name", "Name", "ID",
        "CompanyName", "cvr", "YearCreated", "Status", "Product",
        "Realized2025", "EstPotential", "OnboardSuccess"
    ]
    detail_cols = [c for c in detail_cols if c in df_new.columns]
    st.dataframe(df_new[detail_cols])

    # --- Download -----------------------------------------------------------
    download_df(
        df_new[detail_cols],
        label="Download onboarding-rapport for nye 2025-kunder",
        file_name="new_customers_onboarding_2025.xlsx"
    )


if __name__ == "__main__":
    st.set_page_config(page_title="CS Automation – Revenue")
    revenue_tab()
