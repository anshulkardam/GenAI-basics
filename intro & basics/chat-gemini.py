from google import genai
from google.genai import types
import os

GEMINI_KEY=os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_KEY)

response = client.models.generate_content(
    model='gemini-2.0-flash-001', contents='hey there? how is the flood situation in India as of now ?'
)
print(response.text)