import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.environ.get("GEMINI_API_KEY"),
)

model_name = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").replace("gemini/", "").replace("models/", "")
model = genai.GenerativeModel(model_name)

response = model.generate_content(
    "Explain IEEE citation format."
)

print(response.text)
