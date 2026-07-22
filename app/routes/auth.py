import os
from flask import Blueprint, render_template, request, redirect, session, flash, current_app
from werkzeug.utils import secure_filename
from app.services.db import execute_query
from app.services.auth_utils import check_password, hash_password, login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Query user
        user = execute_query(
            "SELECT u.user_id, u.password_hash, u.account_locked, u.profile_picture, r.role_name "
            "FROM system_users u JOIN access_roles r ON u.role_id = r.role_id "
            "WHERE u.username = %s", 
            (username,), fetch_all=False
        )
        
        if user and not user['account_locked']:
            if check_password(password, user['password_hash']):
                session['user_id'] = user['user_id']
                session['role_name'] = user['role_name']
                session['username'] = username
                session['profile_picture'] = user.get('profile_picture', 'default.png')
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

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        # Verify current password
        user = execute_query("SELECT password_hash FROM system_users WHERE user_id = %s", (user_id,), fetch_all=False)
        if user and check_password(current_password, user['password_hash']):
            # Update password
            new_hash = hash_password(new_password)
            execute_query("UPDATE system_users SET password_hash = %s WHERE user_id = %s", (new_hash, user_id))
            flash("Password updated successfully!", "success")
        else:
            flash("Incorrect current password.", "error")
            
        return redirect('/profile')
        
    # GET Request: Fetch user and staff details
    user_info = execute_query(
        "SELECT u.username, u.profile_picture, r.role_name, s.full_name, s.designation "
        "FROM system_users u "
        "JOIN access_roles r ON u.role_id = r.role_id "
        "LEFT JOIN staff_directory s ON u.user_id = s.user_id "
        "WHERE u.user_id = %s",
        (user_id,), fetch_all=False
    )
    
    return render_template('profile.html', user_info=user_info)

@auth_bp.route('/profile/picture', methods=['POST'])
@login_required
def upload_picture():
    if 'profile_pic' not in request.files:
        flash("No file uploaded", "error")
        return redirect('/profile')
        
    file = request.files['profile_pic']
    if file.filename == '':
        flash("No file selected", "error")
        return redirect('/profile')
        
    if file:
        filename = secure_filename(f"user_{session['user_id']}_{file.filename}")
        file_path = os.path.join(current_app.config['PROFILES_DIR'], filename)
        file.save(file_path)
        
        # Update DB
        execute_query("UPDATE system_users SET profile_picture = %s WHERE user_id = %s", (filename, session['user_id']))
        # Update Session
        session['profile_picture'] = filename
        
        flash("Profile picture updated successfully!", "success")
        
    return redirect('/profile')

