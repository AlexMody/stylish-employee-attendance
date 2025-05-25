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
    
    # Create tables if they don't exist
    with app.app_context():
        try:
            # Check if tables exist
            inspector = db.inspect(db.engine)
            if not inspector.get_table_names():
                db.create_all()
                app.logger.info("Database tables created successfully!")
            else:
                app.logger.info("Database tables already exist.")
        except Exception as e:
            app.logger.error(f"Error initializing database: {str(e)}")
            raise
    
    return db
