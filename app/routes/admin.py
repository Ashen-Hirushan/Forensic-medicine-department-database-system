from flask import Blueprint, render_template, request
from app.services.auth_utils import login_required, roles_allowed
from app.services.db import execute_query

admin_bp = Blueprint('admin', __name__)

# ---------------------------------------------------------------------------
# AUDIT LOG — View system audit trails
# ---------------------------------------------------------------------------
@admin_bp.route('/audit-log', methods=['GET'])
@login_required
@roles_allowed('Admin')
def audit_log():
    table_filter = request.args.get('table', '')
    user_filter = request.args.get('user_id', '')
    
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
    tables = execute_query("SELECT DISTINCT table_affected FROM audit_trails ORDER BY table_affected")
    
    # Get users for filter dropdown
    users = execute_query("SELECT user_id, username FROM system_users ORDER BY username")
    
    return render_template('admin/audit_log.html', logs=logs, tables=tables, users=users,
                           table_filter=table_filter, user_filter=user_filter)
