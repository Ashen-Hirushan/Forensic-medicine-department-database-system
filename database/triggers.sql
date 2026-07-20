-- Forensic Medical Department Database Triggers
-- These triggers silently enforce data integrity, chain of custody, and automate background tasks.

USE forensic_dept_db;

DELIMITER //

-- ==============================================================================
-- 1. Temporal Constraints (Preventing Future Dates)
-- ==============================================================================

CREATE TRIGGER trg_clinical_exam_dates_insert
BEFORE INSERT ON clinical_examinations
FOR EACH ROW
BEGIN
    IF NEW.incident_date > CURRENT_TIMESTAMP OR 
       NEW.admission_date > CURRENT_TIMESTAMP OR 
       NEW.examination_date > CURRENT_TIMESTAMP THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Incident, admission, or examination dates cannot be in the future.';
    END IF;
END //

CREATE TRIGGER trg_clinical_exam_dates_update
BEFORE UPDATE ON clinical_examinations
FOR EACH ROW
BEGIN
    IF NEW.incident_date > CURRENT_TIMESTAMP OR 
       NEW.admission_date > CURRENT_TIMESTAMP OR 
       NEW.examination_date > CURRENT_TIMESTAMP THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Incident, admission, or examination dates cannot be in the future.';
    END IF;
END //

CREATE TRIGGER trg_autopsy_dates_insert
BEFORE INSERT ON postmortem_investigations
FOR EACH ROW
BEGIN
    IF NEW.admission_date > CURRENT_TIMESTAMP OR 
       NEW.autopsy_date > CURRENT_TIMESTAMP THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Admission or autopsy dates cannot be in the future.';
    END IF;
END //

CREATE TRIGGER trg_autopsy_dates_update
BEFORE UPDATE ON postmortem_investigations
FOR EACH ROW
BEGIN
    IF NEW.admission_date > CURRENT_TIMESTAMP OR 
       NEW.autopsy_date > CURRENT_TIMESTAMP THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Admission or autopsy dates cannot be in the future.';
    END IF;
END //

CREATE TRIGGER trg_cadaver_death_date_insert
BEFORE INSERT ON cadavers
FOR EACH ROW
BEGIN
    IF NEW.death_datetime > CURRENT_TIMESTAMP THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Death datetime cannot be in the future.';
    END IF;
END //

CREATE TRIGGER trg_cadaver_death_date_update
BEFORE UPDATE ON cadavers
FOR EACH ROW
BEGIN
    IF NEW.death_datetime > CURRENT_TIMESTAMP THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Death datetime cannot be in the future.';
    END IF;
END //


-- ==============================================================================
-- 2. Chain of Custody Validation
-- ==============================================================================

CREATE TRIGGER trg_evidence_transfer_validation
BEFORE INSERT ON evidence_custody_logs
FOR EACH ROW
BEGIN
    DECLARE v_last_custodian INT;
    
    -- Find the person who received it last
    SELECT to_user_id INTO v_last_custodian 
    FROM evidence_custody_logs 
    WHERE evidence_id = NEW.evidence_id 
    ORDER BY transfer_datetime DESC 
    LIMIT 1;

    -- If there was a previous transfer, the person giving it now must be the person who received it last
    IF v_last_custodian IS NOT NULL AND v_last_custodian != NEW.from_user_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Chain of Custody Error: from_user_id does not match the current custodian of this evidence.';
    END IF;
END //


-- ==============================================================================
-- 3. Immutability of Finalized Records
-- ==============================================================================

CREATE TRIGGER trg_lock_finalized_mlef
BEFORE UPDATE ON mlef_records
FOR EACH ROW
BEGIN
    DECLARE v_status VARCHAR(50);
    
    SELECT report_status INTO v_status 
    FROM mlr_documents 
    WHERE clinical_case_id = NEW.clinical_case_id 
    LIMIT 1;
    
    IF v_status = 'Received by Court' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Cannot modify an MLEF record once the final report is received by the court.';
    END IF;
END //

CREATE TRIGGER trg_lock_finalized_cod
BEFORE UPDATE ON death_certificates
FOR EACH ROW
BEGIN
    DECLARE v_status VARCHAR(50);
    
    SELECT draft_status INTO v_status 
    FROM pmr_drafts 
    WHERE autopsy_case_id = NEW.autopsy_case_id 
    LIMIT 1;
    
    IF v_status = 'Received by Court' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Cannot modify a cause of death form once the final report is received by the court.';
    END IF;
END //


-- ==============================================================================
-- 4. Audit Trail Integrity
-- ==============================================================================

CREATE TRIGGER trg_protect_audit_trails_upd
BEFORE UPDATE ON audit_trails
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Audit trail records are immutable and cannot be updated.';
END //

CREATE TRIGGER trg_protect_audit_trails_del
BEFORE DELETE ON audit_trails
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Audit trail records are immutable and cannot be deleted.';
END //


-- ==============================================================================
-- 5. Automated System Actions (AFTER / POST Triggers)
-- ==============================================================================

-- Automated Audit Logging for MLEF Updates
CREATE TRIGGER trg_audit_mlef_update
AFTER UPDATE ON mlef_records
FOR EACH ROW
BEGIN
    DECLARE v_user_id INT DEFAULT 1; -- Fallback to system admin (id=1) if session variable isn't set
    
    -- In a real application, the backend should execute SET @current_user_id = X before this query
    IF @current_user_id IS NOT NULL THEN
        SET v_user_id = @current_user_id;
    END IF;

    INSERT INTO audit_trails (user_id, action_type, table_affected)
    VALUES (v_user_id, 'UPDATE', 'mlef_records');
END //

-- Automated User Alerts when Lab Results are uploaded
CREATE TRIGGER trg_alert_test_completed
AFTER INSERT ON test_results
FOR EACH ROW
BEGIN
    DECLARE v_doctor_id INT;
    DECLARE v_message TEXT;
    
    -- Find the doctor assigned to the case that ordered this test
    SELECT COALESCE(c.assigned_doctor_id, p.assigned_doctor_id) INTO v_doctor_id
    FROM test_requests tr
    LEFT JOIN clinical_examinations c ON tr.clinical_case_id = c.case_id
    LEFT JOIN postmortem_investigations p ON tr.autopsy_case_id = p.case_id
    WHERE tr.request_id = NEW.request_id
    LIMIT 1;

    IF v_doctor_id IS NOT NULL THEN
        -- We need the actual user_id of the doctor to send the alert.
        -- medical_officers links to staff_directory links to system_users.
        INSERT INTO user_alerts (user_id, message)
        SELECT sd.user_id, CONCAT('A new lab test result has been uploaded for request ID: ', NEW.request_id)
        FROM medical_officers mo
        JOIN staff_directory sd ON mo.staff_id = sd.staff_id
        WHERE mo.doctor_id = v_doctor_id AND sd.user_id IS NOT NULL;
    END IF;
END //

DELIMITER ;
