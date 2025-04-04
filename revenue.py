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

    # Beregn ÅTD revenue
    df_dates['ÅTD 2024'] = df_dates[cols_2024_common].sum(axis=1)
    df_dates['ÅTD 2025'] = df_dates[cols_2025_common].sum(axis=1)

    # Filtrer virksomheder med revenue > 50.000 kr. i begge år
    df_filtered = df_dates[
        (df_dates['ÅTD 2024'] > 50000) &
        (df_dates['ÅTD 2025'] > 50000)
    ].copy()

    # Beregn procentvis ændring
    df_filtered['YTD Change %'] = ((df_filtered['ÅTD 2025'] - df_filtered['ÅTD 2024']) / df_filtered['ÅTD 2024']) * 100

    # Vis tabel med formatering
    def format_currency(x):
        return "kr. " + f"{x:,.0f}".replace(",", ".")

    df_display = df_filtered[['Company Name', 'ÅTD 2024', 'ÅTD 2025', 'YTD Change %']].copy()
    df_display['ÅTD 2024'] = df_display['ÅTD 2024'].apply(format_currency)
    df_display['ÅTD 2025'] = df_display['ÅTD 2025'].apply(format_currency)
    df_display['YTD Change %'] = df_display['YTD Change %'].apply(lambda x: f"{x:.2f}%")

    st.subheader("ÅTD Revenue Sammenligning")
    st.dataframe(df_display)

    # Udtræk top 10 stigninger og top 10 fald
    df_filtered['YTD Change Numeric'] = df_filtered['YTD Change %']
    top_increases = df_filtered.sort_values('YTD Change Numeric', ascending=False).head(10)
    top_decreases = df_filtered.sort_values('YTD Change Numeric', ascending=True).head(10)

    # Vælg en stil
    plt.style.use('ggplot')

    col1, col2 = st.columns(2)

    # --- GRAF: 10 største stigninger ---
    with col1:
        st.subheader("10 største stigninger (YTD Change %)")
        # Dynamisk figurhøjde afhængigt af antal rækker
        fig_height = max(4, len(top_increases) * 0.5)
        fig_inc, ax_inc = plt.subplots(figsize=(6, fig_height))

        bars_inc = ax_inc.barh(top_increases['Company Name'], top_increases['YTD Change Numeric'], color='#4CAF50')
        ax_inc.set_xlabel("YTD Change %", fontsize=11)
        ax_inc.set_title("Stigninger", fontsize=13, pad=10)
        ax_inc.tick_params(axis='y', labelsize=9, pad=5)
        ax_inc.grid(True, axis='x', linestyle='--', alpha=0.7)

        for bar in bars_inc:
            width = bar.get_width()
            ax_inc.text(width + 1, bar.get_y() + bar.get_height()/2,
                        f"{width:.2f}%", va='center', fontsize=9)

        fig_inc.tight_layout()
        st.pyplot(fig_inc, use_container_width=True)

    # --- GRAF: 10 største fald ---
    with col2:
        st.subheader("10 største fald (YTD Change %)")
        fig_height = max(4, len(top_decreases) * 0.5)
        fig_dec, ax_dec = plt.subplots(figsize=(6, fig_height))

        bars_dec = ax_dec.barh(top_decreases['Company Name'], top_decreases['YTD Change Numeric'], color='#F44336')
        ax_dec.set_xlabel("YTD Change %", fontsize=11)
        ax_dec.set_title("Fald", fontsize=13, pad=10)
        ax_dec.tick_params(axis='y', labelsize=9, pad=5)
        ax_dec.grid(True, axis='x', linestyle='--', alpha=0.7)

        # Sørg for at negative værdier ikke klippes
        min_val = top_decreases['YTD Change Numeric'].min()
        max_val = top_decreases['YTD Change Numeric'].max()
        ax_dec.set_xlim(min_val - 5, max_val + 5)

        for bar in bars_dec:
            width = bar.get_width()
            # Placér tekst enten til venstre eller højre
            if width < 0:
                ax_dec.text(width - 1, bar.get_y() + bar.get_height()/2,
                            f"{width:.2f}%", va='center', ha='right', fontsize=9)
            else:
                ax_dec.text(width + 1, bar.get_y() + bar.get_height()/2,
                            f"{width:.2f}%", va='center', ha='left', fontsize=9)

        fig_dec.tight_layout()
        st.pyplot(fig_dec, use_container_width=True)

    st.metric("Antal virksomheder analyseret", f"{len(df_filtered)}")
