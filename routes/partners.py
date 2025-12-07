from flask import Blueprint, request, jsonify  # pyright: ignore[reportMissingImports]
from flask_login import current_user  # pyright: ignore[reportMissingImports]
from extensions import db
from models import StudyPartner, User, Note, Course
from collections import defaultdict
from utils.auth_decorator import api_login_required

partners = Blueprint('partners', __name__)

def build_user_graph():
    """Build a graph of users based on shared courses (Graph DSA concept)"""
    # Get all users and their courses
    users = User.query.all()
    user_courses = {}
    
    for user in users:
        notes = Note.query.filter_by(user_id=user.id).all()
        courses = set(note.course_id for note in notes if note.course_id)
        user_courses[user.id] = courses
    
    # Build graph: users are nodes, shared courses create edges
    graph = defaultdict(list)
    for user1_id, courses1 in user_courses.items():
        for user2_id, courses2 in user_courses.items():
            if user1_id != user2_id:
                # Calculate similarity (shared courses)
                shared = len(courses1.intersection(courses2))
                if shared > 0:
                    match_score = shared / max(len(courses1), len(courses2), 1)
                    graph[user1_id].append({
                        'user_id': user2_id,
                        'match_score': match_score,
                        'shared_courses': shared
                    })
    
    return graph

@partners.route('/partners/find', methods=['GET'])
@api_login_required
def find_partners():
    try:
        # Build user graph
        graph = build_user_graph()
        
        # Get potential partners for current user
        potential_partners = graph.get(current_user.id, [])
        
        # Sort by match score
        potential_partners.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Get user details
        results = []
        for partner_data in potential_partners[:10]:  # Top 10 matches
            user = User.query.get(partner_data['user_id'])
            if user and user.id != current_user.id:
                # Check if partnership already exists
                existing = StudyPartner.query.filter(
                    ((StudyPartner.user1_id == current_user.id) & (StudyPartner.user2_id == user.id)) |
                    ((StudyPartner.user1_id == user.id) & (StudyPartner.user2_id == current_user.id))
                ).first()
                
                results.append({
                    'user_id': user.id,
                    'email': user.email,
                    'match_score': round(partner_data['match_score'] * 100, 2),
                    'shared_courses': partner_data['shared_courses'],
                    'status': existing.status if existing else 'none'
                })
        
        return jsonify({
            'partners': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@partners.route('/partners/request', methods=['POST'])
@api_login_required
def request_partnership():
    try:
        data = request.get_json()
        partner_id = data.get('partner_id')
        
        if not partner_id:
            return jsonify({'error': 'Partner ID is required'}), 400
        
        if partner_id == current_user.id:
            return jsonify({'error': 'Cannot partner with yourself'}), 400
        
        # Check if partnership already exists
        existing = StudyPartner.query.filter(
            ((StudyPartner.user1_id == current_user.id) & (StudyPartner.user2_id == partner_id)) |
            ((StudyPartner.user1_id == partner_id) & (StudyPartner.user2_id == current_user.id))
        ).first()
        
        if existing:
            return jsonify({'error': 'Partnership already exists'}), 400
        
        # Calculate match score
        user1_notes = Note.query.filter_by(user_id=current_user.id).all()
        user2_notes = Note.query.filter_by(user_id=partner_id).all()
        
        user1_courses = set(note.course_id for note in user1_notes if note.course_id)
        user2_courses = set(note.course_id for note in user2_notes if note.course_id)
        
        shared = len(user1_courses.intersection(user2_courses))
        match_score = shared / max(len(user1_courses), len(user2_courses), 1) if user1_courses or user2_courses else 0
        
        # Create partnership request
        partnership = StudyPartner(
            user1_id=current_user.id,
            user2_id=partner_id,
            match_score=match_score,
            status='pending'
        )
        
        db.session.add(partnership)
        db.session.commit()
        
        return jsonify({
            'message': 'Partnership request sent',
            'partnership': {
                'id': partnership.id,
                'partner_id': partner_id,
                'match_score': round(match_score * 100, 2),
                'status': partnership.status
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@partners.route('/partners', methods=['GET'])
@api_login_required
def get_partners():
    try:
        # Get all partnerships for current user
        partnerships = StudyPartner.query.filter(
            (StudyPartner.user1_id == current_user.id) |
            (StudyPartner.user2_id == current_user.id)
        ).all()
        
        results = []
        for partnership in partnerships:
            # Get partner user
            partner_id = partnership.user2_id if partnership.user1_id == current_user.id else partnership.user1_id
            partner = User.query.get(partner_id)
            
            if partner:
                results.append({
                    'partnership_id': partnership.id,
                    'partner_id': partner.id,
                    'partner_email': partner.email,
                    'match_score': round(partnership.match_score * 100, 2),
                    'status': partnership.status,
                    'created_at': partnership.created_at.isoformat()
                })
        
        return jsonify({
            'partners': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@partners.route('/partners/<int:partnership_id>/accept', methods=['POST'])
@api_login_required
def accept_partnership(partnership_id):
    try:
        partnership = StudyPartner.query.get(partnership_id)
        
        if not partnership:
            return jsonify({'error': 'Partnership not found'}), 404
        
        # Check if current user is the recipient
        if partnership.user2_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if partnership.status != 'pending':
            return jsonify({'error': 'Partnership is not pending'}), 400
        
        partnership.status = 'accepted'
        db.session.commit()
        
        return jsonify({
            'message': 'Partnership accepted',
            'partnership': {
                'id': partnership.id,
                'status': partnership.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

