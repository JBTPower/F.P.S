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

from pathlib import Path

import streamlit as st

app_dir = Path(__file__).resolve().parent
pages_dir = app_dir / "pages"

st.set_page_config(page_title="F.P.S. — Felipe's Problem Solver", page_icon="🧩", layout="wide")

team_builder = st.Page(pages_dir / "1_Team_Builder.py", title="Team & Rotation Builder", icon="👥")
class_library = st.Page(pages_dir / "2_Class_Library.py", title="Class Material Library", icon="📁")

pg = st.navigation([team_builder, class_library])

st.sidebar.title("F.P.S.")
st.sidebar.caption("Felipe's Problem Solver — ESS Prague 2026 Capstone")

pg.run()
