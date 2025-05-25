from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from src.models.user import User
from src.models.db import db
from werkzeug.security import generate_password_hash

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('employee.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            # Debugging prints
            print(f"--- Debugging Login ---")
            print(f"User found: {user.username}, Is Admin (from user object): {user.is_admin}")
            print(f"Current user authenticated: {current_user.is_authenticated}")
            print(f"Current user Is Admin (from current_user): {current_user.is_admin}")
            print(f"------------------------")
            
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('employee.employee_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    # Check if any admin exists
    admin_exists = User.query.filter_by(is_admin=True).first() is not None
    
    # If admin exists and user is not authenticated as admin, redirect
    if admin_exists and (not current_user.is_authenticated or not current_user.is_admin):
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('auth/create_admin.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('auth/create_admin.html')
        
        # Create admin user
        admin = User(username=username, email=email, is_admin=True)
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        flash('Admin account created successfully', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/create_admin.html')
