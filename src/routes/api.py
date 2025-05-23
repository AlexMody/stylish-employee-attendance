from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from src.models.user import User
from src.models.db import db
import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/employees-needing-leads')
@login_required
def employees_needing_leads():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Get employees who need leads
    employees = User.query.filter_by(needs_lead=True, is_admin=False).all()
    
    # Format data for API response
    employee_data = []
    for employee in employees:
        employee_data.append({
            'id': employee.id,
            'username': employee.username,
            'email': employee.email
        })
    
    return jsonify(employee_data)
