from flask_sqlalchemy import SQLAlchemy
import os
import logging

db = SQLAlchemy()

def init_db(app):
    # Get database URL from environment variable
    database_url = os.getenv('DATABASE_URL', 'sqlite:///attendance.db')
    
    # Handle PostgreSQL URL format from Render
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully!")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
            raise
    
    return db
