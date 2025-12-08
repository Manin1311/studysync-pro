from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db, login_manager, socketio
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, supports_credentials=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import jsonify, request, redirect, url_for
        if request.is_json or request.path.startswith('/api'):
            return jsonify({'error': 'Unauthorized. Please log in.'}), 401
        return redirect(url_for('login'))

    # Import models
    from models import User, Course, Note, Flashcard, StudyRoom, StudySession, ExamPrediction, StudyPartner, Analytics, Achievement
    from flask_login import current_user, login_required
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except:
            return None
    
    @app.before_request
    def make_session_permanent():
        from flask import session
        session.permanent = True

    # Register blueprints
    from routes.auth import auth
    from routes.notes import notes
    from routes.courses import courses
    from routes.flashcards import flashcards
    from routes.analytics import analytics
    from routes.ai_assistant import ai_assistant
    from routes.partners import partners
    from routes.achievements import achievements
    from routes.exam_predictor import exam_predictor
    from routes.study_plans import study_plans
    from routes.resources import resources
    
    app.register_blueprint(auth, url_prefix='/api/auth')
    
    @app.route('/logout')
    def logout_page():
        from flask_login import logout_user
        from flask import redirect, url_for
        logout_user()
        return redirect(url_for('login'))

    app.register_blueprint(notes, url_prefix='/api')
    app.register_blueprint(courses, url_prefix='/api')
    app.register_blueprint(flashcards, url_prefix='/api')
    app.register_blueprint(analytics, url_prefix='/api')
    app.register_blueprint(ai_assistant, url_prefix='/api')
    app.register_blueprint(partners, url_prefix='/api')
    app.register_blueprint(achievements, url_prefix='/api')
    app.register_blueprint(exam_predictor, url_prefix='/api')
    app.register_blueprint(study_plans, url_prefix='/api')
    app.register_blueprint(resources, url_prefix='/api')

    # Main Routes
    @app.route("/")
    def index():
        from flask import redirect, url_for
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route("/login")
    def login():
        from flask import render_template
        return render_template('login.html')
        
    @app.route("/register")
    def register():
        from flask import render_template
        return render_template('login.html')

    @app.route("/dashboard")
    @login_required
    def dashboard():
        from flask import render_template
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        # Get real user stats
        notes_count = Note.query.filter_by(user_id=current_user.id).count()
        flashcards_count = Flashcard.query.filter_by(user_id=current_user.id).count()
        courses_count = Course.query.filter_by(user_id=current_user.id).count()
        
        # Calculate study streak
        week_ago = datetime.utcnow().date() - timedelta(days=7)
        recent_analytics = Analytics.query.filter(
            Analytics.user_id == current_user.id,
            Analytics.date >= week_ago
        ).all()
        active_days = len(set(a.date for a in recent_analytics))
        
        # Get weekly analytics data for chart
        chart_data = {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'data': [0, 0, 0, 0, 0, 0, 0]
        }
        
        for analytics in recent_analytics:
            day_index = analytics.date.weekday()
            chart_data['data'][day_index] += analytics.notes_created + analytics.flashcards_created
        
        stats = {
            'notes_count': notes_count,
            'flashcards_count': flashcards_count,
            'courses_count': courses_count,
            'active_days': active_days,
            'chart_data': chart_data
        }
        
        return render_template('dashboard.html', active_page='dashboard', stats=stats)

    @app.route("/resources")
    @login_required
    def resources_page():
        from flask import render_template
        return render_template('resources.html', active_page='resources')
        
    @app.route("/study-plan")
    @login_required
    def study_plan_page():
        from flask import render_template
        return render_template('study_plans.html', active_page='dashboard')
        
    @app.route("/rooms")
    @login_required
    def rooms_page():
        from flask import render_template
        return render_template('rooms.html', active_page='rooms')

    # Real Application Routes
    @app.route("/courses")
    @login_required
    def courses_page():
        from flask import render_template
        return render_template('courses.html', active_page='courses')

    @app.route("/notes")
    @login_required
    def notes_page():
        from flask import render_template
        return render_template('notes.html', active_page='notes')

    @app.route("/flashcards")
    @login_required
    def flashcards_page():
        from flask import render_template
        return render_template('flashcards.html', active_page='flashcards')

    @app.route("/ai-chat")
    @login_required
    def ai_chat_page():
        from flask import render_template
        return render_template('ai_chat.html', active_page='ai-assistant')

    @app.route("/study-partner")
    @login_required
    def partners_page():
        from flask import render_template
        return render_template('partners.html', active_page='partners')

    # Import events to register handlers for SocketIO
    import events

    with app.app_context():
        db.create_all()
        print("Database tables & app initialized!")

    return app

app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
