USE forensic_dept_db;

-- 1. Modify the audit_trails table to match the reference project's capabilities
ALTER TABLE audit_trails MODIFY COLUMN user_id INT NULL;

-- Add new columns if they don't exist
DELIMITER $$
CREATE PROCEDURE DropProcedureIfExists(IN procedureName VARCHAR(255))
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.routines WHERE routine_schema = 'forensic_dept_db' AND routine_name = procedureName) THEN
    SET @s = CONCAT('DROP PROCEDURE ', procedureName);
    PREPARE stmt FROM @s;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
  END IF;
END $$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE AddColumnIfNotExists(
    IN dbName VARCHAR(255), 
    IN tableName VARCHAR(255), 
    IN columnName VARCHAR(255), 
    IN columnDefinition VARCHAR(255)
)
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = dbName AND TABLE_NAME = tableName AND COLUMN_NAME = columnName
    ) THEN
        SET @ddl = CONCAT('ALTER TABLE ', dbName, '.', tableName, ' ADD COLUMN ', columnName, ' ', columnDefinition);
        PREPARE stmt FROM @ddl;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END $$
DELIMITER ;

CALL AddColumnIfNotExists('forensic_dept_db', 'audit_trails', 'record_id', 'INT');
CALL AddColumnIfNotExists('forensic_dept_db', 'audit_trails', 'old_value', 'TEXT');
CALL AddColumnIfNotExists('forensic_dept_db', 'audit_trails', 'new_value', 'TEXT');

DROP PROCEDURE AddColumnIfNotExists;
DROP PROCEDURE DropProcedureIfExists;


-- 2. Triggers for clinical_examinations
DELIMITER //

DROP TRIGGER IF EXISTS after_clinical_insert //
CREATE TRIGGER after_clinical_insert
AFTER INSERT ON clinical_examinations
FOR EACH ROW
BEGIN
    INSERT INTO audit_trails (user_id, action_type, table_affected, record_id, new_value)
    VALUES (@app_user_id, 'INSERT', 'clinical_examinations', NEW.case_id, CONCAT('Ref: ', NEW.reference_no, ', Facility: ', NEW.facility_id));
END //

DROP TRIGGER IF EXISTS after_clinical_update //
CREATE TRIGGER after_clinical_update
AFTER UPDATE ON clinical_examinations
FOR EACH ROW
BEGIN
    INSERT INTO audit_trails (user_id, action_type, table_affected, record_id, old_value, new_value)
    VALUES (@app_user_id, 'UPDATE', 'clinical_examinations', NEW.case_id, CONCAT('Ref: ', OLD.reference_no), CONCAT('Ref: ', NEW.reference_no));
END //

-- 3. Triggers for postmortem_investigations
DROP TRIGGER IF EXISTS after_postmortem_insert //
CREATE TRIGGER after_postmortem_insert
AFTER INSERT ON postmortem_investigations
FOR EACH ROW
BEGIN
    INSERT INTO audit_trails (user_id, action_type, table_affected, record_id, new_value)
    VALUES (@app_user_id, 'INSERT', 'postmortem_investigations', NEW.case_id, CONCAT('PM_Serial: ', NEW.pm_serial_no));
END //

DROP TRIGGER IF EXISTS after_postmortem_update //
CREATE TRIGGER after_postmortem_update
AFTER UPDATE ON postmortem_investigations
FOR EACH ROW
BEGIN
    INSERT INTO audit_trails (user_id, action_type, table_affected, record_id, old_value, new_value)
    VALUES (@app_user_id, 'UPDATE', 'postmortem_investigations', NEW.case_id, CONCAT('PM_Serial: ', OLD.pm_serial_no), CONCAT('PM_Serial: ', NEW.pm_serial_no));
END //

-- 4. Triggers for court_submissions
DROP TRIGGER IF EXISTS after_court_insert //
CREATE TRIGGER after_court_insert
AFTER INSERT ON court_submissions
FOR EACH ROW
BEGIN
    INSERT INTO audit_trails (user_id, action_type, table_affected, record_id, new_value)
    VALUES (@app_user_id, 'INSERT', 'court_submissions', NEW.submission_id, CONCAT('Court: ', NEW.court_name, ', Date: ', NEW.trial_date));
END //

DROP TRIGGER IF EXISTS after_court_update //
CREATE TRIGGER after_court_update
AFTER UPDATE ON court_submissions
FOR EACH ROW
BEGIN
    INSERT INTO audit_trails (user_id, action_type, table_affected, record_id, old_value, new_value)
    VALUES (@app_user_id, 'UPDATE', 'court_submissions', NEW.submission_id, CONCAT('Court: ', OLD.court_name), CONCAT('Court: ', NEW.court_name));
END //

DELIMITER ;
