import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def revenue_tab():
    st.header("💸 Revenue analyser")

    uploaded_file = st.file_uploader("Upload revenue-rapport (Excel)", type=["xlsx"])
    if not uploaded_file:
        st.info("Upload en Excel-fil for at starte analysen.")
        return

    # Læs fil og find relevant ark
    try:
        xls = pd.ExcelFile(uploaded_file)
        df = xls.parse("Revenue", skiprows=4)
    except Exception as e:
        st.error(f"Fejl ved indlæsning af Excel-fil: {e}")
        return

    # Fjern tomme rækker og kolonner
    df = df.dropna(how="all")
    df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]

    # Find kolonner med datoer (omsætning) og summer dem som 'Realized Revenue'
    revenue_cols = [col for col in df.columns if isinstance(col, str) and '-' in col]
    if not revenue_cols:
        st.warning("Ingen kolonner med datoformat fundet i regnearket.")
        return

    df['Realized Revenue'] = df[revenue_cols].sum(axis=1)

    # Forventet årlig omsætning estimeres ud fra månedsgennemsnit x 12
    df['Expected Revenue'] = df['Realized Revenue'] / len(revenue_cols) * 12
    df['Performance %'] = df['Realized Revenue'] / df['Expected Revenue'] * 100
    df['Performance Tag'] = pd.cut(
        df['Performance %'],
        bins=[-float('inf'), 50, 80, 100, float('inf')],
        labels=['At risk', 'Lagging', 'On track', 'Overperforming']
    )

    # Vis tabel
    st.subheader("📊 Oversigt over kunder")
    st.dataframe(df[['Name', 'ID', 'Realized Revenue', 'Expected Revenue', 'Performance %', 'Performance Tag']])

    # Visualisering
    st.subheader(":bar_chart: Visualisering")
    top_customers = df.sort_values('Realized Revenue', ascending=False).head(10)

    fig, ax = plt.subplots()
    ax.bar(top_customers['Name'], top_customers['Realized Revenue'], label='Realized')
    ax.bar(top_customers['Name'], top_customers['Expected Revenue'], alpha=0.5, label='Expected')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel("Revenue")
    plt.title("Top 10 kunder: Realized vs. Expected Revenue")
    plt.legend()
    st.pyplot(fig)

    # Samlede nøgletal
    total_realized = df['Realized Revenue'].sum()
    total_expected = df['Expected Revenue'].sum()
    percent = total_realized / total_expected * 100 if total_expected > 0 else 0

    st.metric("📈 Total Realized Revenue", f"{total_realized:,.0f} DKK")
    st.metric("📉 Forventet Revenue (pro rata)", f"{total_expected:,.0f} DKK")
    st.metric("⚡ Performance", f"{percent:.1f}%")
