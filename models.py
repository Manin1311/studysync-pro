from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # pyright: ignore[reportMissingImports]
from flask_login import UserMixin  # pyright: ignore[reportMissingImports]

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_data = db.Column(db.JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    notes = db.relationship('Note', backref='user', lazy=True, cascade='all, delete-orphan')
    flashcards = db.relationship('Flashcard', backref='user', lazy=True, cascade='all, delete-orphan')
    study_sessions = db.relationship('StudySession', backref='user', lazy=True, cascade='all, delete-orphan')
    analytics = db.relationship('Analytics', backref='user', lazy=True, cascade='all, delete-orphan')
    achievements = db.relationship('Achievement', backref='user', lazy=True, cascade='all, delete-orphan')
    partner1 = db.relationship('StudyPartner', foreign_keys='StudyPartner.user1_id', backref='user1', lazy=True)
    partner2 = db.relationship('StudyPartner', foreign_keys='StudyPartner.user2_id', backref='user2', lazy=True)
    study_plans = db.relationship('StudyPlan', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    notes = db.relationship('Note', backref='course', lazy=True, cascade='all, delete-orphan')
    study_rooms = db.relationship('StudyRoom', backref='course', lazy=True, cascade='all, delete-orphan')
    exam_predictions = db.relationship('ExamPrediction', backref='course', lazy=True, cascade='all, delete-orphan')
    resources = db.relationship('Resource', backref='course', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.code}>'

class Note(db.Model):
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    content = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    title = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    flashcards = db.relationship('Flashcard', backref='note', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Note {self.id}>'

class Flashcard(db.Model):
    __tablename__ = 'flashcards'
    
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Integer, default=0)  # 0=easy, 1=medium, 2=hard
    next_review = db.Column(db.DateTime, default=datetime.utcnow)
    review_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Flashcard {self.id}>'

class StudyRoom(db.Model):
    __tablename__ = 'study_rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    max_participants = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    study_sessions = db.relationship('StudySession', backref='study_room', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<StudyRoom {self.name}>'

class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('study_rooms.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer)  # duration in minutes
    end_time = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<StudySession {self.id}>'

class ExamPrediction(db.Model):
    __tablename__ = 'exam_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    question_text = db.Column(db.Text, nullable=False)
    confidence_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ExamPrediction {self.id}>'

class StudyPartner(db.Model):
    __tablename__ = 'study_partners'
    
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    match_score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<StudyPartner {self.id}>'

class Analytics(db.Model):
    __tablename__ = 'analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    study_time = db.Column(db.Integer, default=0)  # in minutes
    topics_covered = db.Column(db.JSON, default=[])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Analytics {self.id}>'

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    badge_type = db.Column(db.String(100), nullable=False)
    earned_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    def __repr__(self):
        return f'<Achievement {self.id}>'

class StudyPlan(db.Model):
    __tablename__ = 'study_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200))
    exam_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Structure: [{'date': '2023-10-27', 'topics': ['Math', 'Physics'], 'hours': 4}]
    schedule = db.Column(db.JSON, default=[]) 
    
    def __repr__(self):
        return f'<StudyPlan {self.title}>'

class Resource(db.Model):
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50)) # pdf, jpg, etc.
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Resource {self.title}>'


