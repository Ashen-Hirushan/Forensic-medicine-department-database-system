# ForensicDB: Role-Based User Guide

The Forensic Medicine Department Management System (ForensicDB) utilizes strict Role-Based Access Control (RBAC). What you can see and do depends entirely on the role assigned to your account during registration.

Here is a comprehensive guide on how to use the system as each of the four primary roles.

---

## 👨‍⚕️ 1. Doctor (JMO - Judicial Medical Officer)
*The Doctor is the core medical user of the system. Their primary focus is managing cases, conducting examinations, and drafting legal reports.*

### Key Workflows
1. **Managing Patients & Cases**
   * **View Patients:** Navigate to the `Living Subjects` registry to view patient details.
   * **Clinical Cases:** Under the `Clinical Cases` tab, you can view cases assigned to you. Click into a case to draft the MLEF (Medico-Legal Examination Form), record injuries in the Wound Chart, and finalize the MLR (Medico-Legal Report).
   * **Autopsy Cases:** Under the `Post-Mortem Cases` tab, you can manage cadaver examinations. You can upload Voice Dictations (audio files) from the autopsy room, fill out the Post-Mortem Report (PMR), and formally declare the Cause of Death (COD).
   
2. **Consultations & Peer Reviews**
   * **Referrals:** Inside a clinical case, use the `Consultations` tab to refer a patient to another specialty (e.g., Psychiatry).
   * **Peer Reviews:** You can invite other Doctors to peer-review your PMR or MLR before finalizing it for court.

3. **Submitting Evidence & Tests**
   * Doctors can log Physical Evidence found on a subject and send Test Requests to the Lab Staff directly through the case interface.

---

## 👔 2. Clerk (Administrative Staff)
*The Clerk handles the intake of patients, dispatching of reports, and managing court relations. They do not have access to draft medical opinions.*

### Key Workflows
1. **Intake & Registration**
   * **Registering Subjects:** Clerks will spend a lot of time in the `Living Subjects` registry. When a new subject arrives (e.g., via Police), the Clerk registers their NIC and demographic details.
   * **Opening Cases:** After registering a subject, the Clerk opens a new Clinical or Autopsy case, assigns it a Reference No/PM Serial No, and routes it to a specific Doctor on duty.

2. **Court Dispatch & Summons**
   * **Managing Submissions:** Navigate to the `Court Dispatch` tab. When a Doctor finalizes an MLR or PMR, the Clerk creates a Court Submission to send the document to the respective Magistrate or High Court.
   * **Logging Receipts:** When the court acknowledges receipt of a report, the Clerk scans the physical receipt and uploads it via the system to officially mark the case as "Received by Court".

3. **Evidence Custody**
   * Clerks often act as the middlemen for physical evidence, logging the transfer of evidence from the Doctor to the Police or Lab using the `Evidence Custody` transfer tool.

---

## 🔬 3. Lab Staff (Technicians & Analysts)
*Lab Staff have a very focused workflow. They do not view full clinical histories; they only see requested tests and upload the scientific results.*

### Key Workflows
1. **Managing Test Requests**
   * **Pending Queue:** Lab Staff monitor the `Lab Requests` or `Evidence` queue. When a Doctor requests a toxicology or histology test, it appears here.
2. **Uploading Results**
   * Once the lab analysis is complete, the Lab Staff selects the pending request, uploads the PDF/Image of the result, and marks the request as "Completed". The Doctor is immediately notified and can view the result in the patient's case file.
3. **Chain of Custody**
   * If physical evidence (like a blood sample or clothing) is transferred to the lab, Lab Staff must accept the custody transfer in the system to maintain a legally watertight chain of custody.

---

## 👑 4. Admin (System Administrator)
*The Admin oversees the entire operation, manages user access, and monitors system integrity. Admins have read access to almost everything but shouldn't interfere with medical opinions.*

### Key Workflows
1. **User Management & Security**
   * **Staff Directory:** Admins approve new signups and manage the `Staff Directory`. They can lock accounts, reset passwords, or change a user's role.
   * **Audit Trails:** The system automatically logs every `INSERT` and `UPDATE` on cases and court submissions. Admins can view the `Audit Logs` to see exactly *who* changed *what* and *when* (including tracking old vs. new values) to prevent tampering.

2. **Reporting & Analytics**
   * **Dashboard Analytics:** Admins have access to the full `Dashboard`, viewing real-time Chart.js graphs of monthly case influx, clinical injury breakdowns (e.g., trauma vs. assault), and pending court backlogs.
   * **Exporting Registers:** Admins can export the full MLEF Register and PM Register for monthly government reporting.

3. **Disaster Recovery**
   * The Admin is responsible for running the `backup.bat` tool on the server to take routine snapshots of the MySQL database.
