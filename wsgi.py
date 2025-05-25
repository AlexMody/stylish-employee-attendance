import os
import sys
import logging

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.routes.main import app
from src.models.db import db
from flask_migrate import Migrate

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize database
with app.app_context():
    try:
        # Check if tables exist
        inspector = db.inspect(db.engine)
        if not inspector.get_table_names():
            db.create_all()
            logger.info("Database tables created successfully!")
        else:
            logger.info("Database tables already exist.")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    app.run() 