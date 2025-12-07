from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import Resource, Course
from utils.auth_decorator import api_login_required
import os
import uuid

resources = Blueprint('resources', __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'ppt', 'pptx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@resources.route('/resources', methods=['POST'])
@api_login_required
def upload_resource():
    try:
        # Check if file part is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        course_id = request.form.get('course_id')
        title = request.form.get('title')
        description = request.form.get('description', '')
        
        if not course_id or not title:
            return jsonify({'error': 'Course ID and Title are required'}), 400
            
        if file and allowed_file(file.filename):
            # Secure filename and add unique ID to prevent overwrites
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # Save file
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            file.save(os.path.join(upload_folder, unique_filename))
            
            # Create DB entry
            resource = Resource(
                course_id=course_id,
                uploader_id=current_user.id,
                title=title,
                file_path=unique_filename,
                file_type=filename.rsplit('.', 1)[1].lower(),
                description=description
            )
            
            db.session.add(resource)
            db.session.commit()
            
            return jsonify({
                'message': 'Resource uploaded successfully',
                'resource': {
                    'id': resource.id,
                    'title': resource.title,
                    'file_type': resource.file_type
                }
            }), 201
        
        return jsonify({'error': 'File type not allowed'}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@resources.route('/resources', methods=['GET'])
@api_login_required
def get_resources():
    try:
        course_id = request.args.get('course_id')
        
        query = Resource.query
        
        if course_id:
            query = query.filter_by(course_id=course_id)
            
        resources_list = query.order_by(Resource.created_at.desc()).all()
        
        return jsonify({
            'resources': [{
                'id': r.id,
                'title': r.title,
                'course_id': r.course_id,
                'uploader_id': r.uploader_id,
                'file_type': r.file_type,
                'description': r.description,
                'created_at': r.created_at.isoformat()
            } for r in resources_list]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resources.route('/resources/<int:resource_id>/download', methods=['GET'])
@api_login_required
def download_resource(resource_id):
    try:
        resource = Resource.query.get(resource_id)
        
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
            
        return send_from_directory(
            current_app.config['UPLOAD_FOLDER'],
            resource.file_path,
            as_attachment=True,
            download_name=f"{resource.title}.{resource.file_type}"
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
