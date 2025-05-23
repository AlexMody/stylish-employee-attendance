from src.models.db import db
import datetime

class Vacation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def get_duration(self):
        """Get the duration of vacation in days"""
        delta = self.end_date - self.start_date
        return delta.days + 1  # Include both start and end dates
    
    def __repr__(self):
        return f'<Vacation {self.id} by User {self.user_id}>'
