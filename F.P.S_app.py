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

DEFAULT_CLASS_NAME = "Summerschool Class Prague 2nd-14th August"

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
if not storage.get_classes():
    storage.add_class(DEFAULT_CLASS_NAME)

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

classes = storage.get_classes()
selected_class_id = st.session_state.get("selected_class_id")
selected_class = storage.get_class(selected_class_id) if selected_class_id else None
if not selected_class and classes:
    selected_class = classes[0]
    st.session_state["selected_class_id"] = selected_class["id"]

nav_col, main_col = st.columns([1, 5], gap="large")

with nav_col:
    st.markdown("### Classes")

    class_names = [item["name"] for item in classes]
    selected_name = st.selectbox(
        "Choose a class",
        class_names,
        index=class_names.index(selected_class["name"]),
        key="selected_class_name",
    )
    if selected_name != selected_class["name"]:
        new_selected = next(
            item for item in classes if item["name"] == selected_name
        )
        st.session_state["selected_class_id"] = new_selected["id"]
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("#### Add another class")
    new_class_name = st.text_input(
        "Class name",
        placeholder="Summerschool Class Prague 2nd-14th August",
        key="new_class_name",
    )
    if st.button("Add next class", key="add_next_class"):
        if not new_class_name.strip():
            st.error("Enter a class name before adding a new class.")
        else:
            success, result = storage.add_class(new_class_name.strip())
            if success:
                st.success(f"Created class '{result['name']}'.")
                st.session_state["selected_class_id"] = result["id"]
                st.experimental_rerun()
            else:
                st.error(result)

    st.markdown("---")
    st.markdown("#### Delete current class")
    if st.button("Delete selected class", key="delete_selected_class"):
        st.session_state["confirm_delete_class"] = True

    if st.session_state.get("confirm_delete_class"):
        confirmation = st.text_input(
            "Type DELETE to confirm deleting this class",
            key="confirm_delete_class",
        )
        if st.button("Confirm delete", key="confirm_delete_submit"):
            if confirmation.strip().upper() == "DELETE":
                success, message = storage.delete_class(selected_class["id"])
                if success:
                    st.success(message)
                    st.session_state["confirm_delete_class"] = False
                    st.experimental_rerun()
                else:
                    st.error(message)
            else:
                st.error("Please type DELETE exactly to confirm deletion.")

with main_col:
    st.title("F.P.S")
    st.subheader(selected_class["name"])
    st.write(
        "This class has a team rotation builder and a module-based materials area."
    )

    tabs = st.tabs(["Team Rotation Builder", "Class Material Library"])
    with tabs[0]:
        page_modules["team_builder"].render(storage, selected_class["id"])
    with tabs[1]:
        page_modules["class_library"].render(storage, selected_class["id"])
