from flask import Blueprint, request, jsonify  # pyright: ignore[reportMissingImports]
from flask_login import current_user  # pyright: ignore[reportMissingImports]
from extensions import db
from models import Note, Course
from utils.dsa_helpers import Trie
from utils.auth_decorator import api_login_required
from utils.ai_integration import generate_ai_response, summarize_text
import re
import os

ai_assistant = Blueprint('ai_assistant', __name__)

# Initialize Trie for keyword search (Fallback logic)
def build_trie_from_notes(user_id):
    """Build a Trie data structure from user's notes for fast keyword search"""
    trie = Trie()
    notes = Note.query.filter_by(user_id=user_id).all()
    
    for note in notes:
        # Extract keywords from note content
        content = (note.title or '') + ' ' + (note.content or '')
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Add each word to trie with note data
        for word in set(words):  # Use set to avoid duplicates
            if len(word) > 2:  # Only index words longer than 2 characters
                trie.insert(word, {
                    'note_id': note.id,
                    'title': note.title,
                    'content': note.content[:200] + '...' if note.content and len(note.content) > 200 else note.content,
                    'course_id': note.course_id
                })
    
    return trie

@ai_assistant.route('/ai/search', methods=['POST'])
@api_login_required
def search_notes():
    try:
        data = request.get_json()
        query = data.get('query', '').strip().lower()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Build Trie from user's notes
        trie = build_trie_from_notes(current_user.id)
        
        # Search using Trie
        results = []
        query_words = re.findall(r'\b\w+\b', query)
        
        for word in query_words:
            if len(word) > 2:
                # Use Trie to find matching notes
                matches = trie.starts_with(word)
                results.extend(matches)
        
        # Remove duplicates and rank by relevance
        seen_note_ids = set()
        unique_results = []
        for result in results:
            if result['note_id'] not in seen_note_ids:
                seen_note_ids.add(result['note_id'])
                unique_results.append(result)
        
        # Get course names for results
        for result in unique_results:
            course = Course.query.get(result.get('course_id'))
            result['course_name'] = course.name if course else 'Unknown'
        
        return jsonify({
            'query': query,
            'results': unique_results[:10],  # Limit to 10 results
            'count': len(unique_results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_assistant.route('/ai/ask', methods=['POST'])
@api_login_required
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
            
        # Context Retrieval (RAG - Retrieval Augmented Generation)
        # 1. Find relevant notes using Trie
        trie = build_trie_from_notes(current_user.id)
        question_words = re.findall(r'\b\w+\b', question.lower())
        relevant_notes = []
        for word in question_words:
            if len(word) > 2:
                matches = trie.starts_with(word)
                relevant_notes.extend(matches)
                
        # Deduplicate
        seen_ids = set()
        context_texts = []
        for note in relevant_notes:
            if note['note_id'] not in seen_ids:
                full_note = Note.query.get(note['note_id'])
                if full_note:
                    context_texts.append(f"Note Title: {full_note.title}\nContent: {full_note.content}")
                seen_ids.add(note['note_id'])
        
        # 2. Construct Prompt
        context_block = "\n\n".join(context_texts[:3]) # Limit to top 3 notes to fit context window
        
        if os.getenv("GEMINI_API_KEY"):
            system_prompt = f"""You are StudySync AI, a helpful academic assistant.
            Use the following context from the user's notes to answer their question.
            If the answer isn't in the notes, use your general knowledge but mention that it wasn't in their notes.
            
            Context:
            {context_block}
            
            User Question: {question}
            """
            answer = generate_ai_response(system_prompt)
        else:
            # Fallback for no API key
            if context_block:
                answer = f"**Local Search Mode (No API Key detected)**\n\nI found relevant information in your notes:\n\n{context_block[:500]}..."
            else:
                answer = "I couldn't find anything relevant in your notes matching that query. Please add a GEMINI_API_KEY to enable full AI capabilities."

        return jsonify({
            'question': question,
            'answer': answer,
            'related_notes': [n for n in relevant_notes[:3]]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_assistant.route('/ai/summarize', methods=['POST'])
@api_login_required
def summarize_note():
    try:
        data = request.get_json()
        note_id = data.get('note_id')
        
        if not note_id:
            return jsonify({'error': 'Note ID is required'}), 400
        
        note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
        
        if not note:
            return jsonify({'error': 'Note not found'}), 404
            
        if os.getenv("GEMINI_API_KEY"):
            summary_text = summarize_text(note.content)
            key_points = ["Generated by Gemini AI"]
        else:
            # Fallback heuristic summary
            content = note.content or ''
            sentences = re.split(r'[.!?]+', content)
            summary_text = sentences[0] if sentences else 'No content'
            key_points = sentences[1:4] if len(sentences) > 1 else []
        
        summary = {
            'title': note.title,
            'first_sentence': summary_text, # Reused field for full summary compatibility
            'key_points': key_points,
            'word_count': len((note.content or '').split()),
            'estimated_read_time': len((note.content or '').split()) // 200
        }
        
        return jsonify({
            'note_id': note_id,
            'summary': summary
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



