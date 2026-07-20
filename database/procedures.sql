-- Forensic Medical Department Database Stored Procedures
-- These procedures encapsulate complex business logic and ensure transactional integrity.

USE forensic_dept_db;

DELIMITER //

-- ==============================================================================
-- 1. sp_register_clinical_case
-- Registers a living subject and their associated clinical examination case.
-- ==============================================================================
CREATE PROCEDURE sp_register_clinical_case (
    IN p_nic VARCHAR(255),
    IN p_name VARCHAR(255),
    IN p_age INT,
    IN p_gender ENUM('Male', 'Female', 'Other'),
    IN p_address TEXT,
    IN p_contact VARCHAR(20),
    IN p_facility_id INT,
    IN p_station_id INT,
    IN p_assigned_doctor_id INT,
    IN p_reference_no VARCHAR(50),
    IN p_incident_date DATETIME,
    IN p_admission_date DATETIME,
    IN p_hospital_bht_no VARCHAR(50)
)
BEGIN
    DECLARE v_subject_id INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Check if patient exists
    SELECT subject_id INTO v_subject_id FROM living_subjects WHERE nic_encrypted = p_nic LIMIT 1;
    
    -- If not, insert new patient
    IF v_subject_id IS NULL THEN
        INSERT INTO living_subjects (nic_encrypted, name_encrypted, age, gender, permanent_address, contact_no)
        VALUES (p_nic, p_name, p_age, p_gender, p_address, p_contact);
        SET v_subject_id = LAST_INSERT_ID();
    END IF;

    -- Insert the new clinical case
    INSERT INTO clinical_examinations (
        subject_id, facility_id, station_id, assigned_doctor_id, 
        reference_no, incident_date, admission_date, hospital_bht_no
    ) VALUES (
        v_subject_id, p_facility_id, p_station_id, p_assigned_doctor_id, 
        p_reference_no, p_incident_date, p_admission_date, p_hospital_bht_no
    );
    
    -- Create an initial blank MLEF record linked to this case
    INSERT INTO mlef_records (clinical_case_id) VALUES (LAST_INSERT_ID());

    COMMIT;
END //


-- ==============================================================================
-- 2. sp_register_autopsy_case
-- Registers a cadaver and their associated postmortem investigation case.
-- ==============================================================================
CREATE PROCEDURE sp_register_autopsy_case (
    IN p_nic VARCHAR(255),
    IN p_name VARCHAR(255),
    IN p_estimated_age INT,
    IN p_gender ENUM('Male', 'Female', 'Other'),
    IN p_address_found TEXT,
    IN p_death_datetime DATETIME,
    IN p_station_id INT,
    IN p_assigned_doctor_id INT,
    IN p_pm_serial_no VARCHAR(50),
    IN p_admission_date DATETIME,
    IN p_hospital_bht_no VARCHAR(50),
    IN p_inquest_ordered_by VARCHAR(100),
    IN p_inquest_order_no VARCHAR(50),
    IN p_place_of_postmortem VARCHAR(150)
)
BEGIN
    DECLARE v_cadaver_id INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Check if cadaver exists
    SELECT cadaver_id INTO v_cadaver_id FROM cadavers WHERE nic_encrypted = p_nic LIMIT 1;
    
    -- If not, insert new cadaver
    IF v_cadaver_id IS NULL THEN
        INSERT INTO cadavers (nic_encrypted, name_encrypted, estimated_age, gender, address_found, death_datetime)
        VALUES (p_nic, p_name, p_estimated_age, p_gender, p_address_found, p_death_datetime);
        SET v_cadaver_id = LAST_INSERT_ID();
    END IF;

    -- Insert the new autopsy case
    INSERT INTO postmortem_investigations (
        cadaver_id, station_id, assigned_doctor_id, pm_serial_no, 
        admission_date, hospital_bht_no, inquest_ordered_by, inquest_order_no, place_of_postmortem
    ) VALUES (
        v_cadaver_id, p_station_id, p_assigned_doctor_id, p_pm_serial_no, 
        p_admission_date, p_hospital_bht_no, p_inquest_ordered_by, p_inquest_order_no, p_place_of_postmortem
    );
    
    -- Create an initial blank PMR draft linked to this case
    INSERT INTO pmr_drafts (autopsy_case_id, draft_status) VALUES (LAST_INSERT_ID(), 'Pending Exam');

    COMMIT;
END //


-- ==============================================================================
-- 3. sp_transfer_evidence_custody
-- Securely logs the transfer of evidence from one custodian to another.
-- ==============================================================================
CREATE PROCEDURE sp_transfer_evidence_custody (
    IN p_evidence_id INT,
    IN p_from_user_id INT,
    IN p_to_user_id INT,
    IN p_location VARCHAR(100)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
    
    INSERT INTO evidence_custody_logs (
        evidence_id, from_user_id, to_user_id, transfer_datetime, location
    ) VALUES (
        p_evidence_id, p_from_user_id, p_to_user_id, CURRENT_TIMESTAMP, p_location
    );

    COMMIT;
END //


-- ==============================================================================
-- 4. sp_submit_test_result
-- Uploads a test result and automatically marks the test request as completed.
-- ==============================================================================
CREATE PROCEDURE sp_submit_test_result (
    IN p_request_id INT,
    IN p_uploaded_by INT,
    IN p_file_pointer VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Insert the actual result
    INSERT INTO test_results (request_id, uploaded_by, file_pointer)
    VALUES (p_request_id, p_uploaded_by, p_file_pointer);

    -- Mark the parent request as completed
    UPDATE test_requests SET request_status = 'Completed' WHERE request_id = p_request_id;

    COMMIT;
END //


-- ==============================================================================
-- 5. sp_log_court_receipt
-- Registers a court receipt and cascades the status to the respective case report.
-- ==============================================================================
CREATE PROCEDURE sp_log_court_receipt (
    IN p_submission_id INT,
    IN p_receipt_scan_path VARCHAR(255)
)
BEGIN
    DECLARE v_clinical_case_id INT;
    DECLARE v_autopsy_case_id INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- 1. Update the court submission record
    UPDATE court_submissions 
    SET receipt_scan_path = p_receipt_scan_path 
    WHERE submission_id = p_submission_id;

    -- 2. Retrieve case info to determine which case table to update
    SELECT clinical_case_id, autopsy_case_id INTO v_clinical_case_id, v_autopsy_case_id 
    FROM court_submissions 
    WHERE submission_id = p_submission_id;

    -- 3. Update the overall report status
    IF v_clinical_case_id IS NOT NULL THEN
        UPDATE mlr_documents SET report_status = 'Received by Court' WHERE clinical_case_id = v_clinical_case_id;
    END IF;

    IF v_autopsy_case_id IS NOT NULL THEN
        UPDATE pmr_drafts SET draft_status = 'Received by Court' WHERE autopsy_case_id = v_autopsy_case_id;
    END IF;

    COMMIT;
END //


-- ==============================================================================
-- 6. sp_get_monthly_statistics
-- Compiles monthly dashboard statistics for administrators.
-- ==============================================================================
CREATE PROCEDURE sp_get_monthly_statistics (
    IN p_month INT,
    IN p_year INT
)
BEGIN
    -- Result Set 1: Total Cases by Type
    SELECT 'Clinical' AS CaseType, COUNT(*) AS Total 
    FROM clinical_examinations 
    WHERE MONTH(admission_date) = p_month AND YEAR(admission_date) = p_year
    UNION ALL
    SELECT 'Autopsy' AS CaseType, COUNT(*) AS Total 
    FROM postmortem_investigations 
    WHERE MONTH(admission_date) = p_month AND YEAR(admission_date) = p_year;

    -- Result Set 2: Currently Pending Court Reports
    SELECT COUNT(*) AS PendingReports 
    FROM court_submissions 
    WHERE receipt_scan_path IS NULL;

    -- Result Set 3: Clinical Injury Frequencies (for the target month)
    SELECT 
        SUM(has_abrasion) AS TotalAbrasions,
        SUM(has_contusion) AS TotalContusions,
        SUM(has_laceration) AS TotalLacerations,
        SUM(has_stab) AS TotalStabs,
        SUM(has_burn) AS TotalBurns,
        SUM(has_fracture) AS TotalFractures
    FROM mlef_records m
    JOIN clinical_examinations c ON m.clinical_case_id = c.case_id
    WHERE MONTH(c.admission_date) = p_month AND YEAR(c.admission_date) = p_year;

END //

DELIMITER ;
