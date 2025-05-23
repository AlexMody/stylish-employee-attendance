from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.models.user import User
from src.models.attendance import Attendance
from src.models.sale import Sale
from src.models.vacation import Vacation
from src.models.db import db
import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    # Debugging prints for admin dashboard
    print(f"--- Debugging Admin Dashboard ---")
    print(f"Current user authenticated: {current_user.is_authenticated}")
    print(f"Current user Is Admin: {current_user.is_admin}")
    print(f"------------------------")

    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    # Get all active employees (currently checked in)
    today = datetime.date.today()
    active_attendances = Attendance.query.filter(
        Attendance.date == today,
        Attendance.check_out_time == None
    ).all()
    
    active_employee_ids = [attendance.user_id for attendance in active_attendances]
    active_employees = User.query.filter(User.id.in_(active_employee_ids)).all() if active_employee_ids else []
    
    # Get employees who need leads
    employees_needing_leads = User.query.filter_by(needs_lead=True, is_admin=False).all()
    
    # Get all employees
    all_employees = User.query.filter_by(is_admin=False).all()
    
    # Get pending vacation requests
    pending_vacations = Vacation.query.filter_by(status='pending').all()
    
    # Get bonus hunters this month
    bonus_hunters = []
    for employee in all_employees:
        if employee.is_bonus_hunter():
            bonus_hunters.append(employee)
    
    return render_template('admin/dashboard.html',
                          active_employees=active_employees,
                          employees_needing_leads=employees_needing_leads,
                          all_employees=all_employees,
                          pending_vacations=pending_vacations,
                          bonus_hunters=bonus_hunters)

@admin_bp.route('/employees')
@login_required
def employees():
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    employees = User.query.filter_by(is_admin=False).all()
    return render_template('admin/employees.html', employees=employees, datetime=datetime)

@admin_bp.route('/add-employee', methods=['GET', 'POST'])
@login_required
def add_employee():
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('admin/add_employee.html', datetime=datetime)
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('admin/add_employee.html', datetime=datetime)
        
        # Create employee user
        employee = User(username=username, email=email, is_admin=False)
        employee.set_password(password)
        
        db.session.add(employee)
        db.session.commit()
        
        flash('Employee added successfully', 'success')
        return redirect(url_for('admin.employees'))
    
    return render_template('admin/add_employee.html', datetime=datetime)

@admin_bp.route('/edit-employee/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def edit_employee(employee_id):
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    employee = User.query.get_or_404(employee_id)
    
    if employee.is_admin:
        flash('Cannot edit admin user', 'danger')
        return redirect(url_for('admin.employees'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if username already exists for another user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != employee_id:
            flash('Username already exists', 'danger')
            return render_template('admin/edit_employee.html', employee=employee, datetime=datetime)
        
        # Check if email already exists for another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != employee_id:
            flash('Email already exists', 'danger')
            return render_template('admin/edit_employee.html', employee=employee, datetime=datetime)
        
        # Update employee
        employee.username = username
        employee.email = email
        if password:
            employee.set_password(password)
        
        db.session.commit()
        
        flash('Employee updated successfully', 'success')
        return redirect(url_for('admin.employees'))
    
    return render_template('admin/edit_employee.html', employee=employee, datetime=datetime)

@admin_bp.route('/delete-employee/<int:employee_id>', methods=['POST'])
@login_required
def delete_employee(employee_id):
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    employee = User.query.get_or_404(employee_id)
    
    if employee.is_admin:
        flash('Cannot delete admin user', 'danger')
        return redirect(url_for('admin.employees'))
    
    db.session.delete(employee)
    db.session.commit()
    
    flash('Employee deleted successfully', 'success')
    return redirect(url_for('admin.employees'))

@admin_bp.route('/attendance-report')
@login_required
def attendance_report():
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    # Get date filter from query params
    date_str = request.args.get('date')
    if date_str:
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date = datetime.date.today()
    else:
        date = datetime.date.today()
    
    # Get all attendance records for the date
    attendances = Attendance.query.filter_by(date=date).all()
    
    # Get all employees
    employees = User.query.filter_by(is_admin=False).all()
    
    return render_template('admin/attendance_report.html', 
                          attendances=attendances,
                          employees=employees,
                          date=date, datetime=datetime)

@admin_bp.route('/sales-report')
@login_required
def sales_report():
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    # Get month filter from query params
    month_str = request.args.get('month')
    year_str = request.args.get('year')
    
    if month_str and year_str:
        try:
            month = int(month_str)
            year = int(year_str)
        except ValueError:
            now = datetime.datetime.utcnow()
            month = now.month
            year = now.year
    else:
        now = datetime.datetime.utcnow()
        month = now.month
        year = now.year
    
    # Get start and end dates for the month
    start_date = datetime.datetime(year, month, 1)
    if month == 12:
        end_date = datetime.datetime(year + 1, 1, 1)
    else:
        end_date = datetime.datetime(year, month + 1, 1)
    
    # Get all sales for the month
    sales = Sale.query.filter(
        Sale.created_at >= start_date,
        Sale.created_at < end_date
    ).order_by(Sale.created_at.desc()).all()
    
    # Get all employees
    employees = User.query.filter_by(is_admin=False).all()
    
    # Calculate sales per employee
    employee_sales = {}
    for employee in employees:
        employee_sales[employee.id] = {
            'employee': employee,
            'sales_count': employee.get_monthly_sales_count(year, month),
            'is_bonus_hunter': employee.is_bonus_hunter(year, month)
        }
    
    return render_template('admin/sales_report.html',
                          sales=sales,
                          employees=employees,
                          employee_sales=employee_sales,
                          month=month,
                          year=year, datetime=datetime)

@admin_bp.route('/vacation-requests')
@login_required
def vacation_requests():
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    # Get all vacation requests
    vacations = Vacation.query.order_by(Vacation.status, Vacation.start_date).all()
    
    return render_template('admin/vacation_requests.html', vacations=vacations, User=User, datetime=datetime)

@admin_bp.route('/approve-vacation/<int:vacation_id>', methods=['POST'])
@login_required
def approve_vacation(vacation_id):
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    vacation = Vacation.query.get_or_404(vacation_id)
    vacation.status = 'approved'
    db.session.commit()
    
    flash('Vacation request approved', 'success')
    return redirect(url_for('admin.vacation_requests'))

@admin_bp.route('/reject-vacation/<int:vacation_id>', methods=['POST'])
@login_required
def reject_vacation(vacation_id):
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    vacation = Vacation.query.get_or_404(vacation_id)
    vacation.status = 'rejected'
    db.session.commit()
    
    flash('Vacation request rejected', 'success')
    return redirect(url_for('admin.vacation_requests'))

@admin_bp.route('/live-attendance')
@login_required
def live_attendance():
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    return render_template('admin/live_attendance.html', datetime=datetime)

@admin_bp.route('/api/live-attendance')
@login_required
def api_live_attendance():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Get today's attendance records
    today = datetime.date.today()
    attendances = Attendance.query.filter_by(date=today).all()
    
    # Get all employees
    employees = User.query.filter_by(is_admin=False).all()
    
    # Format data for API response
    attendance_data = []
    total_check_ins = 0
    total_check_outs = 0
    total_duration = 0
    
    for attendance in attendances:
        user = User.query.get(attendance.user_id)
        if user:
            check_in_time = attendance.check_in_time.strftime('%H:%M:%S')
            check_out_time = attendance.check_out_time.strftime('%H:%M:%S') if attendance.check_out_time else None
            is_active = attendance.check_out_time is None
            
            if check_out_time:
                total_check_outs += 1
                # Calculate duration
                check_in = datetime.datetime.strptime(check_in_time, '%H:%M:%S')
                check_out = datetime.datetime.strptime(check_out_time, '%H:%M:%S')
                duration = (check_out - check_in).total_seconds() / 3600  # Convert to hours
                total_duration += duration
            else:
                duration = None
            
            if check_in_time:
                total_check_ins += 1
            
            # Get today's sales for this employee
            today_sales = Sale.query.filter(
                Sale.user_id == user.id,
                Sale.created_at >= datetime.datetime.combine(today, datetime.time.min),
                Sale.created_at <= datetime.datetime.combine(today, datetime.time.max)
            ).count()
            
            attendance_data.append({
                'id': attendance.id,
                'user_id': attendance.user_id,
                'username': user.username,
                'check_in_time': check_in_time,
                'check_out_time': check_out_time,
                'is_active': is_active,
                'duration': round(duration, 2) if duration else None,
                'needs_lead': user.needs_lead,
                'today_sales': today_sales,
                'monthly_sales': user.get_monthly_sales_count(),
                'is_bonus_hunter': user.is_bonus_hunter()
            })
    
    # Calculate statistics
    stats = {
        'total_check_ins': total_check_ins,
        'total_check_outs': total_check_outs,
        'avg_duration': round(total_duration / total_check_outs, 2) if total_check_outs > 0 else 0,
        'active_count': len([a for a in attendance_data if a['is_active']]),
        'need_leads_count': len([a for a in attendance_data if a['needs_lead']])
    }
    
    return jsonify({
        'attendance': attendance_data,
        'stats': stats
    })
