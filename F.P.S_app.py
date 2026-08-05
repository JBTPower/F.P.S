"""
F.P.S. (Felipe's Problem Solver) - Fully Integrated Dashboard
Includes:
- Crash-free Class Management
- True Folder/Subfolder Module Library (with Add/Remove Modules)
- Felipe's Authoritative Capstone + Non-Repeating Pair/Trio Rotation Engine
- AI Assistant (Summarizer, Quiz, Chat, Material Review)
"""

import streamlit as st
import pandas as pd
import random
from pathlib import Path
from core.ai_helper import (
    extract_text_from_bytes,
    summarize_document,
    generate_quiz,
    chat_with_material,
    review_material,
    generate_team_icebreaker,
)

# --- PAGE CONFIG & MODERN CSS ---
st.set_page_config(
    page_title="F.P.S Dashboard",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #F8F9FA; }
    [data-testid="column"]:nth-of-type(1) {
        background-color: #FFFFFF; padding: 1.5rem; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #E9ECEF;
    }
    .stButton>button {
        border-radius: 8px; font-weight: 600; transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 1rem; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 45px; background-color: #FFFFFF; border-radius: 8px;
        padding: 0.5rem 1.5rem; border: 1px solid #E9ECEF;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4361EE !important; color: white !important; border: none;
    }
    .folder-card {
        background: #FFFFFF; border: 1px solid #E9ECEF; border-radius: 8px;
        padding: 1rem; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- IN-MEMORY STORAGE ENGINE (Simulating Folders & Subfolders) ---
if "fps_data" not in st.session_state:
    st.session_state["fps_data"] = {
        "classes": {
            "c1": {
                "id": "c1",
                "name": "Summerschool Course AI 3rd to 14th August",
                "modules": ["Module 1", "Module 2", "Module 3"],
                "files": {
                    "Module 1": [{"name": "Day01_Syllabus.pdf", "size": "1.2 MB"}],
                    "Module 2": [],
                    "Module 3": []
                },
                "students": [
                    "Sarankan", "Alice", "Laurenz", "Zoe", "Kevin", 
                    "Mahmoud", "Ranya", "Nelson", "Frederik", "Johan", 
                    "Jeremy", "Petar", "Ayman", "Karolina", "Alessandro"
                ]
            }
        },
        "active_class_id": "c1"
    }

data = st.session_state["fps_data"]

# --- NAVIGATION / CLASS MANAGEMENT ---
nav_col, main_col = st.columns([1.3, 4.7], gap="large")

with nav_col:
    st.markdown("### 📚 Classes")
    class_list = list(data["classes"].values())
    class_ids = [c["id"] for c in class_list]
    
    if class_ids:
        # Safe selection logic without session_state API crashes
        current_idx = class_ids.index(data["active_class_id"]) if data["active_class_id"] in class_ids else 0
        selected_id = st.selectbox(
            "Select Workspace",
            class_ids,
            index=current_idx,
            format_func=lambda x: data["classes"][x]["name"],
            label_visibility="collapsed"
        )
        data["active_class_id"] = selected_id
        active_class = data["classes"][selected_id]
    else:
        active_class = None
        st.info("No classes found.")

    st.markdown("---")
    st.markdown("#### ➕ Add Class")
    new_class_name = st.text_input("Class Name", placeholder="e.g. AI Prague Autumn", label_visibility="collapsed")
    if st.button("Create Class", use_container_width=True):
        if new_class_name.strip():
            new_id = f"c_{random.randint(100,999)}"
            data["classes"][new_id] = {
                "id": new_id,
                "name": new_class_name.strip(),
                "modules": ["Module 1", "Module 2"],
                "files": {"Module 1": [], "Module 2": []},
                "students": ["Student A", "Student B", "Student C", "Student D"]
            }
            data["active_class_id"] = new_id
            st.rerun()

    if active_class:
        st.markdown("---")
        with st.expander("⚙️ Delete Class"):
            confirm = st.text_input("Type DELETE to confirm")
            if st.button("Delete Workspace", type="primary", use_container_width=True):
                if confirm == "DELETE":
                    del data["classes"][active_class["id"]]
                    remaining = list(data["classes"].keys())
                    data["active_class_id"] = remaining[0] if remaining else None
                    st.rerun()

# --- MAIN WORKSPACE ---
with main_col:
    st.markdown(
        """
        <div style="padding-bottom: 1rem;">
            <h1 style="color: #212529; font-size: 2.2rem; font-weight: 800; margin-bottom: 0;">F.P.S.</h1>
            <h4 style="color: #4361EE; font-weight: 600; margin-top: -5px;">Felipe's Problem Solver</h4>
        </div>
        """, 
        unsafe_allow_html=True
    )

    if not active_class:
        st.warning("Please create or select a class from the left menu.")
    else:
        st.markdown(f"### 📍 Workspace: **{active_class['name']}**")
        
        tabs = st.tabs(["👥 Team Rotation Builder (Felipe's Logic)", "📁 Class Material Library (Subfolders)", "🤖 AI Assistant"])

        # ==========================================
        # TAB 1: FELIPE'S TEAM & ROTATION BUILDER
        # ==========================================
        with tabs[0]:
            st.markdown("#### 1. Capstone Teams & Student Roster")
            st.write("Edit names below. Odd numbers automatically generate a **Trio** during lab rotations.")
            
            # Easy student roster editing
            student_str = st.text_area(
                "Student List (Comma separated)", 
                value=", ".join(active_class["students"]),
                height=70
            )
            students = [s.strip() for s in student_str.split(",") if s.strip()]
            active_class["students"] = students

            # Step 1: Capstone Teams (Fixed main project teams)
            num_teams = st.slider("Number of Capstone Teams", min_value=2, max_value=8, value=5)
            
            if st.button("⚡ Generate Authoritative Rotation Card", type="primary"):
                if len(students) < 4:
                    st.error("Need at least 4 students to generate rotation matrix.")
                else:
                    # Assign Capstone Teams (Fixed)
                    teams = {f"Team {chr(65+i)}": [] for i in range(num_teams)}
                    for idx, student in enumerate(students):
                        team_name = f"Team {chr(65 + (idx % num_teams))}"
                        teams[team_name].append(student)

                    st.markdown("---")
                    st.markdown("### 🏆 Fixed Capstone Teams (Morning 9:00 AM Stand-up)")
                    cols = st.columns(num_teams)
                    for idx, (t_name, t_members) in enumerate(teams.items()):
                        with cols[idx]:
                            st.markdown(f"**{t_name}**")
                            for m in t_members:
                                st.markdown(f"- {m}")

                    # Step 2: Felipe's Non-Repeating Pair/Trio Generator (Days 2 to 8)
                    st.markdown("---")
                    st.markdown("### 🔄 Daily Lab Partner Rotation (Days 2 to 8)")
                    st.caption("Guaranteed zero repeat pairings across days. Automatically forms a Trio if headcount is odd.")

                    days = [f"Day {d}" for d in range(2, 9)]
                    rotation_record = {s: {} for s in students}
                    past_pairs = set()

                    for day in days:
                        pool = students.copy()
                        random.shuffle(pool)
                        day_pairs = []

                        # If odd, pop 3 students for a Trio
                        trio = None
                        if len(pool) % 2 != 0 and len(pool) >= 3:
                            trio = [pool.pop(), pool.pop(), pool.pop()]
                            for i in range(3):
                                s1, s2 = trio[i], trio[(i+1)%3]
                                rotation_record[s1][day] = f"{trio[(i+1)%3]} + {trio[(i+2)%3]} (TRIO)"
                        
                        # Pair remaining
                        while len(pool) >= 2:
                            s1 = pool.pop()
                            # Find a non-repeating partner if possible
                            partner_idx = 0
                            while partner_idx < len(pool):
                                s2 = pool[partner_idx]
                                pair_key = tuple(sorted([s1, s2]))
                                if pair_key not in past_pairs:
                                    break
                                partner_idx += 1
                            
                            # Fallback if math forces a repeat on late days
                            if partner_idx == len(pool):
                                s2 = pool.pop(0)
                            else:
                                s2 = pool.pop(partner_idx)

                            past_pairs.add(tuple(sorted([s1, s2])))
                            rotation_record[s1][day] = s2
                            rotation_record[s2][day] = s1

                    # Display Matrix
                    df_rotation = pd.DataFrame.from_dict(rotation_record, orient="index", columns=days)
                    df_rotation.index.name = "Student"
                    st.dataframe(df_rotation, use_container_width=True)

                    # Download Authoritative Card
                    csv = df_rotation.to_csv().encode('utf-8')
                    st.download_button(
                        label="📥 Download Student Rotation Cards (CSV/Excel)",
                        data=csv,
                        file_name=f"{active_class['name']}_Rotation_Cards.csv",
                        mime="text/csv"
                    )

        # ==========================================
        # TAB 2: TRUE FOLDER & SUBFOLDER LIBRARY
        # ==========================================
        with tabs[1]:
            st.markdown("#### Subfolder Structure (By Course Module / Days)")
            st.write("Each module acts as a subfolder. Upload documents directly inside the designated module.")

            # Add / Remove Modules dynamically
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                new_mod_name = st.text_input("New Subfolder Name", placeholder="e.g. Module 4 (Day 7-8)", label_visibility="collapsed")
            with c2:
                if st.button("➕ Add Module Subfolder"):
                    if new_mod_name and new_mod_name not in active_class["modules"]:
                        active_class["modules"].append(new_mod_name)
                        active_class["files"][new_mod_name] = []
                        st.rerun()
            with c3:
                if len(active_class["modules"]) > 1:
                    if st.button("➖ Remove Last Subfolder"):
                        removed = active_class["modules"].pop()
                        active_class["files"].pop(removed, None)
                        st.rerun()

            st.markdown("---")

            # Display Subfolders as isolated UI blocks
            for mod in active_class["modules"]:
                with st.container():
                    st.markdown(f"### 📂 {mod}")
                    
                    # File Uploader specific to this subfolder
                    uploaded = st.file_uploader(
                        f"Upload study material to {mod}", 
                        key=f"up_{active_class['id']}_{mod}",
                        label_visibility="collapsed"
                    )
                    if uploaded:
                        # Add file to specific subfolder memory (including raw bytes for AI)
                        existing_names = [f["name"] for f in active_class["files"][mod]]
                        if uploaded.name not in existing_names:
                            file_bytes = uploaded.getvalue()
                            active_class["files"][mod].append({
                                "name": uploaded.name,
                                "size": f"{round(uploaded.size / 1024, 1)} KB",
                                "bytes": file_bytes
                            })
                            st.rerun()

                    # List files inside this subfolder
                    files = active_class["files"].get(mod, [])
                    if not files:
                        st.caption("No files uploaded to this module yet.")
                    else:
                        for idx, file_info in enumerate(files):
                            fc1, fc2, fc3 = st.columns([3, 1, 1])
                            with fc1:
                                st.markdown(f"📄 **{file_info['name']}** `({file_info['size']})`")
                            with fc2:
                                # Download Simulation
                                st.download_button(
                                    label="Download",
                                    data=b"Sample PDF content for student",
                                    file_name=file_info["name"],
                                    key=f"dl_{mod}_{idx}"
                                )
                            with fc3:
                                if st.button("Delete", key=f"del_{mod}_{idx}"):
                                    active_class["files"][mod].pop(idx)
                                    st.rerun()
                    st.markdown("<hr style='margin: 1rem 0; opacity: 0.2;'>", unsafe_allow_html=True)

        # ==========================================
        # TAB 3: AI ASSISTANT
        # ==========================================
        with tabs[2]:
            st.markdown("#### 🤖 AI-Powered Course Assistant")
            st.write("Use AI to analyze, summarize, quiz, and chat about your uploaded course materials.")

            # --- Collect all files across all modules for this class ---
            all_files = []
            for mod_name in active_class["modules"]:
                for f in active_class["files"].get(mod_name, []):
                    if f.get("bytes"):
                        all_files.append({"module": mod_name, "name": f["name"], "bytes": f["bytes"]})

            if not all_files:
                st.info("📂 No files with content found. Upload documents in the **Class Material Library** tab first.")
            else:
                # File selector
                file_labels = [f"{f['module']} / {f['name']}" for f in all_files]
                selected_file_label = st.selectbox("Select a document to work with", file_labels, key="ai_file_select")
                selected_file = all_files[file_labels.index(selected_file_label)]

                # Extract text once
                extracted_text_key = f"extracted_{selected_file['module']}_{selected_file['name']}"
                if extracted_text_key not in st.session_state:
                    st.session_state[extracted_text_key] = extract_text_from_bytes(
                        selected_file["bytes"], selected_file["name"]
                    )
                doc_text = st.session_state[extracted_text_key]

                # Show extraction preview
                with st.expander("📄 Extracted Text Preview", expanded=False):
                    st.text(doc_text[:2000] + ("\n\n... (truncated)" if len(doc_text) > 2000 else ""))

                # AI Sub-tabs
                ai_tabs = st.tabs(["📝 Summarizer", "🧠 Quiz Generator", "💬 Study Chat", "📋 Material Reviewer"])

                # ----- SUMMARIZER -----
                with ai_tabs[0]:
                    st.markdown("##### Summarize this document")
                    st.caption("Get a TL;DR, key concepts, and important details.")
                    if st.button("✨ Generate Summary", key="btn_summarize", type="primary"):
                        with st.spinner("AI is reading and summarizing..."):
                            summary = summarize_document(doc_text)
                            st.session_state["ai_summary"] = summary
                    if "ai_summary" in st.session_state:
                        st.markdown(st.session_state["ai_summary"])

                # ----- QUIZ GENERATOR -----
                with ai_tabs[1]:
                    st.markdown("##### Generate practice questions")
                    st.caption("Create a quiz from the document content.")
                    num_q = st.slider("Number of questions", min_value=3, max_value=10, value=5, key="quiz_num_q")
                    if st.button("🧠 Generate Quiz", key="btn_quiz", type="primary"):
                        with st.spinner("AI is generating questions..."):
                            quiz = generate_quiz(doc_text, num_q)
                            st.session_state["ai_quiz"] = quiz
                    if "ai_quiz" in st.session_state:
                        st.markdown(st.session_state["ai_quiz"])

                # ----- STUDY CHAT -----
                with ai_tabs[2]:
                    st.markdown("##### Chat with this document")
                    st.caption("Ask questions and the AI answers based on the material.")

                    # Initialize chat history
                    if "ai_chat_history" not in st.session_state:
                        st.session_state["ai_chat_history"] = []

                    # Display chat history
                    for msg in st.session_state["ai_chat_history"]:
                        with st.chat_message(msg["role"]):
                            st.markdown(msg["content"])

                    # Chat input
                    user_question = st.chat_input("Ask a question about the document...", key="ai_chat_input")
                    if user_question:
                        # Add user message
                        st.session_state["ai_chat_history"].append({"role": "user", "content": user_question})
                        with st.chat_message("user"):
                            st.markdown(user_question)

                        # Get AI response
                        with st.chat_message("assistant"):
                            with st.spinner("Thinking..."):
                                ai_response = chat_with_material(
                                    doc_text, user_question, st.session_state["ai_chat_history"][:-1]
                                )
                                st.markdown(ai_response)
                        st.session_state["ai_chat_history"].append({"role": "assistant", "content": ai_response})

                    # Clear chat button
                    if st.session_state["ai_chat_history"]:
                        if st.button("🗑️ Clear Chat", key="btn_clear_chat"):
                            st.session_state["ai_chat_history"] = []
                            st.rerun()

                # ----- MATERIAL REVIEWER -----
                with ai_tabs[3]:
                    st.markdown("##### Get AI feedback on this material")
                    st.caption("Professor-facing review: clarity, completeness, difficulty, and suggestions.")
                    if st.button("📋 Review Material", key="btn_review", type="primary"):
                        with st.spinner("AI is reviewing the material..."):
                            review = review_material(doc_text)
                            st.session_state["ai_review"] = review
                    if "ai_review" in st.session_state:
                        st.markdown(st.session_state["ai_review"])