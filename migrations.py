from flask_migrate import Migrate
from src.routes.main import app
from src.models.db import db, init_db
from src.models.user import User
import os
import logging

# Initialize database
init_db(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

def init_db():
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            app.logger.info("Database tables created successfully!")
            
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(username='Mody').first()
            if not admin:
                admin = User(username='Mody', email='admin@newera.com', is_admin=True)
                admin.set_password('Mody0325')
                db.session.add(admin)
                db.session.commit()
                app.logger.info("Admin user created successfully!")
            else:
                app.logger.info("Admin user already exists!")
        except Exception as e:
            app.logger.error(f"Error initializing database: {str(e)}")
            raise

if __name__ == '__main__':
    init_db() 