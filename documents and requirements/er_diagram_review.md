# ER Diagram Review Report: Forensic Medical Department Database

This report provides a detailed review of your proposed **27-table ER diagram**. We evaluate whether it meets all requirements in the **Requirements Analysis Report**, check its logical consistency, and outline the necessary additions, modifications, and corrections.

---

## 1. Overall Assessment
**Rating: Excellent (A+)**
*   **Lecturer Requirement:** It meets and exceeds the lecturer's "at least 25 tables" requirement (containing **27 tables**).
*   **Structural Depth:** The design is highly professional. It segregates generic staff from credentialed users, isolates JMO-specific details, separates living subjects from cadavers, and includes version control for media uploads (`asset_revisions`), audit logging (`audit_trails`), and real-time alerts (`user_alerts`).
*   **Security Focus:** Incorporating `_encrypted` fields (for names, NIC, JMO opinions, and observations) aligns perfectly with the confidentiality requirements for medico-legal data.

---

## 2. Logical Gaps & Required Corrections

While the structure is solid, we must address several missing fields and relationships to satisfy the requirements in the project guidelines and the real-world JMO documents:

### Gap A: Missing Core Patient Demographics
The tables `living_subjects` and `cadavers` store names and NICs, but lack critical demographics needed for court reports:
*   **`living_subjects`:** Needs `age`, `gender`, `permanent_address`, and `contact_no`.
*   **`cadavers`:** Needs `estimated_age`, `gender`, `address_found`, and `date_time_of_death` (or when the body was found/received).
*   **`healthcare_facilities` (BHT association):** Living subjects and cadavers referred from wards need a Bed Head Ticket (BHT) number. We should add a `hospital_bht_no` column to `clinical_examinations` and `postmortem_investigations`.

### Gap B: Missing Critical Date/Time Timelines
Both `clinical_examinations` and `postmortem_investigations` are missing datetime stamps that are legally vital in court and required by the database guidelines:
*   **`clinical_examinations`:** Add `incident_date`, `admission_date`, `examination_date`, and `report_submission_date`.
*   **`postmortem_investigations`:** Add `admission_date` (mortuary intake), `autopsy_date`, `inquest_date`, and `report_submission_date`.

### Gap C: Wound Charting for Autopsies
*   **Current Relationship:** `wound_charts` is linked only to `clinical_case_id` (Living Subjects).
*   **Issue:** Postmortem investigations (autopsies) require JMOs to chart wounds on cadavers (stabs, cuts, gunshot entry/exit points).
*   **Correction:** Change `clinical_case_id` in `wound_charts` to a polymorphic reference (like the physical evidence table) supporting both `clinical_case_id` and `autopsy_case_id`, OR rename it to support general cases.

### Gap D: Autopsy Inquest and Cause of Death (COD) Details
The `postmortem_investigations` and `death_certificates` tables must capture inquest metadata shown in `Digital database.pdf` and `Report Format.docx`:
*   **Inquest data:** Add `inquest_ordered_by` (e.g., Magistrate, Coroner, ISD), `inquest_order_no`, and `place_of_postmortem` to `postmortem_investigations`.
*   **Cause of Death (COD):** The table `death_certificates` must expand its `immediate_cause_encrypted` column to support the three levels of cause of death:
    *   `immediate_cause` (Immediate cause of death)
    *   `antecedent_cause` (Underlying morbid conditions)
    *   `contributory_cause` (Other significant conditions)
    *   `is_maternal_death` (Boolean flag)

### Gap E: Clinical MLEF Medical Findings
*   **Issue:** `mlef_records` contains only a foreign key and `mlef_number`. The JMO's examination checkboxes (presence of Abrasion, Contusion, Laceration, Stab, Cut, Fracture, Burn, and Alcohol influence) are missing.
*   **Correction:** Add boolean flags (`has_abrasion`, `has_contusion`, etc.), a `category_of_hurt` enum, and an `under_influence_of_alcohol` boolean flag to `mlef_records`.

---

## 3. Database Integrity & Constraints Review

### Polymorphic Tables (Arc Relationships)
Several tables use the "Exclusive Foreign Key" pattern to link to either a Clinical Case or an Autopsy Case:
*   `test_requests`, `peer_reviews`, `digital_assets`, `court_submissions`, `physical_evidence`

For this pattern to remain consistent and prevent records from orphaned or double-linked states, you **must** add a database-level `CHECK` constraint to each of these tables during physical implementation.
*   *Example Check Constraint:*
    ```sql
    CHECK (
        (clinical_case_id IS NOT NULL AND autopsy_case_id IS NULL) OR 
        (clinical_case_id IS NULL AND autopsy_case_id IS NOT NULL)
    )
    ```

---

## 4. Summary of Changes

### 1. Add Tables (To support tracking histories)
*   **`evidence_custody_logs` (Optional - 28th Table):** Tracks transfers of physical specimens (`evidence_id`, `from_user_id`, `to_user_id`, `transfer_datetime`, `location`). This fully models the "Chain of Custody" requirement from the Requirement Gathering document.

### 2. Modify Fields in Existing Tables
*   **`living_subjects`:** Add `age`, `gender`, `address`, `contact_number`.
*   **`cadavers`:** Add `estimated_age`, `gender`, `address_found`, `death_datetime`.
*   **`clinical_examinations`:** Add `incident_date`, `admission_date`, `examination_date`, `report_submission_date`, `hospital_bht_no`.
*   **`postmortem_investigations`:** Add `admission_date`, `autopsy_date`, `inquest_date`, `report_submission_date`, `hospital_bht_no`, `inquest_ordered_by`, `inquest_order_no`, `place_of_postmortem`.
*   **`mlef_records`:** Add injury flags (`has_abrasion`, `has_contusion`, etc.), `category_of_hurt` (Enum), `under_influence` (Boolean), `accompanying_officer_info` (Text).
*   **`death_certificates`:** Add `antecedent_cause`, `contributory_cause`, `is_maternal_death`.
*   **`wound_charts`:** Modify to include `autopsy_case_id` (FK, Nullable) alongside `clinical_case_id` (FK, Nullable) and add an exclusive check constraint.
