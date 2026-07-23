from flask import Blueprint, render_template, request, redirect, flash, session
from app.services.db import execute_query
from app.routes.auth import login_required

patients_bp = Blueprint("patients", __name__, url_prefix="/patients")


@patients_bp.route("/")
@login_required
def list_patients():
    query = """
        SELECT subject_id, nic_encrypted, name_encrypted, age, gender, contact_no, created_at
        FROM living_subjects
        ORDER BY created_at DESC
    """
    patients = execute_query(query)
    return render_template("patients/list.html", patients=patients)


@patients_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_patient():
    if request.method == "POST":
        nic = request.form.get("nic", "").strip()
        name = request.form.get("name", "").strip()
        age = request.form.get("age")
        gender = request.form.get("gender")
        address = request.form.get("address", "").strip()
        contact = request.form.get("contact", "").strip()

        if not name or not nic:
            flash("Name and NIC are required fields.", "error")
            return redirect("/patients/new")

        try:
            # Check if patient exists
            existing = execute_query(
                "SELECT subject_id FROM living_subjects WHERE nic_encrypted = %s",
                (nic,),
                fetch_all=False,
            )
            if existing:
                flash("Patient with this NIC already exists.", "error")
                return redirect("/patients/new")

            execute_query(
                """
                INSERT INTO living_subjects (nic_encrypted, name_encrypted, age, gender, permanent_address, contact_no)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (nic, name, age if age else None, gender, address, contact),
            )

            flash("Patient registered successfully.", "success")
            return redirect("/patients")
        except Exception as e:
            flash(f"Error registering patient: {e}", "error")
            return redirect("/patients/new")

    return render_template("patients/new.html")
