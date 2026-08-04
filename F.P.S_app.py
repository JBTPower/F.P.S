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


def _safe_rerun():
    """Safely call Streamlit's experimental rerun if available.

    Some Streamlit environments (or versions) may not expose
    `st.experimental_rerun` or it may raise. We try to call it and fall
    back to `st.stop()` if necessary so the app doesn't raise an
    AttributeError to the user.
    """
    try:
        rerun = getattr(st, "experimental_rerun", None)
        if callable(rerun):
            rerun()
            return
    except Exception:
        pass

    try:
        st.stop()
    except Exception:
        # If even st.stop() fails, silently ignore to avoid crashing the app.
        pass

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

# Build a stable selectbox that uses class IDs as the option values and shows
# class names as labels. This avoids mismatches between stored IDs and names
# and prevents the UI from ending up with a missing `selected_class`.
class_ids = [c["id"] for c in classes]
def _format_class_name(class_id: str) -> str:
    for c in classes:
        if c["id"] == class_id:
            return c.get("name", class_id)
    return class_id

# Ensure session state has a valid selected id
current_id = st.session_state.get("selected_class_id")
if current_id not in class_ids:
    current_id = class_ids[0] if class_ids else None
    if current_id:
        st.session_state["selected_class_id"] = current_id

selected_class = storage.get_class(current_id) if current_id else None

nav_col, main_col = st.columns([1, 5], gap="large")

with nav_col:
    st.markdown("### Classes")

    if classes:
        selected_id = st.selectbox(
            "Choose a class",
            class_ids,
            index=class_ids.index(current_id) if current_id in class_ids else 0,
            format_func=_format_class_name,
            key="selected_class_id",
        )
        # `selected_class` is derived from `st.session_state['selected_class_id']`
        selected_class = storage.get_class(selected_id)
    else:
        st.info("No classes available. Add a new class below.")

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
                _safe_rerun()
            else:
                st.error(result)

    st.markdown("---")
    st.markdown("#### Delete current class")
    if not selected_class:
        st.info("No class selected to delete.")
    else:
        if st.button("Delete selected class", key="delete_selected_class"):
            # Clear any previous input and prompt for confirmation
            if "confirm_delete_class_input" in st.session_state:
                st.session_state.pop("confirm_delete_class_input")
            st.session_state["confirm_delete_class"] = True

        if st.session_state.get("confirm_delete_class"):
            confirmation = st.text_input(
                "Type DELETE to confirm deleting this class",
                key="confirm_delete_class_input",
            )
            if st.button("Confirm delete", key="confirm_delete_submit"):
                if confirmation.strip().upper() == "DELETE":
                    # Guard against missing selected_class
                    if not selected_class:
                        st.error("No class selected to delete.")
                    else:
                        success, message = storage.delete_class(selected_class["id"])
                        if success:
                            st.success(message)
                            st.session_state["confirm_delete_class"] = False
                            # pick a new selected class if any remain
                            remaining = storage.get_classes()
                            if remaining:
                                st.session_state["selected_class_id"] = remaining[0]["id"]
                            else:
                                st.session_state.pop("selected_class_id", None)
                            _safe_rerun()
                        else:
                            st.error(message)
                else:
                    st.error("Please type DELETE exactly to confirm deletion.")

with main_col:
    st.title("F.P.S")
    if not selected_class:
        st.warning("No class is selected. Please add or choose a class.")
    else:
        st.subheader(selected_class["name"])
        st.write(
            "This class has a team rotation builder and a module-based materials area."
        )

        tabs = st.tabs(["Team Rotation Builder", "Class Material Library"])
        with tabs[0]:
            page_modules["team_builder"].render(storage, selected_class["id"])
        with tabs[1]:
            page_modules["class_library"].render(storage, selected_class["id"])
