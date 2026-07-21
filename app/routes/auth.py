from flask import Blueprint, render_template, request, redirect, session, flash
from app.services.db import execute_query
from app.services.auth_utils import check_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Query user
        user = execute_query(
            "SELECT u.user_id, u.password_hash, u.account_locked, r.role_name "
            "FROM system_users u JOIN access_roles r ON u.role_id = r.role_id "
            "WHERE u.username = %s", 
            (username,), fetch_all=False
        )
        
        if user and not user['account_locked']:
            if check_password(password, user['password_hash']):
                session['user_id'] = user['user_id']
                session['role_name'] = user['role_name']
                session['username'] = username
                return redirect('/dashboard')
            else:
                flash("Invalid username or password", "error")
        else:
            flash("User not found or account is locked", "error")
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
