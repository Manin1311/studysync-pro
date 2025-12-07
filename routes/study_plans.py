from flask import Blueprint, request, jsonify
from flask_login import current_user
from extensions import db
from models import StudyPlan, Course
from utils.dsa_helpers import optimize_study_schedule
from utils.auth_decorator import api_login_required
from datetime import datetime, timedelta

study_plans = Blueprint('study_plans', __name__)

@study_plans.route('/study-plans', methods=['POST'])
@api_login_required
def create_study_plan():
    try:
        data = request.get_json()
        
        title = data.get('title', 'My Study Plan')
        exam_date_str = data.get('exam_date')
        topics = data.get('topics', []) # List of {'name': 'Topic 1', 'weight': 2}
        hours_per_day = data.get('hours_per_day', 4)
        
        if not exam_date_str or not topics:
            return jsonify({'error': 'Exam date and topics are required'}), 400
            
        exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d')
        days_until = (exam_date - datetime.utcnow()).days
        
        if days_until <= 0:
            return jsonify({'error': 'Exam date must be in the future'}), 400
            
        # Use DP Algorithm to optimize schedule
        raw_schedule = optimize_study_schedule(days_until, topics, hours_per_day)
        
        # Format schedule with dates
        formatted_schedule = []
        current_date = datetime.utcnow()
        
        for i, daily_topics in enumerate(raw_schedule):
            date = current_date + timedelta(days=i+1)
            formatted_schedule.append({
                'date': date.strftime('%Y-%m-%d'),
                'day_of_week': date.strftime('%A'),
                'topics': daily_topics,
                'total_hours': sum(t['weight'] for t in daily_topics)
            })
            
        plan = StudyPlan(
            user_id=current_user.id,
            title=title,
            exam_date=exam_date,
            schedule=formatted_schedule
        )
        
        db.session.add(plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Study plan generated successfully',
            'plan_id': plan.id,
            'schedule': formatted_schedule
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@study_plans.route('/study-plans', methods=['GET'])
@api_login_required
def get_study_plans():
    try:
        plans = StudyPlan.query.filter_by(user_id=current_user.id).order_by(StudyPlan.created_at.desc()).all()
        
        return jsonify({
            'plans': [{
                'id': p.id,
                'title': p.title,
                'exam_date': p.exam_date.strftime('%Y-%m-%d'),
                'created_at': p.created_at.isoformat(),
                'days_remaining': (p.exam_date - datetime.utcnow()).days
            } for p in plans]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@study_plans.route('/study-plans/<int:plan_id>', methods=['GET'])
@api_login_required
def get_study_plan_detail(plan_id):
    try:
        plan = StudyPlan.query.filter_by(id=plan_id, user_id=current_user.id).first()
        
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
            
        return jsonify({
            'id': plan.id,
            'title': plan.title,
            'exam_date': plan.exam_date.strftime('%Y-%m-%d'),
            'schedule': plan.schedule
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
