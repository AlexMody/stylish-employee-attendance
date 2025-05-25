import os
import sys

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.routes.main import app
from src.models.db import db
from flask_migrate import Migrate

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize database
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")

if __name__ == "__main__":
    app.run() 