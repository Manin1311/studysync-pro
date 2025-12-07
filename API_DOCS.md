# StudySync Pro API Documentation

## Base URL
`http://localhost:5000/api`

## Authentication Endpoints

### Register User
- **POST** `/auth/register`
- **Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "profile_data": {} // optional
}
```
- **Response:** `201 Created`
```json
{
  "message": "User registered successfully",
  "user_id": 1,
  "email": "user@example.com"
}
```

### Login
- **POST** `/auth/login`
- **Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
- **Response:** `200 OK`
```json
{
  "message": "Login successful",
  "user_id": 1,
  "email": "user@example.com"
}
```

### Logout
- **POST** `/auth/logout`
- **Requires:** Authentication
- **Response:** `200 OK`

### Get Current User
- **GET** `/auth/me`
- **Requires:** Authentication
- **Response:** `200 OK`
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "profile_data": {},
  "created_at": "2024-01-01T00:00:00"
}
```

## Courses Endpoints

### Get All Courses
- **GET** `/courses`
- **Response:** `200 OK`
```json
{
  "courses": [
    {
      "id": 1,
      "name": "Data Structures",
      "code": "CS201",
      "description": "Introduction to data structures"
    }
  ]
}
```

### Create Course
- **POST** `/courses`
- **Requires:** Authentication
- **Body:**
```json
{
  "name": "Data Structures",
  "code": "CS201",
  "description": "Introduction to data structures"
}
```

### Get Course by ID
- **GET** `/courses/<course_id>`
- **Response:** `200 OK`

## Notes Endpoints

### Get All Notes
- **GET** `/notes`
- **Requires:** Authentication
- **Query Params:** `course_id` (optional)
- **Response:** `200 OK`
```json
{
  "notes": [
    {
      "id": 1,
      "title": "Lecture 1 Notes",
      "content": "Note content...",
      "course_id": 1,
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### Create Note
- **POST** `/notes`
- **Requires:** Authentication
- **Body:**
```json
{
  "course_id": 1,
  "title": "Lecture 1 Notes",
  "content": "Note content...",
  "file_path": "optional/path/to/file"
}
```

### Get Note by ID
- **GET** `/notes/<note_id>`
- **Requires:** Authentication

### Update Note
- **PUT** `/notes/<note_id>`
- **Requires:** Authentication
- **Body:** (all fields optional)
```json
{
  "title": "Updated Title",
  "content": "Updated content",
  "file_path": "new/path"
}
```

### Delete Note
- **DELETE** `/notes/<note_id>`
- **Requires:** Authentication

## Flashcards Endpoints

### Get All Flashcards
- **GET** `/flashcards`
- **Requires:** Authentication
- **Query Params:** 
  - `note_id` (optional)
  - `due_only=true` (optional) - only flashcards due for review
- **Response:** `200 OK`

### Create Flashcard
- **POST** `/flashcards`
- **Requires:** Authentication
- **Body:**
```json
{
  "note_id": 1,
  "front": "What is Python?",
  "back": "A programming language",
  "difficulty": 0 // 0=easy, 1=medium, 2=hard
}
```

### Review Flashcard (Spaced Repetition)
- **POST** `/flashcards/<flashcard_id>/review`
- **Requires:** Authentication
- **Body:**
```json
{
  "correct": true, // or false
  "difficulty": 1 // optional, current difficulty if not provided
}
```
- Updates next review date based on spaced repetition algorithm

### Get Review Queue
- **GET** `/flashcards/review-queue`
- **Requires:** Authentication
- Returns flashcards due for review (uses Priority Queue DSA concept)
- **Response:** `200 OK`
```json
{
  "review_queue": [
    {
      "id": 1,
      "front": "Question?",
      "back": "Answer",
      "difficulty": 0,
      "next_review": "2024-01-01T00:00:00"
    }
  ],
  "count": 1
}
```

### Delete Flashcard
- **DELETE** `/flashcards/<flashcard_id>`
- **Requires:** Authentication

## Testing with cURL or Postman

### Example: Register and Login
```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Login (saves session cookie)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  -c cookies.txt

# Create Course (use session cookie)
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"name":"Data Structures","code":"CS201","description":"Intro to DS"}'
```

## Analytics Endpoints

### Get Analytics
- **GET** `/analytics`
- **Requires:** Authentication
- **Query Params:** `days` (optional, default: 7)
- **Response:** `200 OK`
```json
{
  "analytics": [...],
  "summary": {
    "total_study_time": 120,
    "days_active": 5,
    "total_topics": 10,
    "weak_topics": [...]
  }
}
```

### Create/Update Analytics
- **POST** `/analytics`
- **Requires:** Authentication
- **Body:**
```json
{
  "date": "2024-01-01",
  "study_time": 60,
  "topics_covered": ["Arrays", "Linked Lists"]
}
```

### Get Stats
- **GET** `/analytics/stats`
- **Requires:** Authentication
- Returns quick stats about user's progress

## AI Assistant Endpoints

### Search Notes (Trie-based)
- **POST** `/ai/search`
- **Requires:** Authentication
- **Body:**
```json
{
  "query": "arrays data structures"
}
```
- Uses **Trie** data structure for fast keyword search

### Ask Question
- **POST** `/ai/ask`
- **Requires:** Authentication
- **Body:**
```json
{
  "question": "What is a binary tree?"
}
```
- Searches notes using Trie and provides answers

### Summarize Note
- **POST** `/ai/summarize`
- **Requires:** Authentication
- **Body:**
```json
{
  "note_id": 1
}
```

## Study Partners Endpoints

### Find Partners (Graph-based)
- **GET** `/partners/find`
- **Requires:** Authentication
- Uses **Graph** algorithm to find users with shared courses
- **Response:** List of potential study partners with match scores

### Request Partnership
- **POST** `/partners/request`
- **Requires:** Authentication
- **Body:**
```json
{
  "partner_id": 2
}
```

### Get Partners
- **GET** `/partners`
- **Requires:** Authentication
- Returns all partnerships (pending/accepted)

### Accept Partnership
- **POST** `/partners/<partnership_id>/accept`
- **Requires:** Authentication

## Achievements Endpoints

### Get Achievements
- **GET** `/achievements`
- **Requires:** Authentication
- Automatically checks and awards new achievements
- **Response:**
```json
{
  "achievements": [...],
  "new_achievements": ["first_note"],
  "total_count": 5
}
```

### Get Achievement Stats
- **GET** `/achievements/stats`
- **Requires:** Authentication
- Returns progress toward next achievements

## Exam Predictor Endpoints

### Analyze Course
- **POST** `/exam-predictor/<course_id>/analyze`
- **Requires:** Authentication
- Analyzes notes using pattern matching and frequency analysis
- Generates predicted exam questions

### Get Predictions
- **GET** `/exam-predictor/<course_id>`
- **Requires:** Authentication
- Returns all predictions for a course, sorted by confidence

### Get Top Predictions
- **GET** `/exam-predictor/<course_id>/top`
- **Requires:** Authentication
- Returns top 5 predictions by confidence score

## Error Responses

All errors follow this format:
```json
{
  "error": "Error message here"
}
```

Common status codes:
- `400` - Bad Request (missing/invalid data)
- `401` - Unauthorized (not logged in)
- `404` - Not Found
- `500` - Internal Server Error

## DSA Concepts Used

- **Trie**: Fast keyword search in AI Assistant (`/ai/search`)
- **Graph**: Study partner matching algorithm (`/partners/find`)
- **Priority Queue**: Flashcard review scheduling (`/flashcards/review-queue`)
- **Hash Tables**: Fast lookups throughout the system
- **Pattern Matching**: Exam question prediction
- **Frequency Analysis**: Topic analysis and exam predictions

