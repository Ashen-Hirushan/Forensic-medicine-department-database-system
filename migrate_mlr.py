import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'forensic_dept_db')
}

migrations = [
    # Add MLR report content columns
    "ALTER TABLE mlr_documents ADD COLUMN history_of_incident TEXT AFTER opinion_encrypted",
    "ALTER TABLE mlr_documents ADD COLUMN examination_findings TEXT AFTER history_of_incident",
    "ALTER TABLE mlr_documents ADD COLUMN conclusions TEXT AFTER examination_findings",
    "ALTER TABLE mlr_documents ADD COLUMN category_of_hurt_opinion VARCHAR(100) AFTER conclusions",
    "ALTER TABLE mlr_documents ADD COLUMN prepared_by_doctor_id INT AFTER category_of_hurt_opinion",
    "ALTER TABLE mlr_documents ADD COLUMN prepared_date DATETIME AFTER prepared_by_doctor_id",
]

def run_migrations():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    for i, sql in enumerate(migrations, 1):
        try:
            cursor.execute(sql)
            conn.commit()
            print(f"  [OK] Migration {i} applied.")
        except mysql.connector.Error as e:
            if e.errno == 1060:
                print(f"  [SKIP] Migration {i}: Column already exists.")
            else:
                print(f"  [ERROR] Migration {i}: {e}")
                conn.rollback()
    
    cursor.close()
    conn.close()
    print("\nMLR migrations complete!")

if __name__ == '__main__':
    print("Running MLR schema migrations...\n")
    run_migrations()
