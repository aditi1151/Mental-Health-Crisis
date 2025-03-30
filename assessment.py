import json
import logging
from datetime import datetime
from app import db
from models import AssessmentType, AssessmentQuestion, AssessmentResult

# Initialize logging
logger = logging.getLogger(__name__)

class AssessmentEngine:
    """
    Engine for managing mental health assessments:
    - PHQ-9 (Depression)
    - GAD-7 (Anxiety)
    - PSS (Perceived Stress Scale)
    """
    
    def __init__(self):
        self.assessment_types = {
            'phq9': {
                'name': 'PHQ-9 Depression Scale',
                'description': 'Screens for depression severity over the past two weeks',
                'instructions': 'Over the last 2 weeks, how often have you been bothered by any of the following problems?',
                'questions': [
                    'Little interest or pleasure in doing things',
                    'Feeling down, depressed, or hopeless',
                    'Trouble falling or staying asleep, or sleeping too much',
                    'Feeling tired or having little energy',
                    'Poor appetite or overeating',
                    'Feeling bad about yourself - or that you are a failure or have let yourself or your family down',
                    'Trouble concentrating on things, such as reading the newspaper or watching television',
                    'Moving or speaking so slowly that other people could have noticed, or the opposite - being so fidgety or restless that you have been moving around a lot more than usual',
                    'Thoughts that you would be better off dead, or of hurting yourself in some way'
                ],
                'options': [
                    {'value': 0, 'text': 'Not at all'},
                    {'value': 1, 'text': 'Several days'},
                    {'value': 2, 'text': 'More than half the days'},
                    {'value': 3, 'text': 'Nearly every day'}
                ],
                'scoring': {
                    'ranges': [
                        {'min': 0, 'max': 4, 'severity': 'Minimal depression', 'interpretation': 'Your symptoms suggest minimal depression. Continue to monitor your mood and practice self-care.'},
                        {'min': 5, 'max': 9, 'severity': 'Mild depression', 'interpretation': 'Your symptoms suggest mild depression. Consider increasing self-care activities and monitoring your symptoms.'},
                        {'min': 10, 'max': 14, 'severity': 'Moderate depression', 'interpretation': 'Your symptoms suggest moderate depression. Consider consulting with a mental health professional for further evaluation.'},
                        {'min': 15, 'max': 19, 'severity': 'Moderately severe depression', 'interpretation': 'Your symptoms suggest moderately severe depression. It\'s recommended to consult with a mental health professional.'},
                        {'min': 20, 'max': 27, 'severity': 'Severe depression', 'interpretation': 'Your symptoms suggest severe depression. Please consider seeking professional help promptly.'}
                    ]
                }
            },
            'gad7': {
                'name': 'GAD-7 Anxiety Scale',
                'description': 'Screens for generalized anxiety disorder over the past two weeks',
                'instructions': 'Over the last 2 weeks, how often have you been bothered by the following problems?',
                'questions': [
                    'Feeling nervous, anxious, or on edge',
                    'Not being able to stop or control worrying',
                    'Worrying too much about different things',
                    'Trouble relaxing',
                    'Being so restless that it\'s hard to sit still',
                    'Becoming easily annoyed or irritable',
                    'Feeling afraid, as if something awful might happen'
                ],
                'options': [
                    {'value': 0, 'text': 'Not at all'},
                    {'value': 1, 'text': 'Several days'},
                    {'value': 2, 'text': 'More than half the days'},
                    {'value': 3, 'text': 'Nearly every day'}
                ],
                'scoring': {
                    'ranges': [
                        {'min': 0, 'max': 4, 'severity': 'Minimal anxiety', 'interpretation': 'Your symptoms suggest minimal anxiety. Continue to monitor your feelings and practice self-care.'},
                        {'min': 5, 'max': 9, 'severity': 'Mild anxiety', 'interpretation': 'Your symptoms suggest mild anxiety. Consider increasing self-care activities and monitoring your symptoms.'},
                        {'min': 10, 'max': 14, 'severity': 'Moderate anxiety', 'interpretation': 'Your symptoms suggest moderate anxiety. Consider consulting with a mental health professional for further evaluation.'},
                        {'min': 15, 'max': 21, 'severity': 'Severe anxiety', 'interpretation': 'Your symptoms suggest severe anxiety. Please consider seeking professional help promptly.'}
                    ]
                }
            },
            'pss': {
                'name': 'Perceived Stress Scale',
                'description': 'Measures your perception of stress over the past month',
                'instructions': 'For each question, please indicate how often you have felt or thought a certain way during the last month.',
                'questions': [
                    'In the last month, how often have you been upset because of something that happened unexpectedly?',
                    'In the last month, how often have you felt that you were unable to control the important things in your life?',
                    'In the last month, how often have you felt nervous and stressed?',
                    'In the last month, how often have you felt confident about your ability to handle your personal problems?',
                    'In the last month, how often have you felt that things were going your way?',
                    'In the last month, how often have you found that you could not cope with all the things that you had to do?',
                    'In the last month, how often have you been able to control irritations in your life?',
                    'In the last month, how often have you felt that you were on top of things?',
                    'In the last month, how often have you been angered because of things that happened that were outside of your control?',
                    'In the last month, how often have you felt difficulties were piling up so high that you could not overcome them?'
                ],
                'options': [
                    {'value': 0, 'text': 'Never'},
                    {'value': 1, 'text': 'Almost never'},
                    {'value': 2, 'text': 'Sometimes'},
                    {'value': 3, 'text': 'Fairly often'},
                    {'value': 4, 'text': 'Very often'}
                ],
                'scoring': {
                    'reverse_items': [3, 4, 6, 7],  # 0-indexed question numbers to reverse score
                    'ranges': [
                        {'min': 0, 'max': 13, 'severity': 'Low stress', 'interpretation': 'Your perceived stress level is low. Continue practicing healthy coping mechanisms.'},
                        {'min': 14, 'max': 26, 'severity': 'Moderate stress', 'interpretation': 'Your perceived stress level is moderate. Consider implementing additional stress management techniques.'},
                        {'min': 27, 'max': 40, 'severity': 'High stress', 'interpretation': 'Your perceived stress level is high. Consider consulting with a mental health professional for support.'}
                    ]
                }
            }
        }
        
        # Initialize assessment types
        self.initialize_assessment_types()
    
    def initialize_assessment_types(self):
        """Initialize assessment types in the database"""
        try:
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            
            if not inspector.has_table('assessment_type'):
                logger.warning("assessment_type table doesn't exist yet, skipping initialization")
                return
                
            for assessment_id, assessment_data in self.assessment_types.items():
                # Check if assessment type exists
                assessment_type = AssessmentType.query.filter_by(name=assessment_data['name']).first()
                
                if not assessment_type:
                    # Create assessment type
                    assessment_type = AssessmentType(
                        name=assessment_data['name'],
                        description=assessment_data['description'],
                        instructions=assessment_data['instructions']
                    )
                    db.session.add(assessment_type)
                    db.session.commit()
                    
                    # Create questions
                    for i, question_text in enumerate(assessment_data['questions']):
                        question = AssessmentQuestion(
                            assessment_type_id=assessment_type.id,
                            question_text=question_text,
                            option_type='likert',
                            options=json.dumps(assessment_data['options']),
                            order=i+1
                        )
                        db.session.add(question)
                    
                    db.session.commit()
                    logger.info(f"Initialized assessment: {assessment_data['name']}")
        except Exception as e:
            logger.error(f"Error initializing assessment types: {str(e)}")
            db.session.rollback()
    
    def get_assessment(self, assessment_id):
        """Get assessment questions and options by ID"""
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            
            if not inspector.has_table('assessment_type'):
                logger.warning("assessment_type table doesn't exist yet, returning default assessment")
                assessment_config = self.assessment_types.get(assessment_id)
                if assessment_config:
                    # Return basic data without database
                    default_questions = []
                    for i, question_text in enumerate(assessment_config['questions']):
                        default_questions.append({
                            'id': i+1,
                            'text': question_text,
                            'options': assessment_config['options']
                        })
                    
                    return {
                        'id': assessment_id,
                        'name': assessment_config['name'],
                        'description': assessment_config['description'],
                        'instructions': assessment_config['instructions'],
                        'questions': default_questions
                    }
                return None
                
            assessment_type = AssessmentType.query.filter_by(name=self.assessment_types[assessment_id]['name']).first()
            
            if not assessment_type:
                logger.error(f"Assessment type not found: {assessment_id}")
                return None
            
            questions = AssessmentQuestion.query.filter_by(assessment_type_id=assessment_type.id).order_by(AssessmentQuestion.order).all()
            
            if not questions:
                logger.error(f"No questions found for assessment type: {assessment_id}")
                return None
            
            assessment_data = {
                'id': assessment_type.id,
                'name': assessment_type.name,
                'description': assessment_type.description,
                'instructions': assessment_type.instructions,
                'questions': []
            }
            
            for question in questions:
                options = json.loads(question.options)
                assessment_data['questions'].append({
                    'id': question.id,
                    'text': question.question_text,
                    'options': options
                })
            
            return assessment_data
        except Exception as e:
            logger.error(f"Error getting assessment: {str(e)}")
            return None
    
    def score_assessment(self, assessment_id, responses):
        """
        Score assessment based on user responses
        
        Args:
            assessment_id: ID of the assessment type
            responses: List of response values in order of questions
        
        Returns:
            Dictionary with score and interpretation
        """
        assessment_config = self.assessment_types.get(assessment_id)
        if not assessment_config:
            logger.error(f"Assessment configuration not found: {assessment_id}")
            return None
        
        # Calculate raw score
        score = 0
        for i, response in enumerate(responses):
            # Check if this is a reverse-scored item (PSS has some)
            if 'reverse_items' in assessment_config['scoring'] and i in assessment_config['scoring']['reverse_items']:
                # Get max value for reverse scoring
                max_value = max(option['value'] for option in assessment_config['options'])
                score += max_value - response
            else:
                score += response
        
        # Find interpretation based on score ranges
        interpretation = None
        severity = None
        for range_info in assessment_config['scoring']['ranges']:
            if range_info['min'] <= score <= range_info['max']:
                interpretation = range_info['interpretation']
                severity = range_info['severity']
                break
        
        return {
            'score': score,
            'max_possible': len(responses) * max(option['value'] for option in assessment_config['options']),
            'severity': severity,
            'interpretation': interpretation
        }
    
    def save_assessment_result(self, user_id, assessment_id, responses, score_data):
        """Save assessment result to database"""
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            
            if not inspector.has_table('assessment_type') or not inspector.has_table('assessment_result'):
                logger.warning("Required tables don't exist yet, skipping save")
                return False
                
            assessment_type = AssessmentType.query.filter_by(name=self.assessment_types[assessment_id]['name']).first()
            
            if not assessment_type:
                logger.error(f"Assessment type not found: {assessment_id}")
                return False
            
            try:
                result = AssessmentResult(
                    user_id=user_id,
                    assessment_type_id=assessment_type.id,
                    responses=json.dumps(responses),
                    score=score_data['score'],
                    interpretation=score_data['interpretation'],
                    created_at=datetime.utcnow()
                )
                
                db.session.add(result)
                db.session.commit()
                
                return result.id
            
            except Exception as e:
                logger.error(f"Error saving assessment result: {str(e)}")
                db.session.rollback()
                return False
        except Exception as e:
            logger.error(f"Error checking database tables: {str(e)}")
            return False

# Create assessment engine instance
assessment_engine = AssessmentEngine()