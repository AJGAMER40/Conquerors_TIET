"""
Education Portal API Tests
Run this file to test all API endpoints
"""

import requests
import json

BASE_URL = 'http://localhost:5000/api'

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_api():
    print("\n🚀 Education Portal API Tests\n")
    
    # Test 1: Register User
    print_section("Test 1: Register New User")
    register_data = {
        'student_id': 'TEST001',
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'test123'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/register', json=register_data)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            token = data['token']
        else:
            print("⚠️  Registration failed (user might already exist)")
            token = None
    except Exception as e:
        print(f"❌ Error: {e}")
        token = None
    
    # Test 2: Login
    print_section("Test 2: Login")
    login_data = {
        'student_id': 'TEST001',
        'password': 'test123'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            token = data['token']
        else:
            print("❌ Login failed!")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 3: Get User Profile
    print_section("Test 3: Get User Profile")
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f'{BASE_URL}/user/profile', headers=headers)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            print("✅ Profile retrieved successfully!")
        else:
            print("❌ Failed to get profile!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Get All Courses
    print_section("Test 4: Get All Courses")
    
    try:
        response = requests.get(f'{BASE_URL}/courses')
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Found {len(data)} courses")
        if len(data) > 0:
            print(f"First course: {json.dumps(data[0], indent=2)}")
            print("✅ Courses retrieved successfully!")
        else:
            print("⚠️  No courses found")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Enroll in Course
    print_section("Test 5: Enroll in Course")
    enroll_data = {'course_id': 1}
    
    try:
        response = requests.post(f'{BASE_URL}/courses/enroll', 
                                json=enroll_data, 
                                headers=headers)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code in [201, 400]:  # 400 if already enrolled
            print("✅ Enrollment processed!")
        else:
            print("❌ Enrollment failed!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Get My Courses
    print_section("Test 6: Get My Enrolled Courses")
    
    try:
        response = requests.get(f'{BASE_URL}/courses/my-courses', headers=headers)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Enrolled in {len(data)} courses")
        if len(data) > 0:
            print(f"Response: {json.dumps(data, indent=2)}")
            print("✅ Enrolled courses retrieved!")
        else:
            print("⚠️  No enrolled courses")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 7: Get User Stats
    print_section("Test 7: Get User Statistics")
    
    try:
        response = requests.get(f'{BASE_URL}/user/stats', headers=headers)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            print("✅ Stats retrieved successfully!")
        else:
            print("❌ Failed to get stats!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 8: Get Quiz Questions
    print_section("Test 8: Get Quiz Questions")
    
    try:
        response = requests.get(f'{BASE_URL}/quiz/1/questions')
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Found {len(data)} questions")
        if len(data) > 0:
            print(f"First question: {json.dumps(data[0], indent=2)}")
            print("✅ Quiz questions retrieved!")
        else:
            print("⚠️  No questions found")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 9: Submit Quiz
    print_section("Test 9: Submit Quiz Answers")
    quiz_answers = {
        'quiz_id': 1,
        'answers': {
            '1': 'B',
            '2': 'D',
            '3': 'C',
            '4': 'B',
            '5': 'C'
        }
    }
    
    try:
        response = requests.post(f'{BASE_URL}/quiz/submit', 
                                json=quiz_answers, 
                                headers=headers)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            print(f"✅ Quiz submitted! Score: {data['score']}/{data['total']} ({data['percentage']}%)")
        else:
            print("❌ Quiz submission failed!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 10: Execute Code
    print_section("Test 10: Execute Python Code")
    code_data = {
        'code': 'def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nprint(fibonacci(10))',
        'language': 'python'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/judge', 
                                json=code_data, 
                                headers=headers)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Output: {data['runOutput']}")
        print(f"AI Analysis: {data['aiAnalysis']}")
        print(f"Success: {data['success']}")
        
        if response.status_code == 200 and data['success']:
            print("✅ Code executed successfully!")
        else:
            print("⚠️  Code execution completed with issues")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 11: Search
    print_section("Test 11: Search Courses")
    
    try:
        response = requests.get(f'{BASE_URL}/search?q=python')
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Found {len(data)} results")
        if len(data) > 0:
            print(f"Response: {json.dumps(data, indent=2)}")
            print("✅ Search successful!")
        else:
            print("⚠️  No results found")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 12: Update Preferences
    print_section("Test 12: Update User Preferences")
    preferences = {
        'reading_level': 'Grade 5',
        'visual_preference': 'High Contrast Mode',
        'learning_pattern': 'Audio Preferred'
    }
    
    try:
        response = requests.put(f'{BASE_URL}/user/preferences', 
                               json=preferences, 
                               headers=headers)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            print("✅ Preferences updated!")
        else:
            print("❌ Failed to update preferences!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("  🎉 All Tests Completed!")
    print("="*60 + "\n")

if __name__ == '__main__':
    print("\n⚠️  Make sure the backend server is running on http://localhost:5000")
    print("   (Run: python app.py in another terminal)\n")
    
    try:
        # Test if server is running
        response = requests.get('http://localhost:5000/')
        print("✅ Backend server is running!\n")
        test_api()
    except Exception as e:
        print("❌ Cannot connect to backend server!")
        print(f"   Error: {e}")
        print("\n   Please start the backend first:")
        print("   python app.py\n")
