from flask import Blueprint, render_template, request, redirect, flash, session
from app.services.auth_utils import login_required, roles_allowed
from app.services.db import execute_query

admin_bp = Blueprint("admin", __name__)


# ---------------------------------------------------------------------------
# AUDIT LOG — View system audit trails
# ---------------------------------------------------------------------------
@admin_bp.route("/audit-log", methods=["GET"])
@login_required
@roles_allowed("Admin")
def audit_log():
    table_filter = request.args.get("table", "")
    user_filter = request.args.get("user_id", "")

    query = """
        SELECT a.audit_id, a.action_type, a.table_affected, a.action_timestamp,
               su.username
        FROM audit_trails a
        JOIN system_users su ON a.user_id = su.user_id
        WHERE 1=1
    """
    params = []

    if table_filter:
        query += " AND a.table_affected = %s"
        params.append(table_filter)
    if user_filter:
        query += " AND a.user_id = %s"
        params.append(int(user_filter))

    query += " ORDER BY a.action_timestamp DESC LIMIT 100"

    logs = execute_query(query, tuple(params))

    # Get unique tables for filter dropdown
    tables = execute_query(
        "SELECT DISTINCT table_affected FROM audit_trails ORDER BY table_affected"
    )

    # Get users for filter dropdown
    users = execute_query(
        "SELECT user_id, username FROM system_users ORDER BY username"
    )

    return render_template(
        "admin/audit_log.html",
        logs=logs,
        tables=tables,
        users=users,
        table_filter=table_filter,
        user_filter=user_filter,
    )


# ---------------------------------------------------------------------------
# USER MANAGEMENT — View system users & delete profile (Admin Only)
# ---------------------------------------------------------------------------
@admin_bp.route("/users", methods=["GET"])
@login_required
@roles_allowed("Admin")
def manage_users():
    users = execute_query("""
        SELECT u.user_id, u.username, u.profile_picture, u.account_locked,
               r.role_name, s.staff_id, s.full_name, s.designation
        FROM system_users u
        JOIN access_roles r ON u.role_id = r.role_id
        LEFT JOIN staff_directory s ON u.user_id = s.user_id
        ORDER BY u.user_id ASC
    """)
    return render_template("admin/users.html", users=users)


@admin_bp.route("/users/delete/<int:target_user_id>", methods=["POST"])
@login_required
@roles_allowed("Admin")
def delete_user_profile(target_user_id):
    current_admin_id = session.get("user_id")

    # Prevent self-deletion of active admin session
    if target_user_id == current_admin_id:
        flash("You cannot delete your own active Admin profile.", "error")
        return redirect("/admin/users")

    # Check if target user exists
    target_user = execute_query(
        "SELECT user_id, username FROM system_users WHERE user_id = %s",
        (target_user_id,),
        fetch_all=False,
    )

    if not target_user:
        flash("User profile not found.", "error")
        return redirect("/admin/users")

    username = target_user["username"]

    try:
        # Disable foreign key checks to allow deletion without failing on historical dependencies
        execute_query("SET FOREIGN_KEY_CHECKS = 0;")

        # Delete dependent user_alerts first
        execute_query("DELETE FROM user_alerts WHERE user_id = %s", (target_user_id,))

        # Check staff_directory and medical_officers
        staff = execute_query(
            "SELECT staff_id FROM staff_directory WHERE user_id = %s",
            (target_user_id,),
            fetch_all=False,
        )
        if staff and staff.get("staff_id"):
            staff_id = staff["staff_id"]
            execute_query(
                "DELETE FROM medical_officers WHERE staff_id = %s", (staff_id,)
            )
            execute_query(
                "DELETE FROM staff_directory WHERE staff_id = %s", (staff_id,)
            )

        # Delete the main user account
        execute_query("DELETE FROM system_users WHERE user_id = %s", (target_user_id,))

        # Log deletion in audit trails
        execute_query(
            "INSERT INTO audit_trails (user_id, action_type, table_affected) VALUES (%s, %s, %s)",
            (current_admin_id, "DELETE", "system_users"),
        )

        # Re-enable foreign key checks
        execute_query("SET FOREIGN_KEY_CHECKS = 1;")

        flash(f"User profile '{username}' has been successfully deleted.", "success")
    except Exception as e:
        execute_query(
            "SET FOREIGN_KEY_CHECKS = 1;"
        )  # Ensure it gets turned back on in case of error
        flash(f"Failed to delete user profile: {str(e)}", "error")

    return redirect("/admin/users")
