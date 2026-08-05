"""
core/ai_helper.py
Handles all OpenRouter AI API calls for F.P.S.
Includes: Icebreaker, Document Summarizer, Quiz Generator, Study Chat, Material Reviewer.
"""
import io
import streamlit as st
from openai import OpenAI


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

def get_ai_client():
    """Initializes the OpenRouter client using Streamlit secrets."""
    api_key = st.secrets.get("OPENROUTER_API_KEY")
    if not api_key:
        return None

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


def get_ai_model() -> str:
    """Gets the OpenRouter model from Streamlit secrets, defaulting to google/gemini-2.5-flash."""
    return st.secrets.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")


def _call_ai(system_prompt: str, user_prompt: str) -> str:
    """Generic helper — sends a system + user message and returns the response text."""
    client = get_ai_client()
    if not client:
        return "⚠️ Error: OpenRouter API key not found. Add it to `.streamlit/secrets.toml`."

    try:
        response = client.chat.completions.create(
            model=get_ai_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"


def _call_ai_chat(messages: list) -> str:
    """Chat-style helper — sends a full message history and returns the response text."""
    client = get_ai_client()
    if not client:
        return "⚠️ Error: OpenRouter API key not found. Add it to `.streamlit/secrets.toml`."

    try:
        response = client.chat.completions.create(
            model=get_ai_model(),
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"


# ---------------------------------------------------------------------------
# Text Extraction
# ---------------------------------------------------------------------------

def extract_text_from_bytes(file_bytes: bytes, file_name: str) -> str:
    """Extracts plain text from uploaded file bytes based on file extension."""
    name_lower = file_name.lower()

    if name_lower.endswith(".txt") or name_lower.endswith(".md"):
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return file_bytes.decode("latin-1", errors="ignore")

    elif name_lower.endswith(".pdf"):
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            return "\n\n".join(pages) if pages else "(Could not extract text from this PDF.)"
        except Exception as e:
            return f"(PDF extraction error: {e})"

    elif name_lower.endswith(".docx"):
        try:
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs) if paragraphs else "(Could not extract text from this DOCX.)"
        except Exception as e:
            return f"(DOCX extraction error: {e})"

    elif name_lower.endswith((".ppt", ".pptx")):
        return "(PowerPoint text extraction is not supported yet. Please upload a PDF or TXT version.)"

    else:
        try:
            return file_bytes.decode("utf-8")
        except Exception:
            return "(Unsupported file format for text extraction.)"


# ---------------------------------------------------------------------------
# 1. Team Icebreaker (existing)
# ---------------------------------------------------------------------------

def generate_team_icebreaker() -> str:
    """Generates a 5-minute technical icebreaker for the daily teams."""
    return _call_ai(
        system_prompt=(
            "You are an AI teaching assistant for a summer school course on "
            "Applied Artificial Intelligence."
        ),
        user_prompt=(
            "Generate a single, highly engaging, 5-minute technical discussion "
            "question or icebreaker related to Artificial Intelligence. "
            "It should be suitable for a small team of students starting their lab work. "
            "Keep it strictly under 3 sentences."
        ),
    )


# ---------------------------------------------------------------------------
# 2. Document Summarizer
# ---------------------------------------------------------------------------

def summarize_document(text: str) -> str:
    """Summarizes a document into TL;DR, key concepts, and important details."""
    return _call_ai(
        system_prompt=(
            "You are a university teaching assistant. Your job is to summarize "
            "course materials clearly and accurately for students."
        ),
        user_prompt=(
            "Summarize the following course material. Structure your response as:\n\n"
            "## TL;DR\n"
            "(2-3 sentence summary)\n\n"
            "## Key Concepts\n"
            "(Bullet list of the main ideas and concepts)\n\n"
            "## Important Details\n"
            "(What students should remember for exams or practical work)\n\n"
            "---\n\n"
            f"DOCUMENT CONTENT:\n\n{text[:15000]}"
        ),
    )


# ---------------------------------------------------------------------------
# 3. Quiz Generator
# ---------------------------------------------------------------------------

def generate_quiz(text: str, num_questions: int = 5) -> str:
    """Generates quiz questions from course material."""
    return _call_ai(
        system_prompt=(
            "You are a university professor creating a practice quiz for students "
            "based on their course materials. Make questions that test real understanding, "
            "not just memorization."
        ),
        user_prompt=(
            f"Generate exactly {num_questions} practice questions based on the following "
            "course material. Include a mix of:\n\n"
            "- **Multiple Choice** (4 options each, mark the correct one with ✅)\n"
            "- **Open-Ended Discussion** questions\n\n"
            "At the end, include a section:\n\n"
            "## Answer Key\n"
            "(Answers for the multiple choice questions)\n\n"
            "---\n\n"
            f"DOCUMENT CONTENT:\n\n{text[:15000]}"
        ),
    )


# ---------------------------------------------------------------------------
# 4. Study Chat
# ---------------------------------------------------------------------------

def chat_with_material(document_text: str, question: str, chat_history: list) -> str:
    """Answers a student question based on loaded document context + chat history."""
    system_msg = {
        "role": "system",
        "content": (
            "You are a helpful AI study assistant for a university course on Applied "
            "Artificial Intelligence. Answer student questions based ONLY on the course "
            "material provided below. If the answer isn't in the material, say so honestly.\n\n"
            f"COURSE MATERIAL:\n\n{document_text[:12000]}"
        ),
    }

    # Build message list: system + history + new question
    messages = [system_msg]
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    return _call_ai_chat(messages)


# ---------------------------------------------------------------------------
# 5. Material Reviewer (for the professor)
# ---------------------------------------------------------------------------

def review_material(text: str) -> str:
    """Provides professor-facing feedback on uploaded course material."""
    return _call_ai(
        system_prompt=(
            "You are an experienced curriculum reviewer and educational consultant. "
            "Provide constructive, actionable feedback on course materials."
        ),
        user_prompt=(
            "Review the following course material from a professor's perspective. "
            "Provide your assessment in this structure:\n\n"
            "## Clarity Score: X/10\n"
            "(Brief justification)\n\n"
            "## Completeness Assessment\n"
            "(Are there gaps? What's covered well?)\n\n"
            "## Difficulty Level\n"
            "(Beginner / Intermediate / Advanced — and is it appropriate?)\n\n"
            "## Suggestions for Improvement\n"
            "(Concrete, actionable suggestions)\n\n"
            "## Potentially Missing Topics\n"
            "(Topics you'd expect to see but are absent)\n\n"
            "---\n\n"
            f"DOCUMENT CONTENT:\n\n{text[:15000]}"
        ),
    )