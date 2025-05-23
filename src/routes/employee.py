from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.models.user import User
from src.models.attendance import Attendance
from src.models.sale import Sale
from src.models.vacation import Vacation
from src.models.db import db
import datetime

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/dashboard')
@login_required
def employee_dashboard():
    # Get today's attendance record
    today = datetime.date.today()
    attendance = Attendance.query.filter_by(
        user_id=current_user.id,
        date=today
    ).order_by(Attendance.check_in_time.desc()).first()
    
    # Get recent sales
    recent_sales = Sale.query.filter_by(user_id=current_user.id).order_by(Sale.created_at.desc()).limit(5).all()
    
    # Get pending vacations
    pending_vacations = Vacation.query.filter_by(
        user_id=current_user.id,
        status='pending'
    ).order_by(Vacation.start_date).all()
    
    # Get monthly sales count
    monthly_sales_count = current_user.get_monthly_sales_count()
    is_bonus_hunter = current_user.is_bonus_hunter()
    
    return render_template('employee/dashboard.html', 
                          attendance=attendance,
                          recent_sales=recent_sales,
                          pending_vacations=pending_vacations,
                          monthly_sales_count=monthly_sales_count,
                          is_bonus_hunter=is_bonus_hunter,
                          datetime=datetime)

@employee_bp.route('/check-in', methods=['POST'])
@login_required
def check_in():
    if current_user.is_admin:
        flash('Admin cannot check in', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Check if already checked in today
    today = datetime.date.today()
    attendance = Attendance.query.filter_by(
        user_id=current_user.id,
        date=today
    ).order_by(Attendance.check_in_time.desc()).first()
    
    if attendance and attendance.check_out_time is None:
        flash('You are already checked in', 'warning')
    else:
        # Create new attendance record
        new_attendance = Attendance(user_id=current_user.id)
        db.session.add(new_attendance)
        db.session.commit()
        flash('Checked in successfully', 'success')
    
    return redirect(url_for('employee.employee_dashboard'))

@employee_bp.route('/check-out', methods=['POST'])
@login_required
def check_out():
    if current_user.is_admin:
        flash('Admin cannot check out', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Find today's attendance record
    today = datetime.date.today()
    attendance = Attendance.query.filter_by(
        user_id=current_user.id,
        date=today
    ).order_by(Attendance.check_in_time.desc()).first()
    
    if attendance and attendance.check_out_time is None:
        attendance.check_out_time = datetime.datetime.utcnow()
        db.session.commit()
        flash('Checked out successfully', 'success')
    else:
        flash('You are not checked in', 'warning')
    
    return redirect(url_for('employee.employee_dashboard'))

@employee_bp.route('/toggle-lead-status', methods=['POST'])
@login_required
def toggle_lead_status():
    if current_user.is_admin:
        flash('Admin cannot request leads', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    current_user.needs_lead = not current_user.needs_lead
    if current_user.needs_lead:
        current_user.lead_requested_at = datetime.datetime.utcnow()
    else:
        current_user.lead_requested_at = None
    db.session.commit()
    
    status = 'requested' if current_user.needs_lead else 'canceled'
    flash(f'Lead request {status}', 'success')
    
    return redirect(url_for('employee.employee_dashboard'))

@employee_bp.route('/record-sale', methods=['GET', 'POST'])
@login_required
def record_sale():
    if current_user.is_admin:
        flash('Admin cannot record sales', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        amount = request.form.get('amount')
        description = request.form.get('description')
        
        if not customer_name or not amount:
            flash('Customer name and amount are required', 'danger')
            return redirect(url_for('employee.record_sale'))
        
        try:
            amount = float(amount)
        except ValueError:
            flash('Amount must be a number', 'danger')
            return redirect(url_for('employee.record_sale'))
        
        sale = Sale(
            user_id=current_user.id,
            customer_name=customer_name,
            amount=amount,
            description=description
        )
        
        db.session.add(sale)
        db.session.commit()
        
        flash('Sale recorded successfully', 'success')
        
        # Check if this sale makes the user a bonus hunter
        monthly_sales = current_user.get_monthly_sales_count()
        if monthly_sales == 5:  # Just reached 5 sales
            flash('Congratulations! You are now a Bonus Hunter for this month!', 'success')
        
        return redirect(url_for('employee.employee_dashboard'))
    
    return render_template('employee/record_sale.html', datetime=datetime)

@employee_bp.route('/request-vacation', methods=['GET', 'POST'])
@login_required
def request_vacation():
    if current_user.is_admin:
        flash('Admin cannot request vacation', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        reason = request.form.get('reason')
        
        if not start_date or not end_date:
            flash('Start and end dates are required', 'danger')
            return redirect(url_for('employee.request_vacation'))
        
        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'danger')
            return redirect(url_for('employee.request_vacation'))
        
        if start_date > end_date:
            flash('End date must be after start date', 'danger')
            return redirect(url_for('employee.request_vacation'))
        
        vacation = Vacation(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )
        
        db.session.add(vacation)
        db.session.commit()
        
        flash('Vacation request submitted successfully', 'success')
        return redirect(url_for('employee.employee_dashboard'))
    
    return render_template('employee/request_vacation.html', datetime=datetime)
