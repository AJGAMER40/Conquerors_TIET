# 🚀 QUICK START GUIDE - Education Portal

## What You Have

A complete full-stack education platform with:

✅ **Backend (Python Flask)**
- User authentication with JWT
- Course management system
- Interactive quiz engine
- Code execution with AI feedback
- RESTful API
- SQLite database

✅ **Frontend (HTML/CSS/JavaScript)**
- Beautiful landing page
- Student dashboard
- Quiz interface
- Code editor (Monaco Editor)
- Real-time stats

## 📦 Files Included

```
education-portal/
│
├── app.py                     # Main Flask backend
├── requirements.txt           # Python dependencies
├── README.md                  # Full documentation
├── API_DOCUMENTATION.md       # Complete API docs
├── test_api.py               # API testing script
├── setup.sh                  # Setup script
│
└── static/                   # Frontend files
    ├── new6.html            # Landing page
    └── new3.html            # Student dashboard
```

## ⚡ Installation (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start Backend
```bash
python app.py
```

You'll see:
```
==================================================
🚀 Education Portal Backend Server
==================================================
Server running on: http://localhost:5000
```

### Step 3: Open Browser
Go to: **http://localhost:5000**

## 🎯 First Time Usage

### 1. Create Account

The app will show a login modal. You need to create an account first.

**Using Python (Recommended for first user):**
```python
import requests

requests.post('http://localhost:5000/api/auth/register', json={
    'student_id': 'STUDENT001',
    'name': 'Your Name',
    'email': 'your@email.com',
    'password': 'your_password'
})
```

**Or using cURL:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STUDENT001",
    "name": "Your Name", 
    "email": "your@email.com",
    "password": "your_password"
  }'
```

### 2. Login

Once registered, login with:
- **Student ID**: STUDENT001
- **Password**: your_password

### 3. Explore Features

- **Dashboard**: View enrolled courses and stats
- **Take Quiz**: Test your knowledge
- **Coding Battle**: Write and execute code with AI feedback

## 🧪 Test Everything Works

Run the test script:
```bash
python test_api.py
```

This will:
- Create a test user
- Test all API endpoints
- Show you everything working

## 📖 What's Pre-loaded

The database comes with:
- ✅ 4 Sample Courses
  - Introduction to Python
  - Data Structures
  - Web Development
  - Machine Learning

- ✅ 1 Sample Quiz (Python Basics)
  - 5 Multiple choice questions
  - Instant feedback
  - Score tracking

## 🎨 Frontend Pages

### Landing Page (`/`)
- Choose between Educator and Learner paths
- Modern glass-morphism design
- Smooth animations

### Student Dashboard (`/new3.html`)
- View courses
- Take quizzes
- Submit code
- Track progress
- AI insights

## 🔗 Important URLs

| URL | Description |
|-----|-------------|
| http://localhost:5000/ | Landing page |
| http://localhost:5000/new3.html | Student dashboard |
| http://localhost:5000/api/courses | API: Get courses |
| http://localhost:5000/api/quiz/1/questions | API: Get quiz |

## 💡 Common Tasks

### Enroll in a Course
```javascript
fetch('http://localhost:5000/api/courses/enroll', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: JSON.stringify({ course_id: 1 })
})
```

### Take a Quiz
1. Click "Take Quiz" in sidebar
2. Answer questions
3. Get instant results
4. View explanations

### Submit Code
1. Click "Coding Battle" in sidebar
2. Write Python code in Monaco editor
3. Click "Submit to AI Judge"
4. Get execution results + AI feedback

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Can't connect from frontend
- Ensure backend is running on port 5000
- Check browser console for errors
- Verify no CORS issues

### Database issues
```bash
# Delete and recreate database
rm education_portal.db
python app.py  # Will auto-create new DB
```

## 📚 Next Steps

1. **Read Full Documentation**: See `README.md`
2. **Check API Docs**: See `API_DOCUMENTATION.md`
3. **Add More Courses**: Use the API to add courses
4. **Customize Frontend**: Edit HTML files in `static/`
5. **Deploy**: Follow deployment section in README.md

## 🎓 Sample Workflow

```
1. User visits landing page (new6.html)
   ↓
2. Clicks "For Learners" → Goes to new3.html
   ↓
3. Sees login modal → Registers/Logs in
   ↓
4. Views dashboard with:
   - Stats (courses, quizzes, scores)
   - Enrolled courses
   - AI insights
   ↓
5. Clicks "Take Quiz" → Answers questions
   ↓
6. Gets results with explanations
   ↓
7. Clicks "Coding Battle" → Writes code
   ↓
8. Submits code → Gets AI feedback
```

## ⚠️ Important Notes

**Security (Development Mode)**
- Change SECRET_KEY in app.py for production
- Don't commit secrets to git
- Use HTTPS in production

**Performance**
- SQLite is for development only
- Use PostgreSQL/MySQL for production
- Add caching for better performance

**Code Execution**
- Currently executes on server (not sandboxed)
- For production, use Docker containers
- Add timeout and resource limits

## 🆘 Need Help?

1. Check README.md for detailed info
2. Check API_DOCUMENTATION.md for API details
3. Run test_api.py to verify everything works
4. Check server logs in terminal

## ✅ Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed
- [ ] Backend server running
- [ ] Can access http://localhost:5000
- [ ] Created user account
- [ ] Successfully logged in
- [ ] Viewed dashboard
- [ ] Enrolled in a course
- [ ] Completed a quiz
- [ ] Submitted code

---

**You're all set! Happy learning! 🎉**

For full documentation, see README.md
For API details, see API_DOCUMENTATION.md
