from flask import Flask
from flask_session import Session
from app.config import Config

# Initialize Flask Extensions
sess = Session()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    sess.init_app(app)

    # Initialize configuration (like creating folders)
    Config.init_app()

    # Initialize Database Connection Pool
    from app.services import db

    db.init_app(app)

    # Register Blueprints (We'll import them locally to avoid circular imports later)
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.clinical import clinical_bp
    from app.routes.autopsy import autopsy_bp
    from app.routes.evidence import evidence_bp
    from app.routes.court import court_bp
    from app.routes.alerts import alerts_bp
    from app.routes.reports import reports_bp
    from app.routes.admin import admin_bp
    from app.routes.patients import patients_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clinical_bp, url_prefix="/clinical")
    app.register_blueprint(autopsy_bp, url_prefix="/autopsy")
    app.register_blueprint(evidence_bp, url_prefix="/evidence")
    app.register_blueprint(court_bp, url_prefix="/court")
    app.register_blueprint(alerts_bp, url_prefix="/alerts")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(patients_bp, url_prefix="/patients")

    # Redirect root to login
    from flask import redirect, render_template

    @app.route("/")
    def index():
        return redirect("/login")

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    return app
