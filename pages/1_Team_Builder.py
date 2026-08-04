import csv
import io
import random
from pathlib import Path

import streamlit as st


def render(storage):
    category_key = "team_builder"
    category_label = storage.get_category_label(category_key)

    st.header(category_label)
    st.caption(f"Default folder: {category_label}")
    st.write(
        "Enter your student roster or upload a class sheet, then create final team groups or rotations for Felipe's class logic."
    )

    _render_team_builder(storage, category_key)
    st.divider()
    _render_new_class_panel(storage, category_key, category_label)
    st.divider()
    _render_existing_classes(storage, category_key)


def _parse_names(raw_text):
    if not raw_text:
        return []

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    names = []
    for line in lines:
        if "," in line and "@" not in line:
            parts = [part.strip() for part in line.split(",") if part.strip()]
            names.extend(parts)
        else:
            names.append(line)
    return names


def _render_team_builder(storage, category_key: str):
    st.subheader("Team creation")
    roster_text = st.text_area(
        "Paste student names here",
        placeholder="One name per line, or comma-separated list",
        height=180,
        key="team_roster_text",
    )

    uploaded_file = st.file_uploader(
        "Or upload class roster (TXT / CSV)",
        type=["txt", "csv"],
        key="team_roster_upload",
    )

    raw_names = roster_text
    if uploaded_file is not None:
        uploaded_bytes = uploaded_file.read()
        try:
            uploaded_text = uploaded_bytes.decode("utf-8")
        except UnicodeDecodeError:
            uploaded_text = uploaded_bytes.decode("latin-1", errors="ignore")
        raw_names = uploaded_text

    names = _parse_names(raw_names)
    if names:
        st.info(f"Loaded {len(names)} student names.")
    else:
        st.warning("No student names loaded yet.")

    cols = st.columns([1, 1, 1])
    with cols[0]:
        group_size = st.number_input(
            "Team size",
            min_value=2,
            max_value=max(2, len(names) or 10),
            value=3,
            step=1,
            key="team_group_size",
        )
    with cols[1]:
        seed = st.number_input(
            "Shuffle seed",
            min_value=0,
            max_value=9999,
            value=42,
            step=1,
            key="team_shuffle_seed",
        )
    with cols[2]:
        include_header = st.checkbox("Show group headers", value=True, key="team_headers")

    if st.button("Generate team groups", key="generate_team_groups"):
        if not names:
            st.error("Please paste or upload a student roster first.")
            return

        group_size = min(group_size, len(names))
        random.Random(seed).shuffle(names)
        groups = [
            names[i : i + group_size] for i in range(0, len(names), group_size)
        ]

        st.success(f"Created {len(groups)} groups from {len(names)} students.")
        output_lines = []
        for index, group in enumerate(groups, start=1):
            if include_header:
                st.markdown(f"**Group {index}**")
            for name in group:
                st.write(f"- {name}")
            output_lines.append(f"Group {index}")
            output_lines.extend(group)
            output_lines.append("")

        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["Group", "Student"])
        for index, group in enumerate(groups, start=1):
            for name in group:
                writer.writerow([index, name])

        st.download_button(
            "Download team mix as CSV",
            data=csv_buffer.getvalue(),
            file_name="fps_team_mix.csv",
            mime="text/csv",
        )


def _render_new_class_panel(storage, category_key: str, category_label: str):
    with st.expander("Create a new class folder", expanded=True):
        new_name = st.text_input(
            "Class name",
            placeholder="Enter a new class name for Team & Rotation Builder",
            key=f"new_class_name_{category_key}",
        )
        if st.button("Create class", key=f"create_class_{category_key}"):
            success, result = storage.add_class(new_name, category_key)
            if success:
                st.success(f"Created class '{result['name']}' in {category_label}.")
                st.experimental_rerun()
            else:
                st.error(result)


def _render_existing_classes(storage, category_key: str):
    classes = storage.get_classes(category_key)
    if not classes:
        st.info("No classes have been created yet in this folder.")
        return

    for class_item in classes:
        with st.expander(class_item["name"], expanded=False):
            st.write(f"Folder: **{class_item['folder']}**")
            st.write("Use the delete action below to remove this class permanently.")

            delete_key = f"delete_{class_item['id']}"
            confirm_key = f"confirm_delete_{class_item['id']}"
            if st.button("Delete class", key=delete_key):
                st.session_state[delete_key] = True

            if st.session_state.get(delete_key, False):
                confirmation = st.text_input(
                    "Type DELETE to confirm deletion",
                    key=confirm_key,
                )
                if st.button("Confirm deletion", key=f"confirm_submit_{class_item['id']}"):
                    if confirmation.strip().upper() == "DELETE":
                        success, message = storage.delete_class(class_item["id"])
                        if success:
                            st.success(message)
                            st.experimental_rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Please type DELETE exactly to confirm deletion.")
