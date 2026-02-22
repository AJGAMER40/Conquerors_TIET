from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import os
import google.generativeai as genai
import subprocess
import tempfile
import json
import urllib.request
import urllib.error
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///education_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ── Gemini API Config ─────────────────────────────────────────────────────────
# Set via environment variable: GEMINI_API_KEY
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Using the latest stable flash model alias
GEMINI_MODEL = 'gemini-flash-latest'

db = SQLAlchemy(app)

# ==================== XP & LEVEL SYSTEM CONFIG ====================

LEVEL_THRESHOLDS = {
    1: 0, 2: 100, 3: 250, 4: 450, 5: 700,
    6: 1000, 7: 1350, 8: 1750, 9: 2200, 10: 2700,
}

EXP_REWARDS = {
    'code_success': 30,
    'code_attempt': 5,
    'quiz_correct': 10,
    'quiz_complete': 20,
    'battle_win': 75,
    'battle_loss': 25,
}

# 🪙 Sikke — in-game currency rewards
SIKKE_REWARDS = {
    'battle_win': 10,
    'battle_loss': 2,
    'battle_win_forfeit': 5,
}

# 🎁 Voucher catalogue for the Coin Shop
VOUCHER_CATALOGUE = [
    {'id': 'v1', 'name': 'Amazon Gift Card ₹100', 'cost': 50,  'icon': '🛍️', 'category': 'Shopping'},
    {'id': 'v2', 'name': 'Swiggy ₹50 Off',        'cost': 25,  'icon': '🍔', 'category': 'Food'},
    {'id': 'v3', 'name': 'Zomato ₹50 Off',        'cost': 25,  'icon': '🍕', 'category': 'Food'},
    {'id': 'v4', 'name': 'Flipkart ₹200 Coupon',  'cost': 100, 'icon': '📦', 'category': 'Shopping'},
    {'id': 'v5', 'name': 'Netflix 1-Month',        'cost': 150, 'icon': '🎬', 'category': 'Entertainment'},
    {'id': 'v6', 'name': 'Spotify 1-Month',        'cost': 80,  'icon': '🎵', 'category': 'Entertainment'},
    {'id': 'v7', 'name': 'Paytm ₹30 Cashback',    'cost': 20,  'icon': '💳', 'category': 'Payments'},
    {'id': 'v8', 'name': 'Extra 100 XP Boost',     'cost': 30,  'icon': '⚡', 'category': 'Game'},
]

BATTLE_PROBLEMS = {
    1: {
        'title': 'Sum of Two Numbers',
        'description': 'Write a function `add(a, b)` that returns the sum of two numbers.\n\nExamples:\nadd(3, 4) → 7\nadd(10, -2) → 8\nadd(0, 0) → 0',
        'test_cases': [
            {'input': 'print(add(3, 4))', 'expected': '7'},
            {'input': 'print(add(10, -2))', 'expected': '8'},
            {'input': 'print(add(0, 0))', 'expected': '0'},
        ],
        'time_limit': 120,
    },
    2: {
        'title': 'FizzBuzz',
        'description': 'Write a function `fizzbuzz(n)` that returns:\n- "Fizz" if n is divisible by 3\n- "Buzz" if divisible by 5\n- "FizzBuzz" if both\n- The number as a string otherwise\n\nExamples:\nfizzbuzz(3) → "Fizz"\nfizzbuzz(5) → "Buzz"\nfizzbuzz(15) → "FizzBuzz"\nfizzbuzz(7) → "7"',
        'test_cases': [
            {'input': 'print(fizzbuzz(3))', 'expected': 'Fizz'},
            {'input': 'print(fizzbuzz(5))', 'expected': 'Buzz'},
            {'input': 'print(fizzbuzz(15))', 'expected': 'FizzBuzz'},
            {'input': 'print(fizzbuzz(7))', 'expected': '7'},
        ],
        'time_limit': 150,
    },
    3: {
        'title': 'Palindrome Check',
        'description': 'Write a function `is_palindrome(s)` that returns True if the string is a palindrome, False otherwise.\n\nExamples:\nis_palindrome("racecar") → True\nis_palindrome("hello") → False\nis_palindrome("level") → True',
        'test_cases': [
            {'input': 'print(is_palindrome("racecar"))', 'expected': 'True'},
            {'input': 'print(is_palindrome("hello"))', 'expected': 'False'},
            {'input': 'print(is_palindrome("level"))', 'expected': 'True'},
        ],
        'time_limit': 150,
    },
    4: {
        'title': 'Fibonacci',
        'description': 'Write a function `fibonacci(n)` that returns the nth Fibonacci number (0-indexed).\n\nExamples:\nfibonacci(0) → 0\nfibonacci(1) → 1\nfibonacci(6) → 8\nfibonacci(10) → 55',
        'test_cases': [
            {'input': 'print(fibonacci(0))', 'expected': '0'},
            {'input': 'print(fibonacci(6))', 'expected': '8'},
            {'input': 'print(fibonacci(10))', 'expected': '55'},
        ],
        'time_limit': 180,
    },
    5: {
        'title': 'Count Vowels',
        'description': 'Write a function `count_vowels(s)` that counts vowels (a,e,i,o,u — case-insensitive).\n\nExamples:\ncount_vowels("Hello World") → 3\ncount_vowels("aeiou") → 5\ncount_vowels("xyz") → 0',
        'test_cases': [
            {'input': 'print(count_vowels("Hello World"))', 'expected': '3'},
            {'input': 'print(count_vowels("aeiou"))', 'expected': '5'},
            {'input': 'print(count_vowels("xyz"))', 'expected': '0'},
        ],
        'time_limit': 180,
    },
}


def get_level_from_exp(exp):
    current_level = 1
    for lvl, threshold in sorted(LEVEL_THRESHOLDS.items(), reverse=True):
        if exp >= threshold:
            current_level = lvl
            break
    return current_level


def get_exp_progress(exp, current_level):
    current_threshold = LEVEL_THRESHOLDS.get(current_level, 0)
    next_level = current_level + 1
    if next_level not in LEVEL_THRESHOLDS:
        return 100
    next_threshold = LEVEL_THRESHOLDS[next_level]
    level_range = next_threshold - current_threshold
    progress_in_level = exp - current_threshold
    return min(100, int((progress_in_level / level_range) * 100))


# ==================== DATABASE MODELS ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='learner')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reading_level = db.Column(db.String(20), default='Grade 8')
    visual_preference = db.Column(db.String(50), default='Normal Mode')
    learning_pattern = db.Column(db.String(50), default='Mixed')
    # XP system
    exp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    # Sikke — in-game currency
    sikke = db.Column(db.Integer, default=0)
    # Relationships
    enrollments = db.relationship('Enrollment', backref='user', lazy=True)
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)
    coding_submissions = db.relationship('CodingSubmission', backref='user', lazy=True)

    def award_exp(self, amount, reason=''):
        old_level = self.level
        self.exp += amount
        new_level = get_level_from_exp(self.exp)
        self.level = new_level
        # Caller must call db.session.commit()
        return {
            'exp_gained': amount,
            'sikke_gained': 0,
            'total_exp': self.exp,
            'total_sikke': self.sikke,
            'old_level': old_level,
            'new_level': new_level,
            'leveled_up': new_level > old_level,
            'reason': reason,
            'progress': get_exp_progress(self.exp, new_level),
            'exp_for_next': LEVEL_THRESHOLDS.get(new_level + 1, LEVEL_THRESHOLDS[max(LEVEL_THRESHOLDS)]),
            'current_threshold': LEVEL_THRESHOLDS.get(new_level, 0),
            'sikke': self.sikke,
        }

    def award_sikke(self, amount, reason=''):
        """Award Sikke currency. Caller must call db.session.commit()."""
        self.sikke += amount
        return {
            'sikke_gained': amount,
            'total_sikke': self.sikke,
            'reason': reason,
        }

    def to_level_info(self):
        return {
            'exp': self.exp,
            'level': self.level,
            'progress': get_exp_progress(self.exp, self.level),
            'exp_for_next': LEVEL_THRESHOLDS.get(self.level + 1, LEVEL_THRESHOLDS[max(LEVEL_THRESHOLDS)]),
            'current_threshold': LEVEL_THRESHOLDS.get(self.level, 0),
        }


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    instructor = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    level = db.Column(db.String(50))
    category = db.Column(db.String(50))
    progress_percentage = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    quizzes = db.relationship('Quiz', backref='course', lazy=True)


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.Column(db.Integer, default=0)


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.String(20), default='Medium')
    questions = db.relationship('Question', backref='quiz', lazy=True)
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1), nullable=False)
    explanation = db.Column(db.Text)


class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)


class CodingSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    problem_id=db.Column(db.String(50), nullable=True)
    code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20), nullable=False)
    output = db.Column(db.Text)
    ai_feedback = db.Column(db.Text)
    success = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


class Battle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    level = db.Column(db.Integer, nullable=False)
    problem_key = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='waiting')  # waiting | active | finished
    winner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    player1_solved_at = db.Column(db.DateTime, nullable=True)
    player2_solved_at = db.Column(db.DateTime, nullable=True)
    player1_accuracy = db.Column(db.Integer, default=0)
    player2_accuracy = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)
    player1 = db.relationship('User', foreign_keys=[player1_id])
    player2 = db.relationship('User', foreign_keys=[player2_id])
    winner = db.relationship('User', foreign_keys=[winner_id])


# ==================== IN-MEMORY STATE ====================
matchmaking_queue = {}   # { level: [user_id, ...] }
user_socket_map = {}     # { user_id: socket_id }


# ==================== HELPERS ====================

def generate_token(user_id):
    payload = {'user_id': user_id, 'exp': datetime.utcnow() + timedelta(days=7)}
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except Exception:
        return None


# ==================== AI JUDGE CORE ====================

# ── GEMINI HELPER ─────────────────────────────────────────────────────────────

def call_gemini(system_prompt: str, user_message: str) -> str:
    """
    Call Google Gemini API.
    Returns the text content of the response.
    Falls back gracefully if the API key is missing or the call fails.
    """
    if not GEMINI_API_KEY:
        return '__NO_KEY__'

    try:
        model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_prompt)
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        print(f'[Gemini API error] {e}')
        return '__API_ERROR__'


def execute_code_safely(code: str) -> dict:
    """Run code in a subprocess and return stdout/stderr + return code."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        result = subprocess.run(
            ['python3', temp_file],
            capture_output=True, text=True, timeout=5,
        )
        os.unlink(temp_file)
        return {
            'stdout':  result.stdout,
            'stderr':  result.stderr,
            'success': result.returncode == 0,
            'timeout': False,
        }
    except subprocess.TimeoutExpired:
        return {'stdout': '', 'stderr': 'Execution timed out.', 'success': False, 'timeout': True}
    except Exception as e:
        return {'stdout': '', 'stderr': str(e), 'success': False, 'timeout': False}


BATTLE_JUDGE_SYSTEM = """You are a strict automated coding contest judge for a student programming battle.

Your ONLY job is to decide whether the student's Python code correctly solves the problem and assign a qualitative accuracy score.

Rules:
1. Mentally execute each test case against the student's code.
2. Assign an "accuracy_score" between 0 and 100 based on:
    -logical correctness (primary factor)
    -Handling of edge cases
    -Code efficiency and idiomatic python usage
3. Respond with ONLY valid JSON — no explanations, no markdown, no explanation outside JSON.
4. JSON schema (all fields required):
{
  "verdict": "PASS" | "FAIL" | "ERROR",
  "accuracy_score": <integer 0-100>,
  "test_results": [
    {"case": 1, "passed": true|false, "expected": "<value>", "actual": "<value>", "note": "<short note>"},
    ...
  ],
  "overall_feedback": "<1-2 sentence feedback on the solution — be educational>",
  "code_quality": "<one of: Excellent | Good | Needs Work | Poor>",
  "hints": ["<hint if failed>"]
}

verdict = PASS only if every test case passes.
verdict = ERROR if the code has syntax errors or crashes.
verdict = FAIL if any test case produces wrong output.
Be exact — whitespace, capitalisation, and types matter."""


def run_code_with_tests(user_code: str, test_cases: list) -> list:
    """
    AI-powered battle judge.
    1. Actually runs each test case to get real output.
    2. Sends code + real outputs + expected values to Gemini for final verdict.
    Returns a list of per-test-case dicts compatible with the old interface,
    PLUS enriches each dict with 'ai_note' and adds top-level 'ai_feedback'.
    """
    # Step 1 — run all test cases for real output
    raw_results = []
    for tc in test_cases:
        full_code = user_code + '\n' + tc['input']
        run = execute_code_safely(full_code)
        actual = run['stdout'].strip() if run['success'] else run['stderr'].strip()
        raw_results.append({
            'input':    tc['input'],
            'expected': tc['expected'].strip(),
            'actual':   actual,
            'runtime_passed': actual == tc['expected'].strip() and run['success'],
            'timeout':  run['timeout'],
        })

    # Step 2 — ask Gemini to verify and give educational feedback
    test_summary = '\n'.join(
        f"  Test {i+1}: input=`{r['input']}` expected=`{r['expected']}` got=`{r['actual']}` runtime_passed={r['runtime_passed']}"
        for i, r in enumerate(raw_results)
    )
    user_msg = f"""Problem test cases and actual runtime outputs:
{test_summary}

Student code:
```python
{user_code}
```

Evaluate correctness strictly and return the JSON verdict."""

    ai_raw = call_gemini(BATTLE_JUDGE_SYSTEM, user_msg)

    # Parse Gemini response
    ai_verdict = None
    if ai_raw not in ('__NO_KEY__', '__API_ERROR__'):
        try:
            # Strip possible markdown fences
            clean = ai_raw.strip().lstrip('```json').lstrip('```').rstrip('```').strip()
            ai_verdict = json.loads(clean)
        except Exception:
            ai_verdict = None

    # Build final results list
    results = []
    for i, r in enumerate(raw_results):
        ai_tc = {}
        if ai_verdict and 'test_results' in ai_verdict and i < len(ai_verdict['test_results']):
            ai_tc = ai_verdict['test_results'][i]

        # Trust AI verdict if available, else fall back to runtime comparison
        passed = ai_tc.get('passed', r['runtime_passed'])
        results.append({
            'passed':   passed,
            'expected': r['expected'],
            'actual':   r['actual'],
            'ai_note':  ai_tc.get('note', ''),
        })

    # Attach overall AI feedback to the last result for the caller to extract
    overall = ''
    hints   = []
    quality = ''
    accuracy = 0
    if ai_verdict:
        overall = ai_verdict.get('overall_feedback', '')
        hints   = ai_verdict.get('hints', [])
        quality = ai_verdict.get('code_quality', '')
        accuracy = ai_verdict.get('accuracy_score', 0)
    else:
        passed_count = sum(1 for r in results if r.get('passed'))
        total_test=len(results)
        if total_test > 0:
            accuracy = int((passed_count / total_test) * 100)
        overall="AI feedback unavailable. Based on test runs"
    results.append({
        '__ai_meta__': True,
        'overall_feedback': overall,
        'hints': hints,
        'code_quality': quality,
        'accuracy_score': accuracy,
    })
    return results


# ── FREE CODING JUDGE: AI reviews any submitted code ─────────────────────────

FREE_JUDGE_SYSTEM = """You are an expert Python coding mentor reviewing a student's code submission in an education portal.

Be encouraging but honest. Respond with ONLY valid JSON — no markdown.
JSON schema:
{
  "summary": "<1 sentence verdict: correct / has bugs / syntax error>",
  "strengths": ["<what they did well>", ...],
  "issues": ["<specific bug or issue>", ...],
  "suggestions": ["<actionable improvement>", ...],
  "code_quality": "<Excellent | Good | Needs Work | Poor>",
  "encouragement": "<short motivational line tailored to their code>"
}"""

def generate_ai_feedback(code: str, output: str) -> str:
    """
    Ask Gemini to review free-form code and return a rich feedback string.
    Falls back to rule-based feedback if API key is missing.
    """
    if not GEMINI_API_KEY:
        # Rule-based fallback (original logic)
        feedback = []
        if 'def' in code:
            feedback.append("✓ Good: You're using functions to organise your code.")
        if len(code.split('\n')) < 10:
            feedback.append("✓ Concise: Your solution is compact and readable.")
        if '#' in code:
            feedback.append("✓ Great: You're using comments to explain your code.")
        if not output or output.strip() == '':
            feedback.append("⚠ Note: Your code doesn't produce any output. Consider adding print statements.")
        if 'error' in output.lower() or 'exception' in output.lower():
            feedback.append("✗ Error detected: Review the error message and fix the issue.")
        else:
            feedback.append("✓ Success: Your code executed without errors!")
        return ' '.join(feedback)

    user_msg = f"""Student's Python code:
```python
{code}
```

Execution output:
```
{output if output.strip() else '(no output)'}
```

Review this code and return the JSON feedback."""

    ai_raw = call_gemini(FREE_JUDGE_SYSTEM, user_msg)

    if ai_raw in ('__NO_KEY__', '__API_ERROR__'):
        return '⚠ AI feedback unavailable right now. Check your code output above.'

    try:
        clean = ai_raw.strip().lstrip('```json').lstrip('```').rstrip('```').strip()
        verdict = json.loads(clean)

        parts = []
        parts.append(f"📋 {verdict.get('summary', '')}")

        strengths = verdict.get('strengths', [])
        if strengths:
            parts.append('✅ Strengths: ' + ' · '.join(strengths))

        issues = verdict.get('issues', [])
        if issues:
            parts.append('⚠️ Issues: ' + ' · '.join(issues))

        suggestions = verdict.get('suggestions', [])
        if suggestions:
            parts.append('💡 Tips: ' + ' · '.join(suggestions))

        quality = verdict.get('code_quality', '')
        if quality:
            parts.append(f'⭐ Code quality: {quality}')

        enc = verdict.get('encouragement', '')
        if enc:
            parts.append(f'🎯 {enc}')

        return '\n'.join(parts)

    except Exception:
        # Gemini returned something but it wasn't clean JSON — return raw
        return ai_raw[:500]


# ==================== AUTH ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    if User.query.filter_by(student_id=data['student_id']).first():
        return jsonify({'error': 'Student ID already exists'}), 400
    user = User(
        student_id=data['student_id'], name=data['name'], email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role=data.get('role', 'learner'), exp=0, level=1, sikke=0,
    )
    db.session.add(user)
    db.session.commit()
    token = generate_token(user.id)
    return jsonify({
        'message': 'User registered successfully', 'token': token,
        'user': {'id': user.id, 'name': user.name, 'email': user.email,
                 'student_id': user.student_id, 'role': user.role, 'exp': 0, 'level': 1, 'sikke': 0},
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(student_id=data['student_id']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    token = generate_token(user.id)
    return jsonify({
        'message': 'Login successful', 'token': token,
        'user': {'id': user.id, 'name': user.name, 'email': user.email,
                 'student_id': user.student_id, 'role': user.role,
                 'exp': user.exp, 'level': user.level, 'sikke': user.sikke},
    }), 200


# ==================== USER ====================

@app.route('/api/user/profile', methods=['GET'])
def get_profile():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    user = User.query.get(user_id)
    return jsonify({
        'id': user.id, 'name': user.name, 'email': user.email,
        'student_id': user.student_id, 'role': user.role,
        'reading_level': user.reading_level, 'visual_preference': user.visual_preference,
        'learning_pattern': user.learning_pattern,
        'sikke': user.sikke,
        **user.to_level_info(),
    }), 200


@app.route('/api/user/preferences', methods=['PUT'])
def update_preferences():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    data = request.get_json()
    user = User.query.get(user_id)
    for field in ('reading_level', 'visual_preference', 'learning_pattern'):
        if field in data:
            setattr(user, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Preferences updated successfully'}), 200


@app.route('/api/user/stats', methods=['GET'])
def get_user_stats():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    user = User.query.get(user_id)
    enrolled_courses = Enrollment.query.filter_by(user_id=user_id).count()
    quiz_attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
    total_quizzes = len(quiz_attempts)
    avg_score = round(sum(a.score for a in quiz_attempts) / total_quizzes, 1) if total_quizzes > 0 else 0
    coding_submissions = CodingSubmission.query.filter_by(user_id=user_id).count()
    battles_won = Battle.query.filter_by(winner_id=user_id).count()
    battles_total = Battle.query.filter(
        ((Battle.player1_id == user_id) | (Battle.player2_id == user_id)),
        Battle.status =='finished'
    ).count()
    return jsonify({
        'enrolled_courses': enrolled_courses, 'quizzes_completed': total_quizzes,
        'average_score': avg_score, 'coding_submissions': coding_submissions,
        'battles_won': battles_won, 'battles_total': battles_total,
        **user.to_level_info(),
    }), 200


@app.route('/api/user/xp', methods=['GET'])
def get_xp():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_level_info()), 200


@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    users = User.query.order_by(User.exp.desc()).limit(20).all()
    return jsonify([{
        'rank': i + 1, 'name': u.name, 'student_id': u.student_id,
        'level': u.level, 'exp': u.exp, 'sikke': u.sikke,
    } for i, u in enumerate(users)]), 200


# ==================== SIKKE & COIN SHOP ====================

@app.route('/api/user/sikke', methods=['GET'])
def get_sikke():
    """Return the authenticated user's Sikke balance."""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    user = User.query.get(user_id)
    return jsonify({'sikke': user.sikke, 'name': user.name}), 200


@app.route('/api/shop/vouchers', methods=['GET'])
def get_vouchers():
    """Return the full voucher catalogue (public)."""
    return jsonify(VOUCHER_CATALOGUE), 200


@app.route('/api/shop/redeem', methods=['POST'])
def redeem_voucher():
    """Spend Sikke to claim a voucher."""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    data = request.get_json()
    voucher_id = data.get('voucher_id')
    voucher = next((v for v in VOUCHER_CATALOGUE if v['id'] == voucher_id), None)
    if not voucher:
        return jsonify({'error': 'Voucher not found'}), 404
    user = User.query.get(user_id)
    if user.sikke < voucher['cost']:
        return jsonify({
            'error': 'Not enough Sikke',
            'required': voucher['cost'],
            'you_have': user.sikke,
        }), 400
    user.sikke -= voucher['cost']
    db.session.commit()
    # In a real system you'd generate a unique code and email it.
    # Here we return a mock redemption code.
    import random, string
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    return jsonify({
        'success': True,
        'voucher': voucher['name'],
        'code': code,
        'remaining_sikke': user.sikke,
        'message': f'🎉 Redeemed! Your code: {code}',
    }), 200


# ==================== COURSES ====================

@app.route('/api/courses', methods=['GET'])
def get_courses():
    return jsonify([{
        'id': c.id, 'title': c.title, 'code': c.code, 'instructor': c.instructor,
        'description': c.description, 'level': c.level, 'category': c.category,
        'progress': c.progress_percentage,
    } for c in Course.query.all()]), 200


@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    return jsonify({
        'id': course.id, 'title': course.title, 'code': course.code,
        'instructor': course.instructor, 'description': course.description,
        'level': course.level, 'category': course.category, 'progress': course.progress_percentage,
    }), 200


@app.route('/api/courses/enroll', methods=['POST'])
def enroll_course():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    data = request.get_json()
    if Enrollment.query.filter_by(user_id=user_id, course_id=data['course_id']).first():
        return jsonify({'error': 'Already enrolled in this course'}), 400
    db.session.add(Enrollment(user_id=user_id, course_id=data['course_id']))
    db.session.commit()
    return jsonify({'message': 'Enrolled successfully'}), 201


@app.route('/api/courses/my-courses', methods=['GET'])
def get_my_courses():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    return jsonify([{
        'id': e.course.id, 'title': e.course.title, 'code': e.course.code,
        'instructor': e.course.instructor, 'description': e.course.description,
        'level': e.course.level, 'category': e.course.category, 'progress': e.progress,
    } for e in Enrollment.query.filter_by(user_id=user_id).all()]), 200


# ==================== QUIZ ====================

@app.route('/api/quizzes/<int:course_id>', methods=['GET'])
def get_course_quizzes(course_id):
    return jsonify([{
        'id': q.id, 'title': q.title, 'difficulty': q.difficulty,
        'question_count': len(q.questions),
    } for q in Quiz.query.filter_by(course_id=course_id).all()]), 200


@app.route('/api/quiz/<int:quiz_id>/questions', methods=['GET'])
def get_quiz_questions(quiz_id):
    return jsonify([{
        'id': q.id, 'question': q.question_text,
        'options': {'A': q.option_a, 'B': q.option_b, 'C': q.option_c, 'D': q.option_d},
        'explanation': q.explanation,
    } for q in Question.query.filter_by(quiz_id=quiz_id).all()]), 200


@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    data = request.get_json()
    quiz_id = data['quiz_id']
    answers = data['answers']
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    correct_count = 0
    results = []
    for q in questions:
        user_answer = answers.get(str(q.id))
        is_correct = user_answer == q.correct_answer
        if is_correct:
            correct_count += 1
        results.append({'question_id': q.id, 'correct': is_correct,
                        'correct_answer': q.correct_answer, 'user_answer': user_answer})
    db.session.add(QuizAttempt(user_id=user_id, quiz_id=quiz_id,
                               score=correct_count, total_questions=len(questions)))
    db.session.commit()
    user = User.query.get(user_id)
    exp_amount = correct_count * EXP_REWARDS['quiz_correct'] + EXP_REWARDS['quiz_complete']
    exp_result = user.award_exp(exp_amount, 'Quiz completion')
    db.session.commit()
    return jsonify({
        'score': correct_count, 'total': len(questions),
        'percentage': round((correct_count / len(questions)) * 100, 1),
        'results': results, 'exp_result': exp_result,
    }), 200


# ==================== CODING JUDGE ====================

@app.route('/api/judge', methods=['POST'])
def judge_code():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    data = request.get_json()
    code = data['code']
    language = data.get('language', 'python')
    exp_result = None

    run = execute_code_safely(code)
    output = run['stdout'] if run['success'] else run['stderr']
    success = run['success']

    if run['timeout']:
        return jsonify({
            'runOutput': 'Execution timed out.',
            'aiAnalysis': '⏰ Your code exceeded the 5-second time limit. Check for infinite loops.',
            'success': False, 'exp_result': None,
        }), 200

    # Ask AI for rich feedback
    ai_analysis = generate_ai_feedback(code, output)

    if user_id:
        user = User.query.get(user_id)
        db.session.add(CodingSubmission(
            user_id=user_id, code=code, language=language,
            output=output, ai_feedback=ai_analysis, success=success,
        ))
        db.session.commit()
        exp_amt = EXP_REWARDS['code_success'] if success else EXP_REWARDS['code_attempt']
        exp_result = user.award_exp(exp_amt, 'Code submission')
        db.session.commit()

    return jsonify({
        'runOutput': output,
        'aiAnalysis': ai_analysis,
        'success': success,
        'exp_result': exp_result,
    }), 200


# ==================== BATTLE SYSTEM ====================

@app.route('/api/battle/queue', methods=['POST'])
def join_battle_queue():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    level = user.level
    problem_key = ((level - 1) % len(BATTLE_PROBLEMS)) + 1
    # Already in an ACTIVE battle? Block re-entry.
    active = Battle.query.filter(
        ((Battle.player1_id == user_id) | (Battle.player2_id == user_id)),
        Battle.status == 'active'
    ).first()
    if active:
        problem = BATTLE_PROBLEMS.get(active.problem_key, {})
        return jsonify({
            'battle_id': active.id, 'status': 'active',
            'message': 'Already in a battle',
            'problem': {'title': problem.get('title', ''),
                        'description': problem.get('description', ''),
                        'time_limit': problem.get('time_limit', 120)},
        }), 200

    # Cancel stale waiting battles for this user before re-queuing
    stale = Battle.query.filter(
        ((Battle.player1_id == user_id) | (Battle.player2_id == user_id)),
        Battle.status == 'waiting'
    ).all()
    for s in stale:
        s.status = 'finished'
    if stale:
        db.session.commit()

    global matchmaking_queue
    if level not in matchmaking_queue:
        matchmaking_queue[level] = []

    # ── Sync in-memory queue with DB ──────────────────────────────────────────
    # If the server restarted, the in-memory queue is empty but waiting Battle
    # rows still exist in the DB. Re-populate the queue from the DB so that
    # players who queued in a previous server session can still be matched.
    waiting_battles = Battle.query.filter_by(level=level, status='waiting').all()
    for wb in waiting_battles:
        # player1 created the waiting slot; player2 is null while waiting
        if wb.player1_id not in matchmaking_queue[level] and wb.player1_id != user_id:
            matchmaking_queue[level].append(wb.player1_id)

    # Find opponent
    opponent_id = None
    for uid in list(matchmaking_queue[level]):
        if uid != user_id:
            opponent_id = uid
            matchmaking_queue[level].remove(uid)
            break
    if opponent_id:
        battle = Battle(
            player1_id=opponent_id, player2_id=user_id,
            level=level, problem_key=problem_key,
            status='active', started_at=datetime.utcnow()
        )
        db.session.add(battle)
        db.session.commit()
        # Remove waiting battles for both players
        # Fix: use player1_id OR player2_id (not player1_id twice)
        Battle.query.filter(
            ((Battle.player1_id == opponent_id) | (Battle.player2_id == opponent_id) |
             (Battle.player1_id == user_id)     | (Battle.player2_id == user_id)),
            Battle.status == 'waiting', Battle.id != battle.id
        ).update({'status': 'finished'})
        db.session.commit()
        problem = BATTLE_PROBLEMS[problem_key]
        opponent = User.query.get(opponent_id)
        # Notify opponent via WebSocket
        opp_sid = user_socket_map.get(opponent_id)
        if opp_sid:
            socketio.emit('battle_start', {
                'battle_id': battle.id,
                'problem': {'title': problem['title'], 'description': problem['description'],
                            'time_limit': problem['time_limit']},
                'opponent': {'name': user.name, 'level': level},
            }, to=opp_sid)
        return jsonify({
            'status': 'matched', 'battle_id': battle.id,
            'problem': {'title': problem['title'], 'description': problem['description'],
                        'time_limit': problem['time_limit']},
            'opponent': {'name': opponent.name, 'level': level},
        }), 200
    else:
        # Add to queue, create waiting battle
        if user_id not in matchmaking_queue[level]:
            matchmaking_queue[level].append(user_id)
        battle = Battle(player1_id=user_id, player2_id=None,
                        level=level, problem_key=problem_key, status='waiting')
        db.session.add(battle)
        db.session.commit()
        return jsonify({
            'status': 'waiting', 'battle_id': battle.id,
            'message': 'Waiting for an opponent at your level...',
        }), 200


@app.route('/api/battle/poll/<int:battle_id>', methods=['GET'])
def poll_battle(battle_id):
    """HTTP polling fallback for clients without WebSocket"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    battle = Battle.query.get_or_404(battle_id)
    problem = BATTLE_PROBLEMS.get(battle.problem_key, {})
    opponent_id = battle.player2_id if battle.player1_id == user_id else battle.player1_id
    opponent = User.query.get(opponent_id) if opponent_id else None
    return jsonify({
        'battle_id': battle.id, 'status': battle.status,
        'level': battle.level, 'winner_id': battle.winner_id,
        'opponent': {'name': opponent.name, 'level': battle.level} if opponent else None,
        'problem': {'title': problem.get('title', ''), 'description': problem.get('description', ''),
                    'time_limit': problem.get('time_limit', 120)} if battle.status == 'active' else None,
        'started_at': battle.started_at.isoformat() if battle.started_at else None,
    }), 200


@app.route('/api/battle/<int:battle_id>/submit', methods=['POST'])
def submit_battle_code(battle_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    battle = Battle.query.get_or_404(battle_id)
    if battle.status != 'active':
        return jsonify({'error': 'Battle is not active'}), 400
    if user_id not in [battle.player1_id, battle.player2_id]:
        return jsonify({'error': 'You are not in this battle'}), 403
    data = request.get_json()
    code = data['code']
    problem = BATTLE_PROBLEMS.get(battle.problem_key)

    # Run AI-powered judge (returns results list + hidden __ai_meta__ entry)
    # Run AI-powered judge (returns results list + hidden __ai_meta__ entry)
    # Run AI-powered judge (returns results list + hidden __ai_meta__ entry)
    raw_results = run_code_with_tests(code, problem['test_cases'])

    # Split out AI meta from test results  ← THIS WAS MISSING
    ai_meta = next((r for r in raw_results if r.get('__ai_meta__')), {})
    test_results = [r for r in raw_results if not r.get('__ai_meta__')]

    accuracy = ai_meta.get('accuracy_score', 0)
    all_passed = all(r['passed'] for r in test_results)
    is_player1 = user_id == battle.player1_id
    if is_player1:
        battle.player1_accuracy=max(battle.player1_accuracy, accuracy)
    else:
        battle.player2_accuracy=max(battle.player2_accuracy, accuracy)
    result_payload = {
        'test_results': test_results,
        'all_passed': all_passed,
        'accuracy_score': accuracy,
        'battle_id': battle_id,
        'battle_over': False,
        'ai_feedback': {
            'overall': ai_meta.get('overall_feedback', ''),
            'hints':   ai_meta.get('hints', []),
            'quality': ai_meta.get('code_quality', ''),
        },
    }

    is_accurate = accuracy >= 80  # Define your own threshold for "solved"
    if is_accurate:
        now = datetime.utcnow()
        if is_player1 and battle.player1_solved_at is None:
            battle.player1_solved_at = now
        elif not is_player1 and battle.player2_solved_at is None:
            battle.player2_solved_at = now
        p1_done = battle.player1_solved_at is not None
        p2_done = battle.player2_solved_at is not None
        if p1_done and p2_done:
           if battle.player1_accuracy>battle.player2_accuracy:
               battle.winner_id=battle.player1_id
           elif battle.player2_accuracy>battle.player1_accuracy:
               battle.winner_id=battle.player2_id
           else:
               battle.winner_id=battle.player1_id if battle.player1_solved_at <= battle.player2_solved_at else battle.player2_id
        if not battle.winner_id:
            if accuracy>=95:
                battle.winner_id = user_id
            elif p1_done and p2_done:
                pass
            if not battle.winner_id:
                battle.winner_id = user_id
            battle.status = 'finished'
            battle.finished_at = now
            db.session.commit()
            winner=User.query.get(battle.winner_id)
            loser_id = battle.player2_id if battle.winner_id == battle.player1_id else battle.player1_id
            loser = User.query.get(loser_id) if loser_id else None
            win_data=winner.award_exp(EXP_REWARDS['battle_win'], 'Battle victory')
            winner.sikke+=10
            win_data['sikke_gained']+=10
            win_data['total_sikke']=winner.sikke
            loss_data=None
            if loser:
                loss_data=loser.award_exp(EXP_REWARDS['battle_loss'], 'Battle Participation')
                loser.sikke+=2
                loss_data['sikke_gained']+=2
                loss_data['total_sikke']=loser.sikke
            db.session.commit()
            # Merge Sikke into exp_result for frontend convenience
            # WebSocket notifications
            for pid, res_data, won in [
                (battle.winner_id, win_data, True),
                (loser_id, loss_data, False),
            ]:
                if pid and res_data:
                    sid = user_socket_map.get(pid)
                    if sid:
                        socketio.emit('battle_result', {
                            'battle_id': battle_id, 'winner_id': battle.winner_id,
                            'winner_name': winner.name, 'you_won': won, 'exp_result': res_data,
                        }, to=sid)
            you_won = user_id == battle.winner_id
            result_payload.update({
                'battle_over': True, 'winner_id': battle.winner_id,
                'winner_name': winner.name, 'you_won': you_won,
                'exp_result': win_data if you_won else loss_data,
            })
        else:
            db.session.commit()
            # Notify opponent
            opponent_id = battle.player2_id if user_id==battle.player1_id else battle.player1_id
            opp_sid = user_socket_map.get(opponent_id)
            if opp_sid:
                socketio.emit('opponent_solved', {
                    'battle_id': battle_id,
                    'message': 'Your opponent solved it! Hurry!',
                }, to=opp_sid)
    else:
        db.session.commit()
    return jsonify(result_payload), 200


@app.route('/api/battle/<int:battle_id>/leave', methods=['POST'])
def leave_battle(battle_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    battle = Battle.query.get_or_404(battle_id)
    if battle.status == 'finished':
        return jsonify({'message': 'Battle already finished'}), 200
    if user_id not in [battle.player1_id, battle.player2_id]:
        return jsonify({'error': 'Not in this battle'}), 403
    if battle.status == 'waiting':
        level = battle.level
        if level in matchmaking_queue and user_id in matchmaking_queue[level]:
            matchmaking_queue[level].remove(user_id)
    elif battle.status == 'active':
        opponent_id = battle.player2_id if user_id == battle.player1_id else battle.player1_id
        if opponent_id:
            battle.winner_id = opponent_id
            opp = User.query.get(opponent_id)
            win_exp = opp.award_exp(EXP_REWARDS['battle_win'], 'Battle victory (forfeit)')
            win_sikke = opp.award_sikke(SIKKE_REWARDS['battle_win_forfeit'], 'Battle victory (forfeit)')
            win_exp['sikke_result'] = win_sikke
            opp_sid = user_socket_map.get(opponent_id)
            if opp_sid:
                socketio.emit('battle_result', {
                    'battle_id': battle_id, 'winner_id': opponent_id,
                    'you_won': True, 'forfeit': True,
                    'message': 'Your opponent forfeited! You win!',
                    'exp_result': win_exp,
                }, to=opp_sid)
    battle.status = 'finished'
    battle.finished_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Left battle'}), 200


@app.route('/api/battle/history', methods=['GET'])
def battle_history():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    battles = Battle.query.filter(
        ((Battle.player1_id == user_id) | (Battle.player2_id == user_id)),
        Battle.status == 'finished'
    ).order_by(Battle.finished_at.desc()).limit(10).all()
    result = []
    for b in battles:
        opp_id = b.player2_id if b.player1_id == user_id else b.player1_id
        opp = User.query.get(opp_id) if opp_id else None
        result.append({
            'battle_id': b.id, 'level': b.level,
            'opponent': opp.name if opp else 'Unknown',
            'you_won': b.winner_id == user_id,
            'date': b.finished_at.isoformat() if b.finished_at else None,
        })
    return jsonify(result), 200


# ==================== PRACTICE SYSTEM ====================

PRACTICE_PROBLEMS = {
    # ── EASY ──────────────────────────────────────────────────────────────────
    'easy': [
        {
            'id': 'e1', 'title': 'Sum of Two Numbers', 'difficulty': 'Easy',
            'tags': ['math', 'basics'],
            'description': 'Write a function `add(a, b)` that returns the sum of two numbers.\n\nExamples:\nadd(3, 4) → 7\nadd(-1, 5) → 4\nadd(0, 0) → 0',
            'starter': 'def add(a, b):\n    # Write your solution here\n    pass\n',
            'test_cases': [
                {'input': 'print(add(3, 4))', 'expected': '7'},
                {'input': 'print(add(-1, 5))', 'expected': '4'},
                {'input': 'print(add(0, 0))', 'expected': '0'},
                {'input': 'print(add(100, 200))', 'expected': '300'},
            ],
        },
        {
            'id': 'e2', 'title': 'FizzBuzz', 'difficulty': 'Easy',
            'tags': ['logic', 'conditionals'],
            'description': 'Write a function `fizzbuzz(n)` that returns:\n- "FizzBuzz" if divisible by both 3 and 5\n- "Fizz" if divisible by 3\n- "Buzz" if divisible by 5\n- The number as a string otherwise\n\nExamples:\nfizzbuzz(15) → "FizzBuzz"\nfizzbuzz(9) → "Fizz"\nfizzbuzz(10) → "Buzz"\nfizzbuzz(7) → "7"',
            'starter': 'def fizzbuzz(n):\n    # Write your solution here\n    pass\n',
            'test_cases': [
                {'input': 'print(fizzbuzz(15))', 'expected': 'FizzBuzz'},
                {'input': 'print(fizzbuzz(9))', 'expected': 'Fizz'},
                {'input': 'print(fizzbuzz(10))', 'expected': 'Buzz'},
                {'input': 'print(fizzbuzz(7))', 'expected': '7'},
            ],
        },
        {
            'id': 'e3', 'title': 'Count Vowels', 'difficulty': 'Easy',
            'tags': ['strings', 'loops'],
            'description': 'Write a function `count_vowels(s)` that counts the number of vowels (a, e, i, o, u) in a string, case-insensitive.\n\nExamples:\ncount_vowels("Hello World") → 3\ncount_vowels("aeiou") → 5\ncount_vowels("xyz") → 0',
            'starter': 'def count_vowels(s):\n    # Write your solution here\n    pass\n',
            'test_cases': [
                {'input': 'print(count_vowels("Hello World"))', 'expected': '3'},
                {'input': 'print(count_vowels("aeiou"))', 'expected': '5'},
                {'input': 'print(count_vowels("xyz"))', 'expected': '0'},
                {'input': 'print(count_vowels("AEIOU"))', 'expected': '5'},
            ],
        },
        {
            'id': 'e4', 'title': 'Palindrome Check', 'difficulty': 'Easy',
            'tags': ['strings'],
            'description': 'Write a function `is_palindrome(s)` that returns True if the string reads the same forwards and backwards, False otherwise.\n\nExamples:\nis_palindrome("racecar") → True\nis_palindrome("hello") → False\nis_palindrome("level") → True\nis_palindrome("a") → True',
            'starter': 'def is_palindrome(s):\n    # Write your solution here\n    pass\n',
            'test_cases': [
                {'input': 'print(is_palindrome("racecar"))', 'expected': 'True'},
                {'input': 'print(is_palindrome("hello"))', 'expected': 'False'},
                {'input': 'print(is_palindrome("level"))', 'expected': 'True'},
                {'input': 'print(is_palindrome("a"))', 'expected': 'True'},
            ],
        },
        {
            'id': 'e5', 'title': 'Reverse a String', 'difficulty': 'Easy',
            'tags': ['strings'],
            'description': 'Write a function `reverse_string(s)` that returns the string reversed.\n\nExamples:\nreverse_string("hello") → "olleh"\nreverse_string("Python") → "nohtyP"\nreverse_string("") → ""',
            'starter': 'def reverse_string(s):\n    # Write your solution here\n    pass\n',
            'test_cases': [
                {'input': 'print(reverse_string("hello"))', 'expected': 'olleh'},
                {'input': 'print(reverse_string("Python"))', 'expected': 'nohtyP'},
                {'input': 'print(reverse_string(""))', 'expected': ''},
                {'input': 'print(reverse_string("a"))', 'expected': 'a'},
            ],
        },
        {
            'id': 'e6', 'title': 'Find Maximum', 'difficulty': 'Easy',
            'tags': ['arrays', 'loops'],
            'description': 'Write a function `find_max(lst)` that returns the largest number in a list. Do not use the built-in max() function.\n\nExamples:\nfind_max([3, 1, 4, 1, 5]) → 5\nfind_max([-1, -5, -3]) → -1\nfind_max([42]) → 42',
            'starter': 'def find_max(lst):\n    # Write your solution here (without using max())\n    pass\n',
            'test_cases': [
                {'input': 'print(find_max([3, 1, 4, 1, 5]))', 'expected': '5'},
                {'input': 'print(find_max([-1, -5, -3]))', 'expected': '-1'},
                {'input': 'print(find_max([42]))', 'expected': '42'},
                {'input': 'print(find_max([0, 0, 0]))', 'expected': '0'},
            ],
        },
    ],
    # ── MEDIUM ────────────────────────────────────────────────────────────────
    'medium': [
        {
            'id': 'm1', 'title': 'Fibonacci Sequence', 'difficulty': 'Medium',
            'tags': ['recursion', 'math'],
            'description': 'Write a function `fibonacci(n)` that returns the nth Fibonacci number (0-indexed).\n\nfibonacci(0) → 0\nfibonacci(1) → 1\nfibonacci(6) → 8\nfibonacci(10) → 55\n\nBonus: Can you solve it iteratively for better performance?',
            'starter': 'def fibonacci(n):\n    # Write your solution here\n    pass\n',
            'test_cases': [
                {'input': 'print(fibonacci(0))', 'expected': '0'},
                {'input': 'print(fibonacci(1))', 'expected': '1'},
                {'input': 'print(fibonacci(6))', 'expected': '8'},
                {'input': 'print(fibonacci(10))', 'expected': '55'},
            ],
        },
        {
            'id': 'm2', 'title': 'Two Sum', 'difficulty': 'Medium',
            'tags': ['arrays', 'hash-map'],
            'description': 'Write a function `two_sum(nums, target)` that returns the indices of two numbers that add up to target. Assume exactly one solution exists.\n\nExamples:\ntwo_sum([2, 7, 11, 15], 9) → [0, 1]\ntwo_sum([3, 2, 4], 6) → [1, 2]\ntwo_sum([3, 3], 6) → [0, 1]',
            'starter': 'def two_sum(nums, target):\n    # Write your solution here\n    pass\n',
            'test_cases': [
                {'input': 'print(two_sum([2, 7, 11, 15], 9))', 'expected': '[0, 1]'},
                {'input': 'print(two_sum([3, 2, 4], 6))', 'expected': '[1, 2]'},
                {'input': 'print(two_sum([3, 3], 6))', 'expected': '[0, 1]'},
            ],
        },
        {
            'id': 'm3', 'title': 'Anagram Check', 'difficulty': 'Medium',
            'tags': ['strings', 'hash-map'],
            'description': 'Write a function `is_anagram(s, t)` that returns True if t is an anagram of s, False otherwise. Ignore spaces and case.\n\nExamples:\nis_anagram("listen", "silent") → True\nis_anagram("hello", "world") → False\nis_anagram("Astronomer", "Moon starer") → True',
            'starter': 'def is_anagram(s, t):\n    # Write your solution here\n    pass\n',
            'test_cases': [
                {'input': 'print(is_anagram("listen", "silent"))', 'expected': 'True'},
                {'input': 'print(is_anagram("hello", "world"))', 'expected': 'False'},
                {'input': 'print(is_anagram("Astronomer", "Moon starer"))', 'expected': 'True'},
            ],
        },
        {
            'id': 'm4', 'title': 'Flatten Nested List', 'difficulty': 'Medium',
            'tags': ['recursion', 'lists'],
            'description': 'Write a function `flatten(lst)` that takes a nested list and returns a flat list of all values.\n\nExamples:\nflatten([1, [2, 3], [4, [5, 6]]]) → [1, 2, 3, 4, 5, 6]\nflatten([1, 2, 3]) → [1, 2, 3]\nflatten([[1, [2]], [3, [4, [5]]]]) → [1, 2, 3, 4, 5]',
            'starter': 'def flatten(lst):\n    # Write your solution here\n    pass\n',
            'test_cases': [
                {'input': 'print(flatten([1, [2, 3], [4, [5, 6]]]))', 'expected': '[1, 2, 3, 4, 5, 6]'},
                {'input': 'print(flatten([1, 2, 3]))', 'expected': '[1, 2, 3]'},
                {'input': 'print(flatten([[1, [2]], [3, [4, [5]]]]))', 'expected': '[1, 2, 3, 4, 5]'},
            ],
        },
        {
            'id': 'm5', 'title': 'Valid Parentheses', 'difficulty': 'Medium',
            'tags': ['stack', 'strings'],
            'description': 'Write a function `is_valid(s)` that returns True if the parentheses string is valid (every open bracket has a matching close bracket in correct order).\n\nExamples:\nis_valid("()[]{}") → True\nis_valid("([)]") → False\nis_valid("{[]}") → True\nis_valid("(") → False',
            'starter': 'def is_valid(s):\n    # Write your solution here\n    pass\n',
            'test_cases': [
                {'input': 'print(is_valid("()[]{}"))' , 'expected': 'True'},
                {'input': 'print(is_valid("([)]"))', 'expected': 'False'},
                {'input': 'print(is_valid("{[]}"))', 'expected': 'True'},
                {'input': 'print(is_valid("("))', 'expected': 'False'},
            ],
        },
        {
            'id': 'm6', 'title': 'Binary Search', 'difficulty': 'Medium',
            'tags': ['search', 'algorithms'],
            'description': 'Write a function `binary_search(arr, target)` that returns the index of target in a sorted list, or -1 if not found.\n\nExamples:\nbinary_search([1, 3, 5, 7, 9], 5) → 2\nbinary_search([1, 3, 5, 7, 9], 4) → -1\nbinary_search([1], 1) → 0',
            'starter': 'def binary_search(arr, target):\n    # Write your solution here\n    pass\n',
            'test_cases': [
                {'input': 'print(binary_search([1, 3, 5, 7, 9], 5))', 'expected': '2'},
                {'input': 'print(binary_search([1, 3, 5, 7, 9], 4))', 'expected': '-1'},
                {'input': 'print(binary_search([1], 1))', 'expected': '0'},
                {'input': 'print(binary_search([], 5))', 'expected': '-1'},
            ],
        },
    ],
    # ── HARD ──────────────────────────────────────────────────────────────────
    'hard': [
        {
            'id': 'h1', 'title': 'Longest Common Subsequence', 'difficulty': 'Hard',
            'tags': ['dynamic-programming', 'strings'],
            'description': 'Write a function `lcs(s1, s2)` that returns the length of the longest common subsequence of two strings.\n\nExamples:\nlcs("abcde", "ace") → 3\nlcs("abc", "abc") → 3\nlcs("abc", "def") → 0',
            'starter': 'def lcs(s1, s2):\n    # Write your solution here (hint: try dynamic programming)\n    pass\n',
            'test_cases': [
                {'input': 'print(lcs("abcde", "ace"))', 'expected': '3'},
                {'input': 'print(lcs("abc", "abc"))', 'expected': '3'},
                {'input': 'print(lcs("abc", "def"))', 'expected': '0'},
                {'input': 'print(lcs("abcba", "abcbcba"))', 'expected': '5'},
            ],
        },
        {
            'id': 'h2', 'title': 'Word Ladder Length', 'difficulty': 'Hard',
            'tags': ['bfs', 'graphs', 'strings'],
            'description': 'Write a function `ladder_length(begin, end, word_list)` that returns the number of words in the shortest transformation sequence from begin to end (changing one letter at a time, each intermediate word must be in word_list). Return 0 if no path exists.\n\nExamples:\nladder_length("hit", "cog", ["hot","dot","dog","lot","log","cog"]) → 5\nladder_length("hit", "cog", ["hot","dot","dog","lot","log"]) → 0',
            'starter': 'def ladder_length(begin, end, word_list):\n    # Write your solution here\n    pass\n',
            'test_cases': [
                {'input': 'print(ladder_length("hit", "cog", ["hot","dot","dog","lot","log","cog"]))', 'expected': '5'},
                {'input': 'print(ladder_length("hit", "cog", ["hot","dot","dog","lot","log"]))', 'expected': '0'},
            ],
        },
        {
            'id': 'h3', 'title': 'Merge K Sorted Lists', 'difficulty': 'Hard',
            'tags': ['heaps', 'sorting', 'lists'],
            'description': 'Write a function `merge_k_sorted(lists)` that merges k sorted lists into one sorted list and returns it.\n\nExamples:\nmerge_k_sorted([[1,4,5],[1,3,4],[2,6]]) → [1,1,2,3,4,4,5,6]\nmerge_k_sorted([]) → []\nmerge_k_sorted([[1],[0]]) → [0,1]',
            'starter': 'def merge_k_sorted(lists):\n    # Write your solution here\n    pass\n',
            'test_cases': [
                {'input': 'print(merge_k_sorted([[1,4,5],[1,3,4],[2,6]]))', 'expected': '[1, 1, 2, 3, 4, 4, 5, 6]'},
                {'input': 'print(merge_k_sorted([]))', 'expected': '[]'},
                {'input': 'print(merge_k_sorted([[1],[0]]))', 'expected': '[0, 1]'},
            ],
        },
        {
            'id': 'h4', 'title': 'Trapping Rain Water', 'difficulty': 'Hard',
            'tags': ['two-pointers', 'arrays'],
            'description': 'Write a function `trap(height)` that computes how much water can be trapped between elevation bars.\n\nExamples:\ntrap([0,1,0,2,1,0,1,3,2,1,2,1]) → 6\ntrap([4,2,0,3,2,5]) → 9\ntrap([]) → 0',
            'starter': 'def trap(height):\n    # Write your solution here\n    pass\n',
            'test_cases': [
                {'input': 'print(trap([0,1,0,2,1,0,1,3,2,1,2,1]))', 'expected': '6'},
                {'input': 'print(trap([4,2,0,3,2,5]))', 'expected': '9'},
                {'input': 'print(trap([]))', 'expected': '0'},
            ],
        },
    ],
}

PRACTICE_AI_SYSTEM = """You are an expert competitive programming coach and Python mentor.

A student has submitted code for a practice problem. Analyze it deeply and return ONLY valid JSON (no markdown fences).

JSON schema (all fields required):
{
  "verdict": "PASS" | "PARTIAL" | "FAIL" | "ERROR",
  "test_results": [
    {"case": 1, "passed": true|false, "expected": "<val>", "actual": "<val>", "note": "<brief note>"}
  ],
  "summary": "<1-2 sentences: plain English verdict>",
  "strengths": ["<what they did well>"],
  "issues": ["<specific bugs or logic errors>"],
  "hints": ["<targeted hints — don't give the answer, guide thinking>"],
  "time_complexity": "<Big-O with explanation>",
  "space_complexity": "<Big-O with explanation>",
  "better_approach": "<if a significantly better algorithm exists, describe it briefly>",
  "code_quality": "Excellent | Good | Needs Work | Poor",
  "encouragement": "<short personalized motivational note>"
}

Rules:
- PASS = all tests pass
- PARTIAL = some tests pass
- FAIL = all tests fail
- ERROR = syntax error or crash
- Give educational hints — never reveal the full solution
- Be specific about line numbers or code patterns when citing issues
- Always check edge cases"""


@app.route('/api/practice/problems', methods=['GET'])
def get_practice_problems():
    """Return all practice problems (metadata only, no test case inputs/expected for security)."""
    difficulty = request.args.get('difficulty', None)
    result = []
    for diff, problems in PRACTICE_PROBLEMS.items():
        if difficulty and diff != difficulty.lower():
            continue
        for p in problems:
            result.append({
                'id': p['id'],
                'title': p['title'],
                'difficulty': p['difficulty'],
                'tags': p['tags'],
                'description': p['description'],
                'starter': p['starter'],
            })
    return jsonify(result), 200


@app.route('/api/practice/problem/<problem_id>', methods=['GET'])
def get_practice_problem(problem_id):
    """Return a single practice problem."""
    for diff, problems in PRACTICE_PROBLEMS.items():
        for p in problems:
            if p['id'] == problem_id:
                return jsonify({
                    'id': p['id'],
                    'title': p['title'],
                    'difficulty': p['difficulty'],
                    'tags': p['tags'],
                    'description': p['description'],
                    'starter': p['starter'],
                }), 200
    return jsonify({'error': 'Problem not found'}), 404


@app.route('/api/practice/submit', methods=['POST'])
def submit_practice():
    """
    Run the student's code against test cases and get AI feedback.
    Adaptive: tracks submission history to tune hint specificity.
    """
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    data = request.get_json()
    problem_id = data.get('problem_id')
    user_code = data.get('code', '')
    attempt_number = data.get('attempt_number', 1)  # frontend tracks this

    # Find the problem
    problem = None
    for diff, problems in PRACTICE_PROBLEMS.items():
        for p in problems:
            if p['id'] == problem_id:
                problem = p
                break

    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    # Run all test cases
    raw_results = []
    for tc in problem['test_cases']:
        full_code = user_code + '\n' + tc['input']
        run = execute_code_safely(full_code)
        actual = run['stdout'].strip() if run['success'] else run['stderr'].strip()
        raw_results.append({
            'input': tc['input'],
            'expected': tc['expected'].strip(),
            'actual': actual,
            'runtime_passed': actual == tc['expected'].strip() and run['success'],
            'timeout': run['timeout'],
            'error': run['stderr'] if not run['success'] else '',
        })

    all_passed = all(r['runtime_passed'] for r in raw_results)
    any_passed = any(r['runtime_passed'] for r in raw_results)

    # Build prompt for AI
    test_summary = '\n'.join(
        f"  Test {i+1}: input=`{r['input']}` expected=`{r['expected']}` got=`{r['actual']}` passed={r['runtime_passed']}"
        for i, r in enumerate(raw_results)
    )

    hint_instruction = ""
    if attempt_number >= 3:
        hint_instruction = "\nThe student has attempted this problem multiple times — give more specific, direct hints."
    elif attempt_number == 2:
        hint_instruction = "\nThis is the student's second attempt — hints can be slightly more specific."
    else:
        hint_instruction = "\nThis is the student's first attempt — give gentle, directional hints only."

    user_msg = f"""Problem: {problem['title']} (Difficulty: {problem['difficulty']})

Problem description:
{problem['description']}

Student code (attempt #{attempt_number}):
```python
{user_code}
```

Runtime test results:
{test_summary}
{hint_instruction}

Analyze and return the JSON verdict."""

    ai_raw = call_gemini(PRACTICE_AI_SYSTEM, user_msg)

    ai_verdict = None
    if ai_raw not in ('__NO_KEY__', '__API_ERROR__'):
        try:
            clean = ai_raw.strip()
            if clean.startswith('```'):
                clean = clean.split('```')[1]
                if clean.startswith('json'):
                    clean = clean[4:]
            clean = clean.strip().rstrip('`').strip()
            ai_verdict = json.loads(clean)
        except Exception:
            ai_verdict = None

    # Build per-test result list
    test_results = []
    for i, r in enumerate(raw_results):
        ai_tc = {}
        if ai_verdict and 'test_results' in ai_verdict and i < len(ai_verdict['test_results']):
            ai_tc = ai_verdict['test_results'][i]
        test_results.append({
            'passed': ai_tc.get('passed', r['runtime_passed']),
            'expected': r['expected'],
            'actual': r['actual'],
            'note': ai_tc.get('note', ''),
        })

    # XP reward
    exp_result = None
    if user_id:
        user = User.query.get(user_id)
        already_solved=CodingSubmission.query.filter_by(user_id=user_id, problem_id=problem['id'], success=True).first() is not None
        if all_passed:
            exp_amt = EXP_REWARDS['code_success'] if not already_solved else 0
        elif any_passed:
            exp_amt = EXP_REWARDS['code_attempt'] + 5
        else:
            exp_amt = EXP_REWARDS['code_attempt']
        # Save submission
        ai_text = ai_verdict.get('summary', '') if ai_verdict else ''
        db.session.add(CodingSubmission(
            user_id=user_id, 
            problem_id=problem['id'],
            code=user_code, language='python',
            output='\n'.join(r['actual'] for r in raw_results),
            ai_feedback=ai_text, 
            success=all_passed,
        ))
        db.session.commit()
        reason=f'Practice: {problem["title"]}'
        if all_passed and already_solved:
            reason+="(Re-Solve)"
        exp_result = user.award_exp(exp_amt, reason)

    return jsonify({
        'all_passed': all_passed,
        'any_passed': any_passed,
        'test_results': test_results,
        'ai': ai_verdict,
        'exp_result': exp_result,
    }), 200


@app.route('/api/practice/hint', methods=['POST'])
def get_practice_hint():
    """Get an AI-generated hint for a specific problem without submitting code."""
    data = request.get_json()
    problem_id = data.get('problem_id')
    user_code = data.get('code', '')
    hint_level = data.get('hint_level', 1)  # 1=vague, 2=medium, 3=specific

    problem = None
    for diff, problems in PRACTICE_PROBLEMS.items():
        for p in problems:
            if p['id'] == problem_id:
                problem = p
                break

    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    specificity = {1: "very vague, just a nudge", 2: "moderately specific", 3: "specific but don't reveal full solution"}
    system = f"""You are a Socratic coding mentor. Give a {specificity.get(hint_level, 'vague')} hint.
Return ONLY a JSON object: {{"hint": "<the hint text>", "concept": "<key concept to study>"}}"""

    code_section = f"\n\nStudent's current code:\n```python\n{user_code}\n```" if user_code.strip() else ""
    user_msg = f"Problem: {problem['title']}\n{problem['description']}{code_section}\n\nProvide hint level {hint_level}."
    ai_raw = call_gemini(system, user_msg)

    if ai_raw in ('__NO_KEY__', '__API_ERROR__'):
        return jsonify({'hint': 'Think about the problem step by step. Break it into smaller parts.', 'concept': 'Problem decomposition'}), 200

    try:
        clean = ai_raw.strip().lstrip('```json').lstrip('```').rstrip('```').strip()
        result = json.loads(clean)
        return jsonify(result), 200
    except Exception:
        return jsonify({'hint': ai_raw[:300], 'concept': ''}), 200


# ==================== UTILITY ====================

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    courses = Course.query.filter(
        (Course.title.contains(query)) | (Course.description.contains(query))
    ).all()
    return jsonify([{'id': c.id, 'title': c.title, 'code': c.code,
                     'instructor': c.instructor, 'type': 'course'} for c in courses]), 200


@app.route('/api/simplify-text', methods=['POST'])
def simplify_text():
    data = request.get_json()
    text = data['text']
    target_level = data.get('level', 'Grade 5')
    return jsonify({
        'original': text,
        'simplified': f"[Simplified to {target_level}]\n\n{text}",
        'level': target_level,
    }), 200


# ==================== WEBSOCKET ====================

@socketio.on('connect')
def on_connect():
    print(f'[WS] Connected: {request.sid}')


@socketio.on('disconnect')
def on_disconnect():
    to_remove = [uid for uid, sid in user_socket_map.items() if sid == request.sid]
    for uid in to_remove:
        del user_socket_map[uid]
        for q in matchmaking_queue.values():
            if uid in q:
                q.remove(uid)
    print(f'[WS] Disconnected: {request.sid}')


@socketio.on('authenticate')
def on_authenticate(data):
    token = data.get('token', '')
    user_id = verify_token(token)
    if user_id:
        user_socket_map[user_id] = request.sid
        emit('authenticated', {'user_id': user_id, 'status': 'ok'})
    else:
        emit('authenticated', {'status': 'error', 'message': 'Invalid token'})


# ==================== STATIC ====================

@app.route('/')
def serve_landing():
    return send_from_directory('static', 'new6.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


# ==================== DB INIT ====================

def migrate_db():
    """Safely add new columns to existing SQLite DB without wiping data."""
    import sqlite3, os
    db_path = 'education_portal.db'
    if not os.path.exists(db_path):
        return
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(user)")
        cols = [row[1] for row in cur.fetchall()]
        if 'sikke' not in cols:
            cur.execute("ALTER TABLE user ADD COLUMN sikke INTEGER NOT NULL DEFAULT 0")
            conn.commit()
            print("✓ DB migrated: added 'sikke' column")
        conn.close()
    except Exception as e:
        print(f"[DB migration] {e}")


def init_sample_data():
    db.create_all()
    if Course.query.first():
        return  # already seeded
    for cd in [
        {'title': 'Introduction to Python', 'code': 'CS101', 'instructor': 'Dr. Sarah Johnson',
         'description': 'Learn Python programming from scratch', 'level': 'Beginner',
         'category': 'Programming', 'progress_percentage': 0},
        {'title': 'Data Structures', 'code': 'CS201', 'instructor': 'Prof. Michael Chen',
         'description': 'Master fundamental data structures', 'level': 'Intermediate',
         'category': 'Computer Science', 'progress_percentage': 0},
        {'title': 'Web Development', 'code': 'WEB101', 'instructor': 'Emma Williams',
         'description': 'Build modern web applications', 'level': 'Beginner',
         'category': 'Web Development', 'progress_percentage': 0},
        {'title': 'Machine Learning', 'code': 'ML301', 'instructor': 'Dr. James Anderson',
         'description': 'Introduction to machine learning algorithms', 'level': 'Advanced',
         'category': 'AI/ML', 'progress_percentage': 0},
    ]:
        db.session.add(Course(**cd))
    db.session.commit()
    course = Course.query.first()
    quiz = Quiz(course_id=course.id, title='Python Basics Quiz', difficulty='Easy')
    db.session.add(quiz)
    db.session.commit()
    for qd in [
        {'quiz_id': quiz.id, 'question_text': 'What is the correct way to create a variable in Python?',
         'option_a': 'var x = 5', 'option_b': 'x = 5', 'option_c': 'int x = 5',
         'option_d': 'declare x = 5', 'correct_answer': 'B',
         'explanation': 'In Python, simply assign a value to a variable name.'},
        {'quiz_id': quiz.id, 'question_text': 'Which of these is a valid Python data type?',
         'option_a': 'String', 'option_b': 'Integer', 'option_c': 'List',
         'option_d': 'All of the above', 'correct_answer': 'D',
         'explanation': 'Python supports all these types.'},
        {'quiz_id': quiz.id, 'question_text': 'How do you write a comment in Python?',
         'option_a': '// comment', 'option_b': '/* comment */', 'option_c': '# comment',
         'option_d': '<!-- comment -->', 'correct_answer': 'C',
         'explanation': 'Python uses # for comments.'},
        {'quiz_id': quiz.id, 'question_text': "What will print(type(5)) output?",
         'option_a': 'number', 'option_b': "<class 'int'>", 'option_c': 'integer',
         'option_d': '5', 'correct_answer': 'B',
         'explanation': 'type() returns the class type.'},
        {'quiz_id': quiz.id, 'question_text': 'Which keyword defines a function in Python?',
         'option_a': 'function', 'option_b': 'func', 'option_c': 'def',
         'option_d': 'define', 'correct_answer': 'C',
         'explanation': "Python uses 'def' to define functions."},
    ]:
        db.session.add(Question(**qd))
    db.session.commit()
    print("✓ Sample data initialized!")


if __name__ == '__main__':
    with app.app_context():
        migrate_db()
        init_sample_data()
    print("\n" + "=" * 50)
    print("🚀 Education Portal — XP + Sikke + Battle System")
    print("=" * 50)
    print("Server:    http://localhost:5000")
    print("WebSocket: Enabled (flask-socketio)")
    print("=" * 50 + "\n")
    # socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
    port=int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)