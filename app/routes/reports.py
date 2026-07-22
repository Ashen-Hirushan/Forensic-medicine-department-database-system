from flask import Blueprint, render_template, request
from app.services.auth_utils import login_required
from app.services.db import execute_query

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/daily', methods=['GET'])
@login_required
def daily_report():
    cases = execute_query("SELECT * FROM view_daily_clinical_cases")
    return render_template('reports/daily.html', cases=cases)

@reports_bp.route('/pending', methods=['GET'])
@login_required
def pending_report():
    reports = execute_query("SELECT * FROM view_pending_court_reports")
    return render_template('reports/pending.html', reports=reports)

@reports_bp.route('/mlef-register', methods=['GET'])
@login_required
def mlef_register():
    search = request.args.get('search', '')
    
    query = """
        SELECT m.mlef_id, m.mlef_number, m.clinical_case_id,
               c.reference_no, c.admission_date, c.case_category,
               s.name_encrypted AS patient_name, s.nic_encrypted AS patient_nic,
               s.age, s.gender,
               m.consent_obtained, m.category_of_hurt,
               COALESCE(mlr.report_status, 'Pending Exam') AS report_status,
               sd.full_name AS doctor_name
        FROM mlef_records m
        JOIN clinical_examinations c ON m.clinical_case_id = c.case_id
        JOIN living_subjects s ON c.subject_id = s.subject_id
        LEFT JOIN mlr_documents mlr ON c.case_id = mlr.clinical_case_id
        LEFT JOIN medical_officers mo ON c.assigned_doctor_id = mo.doctor_id
        LEFT JOIN staff_directory sd ON mo.staff_id = sd.staff_id
    """
    params = []
    if search:
        query += " WHERE m.mlef_number LIKE %s OR c.reference_no LIKE %s OR s.name_encrypted LIKE %s"
        like = f"%{search}%"
        params = [like, like, like]
    
    query += " ORDER BY c.admission_date DESC"
    
    records = execute_query(query, tuple(params))
    return render_template('reports/mlef_register.html', records=records, search=search)

@reports_bp.route('/pm-register', methods=['GET'])
@login_required
def pm_register():
    search = request.args.get('search', '')
    
    query = """
        SELECT p.case_id, p.pm_serial_no, p.admission_date, p.autopsy_date,
               p.manner_of_death, p.place_of_postmortem,
               p.inquest_ordered_by, p.inquest_order_no,
               c.name_encrypted AS cadaver_name, c.nic_encrypted AS cadaver_nic,
               c.estimated_age, c.gender,
               COALESCE(d.draft_status, 'Pending Exam') AS draft_status,
               sd.full_name AS doctor_name
        FROM postmortem_investigations p
        JOIN cadavers c ON p.cadaver_id = c.cadaver_id
        LEFT JOIN pmr_drafts d ON p.case_id = d.autopsy_case_id
        LEFT JOIN medical_officers mo ON p.assigned_doctor_id = mo.doctor_id
        LEFT JOIN staff_directory sd ON mo.staff_id = sd.staff_id
    """
    params = []
    if search:
        query += " WHERE p.pm_serial_no LIKE %s OR c.name_encrypted LIKE %s"
        like = f"%{search}%"
        params = [like, like]
    
    query += " ORDER BY p.admission_date DESC"
    
    records = execute_query(query, tuple(params))
    return render_template('reports/pm_register.html', records=records, search=search)
