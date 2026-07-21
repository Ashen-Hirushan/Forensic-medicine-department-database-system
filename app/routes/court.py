import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, flash, current_app
from app.services.auth_utils import login_required, roles_allowed
from app.services.db import execute_query, call_procedure

court_bp = Blueprint('court', __name__)

@court_bp.route('/dispatch', methods=['GET'])
@login_required
@roles_allowed('Administrator', 'Clerk / Admin Staff')
def dispatch_list():
    pending = execute_query("SELECT * FROM view_pending_court_reports")
    return render_template('court/dispatch.html', pending=pending)

@court_bp.route('/receipt', methods=['POST'])
@login_required
@roles_allowed('Administrator', 'Clerk / Admin Staff')
def upload_receipt():
    if 'receipt' not in request.files:
        flash("No file part", "error")
        return redirect('/court/dispatch')
        
    file = request.files['receipt']
    if file.filename == '':
        flash("No selected file", "error")
        return redirect('/court/dispatch')
        
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['COURT_RECEIPTS_DIR'], filename)
    file.save(filepath)
    
    try:
        call_procedure('sp_log_court_receipt', (request.form.get('submission_id'), filepath))
        flash("Court receipt logged successfully!", "success")
    except Exception as e:
        flash(f"Error logging receipt: {str(e)}", "error")
        
    return redirect('/court/dispatch')
