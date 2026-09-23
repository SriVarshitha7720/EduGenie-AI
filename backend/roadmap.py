from backend.gemini_service import ask_gemini


def generate_roadmap(topic):
    prompt = f"""
Create a complete learning roadmap for

{topic}

The roadmap should include:

Week 1

Week 2

Week 3

...

Resources

Projects

Tips

Return it in beautiful markdown format.
"""

    return ask_gemini(prompt)