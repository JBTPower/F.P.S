"""
app.py

Entry point for the F.P.S. (Felipe's Problem Solver) Streamlit app.
Run with: streamlit run app.py
"""

import importlib.util
from pathlib import Path
import streamlit as st
from core.class_storage import ClassStorage

# Updated to match the initial prompt requirement
DEFAULT_CLASS_NAME = "Summerschool Course AI 3rd to 14th August"

def _safe_rerun():
    """Safely call Streamlit's experimental rerun if available."""
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
        pass

app_dir = Path(__file__).resolve().parent
pages_dir = app_dir / "pages"

st.set_page_config(
    page_title="F.P.S Dashboard",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="collapsed" # We use custom columns instead of standard sidebar
)

# --- MODERN CUSTOM CSS ---
# This drastically changes the look from "standard Streamlit" to a modern dashboard
st.markdown(
    """
    <style>
    /* Hide standard headers/footers */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* App Background */
    .stApp {
        background-color: #F8F9FA;
    }

    /* Customizing the Nav Column (acting as a sidebar) */
    [data-testid="column"]:nth-of-type(1) {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #E9ECEF;
    }

    /* Modern Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        border: none;
        background-color: #4361EE;
        color: white;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #3A56D4;
        box-shadow: 0 4px 12px rgba(67, 97, 238, 0.3);
        transform: translateY(-1px);
    }
    
    /* Specific styling for the Delete button to make it distinct */
    div[data-testid="stButton"] button:has(div:contains("Delete")) {
        background-color: #EF233C;
    }
    div[data-testid="stButton"] button:has(div:contains("Delete")):hover {
        background-color: #D90429;
        box-shadow: 0 4px 12px rgba(239, 35, 60, 0.3);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        border: 1px solid #E9ECEF;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4361EE !important;
        color: white !important;
        border: none;
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #DEE2E6;
        padding: 0.5rem;
    }
    .stSelectbox>div>div>div {
        border-radius: 8px;
    }
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

page_modules = {key: load_page(path) for key, path in PAGE_PATHS.items()}
classes = storage.get_classes()

class_ids = [c["id"] for c in classes]
def _format_class_name(class_id: str) -> str:
    for c in classes:
        if c["id"] == class_id:
            return c.get("name", class_id)
    return class_id

current_id = st.session_state.get("selected_class_id")
if current_id not in class_ids:
    current_id = class_ids[0] if class_ids else None
    if current_id:
        st.session_state["selected_class_id"] = current_id

selected_class = storage.get_class(current_id) if current_id else None

# Layout
nav_col, main_col = st.columns([1.2, 4.8], gap="large")

with nav_col:
    st.markdown("### 📚 Dashboard")
    st.markdown("<p style='color: #6C757D; font-size: 0.9rem;'>Class Management</p>", unsafe_allow_html=True)

    if classes:
        selected_id = st.selectbox(
            "Active Class",
            class_ids,
            index=class_ids.index(current_id) if current_id in class_ids else 0,
            format_func=_format_class_name,
            key="selected_class_id",
            label_visibility="collapsed"
        )
        selected_class = storage.get_class(selected_id)
    else:
        st.info("No classes available. Add a new class below.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### ➕ New Class")
    new_class_name = st.text_input(
        "Class name",
        placeholder="e.g. Autumn Seminar AI...",
        key="new_class_name",
        label_visibility="collapsed"
    )
    if st.button("Create Class", key="add_next_class"):
        if not new_class_name.strip():
            st.error("Enter a name first.")
        else:
            success, result = storage.add_class(new_class_name.strip())
            if success:
                st.toast(f"Created class '{result['name']}'!", icon="✅")
                st.session_state["selected_class_id"] = result["id"]
                _safe_rerun()
            else:
                st.error(result)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if selected_class:
        with st.expander("⚙️ Danger Zone"):
            st.markdown("<p style='color: #6C757D; font-size: 0.8rem;'>Remove current class permanently.</p>", unsafe_allow_html=True)
            if st.button("Delete Selected Class", key="delete_selected_class"):
                if "confirm_delete_class_input" in st.session_state:
                    st.session_state.pop("confirm_delete_class_input")
                st.session_state["confirm_delete_class"] = True

            if st.session_state.get("confirm_delete_class"):
                confirmation = st.text_input(
                    "Type DELETE to confirm",
                    key="confirm_delete_class_input",
                )
                if st.button("Confirm", key="confirm_delete_submit"):
                    if confirmation.strip().upper() == "DELETE":
                        success, message = storage.delete_class(selected_class["id"])
                        if success:
                            st.toast(message, icon="🗑️")
                            st.session_state["confirm_delete_class"] = False
                            remaining = storage.get_classes()
                            if remaining:
                                st.session_state["selected_class_id"] = remaining[0]["id"]
                            else:
                                st.session_state.pop("selected_class_id", None)
                            _safe_rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Type DELETE exactly.")

with main_col:
    # Custom Header for the Main Area
    st.markdown(
        """
        <div style="padding-bottom: 2rem;">
            <h1 style="color: #212529; font-size: 2.5rem; font-weight: 800; margin-bottom: 0;">F.P.S.</h1>
            <h3 style="color: #4361EE; font-weight: 600; margin-top: -10px;">Felipe's Problem Solver</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    if not selected_class:
        st.warning("No class is selected. Please add or choose a class from the menu.")
    else:
        st.markdown(f"### 📍 Workspace: **{selected_class['name']}**")
        st.markdown(
            "<p style='color: #6C757D; margin-bottom: 2rem;'>Manage your team rotation builder and module-based materials below.</p>", 
            unsafe_allow_html=True
        )

        # Using modern styled tabs
        tabs = st.tabs(["👥 Team Rotation Builder", "📁 Class Material Library"])
        
        with tabs[0]:
            st.markdown("<br>", unsafe_allow_html=True)
            page_modules["team_builder"].render(storage, selected_class["id"])
            
        with tabs[1]:
            st.markdown("<br>", unsafe_allow_html=True)
            page_modules["class_library"].render(storage, selected_class["id"])