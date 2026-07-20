# Forensic Medical Department Database Project Plan

This document outlines a structured, step-by-step project plan to design and develop the **Forensic Medical Department Database System** from scratch. It is designed to be executed sequentially, allowing you to focus on one phase at a time.

---

## Phase 1: Requirements Gathering & System Scope

Before writing code or designing tables, you must analyze the department's operations, collect the user requirements, and define what the system will and will not do.

### 1. Identify Stakeholders & Roles
Define who will interact with the system and their respective permissions:
*   **Judicial Medical Officers (JMOs / Doctors):** Conduct examinations, fill out medical findings, specify causes of death, and generate final reports.
*   **Clerical Officers:** Register patients, log incoming cases, handle court document dispatches, and record receipt confirmations.
*   **Laboratory Staff:** Receive specimens (blood, tissue), run toxicology or histology tests, and log results.
*   **System Administrators:** Manage user accounts, monitor security logs, and perform database backup and recovery.
*   **External Stakeholders (Read-only / Output consumers):** Police stations, magistrates, and the Attorney General's (AG) office.

### 2. Define Workflows & Pathways
Separate the system logic into the two primary operational branches:
*   **Clinical Forensic Pathway (Alive Patients):**
    *   *Intake:* Referrals arrive from wards (via hospital police), direct police stations, or other authorities.
    *   *Authorization:* Verify presence of a Medico-Legal Examination Form (MLEF), request letters, or court orders.
    *   *Examination:* JMO examines the victim, notes injuries (abrasions, fractures, etc.), assesses alcohol influence, and takes consent thumbprints.
    *   *Outcome:* Generate a Medico-Legal Report (MLR) and dispatch a copy to the police/court.
*   **Autopsy Pathway (Deceased Patients):**
    *   *Intake:* Hospital deaths, sudden outside deaths, or high-profile cases.
    *   *Authorization:* Verify inquest orders from the Coroner, Magistrate, or High Court.
    *   *Autopsy:* JMO performs the postmortem, records findings on a Postmortem Report (PMR), takes crime scene/body photos, and orders laboratory tests (toxicology/histology) if needed.
    *   *Outcome:* Issue the Cause of Death (COD) form, dispatch the final report, and log receipt from the court.

### 3. List Storage & Document Requirements
Identify all data objects that need representation:
*   **Text/Numeric Data:** Patient demographics, case numbers, incident dates, injury classifications, cause of death forms.
*   **Binary/Media Data:** Consent signatures/thumbprints, injury and crime scene photographs, scanned court orders, and final signed report PDFs.

---

## Phase 2: Deciding the Tech Stack

Select the tools and frameworks that fit the project constraints and learning objectives.

### 1. Database Management System (DBMS)
*   **Choice:** **MySQL**
*   **Rationale:** Provides robust relational integrity (foreign keys, transaction support), scales well for concurrent users (multiple JMOs, clerks, and lab staff accessing the system), and supports index optimizations for fast searches.

### 2. Backend Environment & Framework
*   **Choice:** **Python with Flask** or **Node.js**
*   **Rationale:** Lightweight, easy to set up, supports MVC architecture, and offers simple libraries for database connectivity and security (hashing, session handling).

### 3. Frontend Technology
*   **Choice:** **HTML5, CSS3, and Vanilla JavaScript**
*   **Rationale:** Allows maximum customizability to create a premium, modern dashboard (using glassmorphism containers, dark mode CSS variables, and clean typography). Third-party UI frameworks like Bootstrap can be used, but custom CSS is preferred for visual excellence.
*   **Analytics Visualization:** `Chart.js` for rendering statistics on the dashboard.

---

## Phase 3: Database Design

Design the data models conceptually and logically to ensure normalization and referential integrity.

### 1. Entity-Relationship Diagram (ERD)
Draw the conceptual entities and define how they relate:
*   Identify primary keys (e.g., `PatientID`, `CaseNumber`, `StaffID`) and foreign keys.
*   Establish cardinality:
    *   One `Patient` can have multiple `Cases`.
    *   One `Case` has exactly one `MLEF` (if clinical) or one `PMR` (if autopsy).
    *   One `Case` can have multiple `Evidence` items.
    *   One `Evidence` item can undergo multiple `LaboratoryTests`.
    *   One `Case` has one `CourtReport` dispatch log.

### 2. Normalization
Refine the tables to **Third Normal Form (3NF)**:
*   **1NF:** Ensure all attributes are atomic; no comma-separated injury lists (use a structured junction table or boolean flags for major injury types).
*   **2NF:** Ensure all non-key attributes are fully functional-dependent on the primary key.
*   **3NF:** Eliminate transitive dependencies (e.g., do not store police station contact info in the Case table; reference a separate Police Station entity if needed).

### 3. Data Dictionary
Document the metadata for every table:
*   Column Name, Data Type, Size, Constraints (NOT NULL, UNIQUE, DEFAULT), and Description.

---

## Phase 4: Database Implementation (MySQL)

Translate your database design into SQL scripts and build the physical database.

1.  **Write the DDL Script:** Write the table creation script incorporating:
    *   Primary and Foreign key constraints.
    *   `CHECK` constraints (e.g., verifying that ages are positive, and that dates follow a logical timeline).
2.  **Add Indexes:** Add indexes on high-frequency search fields (like Patient NIC, Case Number, and Dispatch Status) to optimize lookup speeds.
3.  **Create Views:** Write database views for common reports (e.g., a summary view merging Case details, Patient names, and Assigned Doctors for the JMO's task list).
4.  **Create a Seeding Script:** Write a Python script to populate all tables with realistic mock clinical and autopsy cases (e.g., patients with specific injuries, autopsy cases with pending lab reports) to verify schema logic.

---

## Phase 5: Backend API Development

Build the application server and business logic.

1.  **Authentication & Security (RBAC):**
    *   Implement user login with hashed passwords.
    *   Set up session storage to track the user's role (Doctor, Clerk, Lab Staff, Admin).
    *   Write permission checks to block unauthorized access to restricted endpoints.
2.  **Patient & Case Management APIs:**
    *   Create endpoints to register patients and log new incoming cases.
    *   Implement searching and filtering APIs (allowing lookups by NIC, case number, or doctor).
3.  **Clinical & Autopsy Module APIs:**
    *   Create forms submission endpoints for JMOs to record MLEF findings and Autopsy PMR Cause of Death details.
4.  **Lab & Court Dispatch APIs:**
    *   Create endpoints for ordering specimens tests, recording test results, and tracking court dispatches.

---

## Phase 6: Frontend UI Implementation

Create user interfaces representing the user roles and workflows.

1.  **Establish Design Theme:** Set up clean CSS variables for slate backgrounds, neon highlights, and high-readability fonts (e.g., Google Fonts Outfit or Inter).
2.  **Login & Session Interface:** Create a clean credentials gateway.
3.  **Dashboard Screens:**
    *   *Clerk Portal:* Quick links to register patients, log case details, and dispatch reports.
    *   *JMO Portal:* View active case queues, fill out injury check-boxes, record autopsy results, and view pending court deadlines.
    *   *Lab Portal:* Update ordered tests with toxicology/histology results.
    *   *Analytics View:* Render visually appealing graphs showing daily workloads and monthly statistics.

---

## Phase 7: Testing & Verification

Ensure the application is secure, functionally correct, and performs reliably.

1.  **Write Functional Unit Tests:** Test constraints (e.g., ensure you cannot input a report date that is earlier than the incident date).
2.  **Verify Access Control:** Confirm that a clerk or lab staff member cannot edit autopsy findings or cause of death records.
3.  **Manual User Journey Tests:** Walk through a mock patient's complete timeline (Intake -> Examination -> Lab Order -> Test Submission -> Report Generation -> Court Dispatch -> Receipt logging) to verify the system logic.

---

## Phase 8: Documentation, Backup & Final Report

Prepare the system for submission or handoff.

1.  **Backup/Recovery Routines:** Write admin commands to export database backups (using `mysqldump`) and import/restore them.
2.  **User Manual:** Compile simple guidelines showing screenshots and descriptions of the data entry pages, search system, and dashboard analytics.
3.  **Individual Contribution Report:** Create a summary table detailing task allocations, completed items, and challenges faced.
