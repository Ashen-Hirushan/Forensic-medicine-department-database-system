from functools import wraps
from flask import session, redirect, abort, flash, request
import bcrypt

def hash_password(plain_text_password):
    """Hashes a plain text password using bcrypt."""
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(plain_text_password, hashed_password):
    """Checks a plain text password against a bcrypt hashed password."""
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))

def login_required(f):
    """Decorator to require login for a specific route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "error")
            return redirect('/login') 
        return f(*args, **kwargs)
    return decorated_function

def roles_allowed(*allowed_roles):
    """
    Decorator to restrict access to specific roles.
    Example: @roles_allowed('Administrator', 'Doctor / JMO')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in to access this page.", "error")
                return redirect('/login')
            
            user_role = session.get('role_name')
            if user_role not in allowed_roles:
                abort(403) # Forbidden
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
