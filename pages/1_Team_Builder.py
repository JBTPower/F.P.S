"""
pages/1_Team_Builder.py
Handles complex 15-student rotation and AI Icebreakers.
"""
import streamlit as st
from core.ai_helper import generate_team_icebreaker

def generate_round_robin_schedule(students):
    """
    Generates a 7-day schedule for 15 students where no one repeats a partner.
    Uses the Circle Method. 15 students + 1 'dummy' = 16 slots.
    Whoever pairs with the 'dummy' forms the Trio with the adjacent pair.
    """
    if len(students) != 15:
        return None
    
    # Add a dummy player for the math to work on an odd number
    players = students.copy() + ["DUMMY"]
    num_days = 7
    schedule = []

    for day in range(num_days):
        daily_pairs = []
        trio = []
        
        # Pair up the array ends
        for i in range(8):
            p1 = players[i]
            p2 = players[15 - i]
            
            if p1 == "DUMMY":
                trio_target = p2
            elif p2 == "DUMMY":
                trio_target = p1
            else:
                daily_pairs.append([p1, p2])
                
        # Find who is supposed to be in the trio and merge them with the last pair
        # This guarantees exactly 6 pairs and 1 trio
        if 'trio_target' in locals():
            target = locals()['trio_target']
            last_pair = daily_pairs.pop()
            trio = [last_pair[0], last_pair[1], target]
            
        schedule.append({"day": day + 2, "pairs": daily_pairs, "trio": trio})
        
        # Rotate the array (keep index 0 fixed, rotate the rest)
        players = [players[0]] + [players[-1]] + players[1:-1]
        
    return schedule

def render(storage, class_id):
    st.header("👥 Team Rotation Builder")
    st.write("Generate the mathematically perfect 7-day lab partner schedule.")

    # Input for students
    student_input = st.text_area(
        "Paste 15 student names (one per line):", 
        height=200,
        placeholder="Sarankan\nAlice\nLaurenz\n..."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Generate 7-Day Roster", type="primary"):
            students = [s.strip() for s in student_input.split('\n') if s.strip()]
            
            if len(students) != 15:
                st.error(f"Felipe's logic requires exactly 15 students. You entered {len(students)}.")
            else:
                st.session_state["schedule"] = generate_round_robin_schedule(students)
                st.success("Roster generated perfectly without any repeated pairings!")

    with col2:
        if st.button("🤖 Generate AI Icebreaker"):
            with st.spinner("Asking OpenRouter..."):
                icebreaker = generate_team_icebreaker()
                st.session_state["icebreaker"] = icebreaker

    # Display Icebreaker
    if "icebreaker" in st.session_state:
        st.info(f"**Today's AI Icebreaker for Teams:**\n\n{st.session_state['icebreaker']}")

    # Display Schedule
    if "schedule" in st.session_state and st.session_state["schedule"]:
        st.markdown("---")
        st.subheader("🗓️ The Roster")
        
        # Create tabs for the 7 days
        days = [f"Day {s['day']}" for s in st.session_state["schedule"]]
        day_tabs = st.tabs(days)
        
        for idx, tab in enumerate(day_tabs):
            with tab:
                day_data = st.session_state["schedule"][idx]
                
                st.markdown("##### 🤝 Pairs")
                for i, pair in enumerate(day_data["pairs"]):
                    st.write(f"**Pair {i+1}:** {pair[0]} & {pair[1]}")
                    
                st.markdown("##### ⌨️ Trio (Rotate Keyboard!)")
                trio = day_data["trio"]
                st.write(f"**Trio:** {trio[0]}, {trio[1]}, & {trio[2]}")