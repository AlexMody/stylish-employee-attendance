from src.models.db import db
import datetime

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    check_out_time = db.Column(db.DateTime, nullable=True)
    date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    
    def is_checked_in(self):
        """Check if user is currently checked in (no check out time)"""
        return self.check_in_time is not None and self.check_out_time is None
    
    def get_duration(self):
        """Get the duration of attendance in hours"""
        if self.check_out_time is None:
            return None
        
        duration = self.check_out_time - self.check_in_time
        return round(duration.total_seconds() / 3600, 2)  # Convert to hours
    
    def __repr__(self):
        return f'<Attendance {self.user_id} on {self.date}>'
