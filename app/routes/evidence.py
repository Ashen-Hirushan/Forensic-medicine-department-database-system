import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, flash, current_app, session
from app.services.auth_utils import login_required, roles_allowed
from app.services.db import execute_query, call_procedure

evidence_bp = Blueprint('evidence', __name__)

# ---------------------------------------------------------------------------
# MAIN PAGE — Evidence list, registration, transfer, lab results
# ---------------------------------------------------------------------------
@evidence_bp.route('/transfer', methods=['GET'])
@login_required
def evidence_page():
    # Get all physical evidence with case info
    evidence_list = execute_query("""
        SELECT pe.evidence_id, pe.description,
               COALESCE(ce.reference_no, pi.pm_serial_no) AS case_ref,
               CASE
                   WHEN pe.clinical_case_id IS NOT NULL THEN 'Clinical'
                   WHEN pe.autopsy_case_id IS NOT NULL THEN 'Autopsy'
               END AS case_type,
               (SELECT COUNT(*) FROM evidence_custody_logs ecl WHERE ecl.evidence_id = pe.evidence_id) AS transfer_count
        FROM physical_evidence pe
        LEFT JOIN clinical_examinations ce ON pe.clinical_case_id = ce.case_id
        LEFT JOIN postmortem_investigations pi ON pe.autopsy_case_id = pi.case_id
        ORDER BY pe.evidence_id DESC
    """)
    
    # Get custody log for recent transfers
    recent_transfers = execute_query("""
        SELECT ecl.log_id, ecl.evidence_id, ecl.transfer_datetime, ecl.location,
               pe.description AS evidence_desc,
               su_from.username AS from_user, su_to.username AS to_user
        FROM evidence_custody_logs ecl
        JOIN physical_evidence pe ON ecl.evidence_id = pe.evidence_id
        LEFT JOIN system_users su_from ON ecl.from_user_id = su_from.user_id
        JOIN system_users su_to ON ecl.to_user_id = su_to.user_id
        ORDER BY ecl.transfer_datetime DESC
        LIMIT 20
    """)
    
    # Get users for transfer dropdown
    users = execute_query("SELECT user_id, username FROM system_users WHERE account_locked = 0")
    
    # Get cases for evidence registration
    clinical_cases = execute_query("SELECT case_id, reference_no FROM clinical_examinations ORDER BY case_id DESC LIMIT 50")
    autopsy_cases = execute_query("SELECT case_id, pm_serial_no FROM postmortem_investigations ORDER BY case_id DESC LIMIT 50")
    
    return render_template('evidence/transfer.html', evidence_list=evidence_list,
                           recent_transfers=recent_transfers, users=users,
                           clinical_cases=clinical_cases, autopsy_cases=autopsy_cases)

# ---------------------------------------------------------------------------
# REGISTER — Register new physical evidence
# ---------------------------------------------------------------------------
@evidence_bp.route('/register', methods=['POST'])
@login_required
@roles_allowed('Admin', 'Doctor', 'Clerk')
def register_evidence():
    try:
        case_type = request.form.get('case_type')
        case_id = request.form.get('case_id')
        description = request.form.get('description')
        
        if case_type == 'clinical':
            execute_query(
                "INSERT INTO physical_evidence (clinical_case_id, description) VALUES (%s, %s)",
                (case_id, description)
            )
        else:
            execute_query(
                "INSERT INTO physical_evidence (autopsy_case_id, description) VALUES (%s, %s)",
                (case_id, description)
            )
        flash("Physical evidence registered!", "success")
    except Exception as e:
        flash(f"Error registering evidence: {str(e)}", "error")
    return redirect('/evidence/transfer')

# ---------------------------------------------------------------------------
# TRANSFER — Transfer evidence custody
# ---------------------------------------------------------------------------
@evidence_bp.route('/do-transfer', methods=['POST'])
@login_required
def transfer_evidence():
    try:
        call_procedure('sp_transfer_evidence_custody', (
            request.form.get('evidence_id'), session.get('user_id'),
            request.form.get('to_user_id'), request.form.get('location')
        ))
        flash("Evidence transferred successfully!", "success")
    except Exception as e:
        flash(f"Error transferring evidence: {str(e)}", "error")
    return redirect('/evidence/transfer')

# ---------------------------------------------------------------------------
# CHAIN OF CUSTODY — View custody log for a specific evidence item
# ---------------------------------------------------------------------------
@evidence_bp.route('/chain/<int:evidence_id>', methods=['GET'])
@login_required
def chain_of_custody(evidence_id):
    evidence = execute_query(
        "SELECT * FROM physical_evidence WHERE evidence_id = %s", (evidence_id,), fetch_all=False
    )
    logs = execute_query("""
        SELECT ecl.*, su_from.username AS from_user, su_to.username AS to_user
        FROM evidence_custody_logs ecl
        LEFT JOIN system_users su_from ON ecl.from_user_id = su_from.user_id
        JOIN system_users su_to ON ecl.to_user_id = su_to.user_id
        WHERE ecl.evidence_id = %s
        ORDER BY ecl.transfer_datetime ASC
    """, (evidence_id,))
    return render_template('evidence/chain.html', evidence=evidence, logs=logs)

# ---------------------------------------------------------------------------
# LAB RESULT — Upload test result
# ---------------------------------------------------------------------------
@evidence_bp.route('/result', methods=['POST'])
@login_required
@roles_allowed('Admin', 'Lab Staff')
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
