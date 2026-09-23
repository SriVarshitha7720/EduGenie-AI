import json
import re
from backend.gemini_service import ask_gemini


def generate_quiz(topic, difficulty, num_questions):
    prompt = f"""
You are an expert educational quiz generator.

Generate exactly {num_questions} multiple-choice questions for:
Topic: {topic}
Difficulty: {difficulty}

Return ONLY a valid JSON array of objects without markdown formatting.
Each object MUST have:
[
  {{
    "question": "Question text here?",
    "options": [
      "A) Option A text",
      "B) Option B text",
      "C) Option C text",
      "D) Option D text"
    ],
    "answer": "A",
    "explanation": "Short sentence explaining why A is correct."
  }}
]
"""

    raw_response = ask_gemini(prompt)

    # Clean markdown codeblock formatting if present
    cleaned = raw_response.strip()
    if "```" in cleaned:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
        if match:
            cleaned = match.group(1).strip()

    try:
        data = json.loads(cleaned)
        return data
    except Exception:
        return raw_response