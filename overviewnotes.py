# overviewnotes.py

import json
import os
from datetime import datetime
import pandas as pd
import streamlit as st

LOG_PATH = "data/controlling_weekly_log.json"


def _ensure_log_dir():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


def read_weekly_log() -> dict:
    _ensure_log_dir()
    if not os.path.exists(LOG_PATH):
        return {}
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        return {}


def write_weekly_log(data: dict) -> None:
    _ensure_log_dir()
    tmp_path = LOG_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, LOG_PATH)


def overviewnotes_tab():
    st.header("Overblik – Controlling dashboard")
    st.caption("Automatisk log af antal ruter der skal kontrolleres (ugentligt).")

    log = read_weekly_log()

    if not log:
        st.info(
            "Der er endnu ingen historik. Kør en Controlling-analyse (upload fil), "
            "så logges uge og antal ruter automatisk."
        )
        return

    # log format: { "YYYYWW": { "count": int, "updated_at": str } }
    rows = []
    for yearweek, payload in log.items():
        if isinstance(payload, dict):
            rows.append(
                {
                    "YearWeek": yearweek,
                    "Count": int(payload.get("count", 0)),
                    "UpdatedAt": payload.get("updated_at", ""),
                }
            )

    df = pd.DataFrame(rows).sort_values("YearWeek")

    # Metrics
    latest = df.iloc[-1]
    total_weeks = df["YearWeek"].nunique()
    total_routes = int(df["Count"].sum())
    avg_per_week = float(df["Count"].mean()) if len(df) else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Seneste uge", latest["YearWeek"])
    c2.metric("Ruter (seneste uge)", int(latest["Count"]))
    c3.metric("Gns. pr. uge", f"{avg_per_week:.1f}")
    c4.metric("Uger logget", int(total_weeks))

    st.markdown("---")

    # Chart
    st.subheader("Antal ruter der skal kontrolleres pr. uge")
    chart_df = df.set_index("YearWeek")[["Count"]]
    st.bar_chart(chart_df)

    st.markdown("---")

    # Table + download
    st.subheader("Historik")
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "Download historik (JSON)",
        data=json.dumps(log, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="controlling_weekly_log.json",
        mime="application/json",
    )

    # Admin actions
    with st.expander("Admin"):
        st.caption("Brug kun hvis du vil nulstille eller importere historik.")
        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("Nulstil historik"):
                write_weekly_log({})
                st.success("Historik nulstillet.")
                st.rerun()

        with col_b:
            up = st.file_uploader("Import historik (JSON)", type=["json"])
            if up is not None:
                try:
                    imported = json.loads(up.read().decode("utf-8"))
                    if isinstance(imported, dict):
                        # merge (imported overwrites same weeks)
                        merged = {**log, **imported}
                        write_weekly_log(merged)
                        st.success("Historik importeret/merged.")
                        st.rerun()
                    else:
                        st.error("Ugyldigt format. JSON skal være et objekt/dict.")
                except Exception:
                    st.error("Kunne ikke importere filen. Tjek at det er en gyldig JSON.")
