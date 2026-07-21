from flask import Blueprint, render_template, request, redirect, flash
from app.services.auth_utils import login_required, roles_allowed
from app.services.db import execute_query, call_procedure

autopsy_bp = Blueprint('autopsy', __name__)

@autopsy_bp.route('/', methods=['GET'])
@login_required
def list_autopsy():
    cases = execute_query("SELECT * FROM postmortem_investigations ORDER BY admission_date DESC LIMIT 50")
    return render_template('autopsy/list.html', cases=cases)

@autopsy_bp.route('/new', methods=['GET', 'POST'])
@login_required
@roles_allowed('Administrator', 'Doctor / JMO', 'Clerk / Admin Staff')
def new_autopsy():
    if request.method == 'POST':
        try:
            call_procedure('sp_register_autopsy_case', (
                request.form.get('nic'), request.form.get('name'), request.form.get('estimated_age') or 0,
                request.form.get('gender'), request.form.get('address_found'), request.form.get('death_datetime'),
                request.form.get('station_id'), request.form.get('assigned_doctor_id'), request.form.get('pm_serial_no'),
                request.form.get('admission_date'), request.form.get('hospital_bht_no'),
                request.form.get('inquest_ordered_by'), request.form.get('inquest_order_no'), request.form.get('place_of_postmortem')
            ))
            flash("Autopsy case registered successfully!", "success")
            return redirect('/autopsy')
        except Exception as e:
            flash(f"Error registering case: {str(e)}", "error")

    return render_template('autopsy/form.html')
