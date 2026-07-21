from flask import Blueprint, render_template, request, redirect, flash
from app.services.auth_utils import login_required, roles_allowed
from app.services.db import execute_query, call_procedure

clinical_bp = Blueprint('clinical', __name__)

@clinical_bp.route('/', methods=['GET'])
@login_required
def list_clinical():
    cases = execute_query("SELECT * FROM clinical_examinations ORDER BY admission_date DESC LIMIT 50")
    return render_template('clinical/list.html', cases=cases)

@clinical_bp.route('/new', methods=['GET', 'POST'])
@login_required
@roles_allowed('Administrator', 'Doctor / JMO', 'Clerk / Admin Staff')
def new_clinical():
    if request.method == 'POST':
        try:
            call_procedure('sp_register_clinical_case', (
                request.form.get('nic'), request.form.get('name'), int(request.form.get('age') or 0),
                request.form.get('gender'), request.form.get('address'), request.form.get('contact'),
                request.form.get('facility_id'), request.form.get('station_id'), request.form.get('assigned_doctor_id'),
                request.form.get('reference_no'), request.form.get('incident_date'), request.form.get('admission_date'),
                request.form.get('hospital_bht_no')
            ))
            flash("Clinical case registered successfully!", "success")
            return redirect('/clinical')
        except Exception as e:
            flash(f"Error registering case: {str(e)}", "error")

    return render_template('clinical/form.html')
