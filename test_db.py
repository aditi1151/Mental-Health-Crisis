import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure Flask and SQLAlchemy
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///test.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Define a simple model
class TestModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

# Create routes
@app.route('/')
def index():
    return "Database test app"

# Create all tables
with app.app_context():
    db.create_all()
    print("Tables created successfully")
    
    # Try to add a test record
    try:
        test = TestModel(name="Test Entry")
        db.session.add(test)
        db.session.commit()
        print("Test record added successfully")
    except Exception as e:
        print(f"Error adding test record: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)