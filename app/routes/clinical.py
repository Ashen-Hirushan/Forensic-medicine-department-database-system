import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, flash, session, current_app
from app.services.auth_utils import login_required, roles_allowed
from app.services.db import execute_query, call_procedure

clinical_bp = Blueprint('clinical', __name__)

# ---------------------------------------------------------------------------
# LIST — All Clinical Cases (with doctor filter & patient name)
# ---------------------------------------------------------------------------
@clinical_bp.route('/', methods=['GET'])
@login_required
def list_clinical():
    doctor_filter = request.args.get('doctor_id', '')
    
    query = """
        SELECT c.case_id, c.reference_no, c.hospital_bht_no, c.admission_date,
               c.assigned_doctor_id, c.case_category, c.referral_source,
               s.name_encrypted AS patient_name, s.gender, s.age,
               COALESCE(m.report_status, 'Pending Exam') AS report_status
        FROM clinical_examinations c
        JOIN living_subjects s ON c.subject_id = s.subject_id
        LEFT JOIN mlr_documents m ON c.case_id = m.clinical_case_id
    """
    params = []
    if doctor_filter:
        query += " WHERE c.assigned_doctor_id = %s"
        params.append(int(doctor_filter))
    
    query += " ORDER BY c.admission_date DESC LIMIT 50"
    
    cases = execute_query(query, tuple(params))
    
    # Get doctors for filter dropdown
    doctors = execute_query("""
        SELECT mo.doctor_id, sd.full_name 
        FROM medical_officers mo 
        JOIN staff_directory sd ON mo.staff_id = sd.staff_id
    """)
    
    return render_template('clinical/list.html', cases=cases, doctors=doctors, 
                           doctor_filter=doctor_filter)

# ---------------------------------------------------------------------------
# NEW — Register Clinical Case
# ---------------------------------------------------------------------------
@clinical_bp.route('/new', methods=['GET', 'POST'])
@login_required
@roles_allowed('Admin', 'Doctor', 'Clerk')
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
            
            # Update new columns if provided
            new_case = execute_query(
                "SELECT case_id FROM clinical_examinations ORDER BY case_id DESC LIMIT 1",
                fetch_all=False
            )
            if new_case:
                cat = request.form.get('case_category')
                src = request.form.get('referral_source')
                if cat or src:
                    execute_query(
                        "UPDATE clinical_examinations SET case_category=%s, referral_source=%s WHERE case_id=%s",
                        (cat or None, src or None, new_case['case_id'])
                    )
            
            flash("Clinical case registered successfully!", "success")
            return redirect('/clinical')
        except Exception as e:
            flash(f"Error registering case: {str(e)}", "error")

    # Fetch dropdown data
    facilities = execute_query("SELECT facility_id, facility_name FROM healthcare_facilities")
    stations = execute_query("SELECT station_id, station_name FROM police_divisions")
    doctors = execute_query("""
        SELECT mo.doctor_id, sd.full_name 
        FROM medical_officers mo 
        JOIN staff_directory sd ON mo.staff_id = sd.staff_id
    """)
    
    return render_template('clinical/form.html', facilities=facilities, 
                           stations=stations, doctors=doctors)

# ---------------------------------------------------------------------------
# DETAIL — View a single clinical case with all related data
# ---------------------------------------------------------------------------
@clinical_bp.route('/<int:case_id>', methods=['GET'])
@login_required
def detail_clinical(case_id):
    # Main case + patient info
    case = execute_query("""
        SELECT c.*, s.name_encrypted AS patient_name, s.nic_encrypted AS patient_nic,
               s.age, s.gender, s.permanent_address, s.contact_no,
               f.facility_name, pd.station_name,
               sd.full_name AS doctor_name
        FROM clinical_examinations c
        JOIN living_subjects s ON c.subject_id = s.subject_id
        LEFT JOIN healthcare_facilities f ON c.facility_id = f.facility_id
        LEFT JOIN police_divisions pd ON c.station_id = pd.station_id
        LEFT JOIN medical_officers mo ON c.assigned_doctor_id = mo.doctor_id
        LEFT JOIN staff_directory sd ON mo.staff_id = sd.staff_id
        WHERE c.case_id = %s
    """, (case_id,), fetch_all=False)
    
    if not case:
        flash("Case not found.", "error")
        return redirect('/clinical')
    
    # MLEF record
    mlef = execute_query(
        "SELECT * FROM mlef_records WHERE clinical_case_id = %s", (case_id,), fetch_all=False
    )
    
    # MLR document status
    mlr = execute_query(
        "SELECT * FROM mlr_documents WHERE clinical_case_id = %s", (case_id,), fetch_all=False
    )
    
    # Clinical observations
    observations = execute_query(
        "SELECT * FROM clinical_observations WHERE clinical_case_id = %s", (case_id,)
    )
    
    # Wound charts
    wounds = execute_query(
        "SELECT * FROM wound_charts WHERE clinical_case_id = %s", (case_id,)
    )
    
    # Test requests + results
    investigations = execute_query("""
        SELECT tr.*, GROUP_CONCAT(tres.file_pointer) AS result_files
        FROM test_requests tr
        LEFT JOIN test_results tres ON tr.request_id = tres.request_id
        WHERE tr.clinical_case_id = %s
        GROUP BY tr.request_id
    """, (case_id,))
    
    # Consultation referrals
    referrals = execute_query(
        "SELECT * FROM consultation_referrals WHERE clinical_case_id = %s", (case_id,)
    )
    
    # Digital assets (photos)
    photos = execute_query(
        "SELECT * FROM digital_assets WHERE clinical_case_id = %s", (case_id,)
    )
    
    # Court submissions
    court = execute_query(
        "SELECT * FROM court_submissions WHERE clinical_case_id = %s", (case_id,)
    )
    
    # Peer reviews
    peer_reviews = execute_query("""
        SELECT pr.review_id, sd.full_name AS reviewer_name
        FROM peer_reviews pr
        JOIN medical_officers mo ON pr.reviewed_by_doctor_id = mo.doctor_id
        JOIN staff_directory sd ON mo.staff_id = sd.staff_id
        WHERE pr.clinical_case_id = %s
    """, (case_id,))
    
    # Physical evidence
    evidence = execute_query(
        "SELECT * FROM physical_evidence WHERE clinical_case_id = %s", (case_id,)
    )
    
    # Doctors for peer review dropdown
    doctors = execute_query("""
        SELECT mo.doctor_id, sd.full_name 
        FROM medical_officers mo 
        JOIN staff_directory sd ON mo.staff_id = sd.staff_id
    """)
    
    return render_template('clinical/detail.html', case=case, mlef=mlef, mlr=mlr,
                           observations=observations, wounds=wounds,
                           investigations=investigations, referrals=referrals,
                           photos=photos, court=court, peer_reviews=peer_reviews,
                           evidence=evidence, doctors=doctors)

# ---------------------------------------------------------------------------
# MLEF — Edit MLEF record for a clinical case
# ---------------------------------------------------------------------------
@clinical_bp.route('/<int:case_id>/mlef', methods=['GET', 'POST'])
@login_required
@roles_allowed('Admin', 'Doctor')
def edit_mlef(case_id):
    if request.method == 'POST':
        try:
            execute_query("""
                UPDATE mlef_records SET
                    mlef_number = %s,
                    consent_obtained = %s,
                    injury_details = %s,
                    has_abrasion = %s,
                    has_contusion = %s,
                    has_laceration = %s,
                    has_stab = %s,
                    has_fracture = %s,
                    has_burn = %s,
                    category_of_hurt = %s,
                    under_influence_of_alcohol = %s,
                    accompanying_officer_info = %s
                WHERE clinical_case_id = %s
            """, (
                request.form.get('mlef_number'),
                1 if request.form.get('consent_obtained') else 0,
                request.form.get('injury_details'),
                1 if request.form.get('has_abrasion') else 0,
                1 if request.form.get('has_contusion') else 0,
                1 if request.form.get('has_laceration') else 0,
                1 if request.form.get('has_stab') else 0,
                1 if request.form.get('has_fracture') else 0,
                1 if request.form.get('has_burn') else 0,
                request.form.get('category_of_hurt') or None,
                1 if request.form.get('under_influence_of_alcohol') else 0,
                request.form.get('accompanying_officer_info'),
                case_id
            ))
            flash("MLEF record updated successfully!", "success")
            return redirect(f'/clinical/{case_id}')
        except Exception as e:
            flash(f"Error updating MLEF: {str(e)}", "error")
    
    mlef = execute_query(
        "SELECT * FROM mlef_records WHERE clinical_case_id = %s", (case_id,), fetch_all=False
    )
    case = execute_query(
        "SELECT c.reference_no FROM clinical_examinations c WHERE c.case_id = %s",
        (case_id,), fetch_all=False
    )
    
    return render_template('clinical/mlef_form.html', mlef=mlef, case=case, case_id=case_id)

# ---------------------------------------------------------------------------
# OBSERVATIONS — Add clinical observations
# ---------------------------------------------------------------------------
@clinical_bp.route('/<int:case_id>/observations', methods=['POST'])
@login_required
@roles_allowed('Admin', 'Doctor')
def add_observation(case_id):
    try:
        execute_query(
            "INSERT INTO clinical_observations (clinical_case_id, findings_text_encrypted) VALUES (%s, %s)",
            (case_id, request.form.get('findings'))
        )
        flash("Observation added successfully!", "success")
    except Exception as e:
        flash(f"Error adding observation: {str(e)}", "error")
    return redirect(f'/clinical/{case_id}')

# ---------------------------------------------------------------------------
# WOUNDS — Add wound chart entry
# ---------------------------------------------------------------------------
@clinical_bp.route('/<int:case_id>/wounds', methods=['POST'])
@login_required
@roles_allowed('Admin', 'Doctor')
def add_wound(case_id):
    try:
        execute_query("""
            INSERT INTO wound_charts (clinical_case_id, wound_type, weapon_suspected, anatomical_location)
            VALUES (%s, %s, %s, %s)
        """, (
            case_id,
            request.form.get('wound_type'),
            request.form.get('weapon_suspected'),
            request.form.get('anatomical_location')
        ))
        flash("Wound chart entry added!", "success")
    except Exception as e:
        flash(f"Error adding wound: {str(e)}", "error")
    return redirect(f'/clinical/{case_id}')

# ---------------------------------------------------------------------------
# MLR STATUS — Update MLR document status
# ---------------------------------------------------------------------------
@clinical_bp.route('/<int:case_id>/mlr-status', methods=['POST'])
@login_required
@roles_allowed('Admin', 'Doctor', 'Clerk')
def update_mlr_status(case_id):
    new_status = request.form.get('report_status')
    try:
        # Check if MLR record exists
        existing = execute_query(
            "SELECT mlr_id FROM mlr_documents WHERE clinical_case_id = %s", (case_id,), fetch_all=False
        )
        if existing:
            execute_query(
                "UPDATE mlr_documents SET report_status = %s WHERE clinical_case_id = %s",
                (new_status, case_id)
            )
        else:
            execute_query(
                "INSERT INTO mlr_documents (clinical_case_id, report_status) VALUES (%s, %s)",
                (case_id, new_status)
            )
        
        # If dispatched, update report_submission_date
        if new_status in ('Dispatched', 'Received by Court'):
            execute_query(
                "UPDATE clinical_examinations SET report_submission_date = NOW() WHERE case_id = %s AND report_submission_date IS NULL",
                (case_id,)
            )
        
        flash("Report status updated!", "success")
    except Exception as e:
        flash(f"Error updating status: {str(e)}", "error")
    return redirect(f'/clinical/{case_id}')

# ---------------------------------------------------------------------------
# INVESTIGATIONS — Request a new test
# ---------------------------------------------------------------------------
@clinical_bp.route('/<int:case_id>/investigations', methods=['POST'])
@login_required
@roles_allowed('Admin', 'Doctor')
def request_investigation(case_id):
    try:
        execute_query(
            "INSERT INTO test_requests (clinical_case_id, request_status) VALUES (%s, 'Pending')",
            (case_id,)
        )
        flash("Investigation request created!", "success")
    except Exception as e:
        flash(f"Error creating request: {str(e)}", "error")
    return redirect(f'/clinical/{case_id}')

# ---------------------------------------------------------------------------
# REFERRALS — Create consultation referral
# ---------------------------------------------------------------------------
@clinical_bp.route('/<int:case_id>/referrals', methods=['POST'])
@login_required
@roles_allowed('Admin', 'Doctor')
def add_referral(case_id):
    try:
        execute_query("""
            INSERT INTO consultation_referrals (clinical_case_id, referred_to_specialty, referral_status)
            VALUES (%s, %s, %s)
        """, (
            case_id,
            request.form.get('referred_to_specialty'),
            request.form.get('referral_status', 'Pending')
        ))
        flash("Referral added!", "success")
    except Exception as e:
        flash(f"Error adding referral: {str(e)}", "error")
    return redirect(f'/clinical/{case_id}')

# ---------------------------------------------------------------------------
# PHOTOS — Upload case photograph
# ---------------------------------------------------------------------------
@clinical_bp.route('/<int:case_id>/photos', methods=['POST'])
@login_required
@roles_allowed('Admin', 'Doctor')
def upload_photo(case_id):
    if 'photo' not in request.files:
        flash("No file selected.", "error")
        return redirect(f'/clinical/{case_id}')
    
    file = request.files['photo']
    if file.filename == '':
        flash("No file selected.", "error")
        return redirect(f'/clinical/{case_id}')
    
    try:
        filename = secure_filename(file.filename)
        # Create case-specific folder
        case_dir = os.path.join(current_app.config['UPLOADS_DIR'], f'clinical_{case_id}')
        os.makedirs(case_dir, exist_ok=True)
        filepath = os.path.join(case_dir, filename)
        file.save(filepath)
        
        execute_query("""
            INSERT INTO digital_assets (clinical_case_id, uploaded_by, asset_type)
            VALUES (%s, %s, %s)
        """, (case_id, session.get('user_id'), request.form.get('asset_type', 'Photograph')))
        
        # Get asset_id and add revision
        asset = execute_query("SELECT LAST_INSERT_ID() as id", fetch_all=False)
        if asset:
            execute_query("""
                INSERT INTO asset_revisions (asset_id, uploaded_by, file_pointer)
                VALUES (%s, %s, %s)
            """, (asset['id'], session.get('user_id'), filepath))
        
        flash("Photo uploaded successfully!", "success")
    except Exception as e:
        flash(f"Error uploading photo: {str(e)}", "error")
    
    return redirect(f'/clinical/{case_id}')

# ---------------------------------------------------------------------------
# MLR REPORT — Compose / Edit Medico-Legal Report
# ---------------------------------------------------------------------------
@clinical_bp.route('/<int:case_id>/mlr', methods=['GET', 'POST'])
@login_required
@roles_allowed('Admin', 'Doctor')
def edit_mlr(case_id):
    if request.method == 'POST':
        try:
            existing = execute_query(
                "SELECT mlr_id FROM mlr_documents WHERE clinical_case_id = %s", (case_id,), fetch_all=False
            )
            if existing:
                execute_query("""
                    UPDATE mlr_documents SET
                        opinion_encrypted = %s,
                        history_of_incident = %s,
                        examination_findings = %s,
                        conclusions = %s,
                        category_of_hurt_opinion = %s,
                        prepared_by_doctor_id = %s,
                        prepared_date = NOW(),
                        report_status = %s
                    WHERE clinical_case_id = %s
                """, (
                    request.form.get('opinion'),
                    request.form.get('history_of_incident'),
                    request.form.get('examination_findings'),
                    request.form.get('conclusions'),
                    request.form.get('category_of_hurt_opinion'),
                    session.get('user_id'),
                    request.form.get('report_status', 'PMR/MLEF Drafted'),
                    case_id
                ))
            else:
                execute_query("""
                    INSERT INTO mlr_documents 
                        (clinical_case_id, opinion_encrypted, history_of_incident, 
                         examination_findings, conclusions, category_of_hurt_opinion,
                         prepared_by_doctor_id, prepared_date, report_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
                """, (
                    case_id,
                    request.form.get('opinion'),
                    request.form.get('history_of_incident'),
                    request.form.get('examination_findings'),
                    request.form.get('conclusions'),
                    request.form.get('category_of_hurt_opinion'),
                    session.get('user_id'),
                    request.form.get('report_status', 'PMR/MLEF Drafted')
                ))
            flash("MLR report saved successfully!", "success")
            return redirect(f'/clinical/{case_id}')
        except Exception as e:
            flash(f"Error saving MLR: {str(e)}", "error")
    
    # Get case info + patient info for the report header
    case = execute_query("""
        SELECT c.*, s.name_encrypted AS patient_name, s.nic_encrypted AS patient_nic,
               s.age, s.gender, s.permanent_address, s.contact_no,
               f.facility_name, pd.station_name,
               sd.full_name AS doctor_name
        FROM clinical_examinations c
        JOIN living_subjects s ON c.subject_id = s.subject_id
        LEFT JOIN healthcare_facilities f ON c.facility_id = f.facility_id
        LEFT JOIN police_divisions pd ON c.station_id = pd.station_id
        LEFT JOIN medical_officers mo ON c.assigned_doctor_id = mo.doctor_id
        LEFT JOIN staff_directory sd ON mo.staff_id = sd.staff_id
        WHERE c.case_id = %s
    """, (case_id,), fetch_all=False)
    
    mlr = execute_query(
        "SELECT * FROM mlr_documents WHERE clinical_case_id = %s", (case_id,), fetch_all=False
    )
    
    # Get MLEF data for pre-filling
    mlef = execute_query(
        "SELECT * FROM mlef_records WHERE clinical_case_id = %s", (case_id,), fetch_all=False
    )
    
    # Get wound chart data
    wounds = execute_query(
        "SELECT * FROM wound_charts WHERE clinical_case_id = %s", (case_id,)
    )
    
    # Get observations
    observations = execute_query(
        "SELECT * FROM clinical_observations WHERE clinical_case_id = %s", (case_id,)
    )
    
    return render_template('clinical/mlr_form.html', case=case, mlr=mlr, mlef=mlef,
                           wounds=wounds, observations=observations, case_id=case_id)

# ---------------------------------------------------------------------------
# PEER REVIEWS — Add peer review for clinical case
# ---------------------------------------------------------------------------
@clinical_bp.route('/<int:case_id>/peer-review', methods=['POST'])
@login_required
@roles_allowed('Admin', 'Doctor')
def add_peer_review(case_id):
    try:
        execute_query("""
            INSERT INTO peer_reviews (clinical_case_id, reviewed_by_doctor_id)
            VALUES (%s, %s)
        """, (case_id, request.form.get('reviewed_by_doctor_id')))
        flash("Peer review recorded!", "success")
    except Exception as e:
        flash(f"Error adding peer review: {str(e)}", "error")
    return redirect(f'/clinical/{case_id}')


# ---------------------------------------------------------------------------
# REFERRALS — Clinical Consultation Referrals
# ---------------------------------------------------------------------------
@clinical_bp.route('/<int:case_id>/referrals', methods=['GET', 'POST'])
@login_required
@roles_allowed('Admin', 'Doctor')
def referrals(case_id):
    if request.method == 'POST':
        specialty = request.form.get('specialty')
        status = request.form.get('status', 'Pending')
        try:
            execute_query("""
                INSERT INTO consultation_referrals (clinical_case_id, referred_to_specialty, referral_status)
                VALUES (%s, %s, %s)
            """, (case_id, specialty, status))
            flash("Referral created successfully.", "success")
        except Exception as e:
            flash(f"Error creating referral: {e}", "error")
        return redirect(f'/clinical/{case_id}')
        
    # GET method - render the referral page
    case = execute_query("SELECT reference_no FROM clinical_examinations WHERE case_id = %s", (case_id,), fetch_all=False)
    referrals_list = execute_query("SELECT * FROM consultation_referrals WHERE clinical_case_id = %s", (case_id,))
    return render_template('clinical/referrals.html', case=case, case_id=case_id, referrals=referrals_list)
