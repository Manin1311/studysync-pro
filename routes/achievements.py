from flask import Blueprint, request, jsonify  # pyright: ignore[reportMissingImports]
from flask_login import current_user  # pyright: ignore[reportMissingImports]
from extensions import db
from models import Achievement, Note, Flashcard, Analytics
from datetime import datetime, timedelta
from utils.auth_decorator import api_login_required

achievements = Blueprint('achievements', __name__)

def check_and_award_achievements(user_id):
    """Check user progress and award achievements automatically"""
    new_achievements = []
    
    # Count user's progress
    notes_count = Note.query.filter_by(user_id=user_id).count()
    flashcards_count = Flashcard.query.filter_by(user_id=user_id).count()
    
    # Get study streak
    week_ago = datetime.utcnow().date() - timedelta(days=7)
    recent_analytics = Analytics.query.filter(
        Analytics.user_id == user_id,
        Analytics.date >= week_ago
    ).all()
    
    active_days = len(set(a.date for a in recent_analytics))
    
    # Check existing achievements
    existing_badges = set(
        Achievement.query.filter_by(user_id=user_id).with_entities(Achievement.badge_type).all()
    )
    existing_badges = {badge[0] for badge in existing_badges}
    
    # Define achievement criteria
    achievements_to_check = [
        {'badge': 'first_note', 'condition': notes_count >= 1},
        {'badge': 'note_master', 'condition': notes_count >= 10},
        {'badge': 'note_legend', 'condition': notes_count >= 50},
        {'badge': 'flashcard_starter', 'condition': flashcards_count >= 1},
        {'badge': 'flashcard_pro', 'condition': flashcards_count >= 20},
        {'badge': 'flashcard_master', 'condition': flashcards_count >= 100},
        {'badge': 'week_warrior', 'condition': active_days >= 5},
        {'badge': 'dedicated_student', 'condition': active_days >= 7}
    ]
    
    # Award new achievements
    for achievement in achievements_to_check:
        if achievement['condition'] and achievement['badge'] not in existing_badges:
            new_achievement = Achievement(
                user_id=user_id,
                badge_type=achievement['badge']
            )
            db.session.add(new_achievement)
            new_achievements.append(achievement['badge'])
    
    if new_achievements:
        db.session.commit()
    
    return new_achievements

@achievements.route('/achievements', methods=['GET'])
@api_login_required
def get_achievements():
    try:
        # Check and award new achievements
        new_achievements = check_and_award_achievements(current_user.id)
        
        # Get all achievements
        achievements_list = Achievement.query.filter_by(
            user_id=current_user.id
        ).order_by(Achievement.earned_date.desc()).all()
        
        # Badge descriptions
        badge_descriptions = {
            'first_note': 'Created your first note',
            'note_master': 'Created 10 notes',
            'note_legend': 'Created 50 notes',
            'flashcard_starter': 'Created your first flashcard',
            'flashcard_pro': 'Created 20 flashcards',
            'flashcard_master': 'Created 100 flashcards',
            'week_warrior': 'Studied 5 days in a week',
            'dedicated_student': 'Studied every day for a week'
        }
        
        return jsonify({
            'achievements': [{
                'id': a.id,
                'badge_type': a.badge_type,
                'description': badge_descriptions.get(a.badge_type, a.badge_type),
                'earned_date': a.earned_date.isoformat()
            } for a in achievements_list],
            'new_achievements': new_achievements,
            'total_count': len(achievements_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@achievements.route('/achievements/stats', methods=['GET'])
@api_login_required
def get_achievement_stats():
    try:
        # Get user stats
        notes_count = Note.query.filter_by(user_id=current_user.id).count()
        flashcards_count = Flashcard.query.filter_by(user_id=current_user.id).count()
        
        # Get study streak
        week_ago = datetime.utcnow().date() - timedelta(days=7)
        recent_analytics = Analytics.query.filter(
            Analytics.user_id == current_user.id,
            Analytics.date >= week_ago
        ).all()
        
        active_days = len(set(a.date for a in recent_analytics))
        
        # Get total achievements
        total_achievements = Achievement.query.filter_by(user_id=current_user.id).count()
        
        return jsonify({
            'stats': {
                'notes_count': notes_count,
                'flashcards_count': flashcards_count,
                'active_days_week': active_days,
                'total_achievements': total_achievements,
                'progress': {
                    'notes_to_master': max(0, 10 - notes_count),
                    'notes_to_legend': max(0, 50 - notes_count),
                    'flashcards_to_pro': max(0, 20 - flashcards_count),
                    'flashcards_to_master': max(0, 100 - flashcards_count),
                    'days_to_week_warrior': max(0, 5 - active_days),
                    'days_to_dedicated': max(0, 7 - active_days)
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

