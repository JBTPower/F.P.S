"""
Summer Spires Under Prague
Includes:
- Crash-free Class Management
- True Folder/Subfolder Module Library (with Add/Remove Modules)
- Authoritative Capstone + Non-Repeating Pair/Trio Rotation Engine
- AI Assistant (Summarizer, Quiz, Chat, Material Review)
"""

import streamlit as st
import streamlit.components.v1 as components
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
    generate_flashcards,
)
# --- PAGE CONFIG & MODERN CSS ---
st.set_page_config(
    page_title="Summer Spires Under Prague",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown(
    """
    <style>
    footer {visibility: hidden;}
    [data-testid="stSidebarNav"] { display: none !important; }
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
                    "Module 1": [],
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

# --- TOP BANNER: ESS Logo (reduced size, centered) ---
logo_path = Path("assets/PESS logo.png")
if logo_path.exists():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image(str(logo_path), use_container_width=True)

st.markdown("---")

# --- AUTHENTICATION ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    # --- FULLSCREEN VIDEO BACKGROUND ---
    import base64
    starter_video_path = Path("assets/starter_video.mp4")
    if starter_video_path.exists():
        with open(starter_video_path, "rb") as f:
            video_base64 = base64.b64encode(f.read()).decode()
            
        st.markdown(f'''
        <style>
            .stApp {{
                background-color: transparent !important;
            }}
            .stAppHeader {{
                background-color: transparent !important;
            }}
        </style>
        <video autoplay loop muted playsinline id="bg-video" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: -999;
            object-fit: cover;
            opacity: 0.7;
        ">
          <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        </video>
        ''', unsafe_allow_html=True)

    # --- GLASMORPHISM LOGIN FORM ---
    st.markdown("""
        <style>
            div[data-testid="stForm"] {
                background: rgba(255, 255, 255, 0.85);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                border: 1px solid rgba(255, 255, 255, 0.5);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #111827; margin-bottom: 20px; font-weight: 700;'>🔒 Portal Login</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                if username == "student1" and password == "PESS26":
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    st.stop()

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

    st.markdown("---")
    # --- STARTER VIDEO EXPANDER (LOGGED IN) ---
    starter_video_path = Path("assets/starter_video.mp4")
    if starter_video_path.exists():
        with st.expander("🎬 Watch Starter Video", expanded=False):
            st.video(str(starter_video_path), autoplay=False, loop=False, muted=False)
            st.caption("Introduction to F.P.S and Summer Spires Under Prague.")

    # --- PRAGUE VIDEOS (LOGGED IN) ---
    anthem_path = Path("assets/Summer_Under_Prague_Spires.mp4")
    if anthem_path.exists():
        with st.expander("🎵 Summer Under Prague Spires", expanded=False):
            st.video(str(anthem_path), autoplay=False, loop=False, muted=False)
            
    prague_video_path = Path("assets/prague spires transformation.mp4")
    if prague_video_path.exists():
        with st.expander("🎬 Prague Transformation", expanded=False):
            st.video(str(prague_video_path), autoplay=False, loop=False, muted=False)
            
    st.markdown("---")
    # --- LOGOUT BUTTON ---
    st.markdown("""
        <span id="logout-button-hook"></span>
        <style>
        /* Target the element container exactly following the hook */
        div.element-container:has(#logout-button-hook) + div.element-container button {
            background-color: #E53935 !important;
            color: white !important;
            border-color: #E53935 !important;
        }
        div.element-container:has(#logout-button-hook) + div.element-container button:hover {
            background-color: #D32F2F !important;
            border-color: #D32F2F !important;
        }
        </style>
    """, unsafe_allow_html=True)
    if st.button("Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.rerun()

# --- MAIN WORKSPACE ---
with main_col:

    # --- TITLE (full width) ---
    st.markdown(
        """
        <div style="padding-bottom: 0.5rem;">
            <h1 style="color: #212529; font-size: 2.2rem; font-weight: 800; margin-bottom: 0;">Summer Spires Under Prague</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )

    st.markdown("---")


    if not active_class:

        st.warning("Please create or select a class from the left menu.")
    else:
        st.markdown(f"### 📍 Workspace: **{active_class['name']}**")
        
        tabs = st.tabs(["👥 Team Rotation Builder", "📁 Class Material Library (Subfolders)", "🤖 AI Assistant"])

        # ==========================================
        # TAB 1: TEAM & ROTATION BUILDER
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

                    # Step 2: Non-Repeating Pair/Trio Generator (Days 2 to 8)
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

            # Add Module
            c1, c2 = st.columns([3, 1])
            with c1:
                new_mod_name = st.text_input("New Subfolder Name", placeholder="e.g. Module 4 (Day 7-8)", label_visibility="collapsed")
            with c2:
                if st.button("➕ Add Module Subfolder", use_container_width=True):
                    if new_mod_name and new_mod_name not in active_class["modules"]:
                        active_class["modules"].append(new_mod_name)
                        active_class["files"][new_mod_name] = []
                        st.rerun()

            st.markdown("---")

            # Initialize lock states
            if "locked_modules" not in st.session_state:
                st.session_state["locked_modules"] = {}

            # Display Subfolders as isolated UI blocks
            for mod in list(active_class["modules"]):
                is_locked = st.session_state["locked_modules"].get(mod, False)

                with st.container():
                    # Header row: folder name | lock toggle | delete
                    mh1, mh2, mh3 = st.columns([4, 1, 1])
                    with mh1:
                        icon = "🔒" if is_locked else "📂"
                        st.markdown(f"### {icon} {mod}")
                    with mh2:
                        lock_label = "🔓 Unlock" if is_locked else "🔒 Lock"
                        if st.button(lock_label, key=f"lock_{mod}", use_container_width=True):
                            st.session_state["locked_modules"][mod] = not is_locked
                            st.rerun()
                    with mh3:
                        if not is_locked:
                            if st.button("🗑️ Delete", key=f"del_mod_{mod}", use_container_width=True, type="primary"):
                                active_class["modules"].remove(mod)
                                active_class["files"].pop(mod, None)
                                st.session_state["locked_modules"].pop(mod, None)
                                st.rerun()
                        else:
                            st.caption("🔒 Locked")

                    if is_locked:
                        st.caption("This module is locked. Unlock it to upload or delete files.")
                    else:
                        # File Uploader specific to this subfolder
                        uploaded = st.file_uploader(
                            f"Upload study material to {mod}", 
                            key=f"up_{active_class['id']}_{mod}",
                            label_visibility="collapsed"
                        )
                        if uploaded:
                            existing_names = [f["name"] for f in active_class["files"][mod]]
                            if uploaded.name not in existing_names:
                                file_bytes = uploaded.getvalue()
                                active_class["files"][mod].append({
                                    "name": uploaded.name,
                                    "size": f"{round(uploaded.size / 1024, 1)} KB",
                                    "bytes": file_bytes
                                })
                                st.rerun()

                    # List files inside this subfolder (always visible)
                    files = active_class["files"].get(mod, [])
                    if not files:
                        st.caption("No files uploaded to this module yet.")
                    else:
                        for idx, file_info in enumerate(files):
                            fc1, fc2, fc3 = st.columns([3, 1, 1])
                            with fc1:
                                st.markdown(f"📄 **{file_info['name']}** `({file_info['size']})`")
                            with fc2:
                                st.download_button(
                                    label="⬇️ Download",
                                    data=file_info.get("bytes", b""),
                                    file_name=file_info["name"],
                                    key=f"dl_{mod}_{idx}"
                                )
                            with fc3:
                                if not is_locked:
                                    if st.button("🗑️", key=f"del_file_{mod}_{idx}", help="Delete file"):
                                        active_class["files"][mod].pop(idx)
                                        st.rerun()
                                else:
                                    st.caption("🔒")

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

            # --- Module + File selector (multi-select) ---
            modules_with_files = {
                mod: [f for f in active_class["files"].get(mod, []) if f.get("bytes")]
                for mod in active_class["modules"]
            }
            modules_with_files = {m: files for m, files in modules_with_files.items() if files}

            if not modules_with_files:
                st.info("📂 No files with content found. Upload documents in the **Class Material Library** tab first.")
            else:
                # Step 1: Pick one or more modules
                selected_modules = st.multiselect(
                    "📂 Select module(s)",
                    list(modules_with_files.keys()),
                    default=[list(modules_with_files.keys())[0]] if modules_with_files else [],
                    key="ai_module_select"
                )

                if not selected_modules:
                    st.warning("Please select at least one module.")
                else:
                    # Step 2: Pick one or more files across those modules
                    available_files = []
                    for mod in selected_modules:
                        for f in modules_with_files[mod]:
                            available_files.append((mod, f))
                            
                    file_options = [f"[{mod}] {f['name']}" for mod, f in available_files]
                    
                    selected_file_options = st.multiselect(
                        "📄 Select document(s) to work with",
                        file_options,
                        default=file_options if file_options else [],
                        key="ai_file_multiselect"
                    )
    
                    if not selected_file_options:
                        st.warning("Please select at least one file to continue.")
                    else:
                        # Combine text from all selected files
                        combined_text_parts = []
                        for option in selected_file_options:
                            idx = file_options.index(option)
                            mod, file_obj = available_files[idx]
                            fname = file_obj["name"]
                            
                            cache_key = f"extracted_{mod}_{fname}"
                            if cache_key not in st.session_state:
                                st.session_state[cache_key] = extract_text_from_bytes(file_obj["bytes"], fname)
                            combined_text_parts.append(f"--- [{mod}] {fname} ---\\n{st.session_state[cache_key]}")
    
                        doc_text = "\\n\\n".join(combined_text_parts)

                    if len(selected_file_options) > 1:
                        st.success(f"✅ {len(selected_file_options)} files combined for AI analysis.")

                    # Show extraction preview
                    with st.expander("📄 Extracted Text Preview", expanded=False):
                        st.text(doc_text[:2000] + ("\n\n... (truncated)" if len(doc_text) > 2000 else ""))



                    # AI Sub-tabs
                    ai_tabs = st.tabs(["📝 Summarizer", "🧠 Quiz Generator", "🗂️ Flashcards", "💬 Study Chat", "📋 Material Reviewer"])

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

                    # ----- FLASHCARDS -----
                    with ai_tabs[2]:
                        st.markdown("##### 🗂️ Interactive Flashcards")
                        st.caption("Generate a flashcard deck to study actively.")
                        
                        num_q = st.slider("Number of cards", min_value=3, max_value=15, value=5, key="fc_num_q")
                        
                        if st.button("🧠 Generate Deck", key="btn_flashcards", type="primary"):
                            with st.spinner("AI is analyzing and creating flashcards..."):
                                cards = generate_flashcards(doc_text, num_q)
                                st.session_state["flashcards"] = cards
                                st.session_state["fc_index"] = 0
                                st.session_state["fc_flipped"] = False
                                
                        if "flashcards" in st.session_state and st.session_state["flashcards"]:
                            cards = st.session_state["flashcards"]
                            idx = st.session_state.get("fc_index", 0)
                            
                            if idx >= len(cards):
                                st.success("🎉 You've finished the deck!")
                                if st.button("Restart Deck", key="btn_restart_deck"):
                                    st.session_state["fc_index"] = 0
                                    st.session_state["fc_flipped"] = False
                                    st.rerun()
                            else:
                                card = cards[idx]
                                st.progress(idx / len(cards), text=f"Card {idx+1} of {len(cards)}")
                                
                                q_text = card.get('q', 'Error')
                                a_text = card.get('a', 'Error')
                                
                                if not st.session_state.get("fc_flipped", False):
                                    # Front of card (Question)
                                    st.markdown(f"""
                                    <div style="background: linear-gradient(135deg, #ffffff, #f9fafb); border: 2px solid #e5e7eb; border-radius: 12px; padding: 40px 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; margin-bottom: 20px; min-height: 200px; display: flex; flex-direction: column; justify-content: center;">
                                        <p style="color: #6b7280; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; margin-top: 0;">Question</p>
                                        <h3 style="color: #111827; margin: 0; font-weight: 600;">{q_text}</h3>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if st.button("🔄 Flip Card", use_container_width=True, key="btn_flip_card"):
                                        st.session_state["fc_flipped"] = True
                                        st.rerun()
                                else:
                                    # Back of card (Answer)
                                    st.markdown(f"""
                                    <div style="background: linear-gradient(135deg, #f0fdf4, #dcfce7); border: 2px solid #bbf7d0; border-radius: 12px; padding: 40px 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; margin-bottom: 20px; min-height: 200px; display: flex; flex-direction: column; justify-content: center;">
                                        <p style="color: #166534; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; margin-top: 0;">Answer</p>
                                        <h4 style="color: #14532d; margin: 0; font-weight: 500;">{a_text}</h4>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    col1, col2 = st.columns(2)
                                    if col1.button("✅ Got it!", use_container_width=True, type="primary", key="btn_got_it"):
                                        st.session_state["fc_index"] += 1
                                        st.session_state["fc_flipped"] = False
                                        if st.session_state["fc_index"] >= len(cards):
                                            st.balloons()
                                        st.rerun()
                                        
                                    if col2.button("❌ Need Review", use_container_width=True, key="btn_review_card"):
                                        cards.append(card)
                                        st.session_state["fc_index"] += 1
                                        st.session_state["fc_flipped"] = False
                                        st.rerun()

                    # ----- STUDY CHAT -----
                    with ai_tabs[3]:
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
                    with ai_tabs[4]:
                        st.markdown("##### Get AI feedback on this material")
                        st.caption("Professor-facing review: clarity, completeness, difficulty, and suggestions.")
                        if st.button("📋 Review Material", key="btn_review", type="primary"):
                            with st.spinner("AI is reviewing the material..."):
                                review = review_material(doc_text)
                                st.session_state["ai_review"] = review
                        if "ai_review" in st.session_state:
                            st.markdown(st.session_state["ai_review"])

# --- FOOTER / STUDENT HUB ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("## 🎒 Summer School Hub & Explore")

footer_col1, footer_col2, footer_col3 = st.columns([1.5, 1.5, 2])

with footer_col1:
    st.markdown("### 🏫 European Summer School")
    st.markdown("""
    **Address:**<br>
    Opletalova 23<br>
    110 00 Prague, Czechia<br><br>
    **Contact:**<br>
    📧 info@europeansummerschool.com<br>
    📞 +420 776 367 740<br>
    🌐 [europeansummerschool.com](https://europeansummerschool.com/)
    """, unsafe_allow_html=True)
    st.markdown('<div style="height: 38px;"></div>', unsafe_allow_html=True)
    st.markdown("### 🛏️ Accommodation: Botič Student House")
    st.markdown("K Botiči 1439, 101 00 Praha 10-Vršovice", unsafe_allow_html=True)
    components.html(
        '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2561.123!2d14.453!3d50.065!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x470b938c4b752945%3A0x89fc32549216bd98!2zSyBCb3RpxI1pIDE0MzkvNSwgMTAxIDAwIFByYWhhIDEwLVZyxaFvdmljZSwgQ3plY2hpYQ!5e0!3m2!1sen!2scz!4v1" width="100%" height="200" style="border:0;" allowfullscreen="" loading="lazy"></iframe>',
        height=220
    )

with footer_col2:
    st.markdown("### 🎓 Discover More Courses")
    st.info("""
    **Looking to expand your horizons?** 
    - AI & Machine Learning in Practice
    - Behavioral Economics & Psychology
    - Corporate Finance & Valuation
    - European Politics
    """)
    st.markdown("[🌐 View Full Prague Summer School Catalog](https://www.summerschoolsineurope.eu/destination/european-summer-school-in-prague/)", unsafe_allow_html=True)
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    st.markdown("### 🏛️ Classes: French Institute")
    st.markdown("Štěpánská 644/35, 110 00 Nové Město, Czechia", unsafe_allow_html=True)
    components.html(
        '<iframe src="https://maps.google.com/maps?q=French%20Institute%20in%20Prague,%20%C5%A0t%C4%9Bp%C3%A1nsk%C3%A1%2035,%20Prague&t=&z=15&ie=UTF8&iwloc=&output=embed" width="100%" height="200" style="border:0;" allowfullscreen="" loading="lazy"></iframe>',
        height=220
    )

with footer_col3:
    st.markdown("### 🕹️ Study Break: Retro Snake")
    st.caption("Need a mental break? Click the game board and use your arrow keys to play!")
    components.html("""
    <!DOCTYPE html>
    <html>
    <head><style>
    body {background: transparent; display: flex; flex-direction: column; align-items: center; justify-content: center; margin:0; font-family: sans-serif;}
    canvas {background: #212529; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-top: 5px; outline: none; cursor: pointer;}
    .score {font-size: 16px; font-weight: bold; color: #4361EE; margin-bottom: 5px;}
    </style></head>
    <body>
    <div class="score">Score: <span id="score">0</span></div>
    <canvas id="game" width="300" height="300" tabindex="1"></canvas>
    <script>
    const canvas = document.getElementById('game');
    const context = canvas.getContext('2d');
    const grid = 15;
    let count = 0;
    let score = 0;
    let snake = { x: 150, y: 150, dx: grid, dy: 0, cells: [], maxCells: 4 };
    let apple = { x: 105, y: 105 };
    let isPlaying = false;
    
    function getRandomInt(min, max) { return Math.floor(Math.random() * (max - min)) + min; }
    
    function loop() {
        requestAnimationFrame(loop);
        
        if (!isPlaying) {
            context.fillStyle = 'rgba(0, 0, 0, 0.1)'; // Slight darkening
            context.fillRect(0, 0, canvas.width, canvas.height);
            context.fillStyle = 'white';
            context.font = '20px sans-serif';
            context.textAlign = 'center';
            context.fillText('Click to Play / Resume', canvas.width / 2, canvas.height / 2);
            return;
        }
        
        if (++count < 6) return;
        count = 0;
        context.clearRect(0,0,canvas.width,canvas.height);
        
        snake.x += snake.dx;
        snake.y += snake.dy;
        
        if (snake.x < 0) snake.x = canvas.width - grid;
        else if (snake.x >= canvas.width) snake.x = 0;
        if (snake.y < 0) snake.y = canvas.height - grid;
        else if (snake.y >= canvas.height) snake.y = 0;
        
        snake.cells.unshift({x: snake.x, y: snake.y});
        if (snake.cells.length > snake.maxCells) snake.cells.pop();
        
        context.font = (grid) + "px sans-serif";
        context.textBaseline = "top";
        context.fillText('☕', apple.x, apple.y);
        
        context.fillStyle = '#388E3C';
        snake.cells.forEach(function(cell, index) {
            context.fillRect(cell.x, cell.y, grid-1, grid-1);
            if (cell.x === apple.x && cell.y === apple.y) {
                snake.maxCells++;
                score++;
                document.getElementById('score').innerText = score;
                apple.x = getRandomInt(0, 20) * grid;
                apple.y = getRandomInt(0, 20) * grid;
            }
            for (let i = index + 1; i < snake.cells.length; i++) {
                if (cell.x === snake.cells[i].x && cell.y === snake.cells[i].y) {
                    snake.x = 150; snake.y = 150; snake.cells = []; snake.maxCells = 4;
                    snake.dx = grid; snake.dy = 0; score = 0; document.getElementById('score').innerText = score;
                }
            }
        });
    }
    
    canvas.addEventListener('keydown', function(e) {
        if([37, 38, 39, 40].indexOf(e.keyCode) > -1) {
            e.preventDefault();
        }
        if (e.which === 37 && snake.dx === 0) { snake.dx = -grid; snake.dy = 0; }
        else if (e.which === 38 && snake.dy === 0) { snake.dy = -grid; snake.dx = 0; }
        else if (e.which === 39 && snake.dx === 0) { snake.dx = grid; snake.dy = 0; }
        else if (e.which === 40 && snake.dy === 0) { snake.dy = grid; snake.dx = 0; }
    });
    
    canvas.addEventListener('click', () => canvas.focus());
    canvas.addEventListener('focus', () => { isPlaying = true; });
    canvas.addEventListener('blur', () => { isPlaying = false; });
    
    // Initial draw before loop takes over
    context.fillStyle = 'white';
    context.font = '20px sans-serif';
    context.textAlign = 'center';
    context.fillText('Click to Play', canvas.width / 2, canvas.height / 2);
    
    requestAnimationFrame(loop);
    </script>
    </body>
    </html>
    """, height=360)

# --- SIDEBAR (AI & API OVERVIEW) ---
with st.sidebar:
    # 1. Student Profile
    user_name = st.session_state.get("username", "Student").capitalize()
    st.markdown(f"## 👋 Welcome, {user_name}!")
    st.markdown("*European Summer School Prague*")
    
    # 2. Gamification / Study Streak
    st.markdown("### 🔥 Study Streak")
    st.progress(75, text="3 Days Active (Goal: 4 Days)")
    
    st.markdown("---")
    
    # 3. AI Dashboard
    st.markdown("### 🤖 AI Dashboard")
    st.caption("Monitor your OpenRouter API usage here.")
    
    api_key = st.secrets.get("OPENROUTER_API_KEY")
    if api_key:
        st.success("✅ **Status:** Connected")
        st.caption(f"**Key:** `...{api_key[-4:] if len(api_key)>4 else '****'}`")
    else:
        st.error("❌ **Status:** Disconnected")
        st.caption("No `OPENROUTER_API_KEY` found in `.streamlit/secrets.toml`.")
        
    model = st.secrets.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")
    st.info(f"🧠 **Model:** `{model}`")
    
    st.markdown("---")
    st.markdown("### 📊 Session Usage")
    
    # Reading these at the very end of the file ensures they capture any increments
    # made by button clicks earlier in this exact rerun!
    requests = st.session_state.get("ai_requests", 0)
    tokens = st.session_state.get("ai_tokens", 0)
    
    mc1, mc2 = st.columns(2)
    mc1.metric("Requests", requests)
    mc2.metric("Tokens", f"{tokens:,}") 

    st.markdown("---")