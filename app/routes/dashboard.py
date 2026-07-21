from flask import Blueprint, render_template
from app.services.auth_utils import login_required
from app.services.db import call_procedure
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    now = datetime.now()
    stats = call_procedure('sp_get_monthly_statistics', (now.month, now.year))
    
    # sp_get_monthly_statistics returns 3 result sets.
    # stats will be a list of these results.
    
    return render_template('dashboard.html', stats=stats)
