from src.routes.main import app
from src.models.db import db
from src.models.user import User
from src.models.attendance import Attendance
from src.models.sale import Sale
from src.models.vacation import Vacation
import os

def init_db():
    with app.app_context():
        # Drop all tables first to ensure clean state
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='Mody').first()
        if not admin:
            admin = User(username='Mody', email='admin@newera.com', is_admin=True)
            admin.set_password('Mody0325')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists!")

if __name__ == '__main__':
    init_db() 