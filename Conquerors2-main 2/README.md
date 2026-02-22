# Education Portal - Full Stack Integration Guide

This is a complete full-stack education portal with Python Flask backend and interactive HTML frontends.

## 🚀 Features

### Frontend Features
- **Landing Page** (`new6.html`) - Choose between Educator and Learner paths
- **Student Portal** (`new3.html`) - Complete learning dashboard with:
  - Course enrollment and progress tracking
  - Interactive quizzes with AI feedback
  - Live coding challenges with code execution
  - Personalized AI insights (reading level, visual preferences, learning patterns)
  - Real-time statistics and analytics

### Backend Features
- **User Authentication** - JWT-based secure authentication
- **Course Management** - Create, enroll, and track courses
- **Quiz System** - Dynamic quizzes with instant feedback
- **Code Execution** - Sandboxed Python code execution with AI analysis
- **AI Features** - Text simplification, learning pattern analysis
- **RESTful API** - Complete API for all operations
- **SQLite Database** - Persistent data storage

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## ⚡ Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Backend Server

```bash
python app.py
```

You should see:
```
==================================================
🚀 Education Portal Backend Server
==================================================
Server running on: http://localhost:5000
API Documentation: http://localhost:5000/api/docs

Press CTRL+C to stop the server
==================================================
```

### 3. Open the Application

Open your web browser and navigate to:
- **Landing Page**: http://localhost:5000/
- **Student Portal**: http://localhost:5000/new3.html

### 4. Login with Sample Account

The system initializes with sample data. Use these credentials to login:

**Create a new account** through the login modal:
- Click "Register" (you'll need to modify the HTML to add a register link)
- Or manually create via API (see below)

## 📁 Project Structure

```
education-portal/
│
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── education_portal.db     # SQLite database (auto-created)
│
└── static/                 # Frontend files
    ├── new6.html          # Landing page
    └── new3.html          # Student dashboard
```

## 🔌 API Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "student_id": "PEC20CS001",
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "learner"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "student_id": "PEC20CS001",
    "role": "learner"
  }
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "student_id": "PEC20CS001",
  "password": "password123"
}
```

### User Endpoints

#### Get User Profile
```http
GET /api/user/profile
Authorization: Bearer <token>
```

#### Get User Statistics
```http
GET /api/user/stats
Authorization: Bearer <token>
```

**Response:**
```json
{
  "enrolled_courses": 3,
  "quizzes_completed": 5,
  "average_score": 85.6,
  "coding_submissions": 10
}
```

#### Update User Preferences
```http
PUT /api/user/preferences
Authorization: Bearer <token>
Content-Type: application/json

{
  "reading_level": "Grade 5",
  "visual_preference": "High Contrast Mode",
  "learning_pattern": "Audio Preferred"
}
```

### Course Endpoints

#### Get All Courses
```http
GET /api/courses
```

#### Get Specific Course
```http
GET /api/courses/<course_id>
```

#### Enroll in Course
```http
POST /api/courses/enroll
Authorization: Bearer <token>
Content-Type: application/json

{
  "course_id": 1
}
```

#### Get My Enrolled Courses
```http
GET /api/courses/my-courses
Authorization: Bearer <token>
```

### Quiz Endpoints

#### Get Quiz Questions
```http
GET /api/quiz/<quiz_id>/questions
```

**Response:**
```json
[
  {
    "id": 1,
    "question": "What is the correct way to create a variable in Python?",
    "options": {
      "A": "var x = 5",
      "B": "x = 5",
      "C": "int x = 5",
      "D": "declare x = 5"
    },
    "explanation": "In Python, you simply assign a value..."
  }
]
```

#### Submit Quiz Answers
```http
POST /api/quiz/submit
Authorization: Bearer <token>
Content-Type: application/json

{
  "quiz_id": 1,
  "answers": {
    "1": "B",
    "2": "D",
    "3": "C"
  }
}
```

**Response:**
```json
{
  "score": 3,
  "total": 5,
  "percentage": 60.0,
  "results": [
    {
      "question_id": 1,
      "correct": true,
      "correct_answer": "B",
      "user_answer": "B"
    }
  ]
}
```

### Coding Judge Endpoint

#### Execute and Judge Code
```http
POST /api/judge
Authorization: Bearer <token>
Content-Type: application/json

{
  "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nprint(fibonacci(10))",
  "language": "python"
}
```

**Response:**
```json
{
  "runOutput": "55\n",
  "aiAnalysis": "✓ Good: You're using functions... ✓ Success: Your code executed without errors!",
  "success": true
}
```

### Search Endpoint

#### Search Courses
```http
GET /api/search?q=python
```

## 🎨 Frontend Integration Examples

### Login Example

```javascript
const API_BASE_URL = 'http://localhost:5000/api';

async function login(studentId, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            student_id: studentId,
            password: password
        })
    });
    
    const data = await response.json();
    
    if (data.token) {
        localStorage.setItem('authToken', data.token);
        // Redirect to dashboard
        window.location.href = '/new3.html';
    }
}
```

### Fetch User Data Example

```javascript
async function getUserStats() {
    const token = localStorage.getItem('authToken');
    
    const response = await fetch(`${API_BASE_URL}/user/stats`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    const stats = await response.json();
    
    // Update UI
    document.getElementById('enrolledCoursesCount').textContent = stats.enrolled_courses;
    document.getElementById('quizzesCompletedCount').textContent = stats.quizzes_completed;
    document.getElementById('averageScore').textContent = stats.average_score + '%';
}
```

### Submit Quiz Example

```javascript
async function submitQuiz(quizId, answers) {
    const token = localStorage.getItem('authToken');
    
    const response = await fetch(`${API_BASE_URL}/quiz/submit`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            quiz_id: quizId,
            answers: answers
        })
    });
    
    const result = await response.json();
    
    // Show results
    console.log(`Score: ${result.score}/${result.total} (${result.percentage}%)`);
}
```

## 🗄️ Database Schema

### User Table
- `id` (Primary Key)
- `student_id` (Unique)
- `name`
- `email` (Unique)
- `password_hash`
- `role` (learner/educator)
- `reading_level`
- `visual_preference`
- `learning_pattern`
- `created_at`

### Course Table
- `id` (Primary Key)
- `title`
- `code`
- `instructor`
- `description`
- `level`
- `category`
- `progress_percentage`
- `created_at`

### Quiz Table
- `id` (Primary Key)
- `course_id` (Foreign Key)
- `title`
- `difficulty`

### Question Table
- `id` (Primary Key)
- `quiz_id` (Foreign Key)
- `question_text`
- `option_a`, `option_b`, `option_c`, `option_d`
- `correct_answer`
- `explanation`

### Enrollment Table
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `course_id` (Foreign Key)
- `enrolled_at`
- `progress`

### QuizAttempt Table
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `quiz_id` (Foreign Key)
- `score`
- `total_questions`
- `completed_at`

### CodingSubmission Table
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `code`
- `language`
- `output`
- `ai_feedback`
- `submitted_at`

## 🔧 Configuration

### Change Secret Key

In `app.py`, update the secret key for production:

```python
app.config['SECRET_KEY'] = 'your-super-secret-key-here'
```

### Change Port

To run on a different port:

```python
app.run(debug=True, port=8080)  # Change 5000 to 8080
```

And update frontend API URLs in HTML files:

```javascript
const API_BASE_URL = 'http://localhost:8080/api';
```

### Enable CORS for Different Origins

```python
CORS(app, origins=['http://localhost:3000', 'https://yourdomain.com'])
```

## 🧪 Testing the API

### Using cURL

```bash
# Register a new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "TEST001",
    "name": "Test User",
    "email": "test@example.com",
    "password": "test123"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "TEST001",
    "password": "test123"
  }'

# Get courses
curl http://localhost:5000/api/courses

# Get user stats (replace TOKEN with actual token from login)
curl http://localhost:5000/api/user/stats \
  -H "Authorization: Bearer TOKEN"
```

### Using Python Requests

```python
import requests

# Register
response = requests.post('http://localhost:5000/api/auth/register', json={
    'student_id': 'TEST001',
    'name': 'Test User',
    'email': 'test@example.com',
    'password': 'test123'
})
print(response.json())

# Login
response = requests.post('http://localhost:5000/api/auth/login', json={
    'student_id': 'TEST001',
    'password': 'test123'
})
token = response.json()['token']

# Get user stats
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:5000/api/user/stats', headers=headers)
print(response.json())
```

## 🚀 Deployment

### Production Checklist

1. **Change Secret Key**: Use a strong, random secret key
2. **Disable Debug Mode**: Set `debug=False` in `app.run()`
3. **Use Production Database**: Replace SQLite with PostgreSQL or MySQL
4. **Add Environment Variables**: Store sensitive data in env variables
5. **Enable HTTPS**: Use SSL certificates
6. **Add Rate Limiting**: Protect against abuse
7. **Set Up Logging**: Monitor application health
8. **Add Input Validation**: Sanitize all user inputs
9. **Configure CORS Properly**: Only allow trusted origins
10. **Use Production WSGI Server**: Use Gunicorn or uWSGI instead of Flask's dev server

### Deploy with Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🐛 Troubleshooting

### Backend won't start
- Check if port 5000 is already in use
- Verify Python version (3.8+)
- Ensure all dependencies are installed

### Frontend can't connect to backend
- Verify backend is running on http://localhost:5000
- Check browser console for CORS errors
- Ensure API_BASE_URL in HTML matches your backend URL

### Login fails
- Check if database was initialized (should happen automatically)
- Try creating a new user via the register endpoint
- Verify credentials are correct

### Code execution fails
- Python 3 must be installed and in PATH
- Check file permissions for temporary file creation
- Review backend logs for detailed errors

## 📝 Adding New Features

### Add a New Course

```python
course = Course(
    title='New Course',
    code='NEW101',
    instructor='Dr. Smith',
    description='Course description',
    level='Beginner',
    category='Programming'
)
db.session.add(course)
db.session.commit()
```

### Add a New Quiz

```python
quiz = Quiz(
    course_id=1,
    title='New Quiz',
    difficulty='Medium'
)
db.session.add(quiz)
db.session.commit()

# Add questions
question = Question(
    quiz_id=quiz.id,
    question_text='Your question?',
    option_a='Option A',
    option_b='Option B',
    option_c='Option C',
    option_d='Option D',
    correct_answer='B',
    explanation='Because...'
)
db.session.add(question)
db.session.commit()
```

## 🎓 Sample Data

The application comes pre-loaded with:
- 4 sample courses (Python, Data Structures, Web Development, Machine Learning)
- 1 sample quiz with 5 questions on Python basics
- You'll need to create user accounts through the registration endpoint

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check browser console for frontend errors
4. Check terminal output for backend errors

## 📄 License

This project is for educational purposes. Modify and use as needed for your learning platform.

## 🔐 Security Notes

⚠️ **Important**: This is a development setup. For production:
- Never commit secret keys to version control
- Use environment variables for sensitive data
- Implement proper input validation and sanitization
- Add rate limiting to prevent abuse
- Use HTTPS in production
- Implement proper session management
- Add CSRF protection
- Sanitize all user inputs to prevent XSS and SQL injection
- Use secure password hashing (already implemented with Werkzeug)

## 🎉 Enjoy!

You now have a fully functional education portal with:
- User authentication and authorization
- Course management
- Interactive quizzes
- Code execution and AI feedback
- Personalized learning insights

Happy coding! 🚀
