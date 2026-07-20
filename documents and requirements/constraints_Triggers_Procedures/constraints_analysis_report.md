# Constraints Analysis Report

This report outlines the constraints that should be added to the database schema to fully align with the business logic and rules defined in the **Requirements Analysis Report** (`requirements_analysis_report.md`). 

While your current `schema.sql` already implements many essential constraints (like `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, and `CHECK` on ages and dates), there are several more that need to be added to guarantee data integrity.

## 1. Status & State Validation (CHECK / ENUM Constraints)

The requirements document specifies explicit states for various entities, but these are currently defined as generic `VARCHAR(50)` in the schema. We must enforce these valid states.

*   **Test Status (`test_requests.request_status`)**
    *   *Requirement:* Section 5.2 states "Test Status: Tracks whether a test is `Pending` or `Completed`."
    *   *Constraint to Add:* 
        `CHECK (request_status IN ('Pending', 'Completed'))` or change to `ENUM('Pending', 'Completed')`.
*   **Report Status Tracker (`mlr_documents.report_status` & `pmr_drafts.draft_status`)**
    *   *Requirement:* Section 6 explicitly mentions a status tracker: `Pending Exam`, `PMR/MLEF Drafted`, `Dispatched`, `Received by Court`.
    *   *Constraint to Add:* 
        `CHECK (report_status IN ('Pending Exam', 'PMR/MLEF Drafted', 'Dispatched', 'Received by Court'))`.

## 2. Chronological Integrity (CHECK Constraints)

You have already implemented some date validation (e.g., `admission_date >= incident_date`), but the workflow relies heavily on sequential dates that need to be enforced across the board.

*   **Clinical Examinations (`clinical_examinations`)**
    *   *Current constraint:* `CHECK (admission_date >= incident_date AND examination_date >= admission_date)`
    *   *Constraint to Add:* A report cannot be submitted before the examination. 
        `CHECK (report_submission_date >= examination_date)`
*   **Postmortem Investigations (`postmortem_investigations`)**
    *   *Current constraint:* `CHECK (autopsy_date >= admission_date)`
    *   *Constraint to Add:* A report cannot be submitted before the autopsy.
        `CHECK (report_submission_date >= autopsy_date)`

## 3. Data Completeness (NOT NULL Constraints)

To ensure the system captures mandatory information as defined in the requirements, several fields should be made `NOT NULL`.

*   **Test Requests**
    *   `request_status` should be `NOT NULL DEFAULT 'Pending'`.
*   **Evidence Custody Logs (`evidence_custody_logs`)**
    *   Currently, `from_user_id` can be NULL (which might be okay for the initial entry), but `location` should ideally be mandatory if the physical location is being logged.

## 4. Constraints to be implemented via Triggers

MySQL does not allow functions like `CURRENT_TIMESTAMP` inside table-level `CHECK` constraints. Therefore, the following temporal rules must be enforced using database **Triggers**:

*   **Future Date Prevention:** Dates like `incident_date`, `examination_date`, `autopsy_date`, and `death_datetime` cannot be in the future.
*   **Audit Trail Timestamps:** Preventing modification of the `action_timestamp` in the `audit_trails` table.
*   **Chain of Custody:** When transferring evidence in `evidence_custody_logs`, a trigger should verify that the `from_user_id` is the person who currently holds the evidence (the most recent `to_user_id` for that `evidence_id`).

---
**Next Steps:**
If you approve, I can write the SQL commands (`ALTER TABLE` statements and `CREATE TRIGGER` statements) to apply all of these missing constraints to your database!
