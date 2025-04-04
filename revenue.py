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
        (df_dates['ÅTD 2024'] != 0) &
        (df_dates['ÅTD 2025'] != 0) &
        (df_dates['ÅTD 2024'] > 50000) &
        (df_dates['ÅTD 2025'] > 50000)
    ].copy()

    # Beregn procentvis ændring
    df_filtered['YTD Change %'] = ((df_filtered['ÅTD 2025'] - df_filtered['ÅTD 2024']) / df_filtered['ÅTD 2024']) * 100

    # Opret et display-DataFrame med formatering
    def format_currency(x):
        return "kr. " + f"{x:,.0f}".replace(",", ".")
    df_display = df_filtered[['Company Name', 'ÅTD 2024', 'ÅTD 2025', 'YTD Change %']].copy()
    df_display['ÅTD 2024'] = df_display['ÅTD 2024'].apply(format_currency)
    df_display['ÅTD 2025'] = df_display['ÅTD 2025'].apply(format_currency)
    df_display['YTD Change %'] = df_display['YTD Change %'].apply(lambda x: f"{x:.2f}%")
    st.subheader("ÅTD Revenue Sammenligning")
    st.dataframe(df_display)

    # For plottet bruger vi alle virksomheder med positive og negative ændringer
    # Arbejd med den numeriske version af YTD Change
    df_filtered['YTD Change Numeric'] = df_filtered['YTD Change %']
    positive_df = df_filtered[df_filtered['YTD Change Numeric'] >= 0].sort_values('YTD Change Numeric', ascending=False)
    negative_df = df_filtered[df_filtered['YTD Change Numeric'] < 0].sort_values('YTD Change Numeric', ascending=True)

    plt.style.use('ggplot')

    col1, col2 = st.columns(2)

    # Plot for positive ændringer
    with col1:
        st.subheader("Virksomheder med positive YTD Change %")
        # Dynamisk figurstørrelse alt efter antal rækker
        fig_height = max(4, len(positive_df) * 0.4)
        fig_pos, ax_pos = plt.subplots(figsize=(8, fig_height))
        bars_pos = ax_pos.barh(positive_df['Company Name'], positive_df['YTD Change Numeric'], color='#4CAF50')
        ax_pos.set_xlabel("YTD Change %", fontsize=11)
        ax_pos.set_title("Positive ændringer", fontsize=13, pad=10)
        ax_pos.tick_params(axis='y', labelsize=9, pad=5)
        ax_pos.grid(True, axis='x', linestyle='--', alpha=0.7)
        # Tilføj værdietiketter ved enden af stolperne
        for bar in bars_pos:
            width = bar.get_width()
            ax_pos.text(width + 1, bar.get_y() + bar.get_height()/2, f"{width:.2f}%", va='center', fontsize=9)
        fig_pos.tight_layout()
        st.pyplot(fig_pos, use_container_width=True)

    # Plot for negative ændringer
    with col2:
        st.subheader("Virksomheder med negative YTD Change %")
        fig_height = max(4, len(negative_df) * 0.4)
        fig_neg, ax_neg = plt.subplots(figsize=(8, fig_height))
        bars_neg = ax_neg.barh(negative_df['Company Name'], negative_df['YTD Change Numeric'], color='#F44336')
        ax_neg.set_xlabel("YTD Change %", fontsize=11)
        ax_neg.set_title("Negative ændringer", fontsize=13, pad=10)
        ax_neg.tick_params(axis='y', labelsize=9, pad=5)
        ax_neg.grid(True, axis='x', linestyle='--', alpha=0.7)
        for bar in bars_neg:
            width = bar.get_width()
            # Placér værdietiketten til venstre for stolpen
            ax_neg.text(width - 1, bar.get_y() + bar.get_height()/2, f"{width:.2f}%", va='center', fontsize=9, ha='right')
        fig_neg.tight_layout()
        st.pyplot(fig_neg, use_container_width=True)

    st.metric("Antal virksomheder analyseret", f"{len(df_filtered)}")
