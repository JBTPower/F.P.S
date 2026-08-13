import streamlit as st

st.set_page_config(
    page_title="Documentation | Summer Spires Under Prague",
    page_icon="📖",
    layout="wide",
)

st.page_link("F.P.S_app.py", label="Back to Main Dashboard", icon="⬅️")
st.title("📖 Documentation & Guide")
st.markdown("---")

st.markdown("""
### Welcome to Summer Spires Under Prague
This dashboard was created to facilitate the **Prague European Summer School**. It serves as an integrated workspace combining class material management, team building, and artificial intelligence integration.

#### 1. 👥 Team Rotation Builder
- **Purpose**: Creates non-repeating lab partner pairings for students across multiple days of the summer school.
- **How it works**: Uses a round-robin algorithmic rotation. If the class size is an odd number, it intelligently groups the last three students into a Trio so nobody is left alone.
- **Features**: Generates AI Icebreakers tailored to the students' specific team composition.

#### 2. 📁 Class Material Library
- **Purpose**: A digital repository for all course documents (PDFs, Word Docs).
- **How it works**: You can organize files into virtual folders (Modules). Documents uploaded here are parsed in memory and made available for the AI Assistant.

#### 3. 🤖 AI Assistant
- **Purpose**: A powerful suite of AI tools powered by OpenRouter.
- **Summarizer**: Extracts key concepts and provides a TL;DR of selected documents.
- **Flashcards**: Generates interactive study flashcards. Click to flip them and track your learning!
- **Study Chat**: A conversational agent that can answer deep questions based strictly on the uploaded course material.
- **Material Reviewer**: Acts as a peer-reviewer for professors, providing feedback on the clarity, difficulty, and structure of the syllabus or assignment.

#### 4. 🎮 Bonus: Coffee Catcher
- Need a break? Head over to the Map & Info section to play a retro-style mini-game. Catch the coffee cup with your green character without hitting the walls!

---
**Technical Note**: The application operates in-memory. If you wish to save your class configurations permanently, you can export them to a database in future updates. Currently, refreshing the browser (or logging out) will wipe temporary document uploads.
""")
st.page_link("F.P.S_app.py", label="Back to Main Dashboard", icon="⬅️")
