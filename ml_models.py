import os
import pickle
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import logging

# Initialize logging
logger = logging.getLogger(__name__)

# Download NLTK resources if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Sentiment Analysis Model
class SentimentAnalyzer:
    def __init__(self):
        self.model = None
        self.load_or_create_model()
    
    def preprocess_text(self, text):
        """Preprocess text for sentiment analysis"""
        tokens = word_tokenize(text.lower())
        tokens = [lemmatizer.lemmatize(token) for token in tokens if token.isalpha()]
        tokens = [token for token in tokens if token not in stop_words]
        return ' '.join(tokens)
    
    def load_or_create_model(self):
        """Load sentiment model from disk or create a new one"""
        try:
            # Basic sentiment model pipeline
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=5000, preprocessor=self.preprocess_text)),
                ('classifier', MultinomialNB())
            ])
            logger.info("Created new sentiment analysis model")
        except Exception as e:
            logger.error(f"Error loading/creating sentiment model: {str(e)}")
    
    def analyze_text(self, text):
        """
        Simple rule-based sentiment analysis as a fallback
        Returns score from 0 (negative) to 1 (positive)
        """
        if not text:
            return 0.5  # Neutral for empty text
        
        # Simple keyword-based approach as fallback
        positive_words = ['good', 'great', 'happy', 'joy', 'excellent', 'wonderful', 'love', 
                          'positive', 'awesome', 'fantastic', 'calm', 'peaceful', 'excited']
        negative_words = ['bad', 'sad', 'terrible', 'awful', 'hate', 'unhappy', 'depressed', 
                         'anxious', 'worried', 'stress', 'afraid', 'angry', 'upset', 'fear']
        
        processed_text = self.preprocess_text(text).split()
        
        pos_count = sum(1 for word in processed_text if word in positive_words)
        neg_count = sum(1 for word in processed_text if word in negative_words)
        
        if pos_count + neg_count == 0:
            return 0.5  # Neutral
        
        return pos_count / (pos_count + neg_count)

# Recommendation Engine
class RecommendationEngine:
    def __init__(self):
        self.activities = {
            'stress': [
                {'title': 'Progressive Muscle Relaxation', 'type': 'exercise', 
                 'description': 'Tense and relax different muscle groups to reduce physical tension.'},
                {'title': '4-7-8 Breathing Exercise', 'type': 'breathing', 
                 'description': 'Breathe in for 4 seconds, hold for 7, exhale for 8 to activate relaxation response.'},
                {'title': 'Mindful Walking', 'type': 'meditation', 
                 'description': 'Take a slow, mindful walk focusing on each step and your surroundings.'}
            ],
            'anxiety': [
                {'title': 'Grounding Technique: 5-4-3-2-1', 'type': 'exercise', 
                 'description': 'Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste.'},
                {'title': 'Worry Time Exercise', 'type': 'coping_strategy', 
                 'description': 'Schedule a specific time to address worries, postponing them until then.'},
                {'title': 'Body Scan Meditation', 'type': 'meditation', 
                 'description': 'Mentally scan your body from head to toe, observing sensations without judgment.'}
            ],
            'depression': [
                {'title': 'Behavioral Activation', 'type': 'exercise', 
                 'description': 'Schedule and engage in small, enjoyable activities throughout your day.'},
                {'title': 'Gratitude Journaling', 'type': 'writing', 
                 'description': 'Write down three things you are grateful for each day'},
                {'title': 'Morning Sunlight Exposure', 'type': 'lifestyle', 
                 'description': 'Get 15-30 minutes of morning sunlight to help regulate mood and sleep cycles.'}
            ],
            'low_mood': [
                {'title': 'Pleasant Activity Scheduling', 'type': 'exercise', 
                 'description': 'Plan and engage in activities that have brought you joy in the past.'},
                {'title': 'Values Reflection', 'type': 'writing', 
                 'description': 'Write about your core values and small ways to align with them today.'},
                {'title': 'Social Connection Exercise', 'type': 'social', 
                 'description': 'Reach out to someone supportive, even with a brief message or call.'}
            ],
            'sleep': [
                {'title': 'Sleep Hygiene Checklist', 'type': 'lifestyle', 
                 'description': 'Create a bedtime routine and optimize your sleep environment.'},
                {'title': 'Progressive Relaxation for Sleep', 'type': 'exercise', 
                 'description': 'Systematically relax your body from toes to head while in bed.'},
                {'title': 'Worry Download', 'type': 'writing', 
                 'description': 'Write down concerns before bed to clear your mind for sleep.'}
            ]
        }
    
    def get_recommendations(self, user_data):
        """Generate personalized recommendations based on user data"""
        recommendations = []
        
        # Extract user needs from assessment results and mood entries
        needs = self._determine_user_needs(user_data)
        
        # Get relevant activities for each identified need
        for need in needs:
            if need in self.activities:
                # Add 1-2 activities for each identified need
                num_activities = min(2, len(self.activities[need]))
                for i in range(num_activities):
                    recommendations.append(self.activities[need][i])
        
        # If we have fewer than 3 recommendations, add some general wellbeing activities
        if len(recommendations) < 3:
            general_activities = [
                {'title': 'Mindful Breathing', 'type': 'meditation', 
                 'description': 'Focus on your breath for 5 minutes, noticing the sensation of breathing.'},
                {'title': 'Nature Connection', 'type': 'lifestyle', 
                 'description': 'Spend 15 minutes outside, paying attention to natural elements around you.'},
                {'title': 'Gratitude Practice', 'type': 'writing', 
                 'description': 'Write down three things you appreciate in your life right now.'}
            ]
            
            # Add enough general activities to have at least 3 recommendations
            for i in range(min(3 - len(recommendations), len(general_activities))):
                recommendations.append(general_activities[i])
        
        return recommendations[:5]  # Return at most 5 recommendations
    
    def _determine_user_needs(self, user_data):
        """Analyze user data to determine needs"""
        needs = []
        
        # Check assessment results
        if 'assessments' in user_data:
            for assessment in user_data['assessments']:
                # PHQ-9 assessment for depression
                if assessment.get('assessment_type') == 'phq9' and assessment.get('score', 0) > 10:
                    needs.append('depression')
                
                # GAD-7 assessment for anxiety
                if assessment.get('assessment_type') == 'gad7' and assessment.get('score', 0) > 10:
                    needs.append('anxiety')
                
                # PSS assessment for stress
                if assessment.get('assessment_type') == 'pss' and assessment.get('score', 0) > 20:
                    needs.append('stress')
        
        # Check mood entries
        if 'moods' in user_data and user_data['moods']:
            # Calculate average mood from the last 3 entries
            recent_moods = user_data['moods'][:3]
            avg_mood = sum(entry.get('mood_score', 5) for entry in recent_moods) / len(recent_moods)
            
            if avg_mood < 4:
                needs.append('low_mood')
        
        # Check for sleep issues in chat logs
        if 'chat_messages' in user_data:
            sleep_keywords = ['sleep', 'insomnia', 'tired', 'fatigue', 'exhausted', 'rest']
            chat_text = ' '.join([msg.get('message', '') for msg in user_data['chat_messages']])
            
            if any(keyword in chat_text.lower() for keyword in sleep_keywords):
                needs.append('sleep')
        
        # If no specific needs identified, add general wellbeing
        if not needs:
            return ['low_mood']  # Default to general mood improvement
        
        return needs
