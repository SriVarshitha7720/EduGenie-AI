import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")