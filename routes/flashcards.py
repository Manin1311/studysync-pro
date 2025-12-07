from flask import Blueprint, request, jsonify  # pyright: ignore[reportMissingImports]
from flask_login import current_user  # pyright: ignore[reportMissingImports]
from extensions import db
from models import Flashcard, Note
from datetime import datetime, timedelta
from utils.dsa_helpers import PriorityQueue
from utils.auth_decorator import api_login_required

flashcards = Blueprint('flashcards', __name__)

@flashcards.route('/flashcards', methods=['GET'])
@api_login_required
def get_flashcards():
    try:
        note_id = request.args.get('note_id', type=int)
        due_only = request.args.get('due_only', 'false').lower() == 'true'
        
        query = Flashcard.query.filter_by(user_id=current_user.id)
        
        if note_id:
            query = query.filter_by(note_id=note_id)
        
        if due_only:
            query = query.filter(Flashcard.next_review <= datetime.utcnow())
        
        flashcards_list = query.all()
        
        return jsonify({
            'flashcards': [{
                'id': flashcard.id,
                'note_id': flashcard.note_id,
                'front': flashcard.front,
                'back': flashcard.back,
                'difficulty': flashcard.difficulty,
                'next_review': flashcard.next_review.isoformat(),
                'review_count': flashcard.review_count,
                'created_at': flashcard.created_at.isoformat()
            } for flashcard in flashcards_list]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@flashcards.route('/flashcards', methods=['POST'])
@api_login_required
def create_flashcard():
    try:
        data = request.get_json()
        
        if not data or not data.get('note_id') or not data.get('front') or not data.get('back'):
            return jsonify({'error': 'Note ID, front, and back are required'}), 400
        
        note_id = data.get('note_id')
        
        # Verify note exists and belongs to user
        note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        flashcard = Flashcard(
            note_id=note_id,
            user_id=current_user.id,
            front=data.get('front'),
            back=data.get('back'),
            difficulty=data.get('difficulty', 0),
            next_review=datetime.utcnow()
        )
        
        db.session.add(flashcard)
        db.session.commit()
        
        return jsonify({
            'message': 'Flashcard created successfully',
            'flashcard': {
                'id': flashcard.id,
                'note_id': flashcard.note_id,
                'front': flashcard.front,
                'back': flashcard.back,
                'difficulty': flashcard.difficulty
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@flashcards.route('/flashcards/<int:flashcard_id>/review', methods=['POST'])
@api_login_required
def review_flashcard(flashcard_id):
    try:
        flashcard = Flashcard.query.filter_by(id=flashcard_id, user_id=current_user.id).first()
        
        if not flashcard:
            return jsonify({'error': 'Flashcard not found'}), 404
        
        data = request.get_json()
        correct = data.get('correct', False)
        difficulty = data.get('difficulty', flashcard.difficulty)
        
        # Spaced repetition algorithm
        flashcard.review_count += 1
        
        if correct:
            # Increase difficulty level (0=easy, 1=medium, 2=hard)
            if difficulty < 2:
                difficulty = min(difficulty + 1, 2)
            
            # Calculate next review based on difficulty and review count
            days_until_review = {
                0: 1,  # Easy: review in 1 day
                1: 3,  # Medium: review in 3 days
                2: 7   # Hard: review in 7 days
            }.get(difficulty, 1)
            
            # Increase interval based on review count
            multiplier = 1 + (flashcard.review_count * 0.1)
            days_until_review = int(days_until_review * multiplier)
            
            flashcard.next_review = datetime.utcnow() + timedelta(days=days_until_review)
        else:
            # If incorrect, review again soon
            flashcard.next_review = datetime.utcnow() + timedelta(hours=1)
            difficulty = max(0, difficulty - 1)
        
        flashcard.difficulty = difficulty
        
        db.session.commit()
        
        return jsonify({
            'message': 'Flashcard reviewed',
            'flashcard': {
                'id': flashcard.id,
                'difficulty': flashcard.difficulty,
                'review_count': flashcard.review_count,
                'next_review': flashcard.next_review.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@flashcards.route('/flashcards/review-queue', methods=['GET'])
@api_login_required
def get_review_queue():
    try:
        # Get flashcards due for review using Priority Queue concept
        due_flashcards = Flashcard.query.filter(
            Flashcard.user_id == current_user.id,
            Flashcard.next_review <= datetime.utcnow()
        ).order_by(Flashcard.next_review.asc()).limit(20).all()
        
        # Build priority queue (for demonstration of DSA concept)
        pq = PriorityQueue()
        for card in due_flashcards:
            priority = card.next_review.timestamp()
            pq.push(card, priority)
        
        queue_list = []
        while not pq.is_empty():
            card = pq.pop()
            queue_list.append({
                'id': card.id,
                'note_id': card.note_id,
                'front': card.front,
                'back': card.back,
                'difficulty': card.difficulty,
                'next_review': card.next_review.isoformat(),
                'review_count': card.review_count
            })
        
        return jsonify({
            'review_queue': queue_list,
            'count': len(queue_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@flashcards.route('/flashcards/<int:flashcard_id>', methods=['DELETE'])
@api_login_required
def delete_flashcard(flashcard_id):
    try:
        flashcard = Flashcard.query.filter_by(id=flashcard_id, user_id=current_user.id).first()
        
        if not flashcard:
            return jsonify({'error': 'Flashcard not found'}), 404
        
        db.session.delete(flashcard)
        db.session.commit()
        
        return jsonify({'message': 'Flashcard deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

