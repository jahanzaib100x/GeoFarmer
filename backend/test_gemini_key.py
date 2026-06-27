import os
import sys
from dotenv import load_dotenv

# Load env variables from .env file
backend_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(backend_dir, ".env")
load_dotenv(env_path)

key = os.environ.get("GEMINI_API_KEY")

if not key or "your_gemini" in key or len(key) < 10:
    print("Error: GEMINI_API_KEY is not configured or is using a placeholder in backend/.env.")
    print("Please paste your fresh API key into backend/.env before running this test.")
    sys.exit(1)

print(f"Loaded API key preview: {key[:6]}...{key[-4:] if len(key) > 10 else ''}")
print("Attempting to connect to Gemini API...")

try:
    import google.generativeai as genai
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Hello! Please respond with exactly: 'Gemini API key is working perfectly!'")
    if response and response.text:
        print("\n" + "="*50)
        print("API Response:", response.text.strip())
        print("="*50)
        print("\nSuccess! Your Google Cloud Gemini API key is fully active and functioning.")
    else:
        print("Received an empty response from Gemini API.")
except Exception as e:
    print("\n[ERROR] Gemini call failed:")
    print(e)
    print("\nIf you enabled the 'Gemini API' in Google Cloud Console, make sure you enabled the 'Generative Language API' or that billing is correctly configured.")
