"""
core/ai_helper.py
Handles all OpenRouter AI API calls.
"""
import streamlit as st
from openai import OpenAI

def get_ai_client():
    """Initializes the OpenRouter client using Streamlit secrets."""
    # This securely pulls the key from your .streamlit/secrets.toml file
    api_key = st.secrets.get("OPENROUTER_API_KEY")
    if not api_key:
        return None
    
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

def generate_team_icebreaker():
    """Generates a 5-minute technical icebreaker for the daily teams."""
    client = get_ai_client()
    if not client:
        return "⚠️ Error: OpenRouter API key not found in secrets."

    prompt = (
        "You are an AI teaching assistant. Generate a single, highly engaging, "
        "5-minute technical discussion question or icebreaker related to Artificial Intelligence. "
        "It should be suitable for a small team of students starting their lab work. "
        "Keep it strictly under 3 sentences."
    )

    try:
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash", # Fast and reliable model on OpenRouter
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"