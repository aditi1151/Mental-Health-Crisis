import json
import logging
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db
from models import (User, MoodEntry, Resource, ChatSession, ChatMessage,)
from chatbot import EmotionalSupportChatbot


# Initialize logging
logger = logging.getLogger(__name__)

# Initialize chatbot
chatbot = EmotionalSupportChatbot()

# Home route
@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
            
        # Check if user exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already in use.', 'danger')
            return render_template('register.html')
            
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    """Render user dashboard with summary of their data"""
    # Get recent mood entries
    recent_moods = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.created_at.desc()).limit(7).all()
    
    
    # Get mood trend data for chart
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    mood_entries = MoodEntry.query.filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.created_at >= thirty_days_ago
    ).order_by(MoodEntry.created_at).all()
    
    mood_data = {
        'labels': [entry.created_at.strftime("%b %d") for entry in mood_entries],
        'values': [entry.mood_score for entry in mood_entries]
    }
    
    return render_template(
        'dashboard.html',
        recent_moods=recent_moods,
        mood_data=mood_data
    )

# Mood tracking routes
@app.route('/mood-tracker', methods=['GET'])
@login_required
def mood_tracker():
    """Render mood tracker page"""
    # Get recent mood entries
    recent_moods = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.created_at.desc()).limit(30).all()
    
    return render_template('mood_tracker.html', moods=recent_moods)

@app.route('/mood/add', methods=['POST'])
@login_required
def add_mood():
    """Add a new mood entry"""
    try:
        mood_score = int(request.form.get('mood_score'))
        notes = request.form.get('notes', '')
        activities = request.form.get('activities', '')
        
        # Validate mood score (1-10)
        if mood_score < 1 or mood_score > 10:
            flash('Mood score must be between 1 and 10.', 'danger')
            return redirect(url_for('mood_tracker'))
        
        # Create new mood entry
        new_mood = MoodEntry(
            user_id=current_user.id,
            mood_score=mood_score,
            notes=notes,
            activities=activities
        )
        
        db.session.add(new_mood)
        db.session.commit()
        
        flash('Mood entry added successfully!', 'success')
        return redirect(url_for('mood_tracker'))
    
    except ValueError:
        flash('Invalid mood score. Please enter a number between 1 and 10.', 'danger')
        return redirect(url_for('mood_tracker'))
    except Exception as e:
        logger.error(f"Error adding mood entry: {str(e)}")
        flash('An error occurred while adding your mood entry. Please try again.', 'danger')
        return redirect(url_for('mood_tracker'))

@app.route('/mood/data')
@login_required
def get_mood_data():
    """Get mood data for charts"""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    mood_entries = MoodEntry.query.filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.created_at >= start_date
    ).order_by(MoodEntry.created_at).all()
    
    data = {
        'labels': [entry.created_at.strftime("%b %d") for entry in mood_entries],
        'values': [entry.mood_score for entry in mood_entries],
        'notes': [entry.notes for entry in mood_entries]
    }
    
    return jsonify(data)


# Chatbot routes
@app.route('/chatbot')
@login_required
def chatbot_page():
    """Render chatbot page"""
    # Start or retrieve chat session
    session_id = chatbot.start_chat_session(current_user.id)
    
    # Get chat history
    chat_history = chatbot.get_chat_history(session_id)
    
    return render_template('chatbot.html', chat_history=chat_history)

@app.route('/chatbot/message', methods=['POST'])
@login_required
def chatbot_message():
    """Process chatbot message"""
    try:
        message = request.form.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'})
        
        # Process message with chatbot
        response = chatbot.process_message(current_user.id, message)
        
        return jsonify({
            'status': 'success',
            'response': response
        })
    
    except Exception as e:
        logger.error(f"Error processing chatbot message: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while processing your message'
        })

@app.route('/chatbot/end-session', methods=['POST'])
@login_required
def end_chat_session():
    """End current chat session"""
    try:
        session_id = request.form.get('session_id')
        
        if not session_id:
            # Get active session for user
            chat_session = ChatSession.query.filter_by(user_id=current_user.id, ended_at=None).first()
            
            if chat_session:
                session_id = chat_session.id
        
        if session_id:
            success = chatbot.end_chat_session(session_id)
            
            if success:
                
                return jsonify({
                    'status': 'success',
                    'message': 'Chat session ended successfully'
                })
        
        return jsonify({
            'status': 'error',
            'message': 'No active chat session found'
        })
    
    except Exception as e:
        logger.error(f"Error ending chat session: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while ending the chat session'
        })

# Resources routes
@app.route('/resources')
def resources():
    """Render resources page"""
    # Get all resources
    all_resources = Resource.query.all()
    
    # Group resources by category
    resources_by_category = {}
    for resource in all_resources:
        if resource.category not in resources_by_category:
            resources_by_category[resource.category] = []
        
        resources_by_category[resource.category].append(resource)
    
    return render_template('resources.html', resources_by_category=resources_by_category)



# User profile route
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Render and update user profile"""
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Update email
            if email and email != current_user.email:
                # Check if email is already in use
                existing_user = User.query.filter_by(email=email).first()
                if existing_user and existing_user.id != current_user.id:
                    flash('Email already in use by another account.', 'danger')
                else:
                    current_user.email = email
                    db.session.commit()
                    flash('Email updated successfully.', 'success')
            
            # Update password
            if current_password and new_password:
                if not current_user.check_password(current_password):
                    flash('Current password is incorrect.', 'danger')
                elif new_password != confirm_password:
                    flash('New passwords do not match.', 'danger')
                else:
                    current_user.set_password(new_password)
                    db.session.commit()
                    flash('Password updated successfully.', 'success')
            
            return redirect(url_for('profile'))
        
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            flash('An error occurred while updating your profile.', 'danger')
    
    return render_template('profile.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, message='Page not found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, message='Internal server error'), 500
