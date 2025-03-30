import re
import json
import random
import logging
import os
from datetime import datetime
from ml_models import SentimentAnalyzer
from app import db
from models import ChatSession, ChatMessage
from flask_login import current_user

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize sentiment analyzer
sentiment_analyzer = SentimentAnalyzer()

class EmotionalSupportChatbot:
    def __init__(self):
        self.openai_client = None
        self.session = None
        self.initialize_openai()
        
        # Fallback responses if OpenAI is not available
        self.responses = {
            'greeting': [
                "Hello! I'm here to support you today. How are you feeling?",
                "Hi there! I'm here to listen. What's on your mind?",
                "Welcome! I'm your emotional support chatbot. How are you doing today?"
            ],
            'empathy': [
                "That sounds really challenging. I appreciate you sharing that with me.",
                "I can understand why you'd feel that way. It's completely valid.",
                "Thank you for opening up about this. I'm here to listen."
            ],
            'support': [
                "Remember that it's okay to take things one step at a time.",
                "Taking care of your mental health is important, and you're doing that right now.",
                "Remember to be gentle with yourself during difficult times."
            ],
            'question': [
                "Could you tell me more about what's been going on?",
                "How long have you been feeling this way?",
                "What kinds of things have helped you cope in the past?"
            ],
            'resources': [
                "Have you considered trying some mindfulness exercises? They can help ground you in the present moment.",
                "Sometimes talking to a professional can provide additional support. Would you like information about therapy options?",
                "Regular physical activity, even just a short walk, can sometimes help improve mood. Is that something you might try?"
            ],
            'unknown': [
                "I'm here to listen and support you. Could you share more about what's on your mind?",
                "I want to understand better how you're feeling. Could you elaborate?",
                "I'm listening. Please feel free to share what you're comfortable with."
            ]
        }
    
    def initialize_openai(self):
        """Initialize OpenAI client if API key is available"""
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if OPENAI_AVAILABLE and openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {str(e)}")
                self.openai_client = None
        else:
            logger.warning("OpenAI API key not found or package not installed")
            self.openai_client = None
    
    def start_chat_session(self, user_id):
        """Start a new chat session or retrieve active session"""
        # Check for existing active session
        existing_session = ChatSession.query.filter_by(
            user_id=user_id, 
            ended_at=None
        ).first()
        
        if existing_session:
            self.session = existing_session
            return existing_session.id
        
        # Create new session
        new_session = ChatSession(user_id=user_id)
        db.session.add(new_session)
        db.session.commit()
        
        self.session = new_session
        return new_session.id
    
    def end_chat_session(self, session_id):
        """End the chat session and calculate overall sentiment"""
        session = ChatSession.query.get(session_id)
        if session and not session.ended_at:
            # Get all user messages in this session
            user_messages = ChatMessage.query.filter_by(
                session_id=session_id,
                is_user=True
            ).all()
            
            # Calculate average sentiment if there are messages
            if user_messages:
                sentiment_scores = []
                for msg in user_messages:
                    sentiment = sentiment_analyzer.analyze_text(msg.message)
                    sentiment_scores.append(sentiment)
                
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                session.sentiment_score = avg_sentiment
            
            # Mark session as ended
            session.ended_at = datetime.utcnow()
            db.session.commit()
            
            self.session = None
            return True
        
        return False
    
    def get_chat_history(self, session_id, limit=10):
        """Get recent chat history for the session"""
        messages = ChatMessage.query.filter_by(
            session_id=session_id
        ).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
        
        # Return in chronological order
        return list(reversed(messages))
    
    def analyze_message(self, message):
        """Analyze user message to determine response type (fallback method)"""
        message_lower = message.lower()
        
        # Basic detection of message types
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return 'greeting'
        
        if any(word in message_lower for word in ['sad', 'depress', 'unhappy', 'anxious', 'worried', 'stress']):
            return 'empathy'
        
        if any(word in message_lower for word in ['help', 'advice', 'suggest', 'recommend']):
            return 'resources'
        
        if '?' in message:
            return 'question'
        
        return 'support'
    
    def process_message(self, user_id, message):
        """Process user message and generate response"""
        # Ensure session exists
        if not self.session:
            self.start_chat_session(user_id)
        
        # Save user message
        user_msg = ChatMessage(
            session_id=self.session.id,
            is_user=True,
            message=message
        )
        db.session.add(user_msg)
        db.session.commit()
        
        # Generate bot response
        bot_response = self.generate_response(message, self.session.id)
        
        # Save bot response
        bot_msg = ChatMessage(
            session_id=self.session.id,
            is_user=False,
            message=bot_response
        )
        db.session.add(bot_msg)
        db.session.commit()
        
        return bot_response
    
    def generate_response(self, message, session_id):
        """Generate a response using OpenAI GPT or fallback to rule-based"""
        if self.openai_client:
            try:
                # Get recent chat history for context
                history = self.get_chat_history(session_id, limit=5)
                context = []
                
                for msg in history:
                    role = "user" if msg.is_user else "assistant"
                    context.append({"role": role, "content": msg.message})
                
                # Add the current message
                context.append({"role": "user", "content": message})
                
                # Add system message with instructions
                system_message = {
                    "role": "system", 
                    "content": """You are an empathetic mental health support assistant. 
                    Your responses should be warm, supportive, and helpful. 
                    Keep your responses concise (maximum 4 sentences).
                    Focus on validation, empathy, and gentle suggestions.
                    Remember that you are not a licensed therapist, so never diagnose or offer medical advice.
                    Always encourage seeking professional help for serious concerns.
                    Use a warm, supportive tone throughout all interactions."""
                }
                
                messages = [system_message] + context
                
                # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7
                )
                
                return response.choices[0].message.content.strip()
            
            except Exception as e:
                logger.error(f"Error generating OpenAI response: {str(e)}")
                # Fall back to rule-based response
        
        # Rule-based fallback
        response_type = self.analyze_message(message)
        responses = self.responses.get(response_type, self.responses['unknown'])
        return random.choice(responses)
