from backend.gemini_service import ask_gemini


def summarize_text(text):
    prompt = f"""
Summarize the following educational content.

Keep it simple.

Explain important points using bullet points.

Text:

{text}
"""

    return ask_gemini(prompt)