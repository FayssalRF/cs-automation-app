import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def revenue_tab():
    st.header("💸 Revenue analyser")

    uploaded_file = st.file_uploader("Upload revenue-rapport (Excel)", type=["xlsx"])
    if not uploaded_file:
        st.info("Upload en Excel-fil for at starte analysen.")
        return

    # L\u00e6s fil og find relevant ark
    try:
        xls = pd.ExcelFile(uploaded_file)
        df = xls.parse("Revenue", skiprows=4)
    except Exception as e:
        st.error(f"Fejl ved indl\u00e6sning af Excel-fil: {e}")
        return

    # Fjern tomme r\u00e6kker og kun dem med Company Name
    df = df.dropna(subset=["Company Name"])

    # Find kolonner med datoer og behold kun 2023, 2024 og 2025
    date_cols = [col for col in df.columns if isinstance(col, str) and '-' in col and col[-2:] in ['23', '24', '25']]
    df_dates = df[['Company Name', 'Name', 'ID'] + date_cols].copy()

    # Konverter kolonnenavne til datetime-objekter
    df_dates.columns = df_dates.columns[:3].tolist() + pd.to_datetime(df_dates.columns[3:], format='%b-%y').tolist()
    df_dates = df_dates.rename(columns={df_dates.columns[0]: 'Company Name'})

    # Opdel i YTD 2024 og 2025 (første kvartal) og seneste 3 måneder
    now = pd.to_datetime("2025-04-01")
    ytd_2024 = df_dates.loc[:, df_dates.columns[(df_dates.columns >= pd.to_datetime("2024-01-01")) & (df_dates.columns < pd.to_datetime("2024-04-01"))]]
    ytd_2025 = df_dates.loc[:, df_dates.columns[(df_dates.columns >= pd.to_datetime("2025-01-01")) & (df_dates.columns < pd.to_datetime("2025-04-01"))]]
    last_3_months = df_dates.loc[:, df_dates.columns[-3:]]

    # Beregn totaler
    df_dates['YTD 2024'] = ytd_2024.sum(axis=1)
    df_dates['YTD 2025'] = ytd_2025.sum(axis=1)
    df_dates['Last 3 Months'] = last_3_months.sum(axis=1)
    df_dates['Previous 3 Months'] = df_dates.iloc[:, -4:-1].sum(axis=1)

    # Beregn udvikling
    df_dates['3M Growth %'] = ((df_dates['Last 3 Months'] - df_dates['Previous 3 Months']) / df_dates['Previous 3 Months']) * 100
    df_dates['YTD Growth %'] = ((df_dates['YTD 2025'] - df_dates['YTD 2024']) / df_dates['YTD 2024']) * 100

    # Filtrer kunder med >20% stigning i sidste 3 mdr
    df_filtered = df_dates[df_dates['3M Growth %'] > 20].copy()

    st.subheader("\ud83d\udcca Kunder med >20% v\u00e6kst over de seneste 3 m\u00e5neder")
    st.dataframe(df_filtered[['Company Name', 'Name', 'ID', '3M Growth %', 'YTD Growth %']].sort_values('3M Growth %', ascending=False))

    st.subheader(":bar_chart: YTD V\u00e6kst 2025 vs. 2024")
    top_ytd = df_filtered.sort_values('YTD Growth %', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(top_ytd['Company Name'], top_ytd['YTD Growth %'])
    ax.set_xlabel("YTD Growth %")
    ax.set_title("Top 10 kunder - YTD 2025 vs. 2024")
    st.pyplot(fig)

    # Vis samlet statistik
    st.metric("Antal kunder med >20% v\u00e6kst", f"{len(df_filtered)} kunder")
