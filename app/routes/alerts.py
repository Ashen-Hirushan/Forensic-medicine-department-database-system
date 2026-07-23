from flask import Blueprint, jsonify, session, request
from app.services.auth_utils import login_required
from app.services.db import execute_query

alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.route("/", methods=["GET"])
@login_required
def get_alerts():
    user_id = session.get("user_id")
    alerts = execute_query(
        "SELECT * FROM user_alerts WHERE user_id = %s ORDER BY alert_id DESC",
        (user_id,),
    )
    return jsonify(alerts)


@alerts_bp.route("/dismiss", methods=["POST"])
@login_required
def dismiss_alert():
    alert_id = request.form.get("alert_id")
    execute_query(
        "DELETE FROM user_alerts WHERE alert_id = %s AND user_id = %s",
        (alert_id, session.get("user_id")),
    )
    return jsonify({"success": True})
