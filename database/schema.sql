-- Forensic Medical Department Database Schema
-- Based on the 28-table ER Diagram

CREATE DATABASE IF NOT EXISTS forensic_dept_db;
USE forensic_dept_db;

-- 1. access_roles
CREATE TABLE IF NOT EXISTS access_roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    permissions TEXT
);

-- 2. system_users
CREATE TABLE IF NOT EXISTS system_users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    account_locked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (role_id) REFERENCES access_roles(role_id)
);

-- 3. staff_directory
CREATE TABLE IF NOT EXISTS staff_directory (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    full_name VARCHAR(100) NOT NULL,
    designation VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES system_users(user_id)
);

-- 4. medical_officers
CREATE TABLE IF NOT EXISTS medical_officers (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL UNIQUE,
    slmc_reg_no VARCHAR(50) UNIQUE,
    specialization VARCHAR(100),
    FOREIGN KEY (staff_id) REFERENCES staff_directory(staff_id)
);

-- 5. police_divisions
CREATE TABLE IF NOT EXISTS police_divisions (
    station_id INT AUTO_INCREMENT PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL,
    jurisdiction_area VARCHAR(100)
);

-- 6. healthcare_facilities
CREATE TABLE IF NOT EXISTS healthcare_facilities (
    facility_id INT AUTO_INCREMENT PRIMARY KEY,
    facility_name VARCHAR(100) NOT NULL,
    linked_station_id INT,
    FOREIGN KEY (linked_station_id) REFERENCES police_divisions(station_id)
);

-- 7. living_subjects
CREATE TABLE IF NOT EXISTS living_subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    nic_encrypted VARCHAR(255) UNIQUE,
    name_encrypted VARCHAR(255) NOT NULL,
    age INT CHECK (age >= 0 AND age <= 150),
    gender ENUM('Male', 'Female', 'Other'),
    permanent_address TEXT,
    contact_no VARCHAR(20)
);

-- 8. cadavers
CREATE TABLE IF NOT EXISTS cadavers (
    cadaver_id INT AUTO_INCREMENT PRIMARY KEY,
    nic_encrypted VARCHAR(255) UNIQUE,
    name_encrypted VARCHAR(255) NOT NULL,
    estimated_age INT CHECK (estimated_age >= 0 AND estimated_age <= 150),
    gender ENUM('Male', 'Female', 'Other'),
    address_found TEXT,
    death_datetime DATETIME
);

-- 9. clinical_examinations
CREATE TABLE IF NOT EXISTS clinical_examinations (
    case_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    facility_id INT,
    station_id INT,
    assigned_doctor_id INT,
    reference_no VARCHAR(50) UNIQUE NOT NULL,
    incident_date DATETIME,
    admission_date DATETIME,
    examination_date DATETIME,
    report_submission_date DATETIME,
    hospital_bht_no VARCHAR(50),
    FOREIGN KEY (subject_id) REFERENCES living_subjects(subject_id),
    FOREIGN KEY (facility_id) REFERENCES healthcare_facilities(facility_id),
    FOREIGN KEY (station_id) REFERENCES police_divisions(station_id),
    FOREIGN KEY (assigned_doctor_id) REFERENCES medical_officers(doctor_id),
    CONSTRAINT chk_clin_dates CHECK (admission_date >= incident_date AND examination_date >= admission_date AND (report_submission_date IS NULL OR report_submission_date >= examination_date))
);

-- 10. postmortem_investigations
CREATE TABLE IF NOT EXISTS postmortem_investigations (
    case_id INT AUTO_INCREMENT PRIMARY KEY,
    cadaver_id INT NOT NULL,
    station_id INT,
    assigned_doctor_id INT,
    pm_serial_no VARCHAR(50) UNIQUE NOT NULL,
    admission_date DATETIME,
    autopsy_date DATETIME,
    inquest_date DATETIME,
    report_submission_date DATETIME,
    hospital_bht_no VARCHAR(50),
    inquest_ordered_by VARCHAR(100),
    inquest_order_no VARCHAR(50),
    place_of_postmortem VARCHAR(150),
    FOREIGN KEY (cadaver_id) REFERENCES cadavers(cadaver_id),
    FOREIGN KEY (station_id) REFERENCES police_divisions(station_id),
    FOREIGN KEY (assigned_doctor_id) REFERENCES medical_officers(doctor_id),
    CONSTRAINT chk_pm_dates CHECK (autopsy_date >= admission_date AND (report_submission_date IS NULL OR report_submission_date >= autopsy_date))
);

-- 11. mlef_records
CREATE TABLE IF NOT EXISTS mlef_records (
    mlef_id INT AUTO_INCREMENT PRIMARY KEY,
    clinical_case_id INT NOT NULL UNIQUE,
    mlef_number VARCHAR(50) UNIQUE,
    consent_obtained BOOLEAN DEFAULT FALSE,
    injury_details TEXT,
    has_abrasion BOOLEAN DEFAULT FALSE,
    has_contusion BOOLEAN DEFAULT FALSE,
    has_laceration BOOLEAN DEFAULT FALSE,
    has_stab BOOLEAN DEFAULT FALSE,
    has_fracture BOOLEAN DEFAULT FALSE,
    has_burn BOOLEAN DEFAULT FALSE,
    has_bite BOOLEAN DEFAULT FALSE,
    has_dislocation BOOLEAN DEFAULT FALSE,
    has_explosive_inj BOOLEAN DEFAULT FALSE,
    has_gunshot BOOLEAN DEFAULT FALSE,
    has_cut BOOLEAN DEFAULT FALSE,
    has_no_injury BOOLEAN DEFAULT FALSE,
    other_injuries TEXT,
    internal_injuries TEXT,
    weapon_sharp BOOLEAN DEFAULT FALSE,
    weapon_blunt BOOLEAN DEFAULT FALSE,
    weapon_firearm BOOLEAN DEFAULT FALSE,
    weapon_explosive BOOLEAN DEFAULT FALSE,
    weapon_other TEXT,
    category_of_hurt ENUM('Non-grievous', 'Grievous', 'Endangering Life', 'Fatal in ordinary course'),
    is_life_endangering BOOLEAN DEFAULT FALSE,
    under_influence_of_alcohol BOOLEAN DEFAULT FALSE,
    alcohol_smelling BOOLEAN DEFAULT FALSE,
    alcohol_consumed BOOLEAN DEFAULT FALSE,
    drugs_consumed BOOLEAN DEFAULT FALSE,
    drugs_under_influence BOOLEAN DEFAULT FALSE,
    alcohol_drugs_negative BOOLEAN DEFAULT FALSE,
    accompanying_officer_info TEXT,
    sa_history TEXT,
    sa_vaginal_penetration BOOLEAN DEFAULT FALSE,
    sa_anal_penetration BOOLEAN DEFAULT FALSE,
    sa_inter_labial_penetration BOOLEAN DEFAULT FALSE,
    mlef_investigations TEXT,
    mlef_referrals TEXT,
    mlef_other_opinions TEXT,
    FOREIGN KEY (clinical_case_id) REFERENCES clinical_examinations(case_id)
);

-- 12. mlr_documents
CREATE TABLE IF NOT EXISTS mlr_documents (
    mlr_id INT AUTO_INCREMENT PRIMARY KEY,
    clinical_case_id INT NOT NULL UNIQUE,
    report_status ENUM('Pending Exam', 'PMR/MLEF Drafted', 'Dispatched', 'Received by Court'),
    opinion_encrypted TEXT,
    FOREIGN KEY (clinical_case_id) REFERENCES clinical_examinations(case_id)
);

-- 13. clinical_observations
CREATE TABLE IF NOT EXISTS clinical_observations (
    finding_id INT AUTO_INCREMENT PRIMARY KEY,
    clinical_case_id INT NOT NULL,
    findings_text_encrypted TEXT,
    FOREIGN KEY (clinical_case_id) REFERENCES clinical_examinations(case_id)
);

-- 14. pmr_drafts
CREATE TABLE IF NOT EXISTS pmr_drafts (
    pmr_id INT AUTO_INCREMENT PRIMARY KEY,
    autopsy_case_id INT NOT NULL UNIQUE,
    document_url VARCHAR(255),
    draft_status ENUM('Pending Exam', 'PMR/MLEF Drafted', 'Dispatched', 'Received by Court'),
    FOREIGN KEY (autopsy_case_id) REFERENCES postmortem_investigations(case_id)
);

-- 15. death_certificates
CREATE TABLE IF NOT EXISTS death_certificates (
    cod_id INT AUTO_INCREMENT PRIMARY KEY,
    autopsy_case_id INT NOT NULL UNIQUE,
    immediate_cause_encrypted TEXT,
    antecedent_cause_encrypted TEXT,
    contributory_cause_encrypted TEXT,
    is_maternal_death BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (autopsy_case_id) REFERENCES postmortem_investigations(case_id)
);

-- 16. voice_dictations
CREATE TABLE IF NOT EXISTS voice_dictations (
    dictation_id INT AUTO_INCREMENT PRIMARY KEY,
    autopsy_case_id INT NOT NULL,
    audio_file_path VARCHAR(255),
    transcript_text TEXT,
    FOREIGN KEY (autopsy_case_id) REFERENCES postmortem_investigations(case_id)
);

-- EXCLUSIVE ARCS (Shared Dependencies)
-- 17. wound_charts
CREATE TABLE IF NOT EXISTS wound_charts (
    wound_id INT AUTO_INCREMENT PRIMARY KEY,
    clinical_case_id INT,
    autopsy_case_id INT,
    wound_type VARCHAR(100),
    weapon_suspected VARCHAR(100),
    anatomical_location VARCHAR(100),
    FOREIGN KEY (clinical_case_id) REFERENCES clinical_examinations(case_id),
    FOREIGN KEY (autopsy_case_id) REFERENCES postmortem_investigations(case_id),
    CONSTRAINT chk_wound_arc CHECK (
        (clinical_case_id IS NOT NULL AND autopsy_case_id IS NULL) OR 
        (clinical_case_id IS NULL AND autopsy_case_id IS NOT NULL)
    )
);

-- 18. test_requests
CREATE TABLE IF NOT EXISTS test_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    clinical_case_id INT,
    autopsy_case_id INT,
    request_status ENUM('Pending', 'Completed') NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (clinical_case_id) REFERENCES clinical_examinations(case_id),
    FOREIGN KEY (autopsy_case_id) REFERENCES postmortem_investigations(case_id),
    CONSTRAINT chk_testreq_arc CHECK (
        (clinical_case_id IS NOT NULL AND autopsy_case_id IS NULL) OR 
        (clinical_case_id IS NULL AND autopsy_case_id IS NOT NULL)
    )
);

-- 19. test_results
CREATE TABLE IF NOT EXISTS test_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    uploaded_by INT NOT NULL,
    file_pointer VARCHAR(255),
    FOREIGN KEY (request_id) REFERENCES test_requests(request_id),
    FOREIGN KEY (uploaded_by) REFERENCES system_users(user_id)
);

-- 20. consultation_referrals
CREATE TABLE IF NOT EXISTS consultation_referrals (
    referral_id INT AUTO_INCREMENT PRIMARY KEY,
    clinical_case_id INT NOT NULL,
    referred_to_specialty VARCHAR(100),
    referral_status VARCHAR(50),
    FOREIGN KEY (clinical_case_id) REFERENCES clinical_examinations(case_id)
);

-- 21. peer_reviews
CREATE TABLE IF NOT EXISTS peer_reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    clinical_case_id INT,
    autopsy_case_id INT,
    reviewed_by_doctor_id INT NOT NULL,
    FOREIGN KEY (clinical_case_id) REFERENCES clinical_examinations(case_id),
    FOREIGN KEY (autopsy_case_id) REFERENCES postmortem_investigations(case_id),
    FOREIGN KEY (reviewed_by_doctor_id) REFERENCES medical_officers(doctor_id),
    CONSTRAINT chk_peer_arc CHECK (
        (clinical_case_id IS NOT NULL AND autopsy_case_id IS NULL) OR 
        (clinical_case_id IS NULL AND autopsy_case_id IS NOT NULL)
    )
);

-- 22. digital_assets
CREATE TABLE IF NOT EXISTS digital_assets (
    asset_id INT AUTO_INCREMENT PRIMARY KEY,
    clinical_case_id INT,
    autopsy_case_id INT,
    uploaded_by INT NOT NULL,
    asset_type VARCHAR(50),
    FOREIGN KEY (clinical_case_id) REFERENCES clinical_examinations(case_id),
    FOREIGN KEY (autopsy_case_id) REFERENCES postmortem_investigations(case_id),
    FOREIGN KEY (uploaded_by) REFERENCES system_users(user_id),
    CONSTRAINT chk_asset_arc CHECK (
        (clinical_case_id IS NOT NULL AND autopsy_case_id IS NULL) OR 
        (clinical_case_id IS NULL AND autopsy_case_id IS NOT NULL)
    )
);

-- 23. asset_revisions
CREATE TABLE IF NOT EXISTS asset_revisions (
    revision_id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    uploaded_by INT NOT NULL,
    file_pointer VARCHAR(255),
    FOREIGN KEY (asset_id) REFERENCES digital_assets(asset_id),
    FOREIGN KEY (uploaded_by) REFERENCES system_users(user_id)
);

-- 24. court_submissions
CREATE TABLE IF NOT EXISTS court_submissions (
    submission_id INT AUTO_INCREMENT PRIMARY KEY,
    clinical_case_id INT,
    autopsy_case_id INT,
    court_name VARCHAR(100),
    trial_date DATETIME,
    receipt_scan_path VARCHAR(255),
    FOREIGN KEY (clinical_case_id) REFERENCES clinical_examinations(case_id),
    FOREIGN KEY (autopsy_case_id) REFERENCES postmortem_investigations(case_id),
    CONSTRAINT chk_court_arc CHECK (
        (clinical_case_id IS NOT NULL AND autopsy_case_id IS NULL) OR 
        (clinical_case_id IS NULL AND autopsy_case_id IS NOT NULL)
    )
);

-- 25. physical_evidence
CREATE TABLE IF NOT EXISTS physical_evidence (
    evidence_id INT AUTO_INCREMENT PRIMARY KEY,
    clinical_case_id INT,
    autopsy_case_id INT,
    description TEXT,
    FOREIGN KEY (clinical_case_id) REFERENCES clinical_examinations(case_id),
    FOREIGN KEY (autopsy_case_id) REFERENCES postmortem_investigations(case_id),
    CONSTRAINT chk_evid_arc CHECK (
        (clinical_case_id IS NOT NULL AND autopsy_case_id IS NULL) OR 
        (clinical_case_id IS NULL AND autopsy_case_id IS NOT NULL)
    )
);

-- 26. evidence_custody_logs
CREATE TABLE IF NOT EXISTS evidence_custody_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    evidence_id INT NOT NULL,
    from_user_id INT,
    to_user_id INT NOT NULL,
    transfer_datetime DATETIME NOT NULL,
    location VARCHAR(100) NOT NULL,
    FOREIGN KEY (evidence_id) REFERENCES physical_evidence(evidence_id),
    FOREIGN KEY (from_user_id) REFERENCES system_users(user_id),
    FOREIGN KEY (to_user_id) REFERENCES system_users(user_id)
);

-- 27. user_alerts
CREATE TABLE IF NOT EXISTS user_alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES system_users(user_id)
);

-- 28. audit_trails
CREATE TABLE IF NOT EXISTS audit_trails (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action_type VARCHAR(50),
    table_affected VARCHAR(50),
    action_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES system_users(user_id)
);

-- Indexes for performance Optimization
CREATE INDEX idx_clin_ref ON clinical_examinations(reference_no);
CREATE INDEX idx_pm_serial ON postmortem_investigations(pm_serial_no);
CREATE INDEX idx_liv_nic ON living_subjects(nic_encrypted);
CREATE INDEX idx_cad_nic ON cadavers(nic_encrypted);
CREATE INDEX idx_court_sub ON court_submissions(trial_date);

-- Views for Reports
CREATE OR REPLACE VIEW view_daily_clinical_cases AS
SELECT case_id, reference_no, admission_date, assigned_doctor_id 
FROM clinical_examinations 
WHERE DATE(admission_date) = CURDATE();

CREATE OR REPLACE VIEW view_pending_court_reports AS
SELECT submission_id, court_name, trial_date 
FROM court_submissions 
WHERE receipt_scan_path IS NULL AND trial_date >= CURDATE();
