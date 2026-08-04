"""
app.py

Entry point for the F.P.S. (Felipe's Problem Solver) Streamlit app.
Run with: streamlit run app.py

Expected folder layout (create these yourself in your repo):

fps_dashboard/
├── app.py                  <- this file
├── core/
│   ├── __init__.py         <- empty file, just marks core/ as a package
│   ├── pairing.py
│   ├── team_storage.py
│   └── file_manager.py
├── pages/
│   ├── 1_Team_Builder.py
│   └── 2_Class_Library.py
├── requirements.txt
└── data/                   <- created automatically at runtime
"""

import importlib.util
from pathlib import Path

import streamlit as st

from core.class_storage import ClassStorage

app_dir = Path(__file__).resolve().parent
pages_dir = app_dir / "pages"

st.set_page_config(
    page_title="F.P.S",
    page_icon="🧩",
    layout="wide",
)

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

storage = ClassStorage()

PAGE_OPTIONS = [
    ("team_builder", "Team & Rotation Builder"),
    ("class_library", "Class Material Library"),
]

PAGE_PATHS = {
    "team_builder": pages_dir / "1_Team_Builder.py",
    "class_library": pages_dir / "2_Class_Library.py",
}


def load_page(page_path: Path):
    spec = importlib.util.spec_from_file_location(f"page_{page_path.stem}", page_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

page_modules = {
    key: load_page(path) for key, path in PAGE_PATHS.items()
}

if "page" not in st.session_state:
    st.session_state.page = "team_builder"

page_keys = [key for key, _ in PAGE_OPTIONS]
page_labels = [label for _, label in PAGE_OPTIONS]
label_to_key = {label: key for key, label in PAGE_OPTIONS}

nav_col, main_col = st.columns([1, 4], gap="large")

with nav_col:
    st.markdown("### Workspace navigation")
    selected_label = st.radio(
        "Choose a folder",
        page_labels,
        index=page_keys.index(st.session_state.page),
        key="page_radio",
    )
    st.session_state.page = label_to_key[selected_label]

    st.markdown("---")
    st.markdown("#### Quick access")
    for key, label in PAGE_OPTIONS:
        if st.button(label, key=f"nav_button_{key}"):
            st.session_state.page = key
            st.experimental_rerun()

with main_col:
    st.title("F.P.S")
    st.write(
        "Manage Felipe's classes in the two folders below. Add or delete classes with confirmation so the workspace stays clean."
    )

    counts = {
        key: len(storage.get_classes(key)) for key in page_keys
    }
    card_cols = st.columns(2, gap="large")
    for card_col, key in zip(card_cols, page_keys):
        card_col.metric(page_labels[page_keys.index(key)], f"{counts[key]} classes")

    st.divider()
    page_modules[st.session_state.page].render(storage)
