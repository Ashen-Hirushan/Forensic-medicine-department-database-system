from flask import Blueprint, render_template
from app.services.auth_utils import login_required
from app.services.db import call_procedure
from datetime import datetime
import json

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

    for case in recent_cases:
        if case['status'] == 'Under Investigation':
            case['priority'] = 'Urgent'
        else:
            case['priority'] = 'Normal'

    # 6. Monthly Trend Data (last 6 months)
    monthly_trend_query = """
        SELECT months.month_label, months.month_num, months.year_num,
               COALESCE(clinical.cnt, 0) AS clinical_count,
               COALESCE(autopsy.cnt, 0) AS autopsy_count
        FROM (
            SELECT DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL n MONTH), '%%b') AS month_label,
                   MONTH(DATE_SUB(CURDATE(), INTERVAL n MONTH)) AS month_num,
                   YEAR(DATE_SUB(CURDATE(), INTERVAL n MONTH)) AS year_num
            FROM (SELECT 0 AS n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) nums
        ) months
        LEFT JOIN (
            SELECT MONTH(admission_date) AS m, YEAR(admission_date) AS y, COUNT(*) AS cnt
            FROM clinical_examinations
            WHERE admission_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY MONTH(admission_date), YEAR(admission_date)
        ) clinical ON months.month_num = clinical.m AND months.year_num = clinical.y
        LEFT JOIN (
            SELECT MONTH(admission_date) AS m, YEAR(admission_date) AS y, COUNT(*) AS cnt
            FROM postmortem_investigations
            WHERE admission_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY MONTH(admission_date), YEAR(admission_date)
        ) autopsy ON months.month_num = autopsy.m AND months.year_num = autopsy.y
        ORDER BY months.year_num ASC, months.month_num ASC
    """
    monthly_trend = execute_query(monthly_trend_query, fetch_all=True)
    if not monthly_trend:
        monthly_trend = []
    
    trend_labels = [r['month_label'] for r in monthly_trend]
    trend_clinical = [int(r['clinical_count']) for r in monthly_trend]
    trend_autopsy = [int(r['autopsy_count']) for r in monthly_trend]

    # 7. Case Category Breakdown (for clinical)
    category_query = """
        SELECT COALESCE(case_category, 'Uncategorized') AS category, COUNT(*) AS cnt
        FROM clinical_examinations
        GROUP BY case_category
        ORDER BY cnt DESC
        LIMIT 6
    """
    categories = execute_query(category_query, fetch_all=True)
    if not categories:
        categories = []
    
    cat_labels = [r['category'] for r in categories]
    cat_values = [int(r['cnt']) for r in categories]

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
                           current_date=current_date_str,
                           trend_labels=json.dumps(trend_labels),
                           trend_clinical=json.dumps(trend_clinical),
                           trend_autopsy=json.dumps(trend_autopsy),
                           cat_labels=json.dumps(cat_labels),
                           cat_values=json.dumps(cat_values))

