import sys
import os
import logging
from logging.handlers import RotatingFileHandler
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))  # Add project root to path

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, current_user
import datetime
import json

from src.models.db import db, init_db
from src.models.user import User
from src.models.attendance import Attendance
from src.models.sale import Sale
from src.models.vacation import Vacation
from src.config import Config

# Initialize Flask app
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static'))

# Load configuration
app.config.from_object(Config)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Set up logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/attendance.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Attendance System startup')

# Initialize database with app
init_db(app)

# Initialize login manager
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Error handlers
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    db.session.rollback()
    return render_template('error.html', error="Internal Server Error"), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page Not Found"), 404

# Import and register blueprints
from src.routes.auth import bp as auth_bp
from src.routes.main import bp as main_bp
from src.routes.admin import bp as admin_bp
from src.routes.employee import bp as employee_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(employee_bp)

# Create sample data for demonstration
def create_sample_data():
    try:
        # Check if admin user exists
        admin = User.query.filter_by(username='Mody').first()
        if not admin:
            admin = User(username='Mody', email='admin@newera.com', is_admin=True)
            admin.set_password('Mody0325')
            db.session.add(admin)
            db.session.commit()
            app.logger.info('Admin user created successfully')
    except Exception as e:
        app.logger.error(f'Error creating sample data: {str(e)}')
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    app.run(host='0.0.0.0', port=5000, debug=True)
