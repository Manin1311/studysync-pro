from flask import Blueprint, request, jsonify  # pyright: ignore[reportMissingImports]
from flask_login import current_user  # pyright: ignore[reportMissingImports]
from extensions import db
from models import Analytics, Note, Flashcard
from datetime import datetime, timedelta
from collections import defaultdict
from utils.auth_decorator import api_login_required

analytics = Blueprint('analytics', __name__)

@analytics.route('/analytics', methods=['GET'])
@api_login_required
def get_analytics():
    try:
        days = request.args.get('days', 7, type=int)
        start_date = datetime.utcnow().date() - timedelta(days=days)
        
        # Get analytics data
        analytics_list = Analytics.query.filter(
            Analytics.user_id == current_user.id,
            Analytics.date >= start_date
        ).order_by(Analytics.date.desc()).all()
        
        # Calculate totals
        total_study_time = sum(a.study_time for a in analytics_list)
        all_topics = []
        for a in analytics_list:
            if a.topics_covered:
                all_topics.extend(a.topics_covered)
        
        # Count topic frequency
        topic_counts = defaultdict(int)
        for topic in all_topics:
            topic_counts[topic] += 1
        
        # Get weak topics (topics studied less)
        weak_topics = sorted(topic_counts.items(), key=lambda x: x[1])[:5]
        
        return jsonify({
            'analytics': [{
                'date': a.date.isoformat(),
                'study_time': a.study_time,
                'topics_covered': a.topics_covered
            } for a in analytics_list],
            'summary': {
                'total_study_time': total_study_time,
                'days_active': len(set(a.date for a in analytics_list)),
                'total_topics': len(set(all_topics)),
                'weak_topics': [{'topic': t[0], 'count': t[1]} for t in weak_topics]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics.route('/analytics', methods=['POST'])
@api_login_required
def create_analytics():
    try:
        data = request.get_json()
        
        date_str = data.get('date')
        if date_str:
            date = datetime.fromisoformat(date_str).date()
        else:
            date = datetime.utcnow().date()
        
        # Check if analytics entry exists for today
        existing = Analytics.query.filter_by(
            user_id=current_user.id,
            date=date
        ).first()
        
        if existing:
            # Update existing entry
            if data.get('study_time'):
                existing.study_time += data.get('study_time', 0)
            if data.get('topics_covered'):
                existing.topics_covered = list(set(existing.topics_covered + data.get('topics_covered', [])))
            db.session.commit()
            
            return jsonify({
                'message': 'Analytics updated',
                'analytics': {
                    'id': existing.id,
                    'date': existing.date.isoformat(),
                    'study_time': existing.study_time,
                    'topics_covered': existing.topics_covered
                }
            }), 200
        else:
            # Create new entry
            analytics = Analytics(
                user_id=current_user.id,
                date=date,
                study_time=data.get('study_time', 0),
                topics_covered=data.get('topics_covered', [])
            )
            
            db.session.add(analytics)
            db.session.commit()
            
            return jsonify({
                'message': 'Analytics created',
                'analytics': {
                    'id': analytics.id,
                    'date': analytics.date.isoformat(),
                    'study_time': analytics.study_time,
                    'topics_covered': analytics.topics_covered
                }
            }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@analytics.route('/analytics/stats', methods=['GET'])
@api_login_required
def get_stats():
    try:
        # Get user's notes and flashcards count
        notes_count = Note.query.filter_by(user_id=current_user.id).count()
        flashcards_count = Flashcard.query.filter_by(user_id=current_user.id).count()
        
        # Get study time for last 7 days
        week_ago = datetime.utcnow().date() - timedelta(days=7)
        week_analytics = Analytics.query.filter(
            Analytics.user_id == current_user.id,
            Analytics.date >= week_ago
        ).all()
        
        total_week_time = sum(a.study_time for a in week_analytics)
        
        # Get flashcards due for review
        due_flashcards = Flashcard.query.filter(
            Flashcard.user_id == current_user.id,
            Flashcard.next_review <= datetime.utcnow()
        ).count()
        
        return jsonify({
            'stats': {
                'notes_count': notes_count,
                'flashcards_count': flashcards_count,
                'total_study_time_week': total_week_time,
                'due_flashcards': due_flashcards,
                'days_active_week': len(set(a.date for a in week_analytics))
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

