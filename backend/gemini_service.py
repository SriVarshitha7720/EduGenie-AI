import os
import ssl
import warnings
warnings.filterwarnings("ignore")
import requests
import urllib3
import google.generativeai as genai
from backend.config import GEMINI_API_KEY

# Disable SSL verification warnings & fix SSL cert verification on Windows/proxy networks
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["PYTHONHTTPSVERIFY"] = "0"

_old_request = requests.Session.request
def _unverified_request(self, method, url, **kwargs):
    kwargs['verify'] = False
    return _old_request(self, method, url, **kwargs)
requests.Session.request = _unverified_request

# Configure Gemini with REST transport
genai.configure(api_key=GEMINI_API_KEY, transport="rest")

# Primary and Fallback Gemini Models
FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-flash-latest"
]


def ask_gemini(question: str):
    """
    Sends a well-engineered educational prompt to Gemini with model fallbacks.
    """

    prompt = f"""
You are EduGenie, an expert AI Educational Assistant.

Instructions:
1. Break down your explanation into clear, well-structured sections using markdown headings (###).
2. Use bullet points (* or -) for lists and key points. NEVER output long continuous paragraphs.
3. Highlight key terms in **bold**.
4. Provide a distinct section with a relatable real-life example or industry usage.
5. If applicable, provide a formatted code snippet or structured table.
6. End with a key takeaway note.

Student Question:
{question}
"""

    last_error = ""

    for model_name in FALLBACK_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = str(e)
            if "429" in last_error or "Quota" in last_error or "404" in last_error:
                continue
            return f"❌ Error: {last_error}"

    return f"⚠️ Service busy or rate-limited: {last_error}"