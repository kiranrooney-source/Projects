from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash
from .. import load_data, save_data, ROLE_PERMISSIONS
from ..decorators import login_required, role_required
from uuid import uuid4
from datetime import datetime

users_bp = Blueprint('users', __name__, template_folder='../../templates')

@users_bp.route('/users')
@login_required
@role_required(['Admin'])
def users():
    all_users = load_data('users.json')
    return render_template('users.html', users=all_users, roles=ROLE_PERMISSIONS.keys(), ROLE_PERMISSIONS=ROLE_PERMISSIONS)

@users_bp.route('/add_user', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_user():
    users = load_data('users.json')
    user_id = str(uuid4())
    
    # Check for existing username
    if any(u['username'] == request.form['username'] for u in users.values()):
        flash(f"Username '{request.form['username']}' already exists.", 'danger')
        return redirect(url_for('users.users'))

    users[user_id] = {
        'username': request.form['username'],
        'password': generate_password_hash(request.form['password']),
        'name': request.form['name'],
        'email': request.form['email'],
        'role': request.form['role'],
        'status': request.form['status'],
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_data('users.json', users)
    flash('User added successfully!', 'success')
    return redirect(url_for('users.users'))

@users_bp.route('/edit_user/<user_id>', methods=['POST'])
@login_required
@role_required(['Admin'])
def edit_user(user_id):
    users = load_data('users.json')
    if user_id in users:
        # Check for existing username if it's being changed
        new_username = request.form['username']
        if (users[user_id]['username'] != new_username and
                any(u['username'] == new_username for u in users.values())):
            flash(f"Username '{new_username}' already exists.", 'danger')
            return redirect(url_for('users.users'))

        users[user_id]['username'] = new_username
        users[user_id]['name'] = request.form['name']
        users[user_id]['email'] = request.form['email']
        users[user_id]['role'] = request.form['role']
        users[user_id]['status'] = request.form['status']
        
        # Update password only if a new one is provided
        if request.form.get('password'):
            users[user_id]['password'] = generate_password_hash(request.form['password'])

        save_data('users.json', users)
        flash('User updated successfully!', 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('users.users'))

@users_bp.route('/delete_user/<user_id>')
@login_required
@role_required(['Admin'])
def delete_user(user_id):
    users = load_data('users.json')
    if user_id in users:
        # Prevent deleting the logged-in user
        if user_id == session.get('user_id'):
            flash('You cannot delete your own account.', 'danger')
            return redirect(url_for('users.users'))
        
        del users[user_id]
        save_data('users.json', users)
        flash('User deleted successfully!', 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('users.users'))

@users_bp.route('/save_role_permissions', methods=['POST'])
@login_required
@role_required(['Admin'])
def save_role_permissions():
    global ROLE_PERMISSIONS
    permissions = {}
    for role in ROLE_PERMISSIONS.keys():
        permissions[role] = request.form.getlist(f'{role}_permissions')
    save_data('role_permissions.json', permissions)
    ROLE_PERMISSIONS = permissions
    flash('Role permissions updated successfully!', 'success')
    return redirect(url_for('users.users'))
