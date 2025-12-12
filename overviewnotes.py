# overviewnotes.py

import json
from datetime import datetime

import streamlit as st


def _init_state():
    if "notes_items" not in st.session_state:
        st.session_state.notes_items = []  # liste af dicts
    if "help_items" not in st.session_state:
        st.session_state.help_items = []   # liste af dicts


def _now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def overviewnotes_tab():
    _init_state()

    st.header("Overblik & noter")
    st.caption("Lav interne noter og hjælpeartikler til teamet – i et overskueligt dashboard.")

    # Små “overview” metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Noter", len(st.session_state.notes_items))
    c2.metric("Hjælpeartikler", len(st.session_state.help_items))
    c3.metric("Senest opdateret", _now_iso())

    st.markdown("---")

    # --- Layout med cards (2 kolonner) --------------------------------------
    left, right = st.columns([1, 1])

    # Card-stilen kommer fra main.py (.card). Vi bruger den her via st.markdown HTML wrappers.

    with left:
        st.markdown(
            """
            <div class="card">
              <div class="card-title">📝 Ny note</div>
              <div class="card-body">Skriv en intern note til teamet. Brug tags for at gøre den nem at finde.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        title = st.text_input("Titel", key="note_title")
        tags = st.text_input("Tags (kommasepareret)", placeholder="fx controlling, ikea, proces", key="note_tags")
        body = st.text_area("Indhold", height=180, key="note_body")

        col_save, col_clear = st.columns([1, 1])
        with col_save:
            if st.button("Gem note", key="save_note"):
                if title.strip() and body.strip():
                    st.session_state.notes_items.insert(
                        0,
                        {
                            "title": title.strip(),
                            "tags": [t.strip() for t in tags.split(",") if t.strip()],
                            "body": body.strip(),
                            "created_at": _now_iso(),
                        },
                    )
                    st.session_state.note_title = ""
                    st.session_state.note_tags = ""
                    st.session_state.note_body = ""
                    st.success("Note gemt.")
                    st.rerun()
                else:
                    st.warning("Udfyld mindst titel og indhold.")
        with col_clear:
            if st.button("Ryd", key="clear_note"):
                st.session_state.note_title = ""
                st.session_state.note_tags = ""
                st.session_state.note_body = ""
                st.rerun()

    with right:
        st.markdown(
            """
            <div class="card">
              <div class="card-title">📚 Ny hjælpeartikel</div>
              <div class="card-body">Skriv en kort guide eller instruktion som andre kan bruge.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        h_title = st.text_input("Titel", key="help_title")
        h_category = st.text_input("Kategori", placeholder="fx Controlling, Solar, Process", key="help_category")
        h_body = st.text_area("Guide / instruktion", height=180, key="help_body")

        col_save2, col_clear2 = st.columns([1, 1])
        with col_save2:
            if st.button("Gem artikel", key="save_help"):
                if h_title.strip() and h_body.strip():
                    st.session_state.help_items.insert(
                        0,
                        {
                            "title": h_title.strip(),
                            "category": h_category.strip(),
                            "body": h_body.strip(),
                            "created_at": _now_iso(),
                        },
                    )
                    st.session_state.help_title = ""
                    st.session_state.help_category = ""
                    st.session_state.help_body = ""
                    st.success("Hjælpeartikel gemt.")
                    st.rerun()
                else:
                    st.warning("Udfyld mindst titel og guide/indhold.")
        with col_clear2:
            if st.button("Ryd", key="clear_help"):
                st.session_state.help_title = ""
                st.session_state.help_category = ""
                st.session_state.help_body = ""
                st.rerun()

    st.markdown("---")

    # --- Søgning / filtrering ------------------------------------------------
    st.subheader("Bibliotek")
    q = st.text_input("Søg i noter og artikler", placeholder="Søg på titel, tags, kategori eller indhold…")

    # --- Noter (cards) -------------------------------------------------------
    st.markdown("#### Noter")

    notes = st.session_state.notes_items
    if q.strip():
        ql = q.lower()
        notes = [
            n for n in notes
            if ql in n["title"].lower()
            or ql in n["body"].lower()
            or any(ql in t.lower() for t in n.get("tags", []))
        ]

    if not notes:
        st.info("Ingen noter endnu.")
    else:
        for idx, n in enumerate(notes):
            tags_str = ", ".join(n.get("tags", [])) if n.get("tags") else "—"
            st.markdown(
                f"""
                <div class="card" style="margin-bottom: 14px;">
                  <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-size:1.05em; font-weight:700;">{n["title"]}</div>
                    <div style="color:#4A6275; font-size:0.85em;">{n["created_at"]}</div>
                  </div>
                  <div style="color:#4A6275; font-size:0.9em; margin-top:4px; margin-bottom:10px;">
                    Tags: {tags_str}
                  </div>
                  <div style="white-space:pre-wrap; color:#01293D;">{n["body"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_del, _ = st.columns([1, 6])
            with col_del:
                if st.button("Slet note", key=f"delete_note_{idx}"):
                    # Fjern baseret på entydig match (title+created_at)
                    st.session_state.notes_items = [
                        x for x in st.session_state.notes_items
                        if not (x["title"] == n["title"] and x["created_at"] == n["created_at"])
                    ]
                    st.rerun()

    # --- Hjælpeartikler (cards) ---------------------------------------------
    st.markdown("#### Hjælpeartikler")

    helps = st.session_state.help_items
    if q.strip():
        ql = q.lower()
        helps = [
            h for h in helps
            if ql in h["title"].lower()
            or ql in h["body"].lower()
            or ql in h.get("category", "").lower()
        ]

    if not helps:
        st.info("Ingen hjælpeartikler endnu.")
    else:
        for idx, h in enumerate(helps):
            category_str = h.get("category", "") or "—"
            st.markdown(
                f"""
                <div class="card" style="margin-bottom: 14px;">
                  <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-size:1.05em; font-weight:700;">{h["title"]}</div>
                    <div style="color:#4A6275; font-size:0.85em;">{h["created_at"]}</div>
                  </div>
                  <div style="color:#4A6275; font-size:0.9em; margin-top:4px; margin-bottom:10px;">
                    Kategori: {category_str}
                  </div>
                  <div style="white-space:pre-wrap; color:#01293D;">{h["body"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_del, _ = st.columns([1, 6])
            with col_del:
                if st.button("Slet artikel", key=f"delete_help_{idx}"):
                    st.session_state.help_items = [
                        x for x in st.session_state.help_items
                        if not (x["title"] == h["title"] and x["created_at"] == h["created_at"])
                    ]
                    st.rerun()

    st.markdown("---")

    # --- Export / import (delbart) ------------------------------------------
    st.subheader("Eksport / import")

    export_obj = {
        "notes": st.session_state.notes_items,
        "help_articles": st.session_state.help_items,
        "exported_at": _now_iso(),
    }
    export_json = json.dumps(export_obj, ensure_ascii=False, indent=2)

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.download_button(
            "Download som JSON",
            data=export_json.encode("utf-8"),
            file_name="overviewnotes_export.json",
            mime="application/json",
        )

    with col_b:
        uploaded = st.file_uploader("Import JSON (overskriver ikke – tilføjer)", type=["json"])
        if uploaded:
            try:
                imported = json.loads(uploaded.read().decode("utf-8"))
                new_notes = imported.get("notes", [])
                new_help = imported.get("help_articles", [])

                if isinstance(new_notes, list):
                    st.session_state.notes_items = new_notes + st.session_state.notes_items
                if isinstance(new_help, list):
                    st.session_state.help_items = new_help + st.session_state.help_items

                st.success("Import gennemført. Indholdet er tilføjet.")
                st.rerun()
            except Exception:
                st.error("Kunne ikke importere filen. Tjek at det er en gyldig JSON-export.")
