# Testing Guide for StudySync Pro API

## Method 1: Python Test Script (Recommended)

### Step 1: Install requests library
```bash
pip install requests
```

### Step 2: Make sure Flask server is running
```bash
python app.py
```

### Step 3: Run the test script
```bash
python test_api.py
```

This will automatically test all endpoints:
- ✅ User Registration
- ✅ User Login
- ✅ Get Current User
- ✅ Create Course
- ✅ Get All Courses
- ✅ Create Note
- ✅ Get All Notes
- ✅ Create Flashcard
- ✅ Review Flashcard (Spaced Repetition)
- ✅ Get Review Queue
- ✅ Logout

---

## Method 2: Browser Testing (HTML Page)

### Step 1: Open the HTML file
Simply open `test_page.html` in your web browser (Chrome, Firefox, Edge)

### Step 2: Make sure Flask server is running
```bash
python app.py
```

### Step 3: Test endpoints
- Fill in the forms
- Click buttons to test each endpoint
- See responses displayed below each section

**Note:** Browser testing uses cookies for session management, so login will persist across requests.

---

## Method 3: Postman/Thunder Client

### Import Collection (Manual Setup)

#### Authentication
1. **Register User**
   - Method: `POST`
   - URL: `http://localhost:5000/api/auth/register`
   - Body (JSON):
   ```json
   {
     "email": "test@example.com",
     "password": "test123"
   }
   ```

2. **Login**
   - Method: `POST`
   - URL: `http://localhost:5000/api/auth/login`
   - Body (JSON):
   ```json
   {
     "email": "test@example.com",
     "password": "test123"
   }
   ```
   - **Important:** Enable "Send cookies" in Postman settings

3. **Get Current User**
   - Method: `GET`
   - URL: `http://localhost:5000/api/auth/me`

#### Courses
1. **Create Course**
   - Method: `POST`
   - URL: `http://localhost:5000/api/courses`
   - Body (JSON):
   ```json
   {
     "name": "Data Structures",
     "code": "CS201",
     "description": "Introduction to data structures"
   }
   ```

2. **Get All Courses**
   - Method: `GET`
   - URL: `http://localhost:5000/api/courses`

#### Notes
1. **Create Note**
   - Method: `POST`
   - URL: `http://localhost:5000/api/notes`
   - Body (JSON):
   ```json
   {
     "course_id": 1,
     "title": "Lecture 1 Notes",
     "content": "My note content..."
   }
   ```

2. **Get All Notes**
   - Method: `GET`
   - URL: `http://localhost:5000/api/notes`

#### Flashcards
1. **Create Flashcard**
   - Method: `POST`
   - URL: `http://localhost:5000/api/flashcards`
   - Body (JSON):
   ```json
   {
     "note_id": 1,
     "front": "What is Python?",
     "back": "A programming language",
     "difficulty": 0
   }
   ```

2. **Review Flashcard**
   - Method: `POST`
   - URL: `http://localhost:5000/api/flashcards/1/review`
   - Body (JSON):
   ```json
   {
     "correct": true,
     "difficulty": 0
   }
   ```

3. **Get Review Queue**
   - Method: `GET`
   - URL: `http://localhost:5000/api/flashcards/review-queue`

---

## Method 4: cURL Commands

### Authentication
```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  -c cookies.txt

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  -c cookies.txt

# Get Current User
curl -X GET http://localhost:5000/api/auth/me \
  -b cookies.txt
```

### Courses
```bash
# Create Course
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"name":"Data Structures","code":"CS201","description":"Intro to DS"}'

# Get All Courses
curl -X GET http://localhost:5000/api/courses
```

### Notes
```bash
# Create Note
curl -X POST http://localhost:5000/api/notes \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"course_id":1,"title":"Lecture 1","content":"My notes..."}'

# Get All Notes
curl -X GET http://localhost:5000/api/notes \
  -b cookies.txt
```

### Flashcards
```bash
# Create Flashcard
curl -X POST http://localhost:5000/api/flashcards \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"note_id":1,"front":"Question?","back":"Answer"}'

# Get Review Queue
curl -X GET http://localhost:5000/api/flashcards/review-queue \
  -b cookies.txt
```

---

## Expected Responses

### Success Response (201 Created)
```json
{
  "message": "User registered successfully",
  "user_id": 1,
  "email": "test@example.com"
}
```

### Error Response (400 Bad Request)
```json
{
  "error": "Email and password are required"
}
```

### Error Response (401 Unauthorized)
```json
{
  "error": "Invalid email or password"
}
```

---

## Troubleshooting

### Issue: "Could not connect to server"
- **Solution:** Make sure Flask is running: `python app.py`
- Check if port 5000 is available

### Issue: "401 Unauthorized" errors
- **Solution:** Make sure you're logged in first
- For Postman/cURL: Enable cookies/session management
- Try logging in again

### Issue: "500 Internal Server Error"
- **Solution:** Check Flask console for error messages
- Verify database connection in `config.py`
- Make sure all tables are created

### Issue: Browser CORS errors
- **Solution:** CORS is already enabled in `app.py`
- Make sure Flask server is running
- Try clearing browser cache

---

## Quick Test Checklist

- [ ] Flask server running (`python app.py`)
- [ ] Database connected (check console for "Database tables created successfully!")
- [ ] Test registration endpoint
- [ ] Test login endpoint
- [ ] Test create course endpoint
- [ ] Test create note endpoint
- [ ] Test create flashcard endpoint
- [ ] Test review flashcard endpoint
- [ ] Test review queue endpoint

---

## Next Steps

After testing, you can:
1. Build the frontend to connect to these APIs
2. Add more features (AI assistant, study rooms, etc.)
3. Deploy the application

Happy Testing! 🚀

