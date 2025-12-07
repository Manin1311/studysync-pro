import requests  # pyright: ignore[reportMissingModuleSource]
import json

BASE_URL = "http://localhost:5000/api"

# Test data
test_email = "test@example.com"
test_password = "test123"
test_course = {
    "name": "Data Structures",
    "code": "CS201",
    "description": "Introduction to data structures and algorithms"
}

def print_response(title, response):
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_auth():
    print("\n" + "="*60)
    print("TESTING AUTHENTICATION")
    print("="*60)
    
    session = requests.Session()
    
    # Test Register
    print("\n1. Testing User Registration...")
    register_data = {
        "email": test_email,
        "password": test_password
    }
    response = session.post(f"{BASE_URL}/auth/register", json=register_data)
    print_response("Register", response)
    
    # Test Login
    print("\n2. Testing User Login...")
    login_data = {
        "email": test_email,
        "password": test_password
    }
    response = session.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response("Login", response)
    
    # Test Get Current User
    print("\n3. Testing Get Current User...")
    response = session.get(f"{BASE_URL}/auth/me")
    print_response("Get Current User", response)
    
    return session

def test_courses(session):
    print("\n" + "="*60)
    print("TESTING COURSES")
    print("="*60)
    
    # Test Create Course
    print("\n1. Testing Create Course...")
    response = session.post(f"{BASE_URL}/courses", json=test_course)
    print_response("Create Course", response)
    course_id = response.json().get('course', {}).get('id') if response.status_code == 201 else None
    
    # Test Get All Courses
    print("\n2. Testing Get All Courses...")
    response = session.get(f"{BASE_URL}/courses")
    print_response("Get All Courses", response)
    
    # Test Get Course by ID
    if course_id:
        print("\n3. Testing Get Course by ID...")
        response = session.get(f"{BASE_URL}/courses/{course_id}")
        print_response("Get Course by ID", response)
    
    return course_id

def test_notes(session, course_id):
    print("\n" + "="*60)
    print("TESTING NOTES")
    print("="*60)
    
    if not course_id:
        print("Skipping notes test - no course ID available")
        return None
    
    # Test Create Note
    print("\n1. Testing Create Note...")
    note_data = {
        "course_id": course_id,
        "title": "Lecture 1: Introduction to Arrays",
        "content": "Arrays are a fundamental data structure..."
    }
    response = session.post(f"{BASE_URL}/notes", json=note_data)
    print_response("Create Note", response)
    note_id = response.json().get('note', {}).get('id') if response.status_code == 201 else None
    
    # Test Get All Notes
    print("\n2. Testing Get All Notes...")
    response = session.get(f"{BASE_URL}/notes")
    print_response("Get All Notes", response)
    
    # Test Get Note by ID
    if note_id:
        print("\n3. Testing Get Note by ID...")
        response = session.get(f"{BASE_URL}/notes/{note_id}")
        print_response("Get Note by ID", response)
        
        # Test Update Note
        print("\n4. Testing Update Note...")
        update_data = {
            "title": "Updated: Lecture 1 - Arrays",
            "content": "Updated content about arrays..."
        }
        response = session.put(f"{BASE_URL}/notes/{note_id}", json=update_data)
        print_response("Update Note", response)
    
    return note_id

def test_flashcards(session, note_id):
    print("\n" + "="*60)
    print("TESTING FLASHCARDS")
    print("="*60)
    
    if not note_id:
        print("Skipping flashcards test - no note ID available")
        return None
    
    # Test Create Flashcard
    print("\n1. Testing Create Flashcard...")
    flashcard_data = {
        "note_id": note_id,
        "front": "What is an array?",
        "back": "An array is a collection of elements stored in contiguous memory locations.",
        "difficulty": 0
    }
    response = session.post(f"{BASE_URL}/flashcards", json=flashcard_data)
    print_response("Create Flashcard", response)
    flashcard_id = response.json().get('flashcard', {}).get('id') if response.status_code == 201 else None
    
    # Create another flashcard
    print("\n2. Testing Create Another Flashcard...")
    flashcard_data2 = {
        "note_id": note_id,
        "front": "What is the time complexity of array access?",
        "back": "O(1) - constant time",
        "difficulty": 1
    }
    response = session.post(f"{BASE_URL}/flashcards", json=flashcard_data2)
    print_response("Create Flashcard 2", response)
    
    # Test Get All Flashcards
    print("\n3. Testing Get All Flashcards...")
    response = session.get(f"{BASE_URL}/flashcards")
    print_response("Get All Flashcards", response)
    
    # Test Review Flashcard (Spaced Repetition)
    if flashcard_id:
        print("\n4. Testing Review Flashcard (Correct Answer)...")
        review_data = {
            "correct": True,
            "difficulty": 0
        }
        response = session.post(f"{BASE_URL}/flashcards/{flashcard_id}/review", json=review_data)
        print_response("Review Flashcard", response)
        
        # Test Review Queue
        print("\n5. Testing Get Review Queue...")
        response = session.get(f"{BASE_URL}/flashcards/review-queue")
        print_response("Get Review Queue", response)
    
    return flashcard_id

def test_logout(session):
    print("\n" + "="*60)
    print("TESTING LOGOUT")
    print("="*60)
    
    print("\n1. Testing Logout...")
    response = session.post(f"{BASE_URL}/auth/logout")
    print_response("Logout", response)

def main():
    print("\n" + "="*60)
    print("STUDYSYNC PRO API TEST SUITE")
    print("="*60)
    print("\nMake sure your Flask server is running on http://localhost:5000")
    print("Press Enter to start testing...")
    input()
    
    try:
        # Test Authentication
        session = test_auth()
        
        # Test Courses
        course_id = test_courses(session)
        
        # Test Notes
        note_id = test_notes(session, course_id)
        
        # Test Flashcards
        flashcard_id = test_flashcards(session, note_id)
        
        # Test Logout
        test_logout(session)
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED!")
        print("="*60)
        print("\nSummary:")
        print(f"- Course ID: {course_id}")
        print(f"- Note ID: {note_id}")
        print(f"- Flashcard ID: {flashcard_id}")
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to server!")
        print("Make sure Flask is running: python app.py")
    except Exception as e:
        print(f"\nERROR: {str(e)}")

if __name__ == "__main__":
    main()

