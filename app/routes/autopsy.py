import os
from werkzeug.utils import secure_filename
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    session,
    current_app,
)
from app.services.auth_utils import login_required, roles_allowed
from app.services.db import execute_query, call_procedure

autopsy_bp = Blueprint("autopsy", __name__)


# ---------------------------------------------------------------------------
# LIST — All Autopsy Cases (with doctor filter & cadaver name)
# ---------------------------------------------------------------------------
@autopsy_bp.route("/", methods=["GET"])
@login_required
def list_autopsy():
    doctor_filter = request.args.get("doctor_id", "")

    query = """
        SELECT p.case_id, p.pm_serial_no, p.admission_date, p.autopsy_date,
               p.assigned_doctor_id, p.manner_of_death,
               c.name_encrypted AS cadaver_name, c.gender, c.estimated_age,
               COALESCE(d.draft_status, 'Pending Exam') AS draft_status
        FROM postmortem_investigations p
        JOIN cadavers c ON p.cadaver_id = c.cadaver_id
        LEFT JOIN pmr_drafts d ON p.case_id = d.autopsy_case_id
    """
    params = []
    if doctor_filter:
        query += " WHERE p.assigned_doctor_id = %s"
        params.append(int(doctor_filter))

    query += " ORDER BY p.admission_date DESC LIMIT 50"

    cases = execute_query(query, tuple(params))

    doctors = execute_query("""
        SELECT mo.doctor_id, sd.full_name 
        FROM medical_officers mo 
        JOIN staff_directory sd ON mo.staff_id = sd.staff_id
    """)

    return render_template(
        "autopsy/list.html", cases=cases, doctors=doctors, doctor_filter=doctor_filter
    )


# ---------------------------------------------------------------------------
# NEW — Register Autopsy Case
# ---------------------------------------------------------------------------
@autopsy_bp.route("/new", methods=["GET", "POST"])
@login_required
@roles_allowed("Admin", "Doctor", "Clerk")
def new_autopsy():
    if request.method == "POST":
        try:
            call_procedure(
                "sp_register_autopsy_case",
                (
                    request.form.get("nic"),
                    request.form.get("name"),
                    request.form.get("estimated_age") or 0,
                    request.form.get("gender"),
                    request.form.get("address_found"),
                    request.form.get("death_datetime"),
                    request.form.get("station_id"),
                    request.form.get("assigned_doctor_id"),
                    request.form.get("pm_serial_no"),
                    request.form.get("admission_date"),
                    request.form.get("hospital_bht_no"),
                    request.form.get("inquest_ordered_by"),
                    request.form.get("inquest_order_no"),
                    request.form.get("place_of_postmortem"),
                ),
            )

            # Update manner_of_death
            new_case = execute_query(
                "SELECT case_id FROM postmortem_investigations ORDER BY case_id DESC LIMIT 1",
                fetch_all=False,
            )
            if new_case:
                mod = request.form.get("manner_of_death")
                autopsy_date = request.form.get("autopsy_date")
                if mod or autopsy_date:
                    execute_query(
                        "UPDATE postmortem_investigations SET manner_of_death=%s, autopsy_date=%s WHERE case_id=%s",
                        (mod or None, autopsy_date or None, new_case["case_id"]),
                    )

            flash("Autopsy case registered successfully!", "success")
            return redirect("/autopsy")
        except Exception as e:
            flash(f"Error registering case: {str(e)}", "error")

    stations = execute_query("SELECT station_id, station_name FROM police_divisions")
    doctors = execute_query("""
        SELECT mo.doctor_id, sd.full_name 
        FROM medical_officers mo 
        JOIN staff_directory sd ON mo.staff_id = sd.staff_id
    """)

    return render_template("autopsy/form.html", stations=stations, doctors=doctors)


# ---------------------------------------------------------------------------
# DETAIL — View a single autopsy case with all related data
# ---------------------------------------------------------------------------
@autopsy_bp.route("/<int:case_id>", methods=["GET"])
@login_required
def detail_autopsy(case_id):
    case = execute_query(
        """
        SELECT p.*, c.name_encrypted AS cadaver_name, c.nic_encrypted AS cadaver_nic,
               c.estimated_age, c.gender, c.address_found, c.death_datetime,
               pd.station_name,
               sd.full_name AS doctor_name
        FROM postmortem_investigations p
        JOIN cadavers c ON p.cadaver_id = c.cadaver_id
        LEFT JOIN police_divisions pd ON p.station_id = pd.station_id
        LEFT JOIN medical_officers mo ON p.assigned_doctor_id = mo.doctor_id
        LEFT JOIN staff_directory sd ON mo.staff_id = sd.staff_id
        WHERE p.case_id = %s
    """,
        (case_id,),
        fetch_all=False,
    )

    if not case:
        flash("Case not found.", "error")
        return redirect("/autopsy")

    # PMR draft
    pmr = execute_query(
        "SELECT * FROM pmr_drafts WHERE autopsy_case_id = %s",
        (case_id,),
        fetch_all=False,
    )

    # Death certificate / Cause of death
    cod = execute_query(
        "SELECT * FROM death_certificates WHERE autopsy_case_id = %s",
        (case_id,),
        fetch_all=False,
    )

    # Wound charts
    wounds = execute_query(
        "SELECT * FROM wound_charts WHERE autopsy_case_id = %s", (case_id,)
    )

    # Test requests + results
    investigations = execute_query(
        """
        SELECT tr.*, GROUP_CONCAT(tres.file_pointer) AS result_files
        FROM test_requests tr
        LEFT JOIN test_results tres ON tr.request_id = tres.request_id
        WHERE tr.autopsy_case_id = %s
        GROUP BY tr.request_id
    """,
        (case_id,),
    )

    # Digital assets (photos)
    photos = execute_query(
        "SELECT * FROM digital_assets WHERE autopsy_case_id = %s", (case_id,)
    )

    # Voice dictations
    dictations = execute_query(
        "SELECT * FROM voice_dictations WHERE autopsy_case_id = %s", (case_id,)
    )

    # Court submissions
    court = execute_query(
        "SELECT * FROM court_submissions WHERE autopsy_case_id = %s", (case_id,)
    )

    # Peer reviews
    peer_reviews = execute_query(
        """
        SELECT pr.review_id, sd.full_name AS reviewer_name
        FROM peer_reviews pr
        JOIN medical_officers mo ON pr.reviewed_by_doctor_id = mo.doctor_id
        JOIN staff_directory sd ON mo.staff_id = sd.staff_id
        WHERE pr.autopsy_case_id = %s
    """,
        (case_id,),
    )

    # Physical evidence
    evidence = execute_query(
        "SELECT * FROM physical_evidence WHERE autopsy_case_id = %s", (case_id,)
    )

    # Doctors for peer review dropdown
    doctors = execute_query("""
        SELECT mo.doctor_id, sd.full_name 
        FROM medical_officers mo 
        JOIN staff_directory sd ON mo.staff_id = sd.staff_id
    """)

    return render_template(
        "autopsy/detail.html",
        case=case,
        pmr=pmr,
        cod=cod,
        wounds=wounds,
        investigations=investigations,
        photos=photos,
        dictations=dictations,
        court=court,
        peer_reviews=peer_reviews,
        evidence=evidence,
        doctors=doctors,
    )


# ---------------------------------------------------------------------------
# COD — Cause of Death form
# ---------------------------------------------------------------------------
@autopsy_bp.route("/<int:case_id>/cod", methods=["GET", "POST"])
@login_required
@roles_allowed("Admin", "Doctor")
def edit_cod(case_id):
    if request.method == "POST":
        try:
            existing = execute_query(
                "SELECT cod_id FROM death_certificates WHERE autopsy_case_id = %s",
                (case_id,),
                fetch_all=False,
            )
            if existing:
                execute_query(
                    """
                    UPDATE death_certificates SET
                        immediate_cause_encrypted = %s,
                        antecedent_cause_encrypted = %s,
                        contributory_cause_encrypted = %s,
                        is_maternal_death = %s
                    WHERE autopsy_case_id = %s
                """,
                    (
                        request.form.get("immediate_cause"),
                        request.form.get("antecedent_cause"),
                        request.form.get("contributory_cause"),
                        1 if request.form.get("is_maternal_death") else 0,
                        case_id,
                    ),
                )
            else:
                execute_query(
                    """
                    INSERT INTO death_certificates 
                        (autopsy_case_id, immediate_cause_encrypted, antecedent_cause_encrypted, 
                         contributory_cause_encrypted, is_maternal_death)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    (
                        case_id,
                        request.form.get("immediate_cause"),
                        request.form.get("antecedent_cause"),
                        request.form.get("contributory_cause"),
                        1 if request.form.get("is_maternal_death") else 0,
                    ),
                )
            flash("Cause of death form saved!", "success")
            return redirect(f"/autopsy/{case_id}")
        except Exception as e:
            flash(f"Error saving COD: {str(e)}", "error")

    cod = execute_query(
        "SELECT * FROM death_certificates WHERE autopsy_case_id = %s",
        (case_id,),
        fetch_all=False,
    )
    case = execute_query(
        "SELECT pm_serial_no FROM postmortem_investigations WHERE case_id = %s",
        (case_id,),
        fetch_all=False,
    )

    return render_template("autopsy/cod_form.html", cod=cod, case=case, case_id=case_id)


# ---------------------------------------------------------------------------
# WOUNDS — Add wound chart entry for autopsy
# ---------------------------------------------------------------------------
@autopsy_bp.route("/<int:case_id>/wounds", methods=["POST"])
@login_required
@roles_allowed("Admin", "Doctor")
def add_wound(case_id):
    try:
        execute_query(
            """
            INSERT INTO wound_charts (autopsy_case_id, wound_type, weapon_suspected, anatomical_location)
            VALUES (%s, %s, %s, %s)
        """,
            (
                case_id,
                request.form.get("wound_type"),
                request.form.get("weapon_suspected"),
                request.form.get("anatomical_location"),
            ),
        )
        flash("Wound chart entry added!", "success")
    except Exception as e:
        flash(f"Error adding wound: {str(e)}", "error")
    return redirect(f"/autopsy/{case_id}")


# ---------------------------------------------------------------------------
# PMR STATUS — Update PMR draft status
# ---------------------------------------------------------------------------
@autopsy_bp.route("/<int:case_id>/pmr-status", methods=["POST"])
@login_required
@roles_allowed("Admin", "Doctor", "Clerk")
def update_pmr_status(case_id):
    new_status = request.form.get("draft_status")
    try:
        existing = execute_query(
            "SELECT pmr_id FROM pmr_drafts WHERE autopsy_case_id = %s",
            (case_id,),
            fetch_all=False,
        )
        if existing:
            execute_query(
                "UPDATE pmr_drafts SET draft_status = %s WHERE autopsy_case_id = %s",
                (new_status, case_id),
            )
        else:
            execute_query(
                "INSERT INTO pmr_drafts (autopsy_case_id, draft_status) VALUES (%s, %s)",
                (case_id, new_status),
            )

        if new_status in ("Dispatched", "Received by Court"):
            execute_query(
                "UPDATE postmortem_investigations SET report_submission_date = NOW() WHERE case_id = %s AND report_submission_date IS NULL",
                (case_id,),
            )

        flash("PMR status updated!", "success")
    except Exception as e:
        flash(f"Error updating status: {str(e)}", "error")
    return redirect(f"/autopsy/{case_id}")


# ---------------------------------------------------------------------------
# INVESTIGATIONS — Request a new test for autopsy
# ---------------------------------------------------------------------------
@autopsy_bp.route("/<int:case_id>/investigations", methods=["POST"])
@login_required
@roles_allowed("Admin", "Doctor")
def request_investigation(case_id):
    try:
        execute_query(
            "INSERT INTO test_requests (autopsy_case_id, request_status) VALUES (%s, 'Pending')",
            (case_id,),
        )
        flash("Investigation request created!", "success")
    except Exception as e:
        flash(f"Error creating request: {str(e)}", "error")
    return redirect(f"/autopsy/{case_id}")


# ---------------------------------------------------------------------------
# PHOTOS — Upload case photograph for autopsy
# ---------------------------------------------------------------------------
@autopsy_bp.route("/<int:case_id>/photos", methods=["POST"])
@login_required
@roles_allowed("Admin", "Doctor")
def upload_photo(case_id):
    if "photo" not in request.files:
        flash("No file selected.", "error")
        return redirect(f"/autopsy/{case_id}")

    file = request.files["photo"]
    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(f"/autopsy/{case_id}")

    try:
        filename = secure_filename(file.filename)
        case_dir = os.path.join(current_app.config["UPLOADS_DIR"], f"autopsy_{case_id}")
        os.makedirs(case_dir, exist_ok=True)
        filepath = os.path.join(case_dir, filename)
        file.save(filepath)

        execute_query(
            """
            INSERT INTO digital_assets (autopsy_case_id, uploaded_by, asset_type)
            VALUES (%s, %s, %s)
        """,
            (
                case_id,
                session.get("user_id"),
                request.form.get("asset_type", "Photograph"),
            ),
        )

        asset = execute_query("SELECT LAST_INSERT_ID() as id", fetch_all=False)
        if asset:
            execute_query(
                """
                INSERT INTO asset_revisions (asset_id, uploaded_by, file_pointer)
                VALUES (%s, %s, %s)
            """,
                (asset["id"], session.get("user_id"), filepath),
            )

        flash("Photo uploaded successfully!", "success")
    except Exception as e:
        flash(f"Error uploading photo: {str(e)}", "error")

    return redirect(f"/autopsy/{case_id}")


# ---------------------------------------------------------------------------
# PEER REVIEWS — Add peer review for autopsy case
# ---------------------------------------------------------------------------
@autopsy_bp.route("/<int:case_id>/peer-review", methods=["POST"])
@login_required
@roles_allowed("Admin", "Doctor")
def add_peer_review(case_id):
    try:
        execute_query(
            """
            INSERT INTO peer_reviews (autopsy_case_id, reviewed_by_doctor_id)
            VALUES (%s, %s)
        """,
            (case_id, request.form.get("reviewed_by_doctor_id")),
        )
        flash("Peer review recorded!", "success")
    except Exception as e:
        flash(f"Error adding peer review: {str(e)}", "error")
    return redirect(f"/autopsy/{case_id}")


# ---------------------------------------------------------------------------
# VOICE DICTATIONS — Upload audio dictation for autopsy
# ---------------------------------------------------------------------------
@autopsy_bp.route("/<int:case_id>/dictations", methods=["POST"])
@login_required
@roles_allowed("Admin", "Doctor")
def upload_dictation(case_id):
    if "audio_file" not in request.files:
        flash("No file selected.", "error")
        return redirect(f"/autopsy/{case_id}")

    file = request.files["audio_file"]
    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(f"/autopsy/{case_id}")

    try:
        filename = secure_filename(file.filename)
        case_dir = os.path.join(
            current_app.config["UPLOADS_DIR"], f"dictation_{case_id}"
        )
        os.makedirs(case_dir, exist_ok=True)
        filepath = os.path.join(case_dir, filename)
        file.save(filepath)

        execute_query(
            """
            INSERT INTO voice_dictations (autopsy_case_id, audio_file_path, transcript_text)
            VALUES (%s, %s, %s)
        """,
            (case_id, filepath, request.form.get("transcript_text", "")),
        )

        flash("Voice dictation uploaded!", "success")
    except Exception as e:
        flash(f"Error uploading dictation: {str(e)}", "error")

    return redirect(f"/autopsy/{case_id}")
