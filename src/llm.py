import os
from typing import Optional, Dict
import httpx
from google import genai
from .config import (
    LLM_PROVIDER,
    GEMINI_API_KEY, 
    GEMINI_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL
)

_client = None

def render_model_selector():
    import streamlit as st
    st.subheader("⚙️ Active AI Model")
    provider = st.selectbox(
        "Model Provider",
        ["gemini", "ollama"],
        index=0 if st.session_state.get("llm_provider", "gemini") == "gemini" else 1
    )
    st.session_state.llm_provider = provider
    os.environ["LLM_PROVIDER"] = provider
    st.caption("🤖 `llama3.1` (Local)" if provider == "ollama" else "✨ `gemini-2.5-flash` (Cloud)")
    st.divider()

def get_gemini_client() -> Optional[genai.Client]:
    global _client
    api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
    if not api_key:
        return None
    if _client is None:
        _client = genai.Client(api_key=api_key)
    return _client

def call_llm(prompt: str, provider: Optional[str] = None) -> str:
    """
    Unified LLM call supporting Gemini and local Ollama (e.g. Llama 3.1).
    """
    selected_provider = provider or os.getenv("LLM_PROVIDER", LLM_PROVIDER)
    
    if selected_provider == "ollama":
        url = f"{os.getenv('OLLAMA_BASE_URL', OLLAMA_BASE_URL).rstrip('/')}/api/generate"
        model = os.getenv("OLLAMA_MODEL", OLLAMA_MODEL)
        try:
            with httpx.Client(timeout=60.0) as client:
                res = client.post(url, json={"model": model, "prompt": prompt, "stream": False})
                if res.status_code == 200:
                    return res.json().get("response", "").strip()
                return f"Ollama error ({res.status_code}): {res.text}"
        except Exception as e:
            return f"Failed to connect to Ollama at {url}. Make sure Ollama is running (`ollama run {model}`). Error: {str(e)}"
    
    # Default: Gemini
    client = get_gemini_client()
    if not client:
        return (
            "⚠️ Gemini API key is missing. Please set `GEMINI_API_KEY` in `.env` or switch `LLM_PROVIDER=ollama` for local Llama 3.1."
        )
    try:
        model = os.getenv("GEMINI_MODEL", GEMINI_MODEL)
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error communicating with Gemini: {str(e)}"

def generate_grounded_answer(question: str, context: str, provider: Optional[str] = None) -> str:
    """
    Generates an answer strictly grounded in the retrieved context.
    """
    system_instruction = (
        "You are an expert customer support AI assistant.\n"
        "Your task is to answer the customer's question strictly based on the provided support context.\n"
        "Rules:\n"
        "1. Answer concisely and accurately using ONLY facts directly mentioned in the Context.\n"
        "2. If the context does not contain enough clear information to answer, state:\n"
        "'I couldn't find enough information in the available support documentation to answer this reliably. Would you like to contact a support agent?'\n"
        "3. Do not invent policies, prices, steps, or features not in the context.\n"
    )

    prompt = f"""{system_instruction}

CONTEXT:
{context}

CUSTOMER QUESTION:
{question}

ANSWER:"""

    return call_llm(prompt, provider=provider)

def analyze_ticket_question(question: str, context: str = "", provider: Optional[str] = None) -> Dict[str, str]:
    """
    Classifies a ticket into a category and generates AI analysis and suggested response.
    """
    prompt = f"""You are a customer support triage assistant. Analyze this customer issue.

Customer Message: {question}
Available Context: {context if context else 'No relevant documentation found.'}

Provide your analysis in the exact format:
CATEGORY: [one of Technical, Billing, Account, Product, Installation, Bug, Other]
PRIORITY: [one of Low, Normal, High, Urgent]
ANALYSIS: [1-2 sentences summarizing the core issue]
SUGGESTED_RESPONSE: [Professional draft response to the customer]
"""
    try:
        text = call_llm(prompt, provider=provider)
        lines = text.split("\n")
        res = {
            "category": "General",
            "priority": "Normal",
            "analysis": text,
            "suggested_response": "Hello, thank you for reaching out. We are investigating your issue."
        }
        for line in lines:
            if line.startswith("CATEGORY:"):
                res["category"] = line.replace("CATEGORY:", "").strip()
            elif line.startswith("PRIORITY:"):
                res["priority"] = line.replace("PRIORITY:", "").strip()
            elif line.startswith("ANALYSIS:"):
                res["analysis"] = line.replace("ANALYSIS:", "").strip()
            elif line.startswith("SUGGESTED_RESPONSE:"):
                res["suggested_response"] = line.replace("SUGGESTED_RESPONSE:", "").strip()
        return res
    except Exception:
        return {
            "category": "General",
            "priority": "Normal",
            "analysis": "Direct customer escalation.",
            "suggested_response": "Thank you for your inquiry. A support specialist is reviewing your request."
        }
