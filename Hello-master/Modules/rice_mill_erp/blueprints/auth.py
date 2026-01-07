from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import check_password_hash
from .. import load_data, save_data

auth_bp = Blueprint('auth', __name__, template_folder='../../templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_data('users.json')
        
        for user_id, user_data in users.items():
            if user_data['username'] == username and check_password_hash(user_data.get('password', ''), password):
                session['user_id'] = user_id
                session['user_name'] = user_data['name']
                session['user_role'] = user_data['role']
                flash(f'Welcome back, {user_data["name"]}!', 'success')
                return redirect(url_for('main.dashboard'))
        
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
