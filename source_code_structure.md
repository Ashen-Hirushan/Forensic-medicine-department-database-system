# Source Code Structure

```text
Forensic-medicine-department-database-system/
├── .env
├── .env.example
├── ForensicDB_Launcher.bat
├── README.md
├── requirements.txt
├── run_tests.py
├── start.py
├── backup.bat
├── user_guide.md
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── alerts.py
│   │   ├── auth.py
│   │   ├── autopsy.py
│   │   ├── clinical.py
│   │   ├── court.py
│   │   ├── dashboard.py
│   │   ├── evidence.py
│   │   ├── patients.py
│   │   └── reports.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_utils.py
│   │   └── db.py
│   ├── static/
│   │   ├── css/
│   │   │   ├── components.css
│   │   │   ├── layout.css
│   │   │   └── variables.css
│   │   ├── js/
│   │   │   ├── app.js
│   │   │   └── charts.js
│   │   └── uploads/
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── login.html
│       ├── profile.html
│       ├── signup.html
│       ├── admin/
│       │   ├── audit_log.html
│       │   └── users.html
│       ├── autopsy/
│       │   ├── cod_form.html
│       │   ├── detail.html
│       │   ├── form.html
│       │   └── list.html
│       ├── clinical/
│       │   ├── detail.html
│       │   ├── form.html
│       │   ├── list.html
│       │   ├── mlef_form.html
│       │   ├── mlr_form.html
│       │   └── referrals.html
│       ├── components/
│       │   ├── navbar.html
│       │   └── sidebar.html
│       ├── court/
│       │   └── dispatch.html
│       ├── errors/
│       │   ├── 403.html
│       │   └── 404.html
│       ├── evidence/
│       │   ├── chain.html
│       │   └── transfer.html
│       ├── patients/
│       │   ├── list.html
│       │   └── new.html
│       └── reports/
│           ├── daily.html
│           ├── mlef_register.html
│           ├── pending.html
│           ├── pm_register.html
│           ├── print_mlef.html
│           ├── print_mlr.html
│           └── print_pmr.html
├── database/
│   ├── alter_mlef.sql
│   ├── alter_mlef_v2.sql
│   ├── audit_triggers.sql
│   ├── fix_alerts.sql
│   ├── procedures.sql
│   ├── schema.sql
│   ├── seed.py
│   └── triggers.sql
├── documents and requirements/
│   ├── Digital database.pdf
│   ├── Mini Project Assignment.pdf
│   ├── Report Format.docx
│   ├── backend_implementation_plan
│   ├── constraints_Triggers_Procedures/
│   ├── er_diagram_review.md
│   ├── folder_structure
│   ├── frontend implementation plan
│   ├── implementation_plan.md
│   ├── missing part
│   ├── missing parts implimentation
│   ├── requirements_analysis_report.md
│   └── requirment gathering meeting1.pdf
├── flask_session/
├── flask_session_data/
└── uploads/
```
