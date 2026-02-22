import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
# Use the same model as app.py
GEMINI_MODEL = 'gemini-flash-latest'

def call_gemini(system_prompt: str, user_message: str) -> str:
    print(f"DEBUG: Key present: {bool(GEMINI_API_KEY)}")
    if GEMINI_API_KEY:
        print(f"DEBUG: Key prefix: {GEMINI_API_KEY[:4]}")
    
    if not GEMINI_API_KEY:
        return '__NO_KEY__'

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Try finding the model first
        print(f"DEBUG: Using model {GEMINI_MODEL}")
        
        # Initialize model with system_instruction
        model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_prompt)
        
        print("DEBUG: Generating content...")
        response = model.generate_content(user_message)
        print("DEBUG: Content generated")
        return response.text
    except Exception as e:
        print(f'[Gemini API error] {e}')
        return '__API_ERROR__'

print("--- STARTING DEBUG ---")
result = call_gemini("You are a helpful coding tutor.", "Hello, ignore this.")
print(f"--- RESULT: {result} ---")
