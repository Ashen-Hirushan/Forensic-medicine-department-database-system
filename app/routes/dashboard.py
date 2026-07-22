from flask import Blueprint, render_template
from app.services.auth_utils import login_required
from app.services.db import call_procedure
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    from app.services.db import execute_query
    
    # 1. Total Cases & Cases by Type
    clinical_cases_res = execute_query("SELECT COUNT(*) as count FROM clinical_examinations", fetch_all=False)
    autopsy_cases_res = execute_query("SELECT COUNT(*) as count FROM postmortem_investigations", fetch_all=False)
    
    total_clinical = clinical_cases_res['count'] if clinical_cases_res else 0
    total_autopsies = autopsy_cases_res['count'] if autopsy_cases_res else 0
    total_cases = total_clinical + total_autopsies

    # 2. Active Cases
    # Cases where report_submission_date is NULL
    clinical_active_res = execute_query("SELECT COUNT(*) as count FROM clinical_examinations WHERE report_submission_date IS NULL", fetch_all=False)
    autopsy_active_res = execute_query("SELECT COUNT(*) as count FROM postmortem_investigations WHERE report_submission_date IS NULL", fetch_all=False)
    active_cases = (clinical_active_res['count'] if clinical_active_res else 0) + (autopsy_active_res['count'] if autopsy_active_res else 0)
    
    # 3. Total Patients (Registered Living Subjects)
    total_patients_res = execute_query("SELECT COUNT(*) as count FROM living_subjects", fetch_all=False)
    total_patients = total_patients_res['count'] if total_patients_res else 0
    
    # 4. Pending Reports
    pending_reports_res = execute_query("SELECT COUNT(*) as count FROM court_submissions WHERE receipt_scan_path IS NULL", fetch_all=False)
    pending_reports = pending_reports_res['count'] if pending_reports_res else 0

    # 5. Recent Cases (Union Query)
    recent_cases_query = """
        SELECT 
            c.reference_no AS case_no, 
            s.name_encrypted AS patient_name, 
            'Clinical' AS type, 
            COALESCE(m.report_status, 'Under Investigation') AS status, 
            c.admission_date AS date 
        FROM clinical_examinations c 
        JOIN living_subjects s ON c.subject_id = s.subject_id 
        LEFT JOIN mlr_documents m ON c.case_id = m.clinical_case_id 
        UNION ALL 
        SELECT 
            a.pm_serial_no AS case_no, 
            cad.name_encrypted AS patient_name, 
            'Autopsy' AS type, 
            COALESCE(p.draft_status, 'Under Investigation') AS status, 
            a.admission_date AS date 
        FROM postmortem_investigations a 
        JOIN cadavers cad ON a.cadaver_id = cad.cadaver_id 
        LEFT JOIN pmr_drafts p ON a.case_id = p.autopsy_case_id 
        ORDER BY date DESC 
        LIMIT 5
    """
    recent_cases = execute_query(recent_cases_query, fetch_all=True)
    if not recent_cases:
        recent_cases = []

    # Map priority based on type or random logic since it's not in DB
    # We will simulate priority based on status
    for case in recent_cases:
        if case['status'] == 'Under Investigation':
            case['priority'] = 'Urgent'
        else:
            case['priority'] = 'Normal'

    # Current date for header
    current_date_str = datetime.now().strftime('%A, %B %d, %Y')
    
    return render_template('dashboard.html', 
                           total_cases=total_cases,
                           total_clinical=total_clinical,
                           total_autopsies=total_autopsies,
                           active_cases=active_cases,
                           total_patients=total_patients,
                           pending_reports=pending_reports,
                           recent_cases=recent_cases,
                           current_date=current_date_str)
