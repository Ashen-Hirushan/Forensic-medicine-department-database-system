USE forensic_dept_db;

DELIMITER //

DROP PROCEDURE IF EXISTS sp_register_clinical_case //
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
    DECLARE v_doctor_user_id INT;
    
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

    -- Create notification alert for the assigned doctor
    IF p_assigned_doctor_id IS NOT NULL THEN
        SELECT sd.user_id INTO v_doctor_user_id
        FROM medical_officers mo
        JOIN staff_directory sd ON mo.staff_id = sd.staff_id
        WHERE mo.doctor_id = p_assigned_doctor_id;
        
        IF v_doctor_user_id IS NOT NULL THEN
            INSERT INTO user_alerts (user_id, message) 
            VALUES (v_doctor_user_id, CONCAT('New Clinical Case assigned to you: ', p_reference_no));
        END IF;
    END IF;

    COMMIT;
END //

DROP PROCEDURE IF EXISTS sp_register_autopsy_case //
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
    DECLARE v_doctor_user_id INT;
    
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

    -- Create notification alert for the assigned doctor
    IF p_assigned_doctor_id IS NOT NULL THEN
        SELECT sd.user_id INTO v_doctor_user_id
        FROM medical_officers mo
        JOIN staff_directory sd ON mo.staff_id = sd.staff_id
        WHERE mo.doctor_id = p_assigned_doctor_id;
        
        IF v_doctor_user_id IS NOT NULL THEN
            INSERT INTO user_alerts (user_id, message) 
            VALUES (v_doctor_user_id, CONCAT('New Autopsy Case assigned to you: ', p_pm_serial_no));
        END IF;
    END IF;

    COMMIT;
END //

DELIMITER ;
