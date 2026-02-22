# Migration Summary: Claude to Gemini

Here is a detailed breakdown of the changes made to migrate the AI functionality from Anthropic (Claude) to Google (Gemini) and restructure the project.

## 1. Dependencies (`requirements.txt`)

We added the Google AI SDK and a library to manage environment variables.

**Added:**
```text
google-generativeai==0.5.0
python-dotenv
```

## 2. Environment Configuration (`.env`)

We moved sensitive keys out of the code and into a `.env` file.

**Old Approach (Hardcoded in `app.py`):**
```python
ANTHROPIC_API_KEY = "sk-..."
```

**New Approach (`.env` file):**
```bash
GEMINI_API_KEY=AIza...
SECRET_KEY=your-secret-key...
```

**Updated `app.py`:**
```python
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-key')
```

## 3. Code Changes in `app.py`

### A. Imports & Setup

**Old:**
```python
import urllib.request
import urllib.error
# (No SDK import)
```

**New:**
```python
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
# Using 'gemini-flash-latest' to avoid quota issues with 1.5-flash
GEMINI_MODEL = 'gemini-flash-latest'
```

### B. API Helper Function

We replaced the manual HTTP request to Anthropic with the Google SDK call.

**Old (`call_claude`):**
```python
def call_claude(system_prompt, user_message):
    req = urllib.request.Request(ANTHROPIC_API_URL, ...)
    # ... complex JSON handling ...
    return response_text
```

**New (`call_gemini`):**
```python
def call_gemini(system_prompt, user_message):
    try:
        model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_prompt)
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        return '__API_ERROR__'
```

### C. Battle Judge Logic

We updated the function `run_code_with_tests` to use `call_gemini`. The logic remains mostly the same, but the underlying AI call is different.

**Changed:**
```python
# Old
ai_raw = call_claude(BATTLE_JUDGE_SYSTEM, user_msg)

# New
ai_raw = call_gemini(BATTLE_JUDGE_SYSTEM, user_msg)
# Added logic to strip markdown code blocks from the JSON response,
# as Gemini sometimes wraps JSON in ```json ... ```
clean = ai_raw.strip().lstrip('```json').rstrip('```').strip()
```

### D. Free Coding Judge

Similarly, `generate_ai_feedback` was updated.

**Changed:**
```python
# Old
ai_raw = call_claude(FREE_JUDGE_SYSTEM, user_msg)

# New
ai_raw = call_gemini(FREE_JUDGE_SYSTEM, user_msg)
```

## 4. Project Structure (Static Files)

To follow best practices and fix the 404 errors, we restructured the frontend files.

**Old Structure:**
```
/app.py
/new6.html
/new3.html
/battle_arena.html
```

**New Structure:**
```
/app.py
/static/
    /new6.html
    /new3.html
    /battle_arena.html
```

**Updated Routes in `app.py`:**
```python
@app.route('/')
def index():
    return send_from_directory('static', 'new6.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)
```
