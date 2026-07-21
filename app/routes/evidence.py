import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, flash, current_app, session
from app.services.auth_utils import login_required, roles_allowed
from app.services.db import call_procedure

evidence_bp = Blueprint('evidence', __name__)

@evidence_bp.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer_evidence():
    if request.method == 'POST':
        try:
            call_procedure('sp_transfer_evidence_custody', (
                request.form.get('evidence_id'), session.get('user_id'),
                request.form.get('to_user_id'), request.form.get('location')
            ))
            flash("Evidence transferred successfully!", "success")
            return redirect('/evidence/transfer')
        except Exception as e:
            flash(f"Error transferring evidence: {str(e)}", "error")
    return render_template('evidence/transfer.html')

@evidence_bp.route('/result', methods=['POST'])
@login_required
@roles_allowed('Administrator', 'Laboratory Staff')
def submit_result():
    if 'file' not in request.files:
        flash("No file part", "error")
        return redirect(request.referrer or '/')
        
    file = request.files['file']
    if file.filename == '':
        flash("No selected file", "error")
        return redirect(request.referrer or '/')
        
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOADS_DIR'], filename)
    file.save(filepath)
    
    try:
        call_procedure('sp_submit_test_result', (
            request.form.get('request_id'), session.get('user_id'), filepath
        ))
        flash("Test result submitted successfully!", "success")
    except Exception as e:
        flash(f"Error submitting result: {str(e)}", "error")
        
    return redirect(request.referrer or '/')
