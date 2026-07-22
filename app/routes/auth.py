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


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        designation = request.form.get('designation', '').strip()
        username = request.form.get('username', '').strip()
        role_id = request.form.get('role_id')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        slmc_reg_no = request.form.get('slmc_reg_no', '').strip()

        # Validation
        if not full_name or not username or not password:
            flash("Full name, username, and password are required.", "error")
            return redirect('/signup')

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect('/signup')

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect('/signup')

        # Check if username already exists
        existing = execute_query(
            "SELECT user_id FROM system_users WHERE username = %s",
            (username,), fetch_all=False
        )
        if existing:
            flash("Username already exists. Please choose another.", "error")
            return redirect('/signup')

        # Create user, staff, and optionally doctor
        try:
            pw_hash = hash_password(password)

            # 1. Insert into system_users
            execute_query(
                "INSERT INTO system_users (role_id, username, password_hash) VALUES (%s, %s, %s)",
                (role_id, username, pw_hash)
            )

            # Get the new user_id
            new_user = execute_query(
                "SELECT user_id FROM system_users WHERE username = %s",
                (username,), fetch_all=False
            )
            user_id = new_user['user_id']

            # 2. Insert into staff_directory
            execute_query(
                "INSERT INTO staff_directory (user_id, full_name, designation) VALUES (%s, %s, %s)",
                (user_id, full_name, designation or None)
            )

            # 3. If SLMC reg no is provided, create a medical officer entry
            if slmc_reg_no:
                staff = execute_query(
                    "SELECT staff_id FROM staff_directory WHERE user_id = %s",
                    (user_id,), fetch_all=False
                )
                if staff:
                    execute_query(
                        "INSERT INTO medical_officers (staff_id, slmc_reg_no) VALUES (%s, %s)",
                        (staff['staff_id'], slmc_reg_no)
                    )

            flash("Account created successfully! Please log in.", "success")
            return redirect('/login')

        except Exception as e:
            flash(f"Registration failed: {str(e)}", "error")
            return redirect('/signup')

    # GET: Fetch roles for the dropdown
    roles = execute_query("SELECT role_id, role_name FROM access_roles ORDER BY role_id")
    if not roles:
        roles = []

    return render_template('signup.html', roles=roles)

