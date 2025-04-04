import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def revenue_tab():
    st.header("💸 ÅTD Revenue Sammenligning 2025 vs. 2024")

    uploaded_file = st.file_uploader("Upload revenue-rapport (Excel)", type=["xlsx"])
    if not uploaded_file:
        st.info("Upload en Excel-fil for at starte analysen.")
        return

    try:
        xls = pd.ExcelFile(uploaded_file)
        df = xls.parse("Revenue", skiprows=4)
    except Exception as e:
        st.error(f"Fejl ved indlæsning af Excel-fil: {e}")
        return

    # Fjern rækker uden Company Name
    df = df.dropna(subset=["Company Name"])

    # Find dato-kolonner og filtrer for 2023-2025
    date_cols = [col for col in df.columns if isinstance(col, str) and '-' in col and col[-2:] in ['23', '24', '25']]
    df_dates = df[['Company Name', 'Name', 'ID'] + date_cols].copy()

    # Konverter dato-kolonner til datetime-objekter
    df_dates.columns = df_dates.columns[:3].tolist() + pd.to_datetime(df_dates.columns[3:], format='%b-%y').tolist()
    df_dates = df_dates.rename(columns={df_dates.columns[0]: 'Company Name'})

    # Identificér datetime-kolonner og opdel efter år
    datetime_cols = [col for col in df_dates.columns if isinstance(col, pd.Timestamp)]
    cols_2024 = [col for col in datetime_cols if col.year == 2024]
    cols_2025 = [col for col in datetime_cols if col.year == 2025]

    # Find fælles måneder for begge år
    common_months = set(col.month for col in cols_2024) & set(col.month for col in cols_2025)
    cols_2024_common = sorted([col for col in cols_2024 if col.month in common_months])
    cols_2025_common = sorted([col for col in cols_2025 if col.month in common_months])

    # Beregn ÅTD revenue for de fælles måneder
    df_dates['ÅTD 2024'] = df_dates[cols_2024_common].sum(axis=1)
    df_dates['ÅTD 2025'] = df_dates[cols_2025_common].sum(axis=1)

    # Filtrer virksomheder med revenue > 50.000 kr. i begge år
    df_filtered = df_dates[(df_dates['ÅTD 2024'] != 0) & (df_dates['ÅTD 2025'] != 0) &
                           (df_dates['ÅTD 2024'] > 50000) & (df_dates['ÅTD 2025'] > 50000)].copy()

    # Beregn procentvis ændring
    df_filtered['YTD Change %'] = ((df_filtered['ÅTD 2025'] - df_filtered['ÅTD 2024']) / df_filtered['ÅTD 2024']) * 100

    # Formatteringsfunktion for DKK
    def format_currency(x):
        return "kr. " + f"{x:,.0f}".replace(",", ".")

    df_display = df_filtered[['Company Name', 'ÅTD 2024', 'ÅTD 2025', 'YTD Change %']].sort_values('YTD Change %', ascending=False).copy()
    df_display['ÅTD 2024'] = df_display['ÅTD 2024'].apply(format_currency)
    df_display['ÅTD 2025'] = df_display['ÅTD 2025'].apply(format_currency)
    df_display['YTD Change %'] = df_display['YTD Change %'].apply(lambda x: f"{x:.2f}%")

    st.subheader("ÅTD Revenue Sammenligning")
    st.dataframe(df_display)

    # Forbered grafer for top 10 stigninger og top 10 fald
    top_10 = df_filtered.sort_values('YTD Change %', ascending=False).head(10)
    bottom_10 = df_filtered.sort_values('YTD Change %', ascending=True).head(10)

    # Sæt en flot stil
    plt.style.use('ggplot')

    # Placer graferne side om side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 virksomheder - YTD Change % (Stigninger)")
        fig_top, ax_top = plt.subplots(figsize=(4, 3))
        bars_top = ax_top.barh(top_10['Company Name'], top_10['YTD Change %'], color='#4CAF50')
        ax_top.set_xlabel("YTD Change %", fontsize=12, labelpad=10)
        ax_top.set_title("Top 10 Stigninger", fontsize=14, pad=15)
        ax_top.tick_params(axis='y', labelsize=10, pad=50)
        ax_top.grid(True, axis='x', linestyle='--', alpha=0.7)
        # Tilføj værdietiketter på stolperne
        for bar in bars_top:
            width = bar.get_width()
            ax_top.text(width + 0.5, bar.get_y() + bar.get_height()/2, f"{width:.2f}%", va='center', fontsize=10)
        st.pyplot(fig_top, use_container_width=False)

    with col2:
        st.subheader("Top 10 virksomheder - YTD Change % (Fald)")
        fig_bottom, ax_bottom = plt.subplots(figsize=(4, 3))
        bars_bottom = ax_bottom.barh(bottom_10['Company Name'], bottom_10['YTD Change %'], color='#F44336')
        ax_bottom.set_xlabel("YTD Change %", fontsize=12, labelpad=10)
        ax_bottom.set_title("Top 10 Fald", fontsize=14, pad=15)
        ax_bottom.tick_params(axis='y', labelsize=10, pad=50)
        ax_bottom.grid(True, axis='x', linestyle='--', alpha=0.7)
        # Tilføj værdietiketter på stolperne
        for bar in bars_bottom:
            width = bar.get_width()
            ax_bottom.text(width + 0.5, bar.get_y() + bar.get_height()/2, f"{width:.2f}%", va='center', fontsize=10)
        st.pyplot(fig_bottom, use_container_width=False)

    st.metric("Antal virksomheder analyseret", f"{len(df_filtered)}")
