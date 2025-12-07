from flask import Blueprint, request, jsonify  # pyright: ignore[reportMissingImports]
from flask_login import current_user  # pyright: ignore[reportMissingImports]
from extensions import db
from models import Note, Course
from utils.auth_decorator import api_login_required

notes = Blueprint('notes', __name__)

@notes.route('/notes', methods=['GET'])
@api_login_required
def get_notes():
    try:
        course_id = request.args.get('course_id', type=int)
        
        query = Note.query.filter_by(user_id=current_user.id)
        if course_id:
            query = query.filter_by(course_id=course_id)
        
        notes_list = query.all()
        
        return jsonify({
            'notes': [{
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'course_id': note.course_id,
                'file_path': note.file_path,
                'created_at': note.created_at.isoformat(),
                'updated_at': note.updated_at.isoformat()
            } for note in notes_list]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes.route('/notes', methods=['POST'])
@api_login_required
def create_note():
    try:
        data = request.get_json()
        
        if not data or not data.get('course_id'):
            return jsonify({'error': 'Course ID is required'}), 400
        
        course_id = data.get('course_id')
        
        # Verify course exists
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        note = Note(
            user_id=current_user.id,
            course_id=course_id,
            title=data.get('title', ''),
            content=data.get('content', ''),
            file_path=data.get('file_path')
        )
        
        db.session.add(note)
        db.session.commit()
        
        return jsonify({
            'message': 'Note created successfully',
            'note': {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'course_id': note.course_id,
                'created_at': note.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notes.route('/notes/<int:note_id>', methods=['GET'])
@api_login_required
def get_note(note_id):
    try:
        note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
        
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        return jsonify({
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'course_id': note.course_id,
            'file_path': note.file_path,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes.route('/notes/<int:note_id>', methods=['PUT'])
@api_login_required
def update_note(note_id):
    try:
        note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
        
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        data = request.get_json()
        
        if data.get('title') is not None:
            note.title = data.get('title')
        if data.get('content') is not None:
            note.content = data.get('content')
        if data.get('file_path') is not None:
            note.file_path = data.get('file_path')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Note updated successfully',
            'note': {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'updated_at': note.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notes.route('/notes/<int:note_id>', methods=['DELETE'])
@api_login_required
def delete_note(note_id):
    try:
        note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
        
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        db.session.delete(note)
        db.session.commit()
        
        return jsonify({'message': 'Note deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

