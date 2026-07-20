# Database Triggers Analysis Report

While `schema.sql` defines the structure of your data and `procedures.sql` defines complex transactions, **Database Triggers** are needed to silently and automatically enforce rules every time an `INSERT`, `UPDATE`, or `DELETE` occurs. 

Based on the forensic workflows and the constraints identified earlier, the following triggers should be implemented in your system:

## 1. Temporal Constraints (Preventing Future Dates)
MySQL does not allow functions like `CURRENT_TIMESTAMP()` inside table-level `CHECK` constraints. To prevent staff from accidentally entering dates in the future (e.g., claiming an autopsy happened tomorrow), we must use `BEFORE INSERT` and `BEFORE UPDATE` triggers.

*   **`trg_clinical_exam_dates`**
    *   **Table:** `clinical_examinations`
    *   **Action:** Validates that `incident_date`, `admission_date`, and `examination_date` are not greater than `CURRENT_TIMESTAMP`. Throws an SQL error (SQLSTATE '45000') if they are.
*   **`trg_autopsy_dates`**
    *   **Table:** `postmortem_investigations`
    *   **Action:** Validates that `admission_date` and `autopsy_date` are not in the future.
*   **`trg_cadaver_death_date`**
    *   **Table:** `cadavers`
    *   **Action:** Validates that the `death_datetime` is not in the future.

## 2. Chain of Custody Validation
The integrity of physical evidence relies on a strict, unbroken chain of custody.

*   **`trg_evidence_transfer_validation`**
    *   **Table:** `evidence_custody_logs`
    *   **Action:** `BEFORE INSERT`
    *   **Logic:** Before a new transfer is logged, this trigger checks the most recent log entry for that `evidence_id`. It ensures that the person transferring the evidence (`from_user_id`) is the exact same person who previously received it (the `to_user_id` of the last transaction). If it does not match, the trigger aborts the transfer, preventing illegal gaps in the custody chain.

## 3. Immutability of Finalized Records
Once a Medico-Legal Report or Cause of Death form is dispatched and received by the court, it becomes a legal document and should not be tampered with.

*   **`trg_lock_finalized_mlef`**
    *   **Table:** `mlef_records`
    *   **Action:** `BEFORE UPDATE`
    *   **Logic:** Checks the parent `mlr_documents` table. If `report_status` is `'Received by Court'`, the trigger blocks any modifications to the MLEF data.
*   **`trg_lock_finalized_cod`**
    *   **Table:** `death_certificates`
    *   **Action:** `BEFORE UPDATE`
    *   **Logic:** Checks the parent `pmr_drafts` table. If `draft_status` is `'Received by Court'`, it blocks modifications to the cause of death.

## 4. Audit Trail Integrity
Your system has an `audit_trails` table. We must protect the integrity of the audit logs themselves.

*   **`trg_protect_audit_trails`**
    *   **Table:** `audit_trails`
    *   **Action:** `BEFORE UPDATE` and `BEFORE DELETE`
    *   **Logic:** Silently aborts any attempt to modify or delete an existing audit log. Audit logs must be strictly append-only.

## 5. Automated System Actions (AFTER / POST Triggers)
"Post" triggers (`AFTER INSERT`, `AFTER UPDATE`, `AFTER DELETE`) execute after the main data has been successfully saved. They are crucial for automating background tasks without requiring the application code to send extra queries.

*   **Automated Audit Logging (`trg_audit_mlef_update`, `trg_audit_cod_update`)**
    *   **Tables:** `mlef_records`, `death_certificates`
    *   **Action:** `AFTER UPDATE`
    *   **Logic:** Whenever a doctor modifies a medical examination form or cause of death, this trigger automatically inserts a row into the `audit_trails` table indicating exactly which table was affected and at what time. *(Note: Tracking exactly "who" made the change via purely MySQL triggers requires the application to set a session variable like `@current_user_id` before running the update).*
*   **Automated User Alerts (`trg_alert_test_completed`)**
    *   **Table:** `test_results`
    *   **Action:** `AFTER INSERT`
    *   **Logic:** When lab staff insert a new test result, this trigger looks up the `assigned_doctor_id` for the corresponding case and automatically inserts a notification message into the `user_alerts` table, instantly notifying the doctor that results are ready.

---
**Next Steps:**
If you agree with these automatic enforcement rules, I can compile all the necessary `CREATE TRIGGER` statements into a `database/triggers.sql` file!
