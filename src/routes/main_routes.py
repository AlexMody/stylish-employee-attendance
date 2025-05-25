from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('employee.dashboard')) 