# Stored Procedures Analysis Report

Based on the workflows outlined in the **Requirements Analysis Report**, your application requires several multi-step operations that must be executed as atomic transactions (meaning either all steps succeed, or none do). 

Implementing these as **Stored Procedures** in the database will ensure data consistency, reduce the number of queries your backend needs to send, and encapsulate complex business logic.

Here is a breakdown of the stored procedures that should be added to your system:

## 1. Case & Patient Registration Procedures
Registering a new case often requires checking if a patient already exists, inserting them if they don't, and then linking them to a new case record. This must be a seamless transaction.

*   **`sp_register_clinical_case`**
    *   **Inputs:** Patient Details (Name, NIC, Age, etc.), Case Details (Reference No, Incident Date, Assigned Doctor).
    *   **Logic:** 
        1. Checks if a `living_subjects` record exists for the provided NIC. If not, creates one.
        2. Creates a new record in `clinical_examinations`.
        3. Creates a blank draft entry in `mlef_records` linked to the case.
    *   **Benefit:** Prevents orphaned cases if the application crashes between inserting the patient and inserting the case.

*   **`sp_register_autopsy_case`**
    *   **Inputs:** Cadaver Details (NIC, estimated age, death datetime), PM Serial No, Inquest details.
    *   **Logic:** Similar to the clinical case, ensures the `cadavers` record and `postmortem_investigations` record are created together.

## 2. Evidence & Chain of Custody Procedures
The chain of custody must be strictly preserved. Transferring evidence should be an immutable transaction.

*   **`sp_transfer_evidence_custody`**
    *   **Inputs:** `evidence_id`, `from_user_id`, `to_user_id`, `location_description`.
    *   **Logic:**
        1. Verifies that `from_user_id` is the current custodian.
        2. Inserts a new record into `evidence_custody_logs`.
    *   **Benefit:** Centralizes the transfer logic and ensures no evidence "skips" a custodian without proper logging.

## 3. Laboratory Workflow Procedures
Ordering and completing tests span across multiple tables (`test_requests` and `test_results`).

*   **`sp_submit_test_result`**
    *   **Inputs:** `request_id`, `uploaded_by`, `file_pointer` (Result Document URL).
    *   **Logic:**
        1. Inserts the result into `test_results`.
        2. Automatically updates the `request_status` in `test_requests` to `'Completed'`.
    *   **Benefit:** Ensures that a test is never marked as "Completed" unless a result file is actually uploaded.

## 4. Court Dispatch & Verification
According to the requirements, a report is not finalized until a court receipt is scanned and uploaded.

*   **`sp_log_court_receipt`**
    *   **Inputs:** `submission_id`, `receipt_scan_path`.
    *   **Logic:**
        1. Updates `court_submissions.receipt_scan_path`.
        2. Looks up the associated case (Clinical or Autopsy).
        3. Updates `mlr_documents.report_status` or `pmr_drafts.draft_status` to `'Received by Court'`.
    *   **Benefit:** Keeps the overall case status perfectly synchronized with the court dispatch subsystem.

## 5. Statistical Dashboard Procedures
While simple reports can use Views, generating multi-dimensional metrics for the dashboard is better suited for procedures.

*   **`sp_get_monthly_statistics`**
    *   **Inputs:** `target_month`, `target_year`.
    *   **Logic:** Runs complex aggregations to return:
        1. Total clinical vs autopsy cases.
        2. Most frequent injury types (parsing boolean flags in `mlef_records`).
        3. Pending court dispatch counts.

---
**Next Steps:**
If these procedures align with how you plan to build the backend (e.g., in Python/Flask), I can create a `database/procedures.sql` file containing all the actual SQL code for these procedures!
