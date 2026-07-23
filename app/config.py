import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # Flask secret key for sessions
    SECRET_KEY = os.environ.get("SECRET_KEY", "default-dev-secret-key-change-in-prod")
    TEMPLATES_AUTO_RELOAD = True

    # Database Configuration
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "forensic_dept_db")

    # Session Configuration (using filesystem to avoid requiring Redis for now)
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
    SESSION_FILE_DIR = os.path.join(
        os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
        "flask_session_data",
    )

    # Upload Folders Paths
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
    COURT_RECEIPTS_DIR = os.path.join(UPLOADS_DIR, "court_receipts")
    CRIME_SCENES_DIR = os.path.join(UPLOADS_DIR, "crime_scenes")
    CONSENT_SCANS_DIR = os.path.join(UPLOADS_DIR, "consent_scans")
    PROFILES_DIR = os.path.join(BASE_DIR, "app", "static", "uploads", "profiles")

    @classmethod
    def init_app(cls):
        # Create upload directories if they don't exist
        os.makedirs(cls.COURT_RECEIPTS_DIR, exist_ok=True)
        os.makedirs(cls.CRIME_SCENES_DIR, exist_ok=True)
        os.makedirs(cls.CONSENT_SCANS_DIR, exist_ok=True)
        os.makedirs(cls.PROFILES_DIR, exist_ok=True)
