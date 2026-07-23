import os
import mysql.connector
from mysql.connector import Error
import bcrypt
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file (if exists)
load_dotenv()

# Database connection configuration
db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'forensic_dept_db')
}

def seed_database():
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print("Connected to MySQL database")
            cursor = conn.cursor()

            # Disable foreign key checks to safely truncate tables
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            
            # Truncate tables to ensure idempotency
            tables = [
                'audit_trails', 'user_alerts', 'evidence_custody_logs', 'physical_evidence',
                'court_submissions', 'asset_revisions', 'digital_assets', 'peer_reviews',
                'consultation_referrals', 'test_results', 'test_requests', 'wound_charts',
                'voice_dictations', 'death_certificates', 'pmr_drafts', 'clinical_observations',
                'mlr_documents', 'mlef_records', 'postmortem_investigations', 'clinical_examinations',
                'cadavers', 'living_subjects', 'healthcare_facilities', 'police_divisions',
                'medical_officers', 'staff_directory', 'system_users', 'access_roles'
            ]
            for table in tables:
                cursor.execute(f"TRUNCATE TABLE {table};")
            
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

            # 1. Seed access_roles
            roles_data = [
                (1, 'Admin', 'All Permissions'),
                (2, 'Doctor', 'Examine, PMR, MLEF, Order Tests'),
                (3, 'Clerk', 'Register, Dispatch, Search'),
                (4, 'Lab Staff', 'Update Test Results')
            ]
            cursor.executemany("INSERT INTO access_roles (role_id, role_name, permissions) VALUES (%s, %s, %s)", roles_data)

            # 2. Seed system_users (Hash password)
            salt = bcrypt.gensalt()
            hashed_pwd = bcrypt.hashpw(b"securepass123", salt).decode('utf-8')
            users_data = [
                (1, 1, 'admin1', hashed_pwd, False),
                (2, 2, 'dr_chathula', hashed_pwd, False),
                (3, 2, 'dr_perera', hashed_pwd, False),
                (4, 3, 'clerk_nimal', hashed_pwd, False),
                (5, 4, 'lab_kamal', hashed_pwd, False),
                (6, 1, 'admin2', hashed_pwd, False)
            ]
            cursor.executemany("INSERT INTO system_users (user_id, role_id, username, password_hash, account_locked) VALUES (%s, %s, %s, %s, %s)", users_data)

            # 3. Seed staff_directory
            staff_data = [
                (1, 1, 'Admin Officer 1', 'System Administrator'),
                (2, 2, 'Dr. Chathula Wickramasinghe', 'Consultant JMO'),
                (3, 3, 'Dr. Suneth Perera', 'Assistant JMO'),
                (4, 4, 'Nimal Fernando', 'Chief Clerk'),
                (5, 5, 'Kamal Silva', 'Senior Lab Technician'),
                (6, 6, 'Admin Officer 2', 'System Administrator')
            ]
            cursor.executemany("INSERT INTO staff_directory (staff_id, user_id, full_name, designation) VALUES (%s, %s, %s, %s)", staff_data)

            # 4. Seed medical_officers
            mo_data = [
                (1, 2, 'SLMC-10023', 'Forensic Medicine'),
                (2, 3, 'SLMC-12045', 'Forensic Pathology')
            ]
            cursor.executemany("INSERT INTO medical_officers (doctor_id, staff_id, slmc_reg_no, specialization) VALUES (%s, %s, %s, %s)", mo_data)

            # 5. Seed police_divisions
            police_data = [
                (1, 'Peradeniya Police Station', 'Peradeniya City Limits'),
                (2, 'Kandy Central Police', 'Kandy Metro')
            ]
            cursor.executemany("INSERT INTO police_divisions (station_id, station_name, jurisdiction_area) VALUES (%s, %s, %s)", police_data)

            # 6. Seed healthcare_facilities
            health_data = [
                (1, 'Teaching Hospital Peradeniya', 1),
                (2, 'Kandy General Hospital', 2)
            ]
            cursor.executemany("INSERT INTO healthcare_facilities (facility_id, facility_name, linked_station_id) VALUES (%s, %s, %s)", health_data)

            # 7. Seed living_subjects (Clinical Patients)
            living_data = [
                (1, 'ENC-901123456V', 'ENC-Ruwan Kumara', 34, 'Male', '12 Temple Rd, Kandy', '0771234567'),
                (2, 'ENC-199578290123', 'ENC-Sithmi Perera', 29, 'Female', '45 Main St, Peradeniya', '0719876543')
            ]
            cursor.executemany("INSERT INTO living_subjects (subject_id, nic_encrypted, name_encrypted, age, gender, permanent_address, contact_no) VALUES (%s, %s, %s, %s, %s, %s, %s)", living_data)

            # 8. Seed cadavers (Autopsy Patients)
            cadaver_data = [
                (1, 'ENC-651234567V', 'ENC-Unknown Male', 60, 'Male', 'Found near Peradeniya Station', '2024-05-10 06:30:00')
            ]
            cursor.executemany("INSERT INTO cadavers (cadaver_id, nic_encrypted, name_encrypted, estimated_age, gender, address_found, death_datetime) VALUES (%s, %s, %s, %s, %s, %s, %s)", cadaver_data)

            # 9. Seed clinical_examinations
            clinical_data = [
                (1, 1, 1, 1, 1, 'CW/CL/24-001', '2024-05-12 14:00:00', '2024-05-12 15:30:00', '2024-05-12 16:00:00', '2024-05-15 10:00:00', 'BHT-88123'),
                (2, 2, 2, 2, 2, 'CW/CL/24-002', '2024-05-14 09:00:00', '2024-05-14 10:15:00', '2024-05-14 11:00:00', None, 'BHT-99012')
            ]
            cursor.executemany("INSERT INTO clinical_examinations (case_id, subject_id, facility_id, station_id, assigned_doctor_id, reference_no, incident_date, admission_date, examination_date, report_submission_date, hospital_bht_no) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", clinical_data)

            # 10. Seed postmortem_investigations
            pm_data = [
                (1, 1, 1, 1, 'CW/PM/24-001', '2024-05-10 08:00:00', '2024-05-11 09:00:00', '2024-05-10 14:00:00', '2024-05-20 10:00:00', 'BHT-NONE', 'Inquirer into Sudden Deaths', 'ISD/24/055', 'TH Peradeniya Mortuary')
            ]
            cursor.executemany("INSERT INTO postmortem_investigations (case_id, cadaver_id, station_id, assigned_doctor_id, pm_serial_no, admission_date, autopsy_date, inquest_date, report_submission_date, hospital_bht_no, inquest_ordered_by, inquest_order_no, place_of_postmortem) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", pm_data)

            # 11. Seed mlef_records
            mlef_data = [
                (1, 1, 'MLEF-1001', True, 'Patient involved in RTA. Laceration on left thigh.', False, True, True, False, False, False, 'Non-grievous', False, 'PC 54321 Bandara'),
                (2, 2, 'MLEF-1002', True, 'Assault victim. Multiple contusions.', False, True, False, False, False, False, 'Non-grievous', False, 'Sgt 12345 Silva')
            ]
            cursor.executemany("INSERT INTO mlef_records (mlef_id, clinical_case_id, mlef_number, consent_obtained, injury_details, has_abrasion, has_contusion, has_laceration, has_stab, has_fracture, has_burn, category_of_hurt, under_influence_of_alcohol, accompanying_officer_info) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", mlef_data)

            # 12. Seed death_certificates
            cod_data = [
                (1, 1, 'ENC-Myocardial Infarction', 'ENC-Coronary Artery Disease', 'ENC-Hypertension', False)
            ]
            cursor.executemany("INSERT INTO death_certificates (cod_id, autopsy_case_id, immediate_cause_encrypted, antecedent_cause_encrypted, contributory_cause_encrypted, is_maternal_death) VALUES (%s, %s, %s, %s, %s, %s)", cod_data)

            # 13. Seed wound_charts (Exclusive Arc implementation)
            wound_data = [
                (1, 1, None, 'Laceration', 'Blunt object (Road surface)', 'Left Thigh'),
                (2, None, 1, 'Abrasion', 'Unknown', 'Right Forearm')
            ]
            cursor.executemany("INSERT INTO wound_charts (wound_id, clinical_case_id, autopsy_case_id, wound_type, weapon_suspected, anatomical_location) VALUES (%s, %s, %s, %s, %s, %s)", wound_data)

            # 14. Seed physical_evidence
            evidence_data = [
                (1, None, 1, 'Blood sample for Toxicology')
            ]
            cursor.executemany("INSERT INTO physical_evidence (evidence_id, clinical_case_id, autopsy_case_id, description) VALUES (%s, %s, %s, %s)", evidence_data)

            # 15. Seed evidence_custody_logs
            custody_data = [
                (1, 1, 2, 5, '2024-05-11 10:30:00', 'Toxicology Lab Fridge A')
            ]
            cursor.executemany("INSERT INTO evidence_custody_logs (log_id, evidence_id, from_user_id, to_user_id, transfer_datetime, location) VALUES (%s, %s, %s, %s, %s, %s)", custody_data)

            # 16. Seed test_requests & test_results
            test_req_data = [
                (1, None, 1, 'Completed')
            ]
            cursor.executemany("INSERT INTO test_requests (request_id, clinical_case_id, autopsy_case_id, request_status) VALUES (%s, %s, %s, %s)", test_req_data)

            test_res_data = [
                (1, 1, 5, 'uploads/results/tox_res_001.pdf')
            ]
            cursor.executemany("INSERT INTO test_results (result_id, request_id, uploaded_by, file_pointer) VALUES (%s, %s, %s, %s)", test_res_data)

            # Commit the transaction
            conn.commit()
            print("Successfully inserted mock data into all tables!")

    except Error as e:
        print(f"Error while connecting to MySQL or executing queries: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection is closed.")

if __name__ == "__main__":
    seed_database()
