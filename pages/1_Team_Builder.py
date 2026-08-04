import csv
import io
import random
import streamlit as st


def render(storage, class_id: str):
    st.header("Team Rotation Builder")
    st.write(
        "Build Felipe's team mix for the class period. "
        "Once generated, the latest rotation is kept as the active class overview."
    )

    latest_rotation = storage.get_latest_rotation(class_id)
    if latest_rotation:
        with st.expander("Current rotation overview", expanded=True):
            st.write(f"Created: {latest_rotation['created_at']}")
            st.write(f"Students: {latest_rotation['student_count']}")
            st.write(f"Group size: {latest_rotation['group_size']}")
            st.write(f"Seed: {latest_rotation['seed']}")
            for index, group in enumerate(latest_rotation["groups"], start=1):
                st.markdown(f"**Group {index}**")
                for member in group:
                    st.write(f"- {member}")
            st.download_button(
                "Download current rotation as CSV",
                data=_rotation_csv(latest_rotation),
                file_name="fps_current_rotation.csv",
                mime="text/csv",
            )
    else:
        st.info("No rotation has been generated for this class yet.")

    st.divider()
    _render_team_builder(storage, class_id)

    past = storage.get_rotations(class_id)
    if past:
        with st.expander("Past rotation history", expanded=False):
            for rotation in reversed(past[:-1]):
                st.write(f"{rotation['created_at']} — {rotation['student_count']} students")


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


def _render_team_builder(storage, class_id: str):
    st.subheader("Generate team rotation")
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

    if st.button("Generate rotation", key="generate_team_rotation"):
        if not names:
            st.error("Please paste or upload a student roster first.")
            return

        group_size = min(group_size, len(names))
        random.Random(seed).shuffle(names)
        groups = [
            names[i : i + group_size] for i in range(0, len(names), group_size)
        ]

        success, result = storage.add_rotation(
            class_id,
            groups,
            group_size,
            seed,
            raw_names,
        )
        if success:
            st.success("Rotation saved for the class period.")
            try:
                rerun = getattr(st, "experimental_rerun", None)
                if callable(rerun):
                    rerun()
            except Exception:
                try:
                    st.stop()
                except Exception:
                    pass
        else:
            st.error(result)


def _rotation_csv(rotation):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Group", "Student"])
    for index, group in enumerate(rotation["groups"], start=1):
        for student in group:
            writer.writerow([index, student])
    return buffer.getvalue()
