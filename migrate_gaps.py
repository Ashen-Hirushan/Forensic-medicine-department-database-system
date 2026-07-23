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
    # Phase 1: Add case_category and referral_source to clinical_examinations
    """ALTER TABLE clinical_examinations 
       ADD COLUMN case_category ENUM(
           'Trauma', 'Domestic Abuse', 'Sexual Abuse', 'Child Abuse', 
           'Detainee', 'Drug Addict', 'Age Estimation', 'DNA Sample', 'Other'
       ) DEFAULT NULL AFTER hospital_bht_no""",

    """ALTER TABLE clinical_examinations 
       ADD COLUMN referral_source ENUM(
           'Ward', 'Police Station', 'AG Office', 'Human Rights Commission', 
           'Court Order', 'Other'
       ) DEFAULT NULL AFTER case_category""",

    # Phase 2: Add manner_of_death to postmortem_investigations
    """ALTER TABLE postmortem_investigations 
       ADD COLUMN manner_of_death ENUM(
           'Natural', 'Accidental', 'Suicidal', 'Homicidal', 'Undetermined'
       ) DEFAULT NULL AFTER place_of_postmortem""",
]

def run_migrations():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    for i, sql in enumerate(migrations, 1):
        try:
            cursor.execute(sql)
            conn.commit()
            print(f"  [OK] Migration {i} applied successfully.")
        except mysql.connector.Error as e:
            if e.errno == 1060:  # Duplicate column
                print(f"  [SKIP] Migration {i}: Column already exists.")
            else:
                print(f"  [ERROR] Migration {i}: {e}")
                conn.rollback()
    
    cursor.close()
    conn.close()
    print("\nAll migrations complete!")

if __name__ == '__main__':
    print("Running schema migrations...\n")
    run_migrations()
