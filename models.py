from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    moods = db.relationship('MoodEntry', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    assessments = db.relationship('AssessmentResult', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    chat_sessions = db.relationship('ChatSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mood_score = db.Column(db.Integer, nullable=False)  # 1-10 scale
    notes = db.Column(db.Text)
    activities = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Mood {self.mood_score} at {self.created_at}>'

class AssessmentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    
    # Relationships
    questions = db.relationship('AssessmentQuestion', backref='assessment_type', lazy='dynamic', cascade='all, delete-orphan')
    results = db.relationship('AssessmentResult', backref='assessment_type', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<AssessmentType {self.name}>'

class AssessmentQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assessment_type_id = db.Column(db.Integer, db.ForeignKey('assessment_type.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_type = db.Column(db.String(50), nullable=False)  # likert, binary, multiple_choice
    options = db.Column(db.Text)  # JSON string of options if applicable
    order = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<Question {self.id}: {self.question_text[:30]}...>'

class AssessmentResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_type_id = db.Column(db.Integer, db.ForeignKey('assessment_type.id'), nullable=False)
    responses = db.Column(db.Text)  # JSON string of responses
    score = db.Column(db.Float, nullable=False)
    interpretation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AssessmentResult {self.id} Score: {self.score}>'

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    category = db.Column(db.String(100))
    resource_type = db.Column(db.String(50))  # article, video, exercise, etc.
    external_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Resource {self.title}>'

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    sentiment_score = db.Column(db.Float)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ChatSession {self.id}>'

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    is_user = db.Column(db.Boolean, default=True)  # True if sent by user, False if by bot
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        sender = "User" if self.is_user else "Bot"
        return f'<Message from {sender}: {self.message[:30]}...>'

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(100))  # exercise, meditation, reading, etc.
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Recommendation {self.title}>'