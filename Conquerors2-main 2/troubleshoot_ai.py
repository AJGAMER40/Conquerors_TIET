import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_setup():
    print("🔍 AI Analysis Troubleshooting Tool")
    print("===================================\n")

    # 1. Check Python Version
    print(f"1. Python Version: {sys.version.split()[0]}")
    
    # 2. Check SDK Version
    try:
        print(f"2. google-generativeai Version: {genai.__version__}")
        if genai.__version__ < '0.5.0':
             print("   ⚠️  WARNING: Your SDK version is old (v0.3.2 in requirements.txt).")
             print("   The 'gemini-flash-latest' model requires a newer version.")
             print("   👉 Recommendation: upgrade to at least 0.5.0")
    except AttributeError:
        print("2. google-generativeai Version: Unknown (AttributeError)")

    # 3. Check API Key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("\n3. API Key Status: ❌ MISSING")
        print("   👉 Cause: 'GEMINI_API_KEY' not found in environment variables.")
        print("   👉 Fix: Create a .env file and add GEMINI_API_KEY=your_key_here")
        return
    else:
        print(f"\n3. API Key Status: ✅ PRESENT (Starts with {api_key[:4]}...)")

    # 4. Connectivity Check
    print("\n4. Testing Connectivity to Gemini API...")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content("Hello, simply reply 'OK'.")
            print(f"   Response from AI: {response.text.strip()}")
            print("\n✅ SUCCESS: AI connection is working!")
        except Exception as e:
            print(f"\n❌ CONNECTION FAILED: {e}")
            print("   👉 Cause: Possible network firewall, invalid key, or model not found.")

if __name__ == "__main__":
    check_setup()
