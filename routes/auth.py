from flask import Blueprint, request, jsonify, current_app  # pyright: ignore[reportMissingImports]
from flask_login import login_user, logout_user, current_user  # pyright: ignore[reportMissingImports]
from extensions import db
from models import User
from utils.auth_decorator import api_login_required

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data.get('email').strip().lower()
        password = data.get('password')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User already exists'}), 400
        
        # Create new user
        user = User(email=email)
        user.set_password(password)
        
        # Add profile data if provided
        if data.get('profile_data'):
            user.profile_data = data.get('profile_data')
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.id,
            'email': user.email
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data.get('email').strip().lower()
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Login user - Flask-Login automatically sets session cookie
        login_user(user, remember=True)
        
        # Mark session as permanent
        from flask import session
        session.permanent = True
        
        return jsonify({
            'message': 'Login successful',
            'user_id': user.id,
            'email': user.email,
            'profile_data': user.profile_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth.route('/logout', methods=['POST'])
@api_login_required
def logout():
    try:
        logout_user()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth.route('/me', methods=['GET'])
@api_login_required
def get_current_user():
    try:
        return jsonify({
            'user_id': current_user.id,
            'email': current_user.email,
            'profile_data': current_user.profile_data,
            'created_at': current_user.created_at.isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

