from app import create_app
from extensions import db
from models import User, Course, Note
import random

app = create_app()

def seed_database():
    with app.app_context():
        print("🌱 Seeding database with demo data...")
        
        # 1. Create Courses
        courses_data = [
            {"name": "Introduction to Computer Science", "code": "CS101", "desc": "Basics of programming and algorithms"},
            {"name": "Advanced Calculus", "code": "MATH201", "desc": "Limits, derivatives, and integrals"},
            {"name": "Biology: Cell Structure", "code": "BIO105", "desc": "Introduction to cell biology"},
            {"name": "World History", "code": "HIST100", "desc": "Ancient civilizations to modern times"},
            {"name": "Physics: Mechanics", "code": "PHYS110", "desc": "Motion, forces, and energy"},
            {"name": "Psychology 101", "code": "PSY101", "desc": "Intro to human behavior"}
        ]
        
        db_courses = []
        for c in courses_data:
            existing = Course.query.filter_by(code=c["code"]).first()
            if not existing:
                new_course = Course(name=c["name"], code=c["code"], description=c["desc"])
                db.session.add(new_course)
                db_courses.append(new_course)
            else:
                db_courses.append(existing)
        
        db.session.commit()
        print(f"✅ Created/Found {len(db_courses)} courses")

        # 2. Create Fake Students
        students_data = [
            {"email": "alex.chen@uni.edu", "password": "password123"},
            {"email": "sarah.jones@uni.edu", "password": "password123"},
            {"email": "mike.ross@uni.edu", "password": "password123"},
            {"email": "emily.wang@uni.edu", "password": "password123"},
            {"email": "david.miller@uni.edu", "password": "password123"}
        ]

        db_students = []
        for s in students_data:
            existing = User.query.filter_by(email=s["email"]).first()
            if not existing:
                new_user = User(email=s["email"])
                new_user.set_password(s["password"])
                db.session.add(new_user)
                db_students.append(new_user)
            else:
                db_students.append(existing)
        
        db.session.commit()
        print(f"✅ Created/Found {len(db_students)} students")

        # 3. Assign Notes to Students (Linking them to courses)
        # This simulates that they are "taking" the class because our partner logic relies on users having notes in a course
        for student in db_students:
            # Assign 2-3 random courses to each student
            student_courses = random.sample(db_courses, k=random.randint(2, 3))
            
            for course in student_courses:
                # distinct title to avoid uniqueness constraint? Note title isn't unique usually, but let's be safe
                note = Note(
                    user_id=student.id,
                    course_id=course.id,
                    title=f"{course.code} Notes - Chapter {random.randint(1,5)}",
                    content=f"These are my notes for {course.name}. The professor mentioned that..."
                )
                db.session.add(note)
        
        db.session.commit()
        print("✅ Assigned courses/notes to students to create match data")
        
        print("\n🎉 Database seeded! You can now log in or check 'Study Partners' to see matches.")

if __name__ == "__main__":
    seed_database()
