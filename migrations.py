from flask_migrate import Migrate
from src.routes.main import app
from src.models.db import db, init_db
from src.models.user import User
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

def init_db():
    with app.app_context():
        try:
            # Check if tables exist
            inspector = db.inspect(db.engine)
            if not inspector.get_table_names():
                db.create_all()
                logger.info("Database tables created successfully!")
            else:
                logger.info("Database tables already exist.")
            
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(username='Mody').first()
            if not admin:
                admin = User(username='Mody', email='admin@newera.com', is_admin=True)
                admin.set_password('Mody0325')
                db.session.add(admin)
                db.session.commit()
                logger.info("Admin user created successfully!")
            else:
                logger.info("Admin user already exists!")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

if __name__ == '__main__':
    init_db() 