from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('login.html')


@main_bp.route('/board')
def board_view():
    return render_template('board.html')


@main_bp.route('/manage')
def manage_view():
    return render_template('manage.html')


@main_bp.route('/dashboard')
def dashboard_view():
    return render_template('dashboard.html')


@main_bp.route('/super-admin')
def super_admin_view():
    return render_template('admin.html')
