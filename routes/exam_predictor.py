from flask import Blueprint, request, jsonify  # pyright: ignore[reportMissingImports]
from flask_login import current_user  # pyright: ignore[reportMissingImports]
from extensions import db
from models import ExamPrediction, Course, Note
from collections import Counter
from utils.auth_decorator import api_login_required
import re

exam_predictor = Blueprint('exam_predictor', __name__)

def analyze_note_patterns(course_id):
    """Analyze notes to find frequently mentioned topics (pattern matching)"""
    notes = Note.query.filter_by(course_id=course_id).all()
    
    # Extract keywords and phrases
    all_keywords = []
    question_patterns = []
    
    for note in notes:
        content = (note.title or '') + ' ' + (note.content or '')
        
        # Find question-like patterns
        questions = re.findall(r'[^.!?]*\?', content)
        question_patterns.extend(questions)
        
        # Extract important keywords (capitalized words, technical terms)
        words = re.findall(r'\b[A-Z][a-z]+\b|\b\w{5,}\b', content)
        all_keywords.extend(words)
    
    # Count frequency
    keyword_counts = Counter(all_keywords)
    most_common = keyword_counts.most_common(20)
    
    return {
        'keywords': [{'word': word, 'frequency': count} for word, count in most_common],
        'question_patterns': question_patterns[:10]
    }

@exam_predictor.route('/exam-predictor/<int:course_id>/analyze', methods=['POST'])
@api_login_required
def analyze_course(course_id):
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Analyze notes for patterns
        patterns = analyze_note_patterns(course_id)
        
        # Generate predictions based on patterns
        predictions = []
        
        # Create predictions from frequent keywords
        for keyword_data in patterns['keywords'][:10]:
            if keyword_data['frequency'] >= 3:  # Only if mentioned 3+ times
                confidence = min(keyword_data['frequency'] * 10, 95)  # Max 95%
                
                prediction = ExamPrediction(
                    course_id=course_id,
                    question_text=f"Explain {keyword_data['word']} in detail.",
                    confidence_score=confidence / 100
                )
                db.session.add(prediction)
                predictions.append({
                    'question': prediction.question_text,
                    'confidence': round(confidence, 1)
                })
        
        # Create predictions from question patterns
        for question in patterns['question_patterns'][:5]:
            if len(question.strip()) > 10:
                prediction = ExamPrediction(
                    course_id=course_id,
                    question_text=question.strip(),
                    confidence_score=0.75  # Medium confidence for question patterns
                )
                db.session.add(prediction)
                predictions.append({
                    'question': prediction.question_text,
                    'confidence': 75.0
                })
        
        db.session.commit()
        
        return jsonify({
            'message': 'Course analyzed and predictions generated',
            'course_id': course_id,
            'course_name': course.name,
            'predictions': predictions,
            'patterns_found': {
                'keywords': len(patterns['keywords']),
                'question_patterns': len(patterns['question_patterns'])
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exam_predictor.route('/exam-predictor/<int:course_id>', methods=['GET'])
@api_login_required
def get_predictions(course_id):
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Get predictions, sorted by confidence
        predictions = ExamPrediction.query.filter_by(
            course_id=course_id
        ).order_by(ExamPrediction.confidence_score.desc()).limit(20).all()
        
        return jsonify({
            'course_id': course_id,
            'course_name': course.name,
            'predictions': [{
                'id': p.id,
                'question_text': p.question_text,
                'confidence_score': round(p.confidence_score * 100, 1),
                'created_at': p.created_at.isoformat()
            } for p in predictions],
            'count': len(predictions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exam_predictor.route('/exam-predictor/<int:course_id>/top', methods=['GET'])
@api_login_required
def get_top_predictions(course_id):
    try:
        # Get top 5 predictions by confidence
        predictions = ExamPrediction.query.filter_by(
            course_id=course_id
        ).order_by(ExamPrediction.confidence_score.desc()).limit(5).all()
        
        return jsonify({
            'top_predictions': [{
                'question': p.question_text,
                'confidence': round(p.confidence_score * 100, 1)
            } for p in predictions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

