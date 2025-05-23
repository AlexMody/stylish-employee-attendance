from src.models.db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from src.models.sale import Sale

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    attendances = db.relationship('Attendance', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    sales = db.relationship('Sale', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    vacations = db.relationship('Vacation', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    
    # Need lead status
    needs_lead = db.Column(db.Boolean, default=False)
    lead_requested_at = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_monthly_sales_count(self, year=None, month=None):
        """Get the number of sales for a specific month"""
        if year is None or month is None:
            now = datetime.datetime.utcnow()
            year = now.year
            month = now.month
            
        start_date = datetime.datetime(year, month, 1)
        if month == 12:
            end_date = datetime.datetime(year + 1, 1, 1)
        else:
            end_date = datetime.datetime(year, month + 1, 1)
            
        return self.sales.filter(
            Sale.created_at >= start_date,
            Sale.created_at < end_date
        ).count()
    
    def is_bonus_hunter(self, year=None, month=None):
        """Check if user has achieved 5 or more sales in the current month"""
        return self.get_monthly_sales_count(year, month) >= 5
    
    def __repr__(self):
        return f'<User {self.username}>'
