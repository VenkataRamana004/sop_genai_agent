import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from pypdf import PdfReader

# --------------------------------------------------
# Load API key
# --------------------------------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --------------------------------------------------
# SYSTEM PROMPT (STRICT & SAFE)
# --------------------------------------------------
SYSTEM_PROMPT = """
You are a Manufacturing Plant SOP & Safety Explainer Assistant.

PRIMARY PURPOSE:
Your ONLY purpose is to explain manufacturing Standard Operating Procedures (SOPs),
industrial safety rules, and workplace safety concepts in simple, easy-to-understand language.

SCOPE (YOU MAY ANSWER ONLY THESE):
- Manufacturing SOP explanations
- Machine safety concepts (high-level only)
- PPE (Personal Protective Equipment) explanations
- Emergency procedures (general awareness only)
- Safety rules, warnings, and best practices
- Step-by-step explanation of SOPs (EXPLANATION ONLY)

STRICT LIMITATIONS:
- Do NOT approve, authorize, validate, or permit any action.
- Do NOT give operational instructions that replace supervisors.
- Do NOT give legal, medical, or compliance judgments.
- Do NOT provide troubleshooting or optimization advice.
- Do NOT answer questions outside manufacturing SOPs or safety.

IRRELEVANT QUESTION HANDLING:
Politely refuse and redirect to SOP or safety-related questions.

MANDATORY DISCLAIMER:
Always include:
"This explanation is for awareness and training purposes only.
Always follow official SOPs and supervisor instructions."
"""

# --------------------------------------------------
# MODEL (STABLE & FREE-TIER SAFE)
# --------------------------------------------------
model = genai.GenerativeModel(
    model_name="gemini-pro",
    system_instruction=SYSTEM_PROMPT
)

# --------------------------------------------------
# STREAMLIT UI
# --------------------------------------------------
st.set_page_config(page_title="Manufacturing SOP Explainer", layout="centered")

st.title("🏭 Manufacturing SOP & Safety Explainer Bot")
st.warning(
    "⚠️ This AI explains SOPs for awareness only. "
    "Always follow supervisor instructions."
)

# --------------------------------------------------
# ALLOWED KEYWORDS (FOR STRICT FILTERING)
# --------------------------------------------------
ALLOWED_KEYWORDS = [
    "sop", "safety", "procedure", "manufacturing", "machine",
    "ppe", "lockout", "tagout", "emergency", "hazard",
    "equipment", "process", "workplace"
]

def is_relevant_question(question: str) -> bool:
    q = question.lower()
    return any(keyword in q for keyword in ALLOWED_KEYWORDS)

def is_sop_document(text: str) -> bool:
    t = text.lower()
    sop_indicators = ["sop", "procedure", "safety", "equipment", "process"]
    return any(word in t for word in sop_indicators)

# --------------------------------------------------
# SOP PDF UPLOAD
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload SOP PDF (optional)",
    type=["pdf"]
)

sop_text = ""

if uploaded_file:
    reader = PdfReader(uploaded_file)
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            sop_text += extracted

    if not is_sop_document(sop_text):
        st.error(
            "❌ The uploaded PDF does not appear to be a manufacturing SOP or safety document.\n\n"
            "Please upload a valid SOP or safety-related PDF."
        )
        sop_text = ""

# --------------------------------------------------
# USER QUESTION
# --------------------------------------------------
question = st.text_input("Ask a question about SOP or safety:")

# --------------------------------------------------
# BUTTON ACTION
# --------------------------------------------------
if st.button("Explain"):
    if not question:
        st.error("Please enter a question.")

    elif not is_relevant_question(question):
        st.warning(
            "❌ This assistant only explains manufacturing SOPs and safety procedures.\n\n"
            "Please ask a relevant SOP or safety-related question."
        )

    else:
        prompt = f"""
SOP Content (if any):
{sop_text[:3000]}

User Question:
{question}
"""

        try:
            response = model.generate_content(prompt)
            st.success(response.text)

        except Exception:
            st.error(
                "⚠️ Unable to generate response due to free-tier limits or model availability.\n"
                "Please try again later."
            )
