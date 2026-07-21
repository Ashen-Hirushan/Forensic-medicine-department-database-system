from flask import Blueprint, render_template
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
