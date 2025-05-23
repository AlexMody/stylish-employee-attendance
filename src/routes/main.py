import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))  # Add project root to path

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, current_user
import datetime
import json

from src.models.db import db
from src.models.user import User
from src.models.attendance import Attendance
from src.models.sale import Sale
from src.models.vacation import Vacation

# Initialize Flask app
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static'))
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

# Initialize login manager
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import and register blueprints
from src.routes.auth import auth_bp
from src.routes.employee import employee_bp
from src.routes.admin import admin_bp
from src.routes.api import api_bp

app.register_blueprint(auth_bp)
app.register_blueprint(employee_bp, url_prefix='/employee')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

# Create sample data for demonstration
def create_sample_data():
    # Check if admin user exists
    admin = User.query.filter_by(username='Mody').first()
    if not admin:
        admin = User(username='Mody', email='admin@newera.com', is_admin=True)
        admin.set_password('Mody0325')
        db.session.add(admin)
        
        # Create sample employees
        employee_data = [
            {'username': 'john', 'email': 'john@newera.com', 'password': 'password123'},
            {'username': 'sarah', 'email': 'sarah@newera.com', 'password': 'password123'},
            {'username': 'mike', 'email': 'mike@newera.com', 'password': 'password123'},
            {'username': 'lisa', 'email': 'lisa@newera.com', 'password': 'password123'},
            {'username': 'david', 'email': 'david@newera.com', 'password': 'password123'},
        ]
        
        employees = []
        for data in employee_data:
            employee = User(username=data['username'], email=data['email'], is_admin=False)
            employee.set_password(data['password'])
            db.session.add(employee)
            employees.append(employee)
        
        db.session.commit()
        
        # Create sample attendance records
        today = datetime.date.today()
        
        # John checked in and still active
        attendance1 = Attendance(
            user_id=employees[0].id,
            check_in_time=datetime.datetime.now() - datetime.timedelta(hours=2),
            date=today
        )
        
        # Sarah checked in and out
        attendance2 = Attendance(
            user_id=employees[1].id,
            check_in_time=datetime.datetime.now() - datetime.timedelta(hours=4),
            check_out_time=datetime.datetime.now() - datetime.timedelta(hours=1),
            date=today
        )
        
        # Mike checked in and still active, needs lead
        attendance3 = Attendance(
            user_id=employees[2].id,
            check_in_time=datetime.datetime.now() - datetime.timedelta(hours=3),
            date=today
        )
        employees[2].needs_lead = True
        
        # Lisa checked in and still active
        attendance4 = Attendance(
            user_id=employees[3].id,
            check_in_time=datetime.datetime.now() - datetime.timedelta(hours=1),
            date=today
        )
        
        db.session.add_all([attendance1, attendance2, attendance3, attendance4])
        
        # Create sample sales
        # Mike has 5 sales (bonus hunter)
        for i in range(5):
            sale = Sale(
                user_id=employees[2].id,
                amount=100 + i * 10,
                customer_name=f'Customer {i+1}',
                description=f'Sale description {i+1}',
                created_at=datetime.datetime.now() - datetime.timedelta(days=i)
            )
            db.session.add(sale)
        
        # Sarah has 3 sales
        for i in range(3):
            sale = Sale(
                user_id=employees[1].id,
                amount=150 + i * 15,
                customer_name=f'Customer {i+6}',
                description=f'Sale description {i+6}',
                created_at=datetime.datetime.now() - datetime.timedelta(days=i)
            )
            db.session.add(sale)
        
        # John has 2 sales
        for i in range(2):
            sale = Sale(
                user_id=employees[0].id,
                amount=200 + i * 20,
                customer_name=f'Customer {i+9}',
                description=f'Sale description {i+9}',
                created_at=datetime.datetime.now() - datetime.timedelta(days=i)
            )
            db.session.add(sale)
        
        # Create sample vacation requests
        # Pending vacation for John
        vacation1 = Vacation(
            user_id=employees[0].id,
            start_date=today + datetime.timedelta(days=10),
            end_date=today + datetime.timedelta(days=15),
            reason='Family vacation',
            status='pending'
        )
        
        # Approved vacation for Sarah
        vacation2 = Vacation(
            user_id=employees[1].id,
            start_date=today + datetime.timedelta(days=20),
            end_date=today + datetime.timedelta(days=25),
            reason='Personal time',
            status='approved'
        )
        
        # Rejected vacation for Mike
        vacation3 = Vacation(
            user_id=employees[2].id,
            start_date=today + datetime.timedelta(days=5),
            end_date=today + datetime.timedelta(days=7),
            reason='Medical appointment',
            status='rejected'
        )
        
        db.session.add_all([vacation1, vacation2, vacation3])
        db.session.commit()
        
        print("Sample data created successfully!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    app.run(host='0.0.0.0', port=5000, debug=True)
