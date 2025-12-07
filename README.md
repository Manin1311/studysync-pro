# StudySync Pro - AI-Powered Learning Ecosystem

A comprehensive learning platform that combines AI study assistance, smart note-taking, peer learning, and performance analytics.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
- PostgreSQL database `StudySync` should already be created in pgAdmin4
- Update `config.py` with your database credentials if needed
- Run the application once to create all tables automatically

### 3. Run the Application
```bash
python app.py
```

The application will:
- Connect to PostgreSQL database
- Create all necessary tables automatically
- Start the Flask server on http://localhost:5000

## Database Schema

All tables are defined in:
- `models.py` - SQLAlchemy models
- `schema.sql` - Raw PostgreSQL schema (for reference)

## Project Structure

```
FInal_Project/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── models.py            # Database models
├── schema.sql           # SQL schema reference
├── requirements.txt     # Python dependencies
├── routes/              # API routes
└── utils/               # Utility functions (DSA helpers)
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user info

### Courses
- `GET /api/courses` - Get all courses
- `POST /api/courses` - Create course
- `GET /api/courses/<id>` - Get course by ID

### Notes
- `GET /api/notes` - Get all notes (filter by course_id)
- `POST /api/notes` - Create note
- `GET /api/notes/<id>` - Get note by ID
- `PUT /api/notes/<id>` - Update note
- `DELETE /api/notes/<id>` - Delete note

### Flashcards
- `GET /api/flashcards` - Get all flashcards
- `POST /api/flashcards` - Create flashcard
- `POST /api/flashcards/<id>/review` - Review flashcard (spaced repetition)
- `GET /api/flashcards/review-queue` - Get flashcards due for review
- `DELETE /api/flashcards/<id>` - Delete flashcard

See `API_DOCS.md` for detailed API documentation.

## Features Implemented

✅ User Authentication (Register/Login/Logout)
✅ Notes Management (CRUD operations)
✅ Smart Flashcards with Spaced Repetition Algorithm
✅ Courses Management
✅ Performance Analytics Dashboard
✅ AI Study Assistant (Trie-based keyword search)
✅ Study Partner Matching (Graph algorithm)
✅ Achievements & Gamification System
✅ Exam Question Predictor (Pattern matching)
✅ Priority Queue for Review Scheduling (DSA)

## Features (To Be Implemented)

1. AI Study Assistant
2. Study Rooms
3. Performance Analytics
4. Study Partner Matching
5. Exam Predictor
6. Gamification & Achievements

