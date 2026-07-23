from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.auth_utils import login_required, roles_allowed
from app.services.db import execute_query, get_db

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/daily", methods=["GET"])
@login_required
def daily_report():
    cases = execute_query("SELECT * FROM view_daily_clinical_cases")
    return render_template("reports/daily.html", cases=cases)


@reports_bp.route("/pending", methods=["GET"])
@login_required
def pending_report():
    reports = execute_query("SELECT * FROM view_pending_court_reports")
    return render_template("reports/pending.html", reports=reports)


@reports_bp.route("/mlef-register", methods=["GET"])
@login_required
def mlef_register():
    search = request.args.get("search", "")

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
    return render_template("reports/mlef_register.html", records=records, search=search)


@reports_bp.route("/mlef-register/delete/<int:case_id>", methods=["POST"])
@login_required
@roles_allowed("Admin")
def delete_mlef(case_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM evidence_custody_logs WHERE evidence_id IN (SELECT evidence_id FROM physical_evidence WHERE clinical_case_id = %s)",
            (case_id,),
        )
        cursor.execute(
            "DELETE FROM physical_evidence WHERE clinical_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM asset_revisions WHERE asset_id IN (SELECT asset_id FROM digital_assets WHERE clinical_case_id = %s)",
            (case_id,),
        )
        cursor.execute(
            "DELETE FROM digital_assets WHERE clinical_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM test_results WHERE request_id IN (SELECT request_id FROM test_requests WHERE clinical_case_id = %s)",
            (case_id,),
        )
        cursor.execute(
            "DELETE FROM test_requests WHERE clinical_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM wound_charts WHERE clinical_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM peer_reviews WHERE clinical_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM court_submissions WHERE clinical_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM consultation_referrals WHERE clinical_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM clinical_observations WHERE clinical_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM mlr_documents WHERE clinical_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM mlef_records WHERE clinical_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM clinical_examinations WHERE case_id = %s", (case_id,)
        )
        conn.commit()
        flash("MLEF Case and all associated records deleted successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Failed to delete case: {str(e)}", "danger")
    finally:
        cursor.close()
    return redirect(url_for("reports.mlef_register"))


@reports_bp.route("/pm-register", methods=["GET"])
@login_required
def pm_register():
    search = request.args.get("search", "")

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
    return render_template("reports/pm_register.html", records=records, search=search)


@reports_bp.route("/pm-register/delete/<int:case_id>", methods=["POST"])
@login_required
@roles_allowed("Admin")
def delete_pm(case_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM evidence_custody_logs WHERE evidence_id IN (SELECT evidence_id FROM physical_evidence WHERE autopsy_case_id = %s)",
            (case_id,),
        )
        cursor.execute(
            "DELETE FROM physical_evidence WHERE autopsy_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM asset_revisions WHERE asset_id IN (SELECT asset_id FROM digital_assets WHERE autopsy_case_id = %s)",
            (case_id,),
        )
        cursor.execute(
            "DELETE FROM digital_assets WHERE autopsy_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM test_results WHERE request_id IN (SELECT request_id FROM test_requests WHERE autopsy_case_id = %s)",
            (case_id,),
        )
        cursor.execute(
            "DELETE FROM test_requests WHERE autopsy_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM wound_charts WHERE autopsy_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM peer_reviews WHERE autopsy_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM court_submissions WHERE autopsy_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM voice_dictations WHERE autopsy_case_id = %s", (case_id,)
        )
        cursor.execute(
            "DELETE FROM death_certificates WHERE autopsy_case_id = %s", (case_id,)
        )
        cursor.execute("DELETE FROM pmr_drafts WHERE autopsy_case_id = %s", (case_id,))
        cursor.execute(
            "DELETE FROM postmortem_investigations WHERE case_id = %s", (case_id,)
        )
        conn.commit()
        flash("PM Case and all associated records deleted successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Failed to delete case: {str(e)}", "danger")
    finally:
        cursor.close()
    return redirect(url_for("reports.pm_register"))


@reports_bp.route("/mlr/<int:case_id>/print", methods=["GET"])
@login_required
def print_mlr(case_id):
    case = execute_query(
        """
        SELECT ce.*, ls.name_encrypted, ls.nic_encrypted, ls.age, ls.gender
        FROM clinical_examinations ce
        JOIN living_subjects ls ON ce.subject_id = ls.subject_id
        WHERE ce.case_id = %s
    """,
        (case_id,),
        fetch_all=False,
    )

    mlef = execute_query(
        "SELECT * FROM mlef_records WHERE clinical_case_id = %s",
        (case_id,),
        fetch_all=False,
    )
    mlr = execute_query(
        "SELECT * FROM mlr_documents WHERE clinical_case_id = %s",
        (case_id,),
        fetch_all=False,
    )
    wounds = execute_query(
        "SELECT * FROM wound_charts WHERE clinical_case_id = %s", (case_id,)
    )
    observations = execute_query(
        "SELECT * FROM clinical_observations WHERE clinical_case_id = %s", (case_id,)
    )

    return render_template(
        "reports/print_mlr.html",
        case=case,
        mlef=mlef,
        mlr=mlr,
        wounds=wounds,
        observations=observations,
    )


@reports_bp.route("/mlef/<int:case_id>/print", methods=["GET"])
@login_required
def print_mlef(case_id):
    case = execute_query(
        """
        SELECT ce.*, ls.name_encrypted, ls.nic_encrypted, ls.age, ls.gender
        FROM clinical_examinations ce
        JOIN living_subjects ls ON ce.subject_id = ls.subject_id
        WHERE ce.case_id = %s
    """,
        (case_id,),
        fetch_all=False,
    )

    mlef = execute_query(
        "SELECT * FROM mlef_records WHERE clinical_case_id = %s",
        (case_id,),
        fetch_all=False,
    )

    return render_template("reports/print_mlef.html", case=case, mlef=mlef)


@reports_bp.route("/pmr/<int:case_id>/print", methods=["GET"])
@login_required
def print_pmr(case_id):
    case = execute_query(
        """
        SELECT pi.*, c.name_encrypted, c.nic_encrypted, c.estimated_age, c.gender
        FROM postmortem_investigations pi
        JOIN cadavers c ON pi.cadaver_id = c.cadaver_id
        WHERE pi.case_id = %s
    """,
        (case_id,),
        fetch_all=False,
    )

    pmr = execute_query(
        "SELECT * FROM pmr_drafts WHERE autopsy_case_id = %s",
        (case_id,),
        fetch_all=False,
    )
    cod = execute_query(
        "SELECT * FROM death_certificates WHERE autopsy_case_id = %s",
        (case_id,),
        fetch_all=False,
    )

    return render_template("reports/print_pmr.html", case=case, pmr=pmr, cod=cod)
