import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, flash, current_app
from app.services.auth_utils import login_required, roles_allowed
from app.services.db import execute_query, call_procedure

court_bp = Blueprint('court', __name__)

# ---------------------------------------------------------------------------
# LIST — Court dispatch page with submissions list
# ---------------------------------------------------------------------------
@court_bp.route('/dispatch', methods=['GET'])
@login_required
@roles_allowed('Admin', 'Clerk')
def dispatch_list():
    # All court submissions with case references
    submissions = execute_query("""
        SELECT cs.submission_id, cs.court_name, cs.trial_date, cs.receipt_scan_path,
               COALESCE(ce.reference_no, pi.pm_serial_no) AS case_ref,
               CASE
                   WHEN cs.clinical_case_id IS NOT NULL THEN 'Clinical'
                   WHEN cs.autopsy_case_id IS NOT NULL THEN 'Autopsy'
               END AS case_type
        FROM court_submissions cs
        LEFT JOIN clinical_examinations ce ON cs.clinical_case_id = ce.case_id
        LEFT JOIN postmortem_investigations pi ON cs.autopsy_case_id = pi.case_id
        ORDER BY cs.trial_date DESC
    """)
    
    # Pending (no receipt)
    pending = [s for s in submissions if not s.get('receipt_scan_path')]
    
    # Cases for creating new submission
    clinical_cases = execute_query("SELECT case_id, reference_no FROM clinical_examinations ORDER BY case_id DESC LIMIT 50")
    autopsy_cases = execute_query("SELECT case_id, pm_serial_no FROM postmortem_investigations ORDER BY case_id DESC LIMIT 50")
    
    return render_template('court/dispatch.html', submissions=submissions, pending=pending,
                           clinical_cases=clinical_cases, autopsy_cases=autopsy_cases)

# ---------------------------------------------------------------------------
# NEW — Create a new court submission
# ---------------------------------------------------------------------------
@court_bp.route('/new', methods=['POST'])
@login_required
@roles_allowed('Admin', 'Clerk')
def new_submission():
    try:
        case_type = request.form.get('case_type')
        case_id = request.form.get('case_id')
        court_name = request.form.get('court_name')
        trial_date = request.form.get('trial_date') or None
        
        if case_type == 'clinical':
            execute_query(
                "INSERT INTO court_submissions (clinical_case_id, court_name, trial_date) VALUES (%s, %s, %s)",
                (case_id, court_name, trial_date)
            )
        else:
            execute_query(
                "INSERT INTO court_submissions (autopsy_case_id, court_name, trial_date) VALUES (%s, %s, %s)",
                (case_id, court_name, trial_date)
            )
        flash("Court submission created!", "success")
    except Exception as e:
        flash(f"Error creating submission: {str(e)}", "error")
    return redirect('/court/dispatch')

# ---------------------------------------------------------------------------
# RECEIPT — Upload court receipt scan
# ---------------------------------------------------------------------------
@court_bp.route('/receipt', methods=['POST'])
@login_required
@roles_allowed('Admin', 'Clerk')
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
