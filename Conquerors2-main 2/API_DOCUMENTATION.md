# Education Portal API Documentation

Base URL: `http://localhost:5000/api`

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

---

## 1. Authentication Endpoints

### 1.1 Register User

**Endpoint:** `POST /auth/register`

**Description:** Create a new user account

**Request Body:**
```json
{
  "student_id": "PEC20CS001",
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "learner"  // optional, defaults to "learner"
}
```

**Response (201 Created):**
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

**Error Responses:**
- `400`: Email or Student ID already exists

---

### 1.2 Login

**Endpoint:** `POST /auth/login`

**Description:** Authenticate user and receive JWT token

**Request Body:**
```json
{
  "student_id": "PEC20CS001",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
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

**Error Responses:**
- `401`: Invalid credentials

---

## 2. User Endpoints

### 2.1 Get User Profile

**Endpoint:** `GET /user/profile`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "student_id": "PEC20CS001",
  "role": "learner",
  "reading_level": "Grade 8",
  "visual_preference": "Normal Mode",
  "learning_pattern": "Mixed"
}
```

---

### 2.2 Update User Preferences

**Endpoint:** `PUT /user/preferences`

**Authentication:** Required

**Request Body:**
```json
{
  "reading_level": "Grade 5",
  "visual_preference": "High Contrast Mode",
  "learning_pattern": "Audio Preferred"
}
```

**Response (200 OK):**
```json
{
  "message": "Preferences updated successfully"
}
```

---

### 2.3 Get User Statistics

**Endpoint:** `GET /user/stats`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "enrolled_courses": 3,
  "quizzes_completed": 5,
  "average_score": 85.6,
  "coding_submissions": 10
}
```

---

## 3. Course Endpoints

### 3.1 Get All Courses

**Endpoint:** `GET /courses`

**Authentication:** Not required

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Introduction to Python",
    "code": "CS101",
    "instructor": "Dr. Sarah Johnson",
    "description": "Learn Python programming from scratch",
    "level": "Beginner",
    "category": "Programming",
    "progress": 0
  },
  {
    "id": 2,
    "title": "Data Structures",
    "code": "CS201",
    "instructor": "Prof. Michael Chen",
    "description": "Master fundamental data structures",
    "level": "Intermediate",
    "category": "Computer Science",
    "progress": 0
  }
]
```

---

### 3.2 Get Specific Course

**Endpoint:** `GET /courses/<course_id>`

**Authentication:** Not required

**Parameters:**
- `course_id` (integer): Course ID

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Introduction to Python",
  "code": "CS101",
  "instructor": "Dr. Sarah Johnson",
  "description": "Learn Python programming from scratch",
  "level": "Beginner",
  "category": "Programming",
  "progress": 0
}
```

**Error Responses:**
- `404`: Course not found

---

### 3.3 Enroll in Course

**Endpoint:** `POST /courses/enroll`

**Authentication:** Required

**Request Body:**
```json
{
  "course_id": 1
}
```

**Response (201 Created):**
```json
{
  "message": "Enrolled successfully"
}
```

**Error Responses:**
- `400`: Already enrolled in this course

---

### 3.4 Get My Enrolled Courses

**Endpoint:** `GET /courses/my-courses`

**Authentication:** Required

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Introduction to Python",
    "code": "CS101",
    "instructor": "Dr. Sarah Johnson",
    "description": "Learn Python programming from scratch",
    "level": "Beginner",
    "category": "Programming",
    "progress": 45
  }
]
```

---

## 4. Quiz Endpoints

### 4.1 Get Course Quizzes

**Endpoint:** `GET /quizzes/<course_id>`

**Authentication:** Not required

**Parameters:**
- `course_id` (integer): Course ID

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Python Basics Quiz",
    "difficulty": "Easy",
    "question_count": 5
  }
]
```

---

### 4.2 Get Quiz Questions

**Endpoint:** `GET /quiz/<quiz_id>/questions`

**Authentication:** Not required

**Parameters:**
- `quiz_id` (integer): Quiz ID

**Response (200 OK):**
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
    "explanation": "In Python, you simply assign a value to a variable name without declaring its type."
  },
  {
    "id": 2,
    "question": "Which of these is a valid Python data type?",
    "options": {
      "A": "String",
      "B": "Integer",
      "C": "List",
      "D": "All of the above"
    },
    "explanation": "Python supports all these data types: strings, integers, lists, and many more."
  }
]
```

---

### 4.3 Submit Quiz Answers

**Endpoint:** `POST /quiz/submit`

**Authentication:** Required

**Request Body:**
```json
{
  "quiz_id": 1,
  "answers": {
    "1": "B",
    "2": "D",
    "3": "C",
    "4": "B",
    "5": "C"
  }
}
```

**Response (200 OK):**
```json
{
  "score": 4,
  "total": 5,
  "percentage": 80.0,
  "results": [
    {
      "question_id": 1,
      "correct": true,
      "correct_answer": "B",
      "user_answer": "B"
    },
    {
      "question_id": 2,
      "correct": true,
      "correct_answer": "D",
      "user_answer": "D"
    },
    {
      "question_id": 3,
      "correct": true,
      "correct_answer": "C",
      "user_answer": "C"
    },
    {
      "question_id": 4,
      "correct": false,
      "correct_answer": "B",
      "user_answer": "A"
    },
    {
      "question_id": 5,
      "correct": true,
      "correct_answer": "C",
      "user_answer": "C"
    }
  ]
}
```

---

## 5. Coding Judge Endpoint

### 5.1 Execute and Judge Code

**Endpoint:** `POST /judge`

**Authentication:** Optional (saves to database if authenticated)

**Request Body:**
```json
{
  "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nprint(fibonacci(10))",
  "language": "python"
}
```

**Response (200 OK - Success):**
```json
{
  "runOutput": "55\n",
  "aiAnalysis": "✓ Good: You're using functions to organize your code. ✓ Concise: Your solution is compact and readable. ✓ Success: Your code executed without errors!",
  "success": true
}
```

**Response (200 OK - Error):**
```json
{
  "runOutput": "Traceback (most recent call last):\n  File \"temp.py\", line 1\n    def fibonacci(n)\n                   ^\nSyntaxError: invalid syntax",
  "aiAnalysis": "✗ Error detected: Review the error message and fix the issue.",
  "success": false
}
```

**Response (200 OK - Timeout):**
```json
{
  "runOutput": "Execution timed out",
  "aiAnalysis": "Your code took too long to execute. Check for infinite loops.",
  "success": false
}
```

---

## 6. Utility Endpoints

### 6.1 Search Courses

**Endpoint:** `GET /search`

**Authentication:** Not required

**Query Parameters:**
- `q` (string): Search query

**Example:** `GET /search?q=python`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Introduction to Python",
    "code": "CS101",
    "instructor": "Dr. Sarah Johnson",
    "type": "course"
  }
]
```

---

### 6.2 Simplify Text

**Endpoint:** `POST /simplify-text`

**Authentication:** Not required

**Request Body:**
```json
{
  "text": "Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods with the aid of chlorophyll.",
  "level": "Grade 5"
}
```

**Response (200 OK):**
```json
{
  "original": "Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods with the aid of chlorophyll.",
  "simplified": "[Simplified to Grade 5]\n\nPhotosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods with the aid of chlorophyll.",
  "level": "Grade 5"
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 201  | Created |
| 400  | Bad Request - Invalid input data |
| 401  | Unauthorized - Invalid or missing token |
| 404  | Not Found - Resource doesn't exist |
| 500  | Internal Server Error |

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider implementing:
- 100 requests per hour for unauthenticated users
- 1000 requests per hour for authenticated users
- Special limits for code execution (e.g., 50 per hour)

---

## CORS Policy

By default, CORS is enabled for all origins in development. For production, configure specific allowed origins in `app.py`.

---

## Pagination

Currently not implemented. For large datasets, consider adding pagination:

```
GET /api/courses?page=1&limit=10
```

---

## WebSocket Support

Not currently implemented. Future versions may include WebSocket support for:
- Real-time collaboration
- Live quiz competitions
- Instant notifications

---

## Example Code Snippets

### JavaScript (Fetch API)

```javascript
// Login
const login = async (studentId, password) => {
  const response = await fetch('http://localhost:5000/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ student_id: studentId, password })
  });
  return await response.json();
};

// Get courses with auth
const getCourses = async (token) => {
  const response = await fetch('http://localhost:5000/api/courses/my-courses', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
};
```

### Python (Requests)

```python
import requests

# Login
response = requests.post('http://localhost:5000/api/auth/login', json={
    'student_id': 'PEC20CS001',
    'password': 'password123'
})
token = response.json()['token']

# Get user stats
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:5000/api/user/stats', headers=headers)
stats = response.json()
print(stats)
```

### cURL

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"student_id":"TEST001","name":"Test User","email":"test@test.com","password":"test123"}'

# Login and get token
TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"student_id":"TEST001","password":"test123"}' \
  | jq -r '.token')

# Get user stats
curl http://localhost:5000/api/user/stats \
  -H "Authorization: Bearer $TOKEN"
```

---

## Version History

- **v1.0** (Current) - Initial release with core features
  - User authentication
  - Course management
  - Quiz system
  - Code execution
  - Basic AI features

---

## Support

For issues or questions, please check:
1. README.md for setup instructions
2. This documentation for API details
3. Server logs for debugging errors

Happy coding! 🚀
