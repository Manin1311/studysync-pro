from flask import Blueprint, request, jsonify  # pyright: ignore[reportMissingImports]
from extensions import db
from models import Course
from utils.auth_decorator import api_login_required

courses = Blueprint('courses', __name__)

@courses.route('/courses', methods=['GET'])
def get_courses():
    try:
        courses_list = Course.query.all()
        
        return jsonify({
            'courses': [{
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'description': course.description,
                'created_at': course.created_at.isoformat()
            } for course in courses_list]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses.route('/courses', methods=['POST'])
@api_login_required
def create_course():
    try:
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('code'):
            return jsonify({'error': 'Name and code are required'}), 400
        
        code = data.get('code').strip().upper()
        
        # Check if course code already exists
        if Course.query.filter_by(code=code).first():
            return jsonify({'error': 'Course code already exists'}), 400
        
        course = Course(
            name=data.get('name'),
            code=code,
            description=data.get('description', '')
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({
            'message': 'Course created successfully',
            'course': {
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'description': course.description
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@courses.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    try:
        course = Course.query.get(course_id)
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        return jsonify({
            'id': course.id,
            'name': course.name,
            'code': course.code,
            'description': course.description,
            'created_at': course.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

