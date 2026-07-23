# ForensicDB — Forensic Medicine Department Management System

ForensicDB is an automated, web-based management system designed for forensic medicine departments. It manages clinical cases, post-mortem cadaver investigations, evidence chain-of-custody, lab test requests, and court submissions under strict Role-Based Access Control (RBAC).

---

## 🚀 How to Run (One-Click Setup)

This project includes a **Zero-Configuration Automated Launcher**. When running on any new PC for the first time, it automatically installs all requirements, sets up the MySQL database, and launches the web application.

### Windows (Double-Click)
1. Ensure **Python** (3.8+) and **MySQL Server** are installed on the PC.
2. Double-click **`start.bat`** in the project folder.

### Command Line (Any OS)
Run either command in your terminal:
```bash
python start.py
```
*or*
```bash
python run.py
```

---

## 🛠 What the Launcher Does Automatically
- **`.env` Creation**: Generates a default `.env` file if missing.
- **Dependency Installation**: Runs `pip install -r requirements.txt` automatically.
- **MySQL Setup**: Connects to MySQL (prompts for the MySQL password if credentials differ).
- **Database Initialization**: Creates `forensic_dept_db`, executes schemas, procedures, triggers, and seeds 28 tables of initial data.
- **Browser Launch**: Opens `http://127.0.0.1:5000` automatically in your browser.

---

## 🔑 Default Accounts (Seeded Data)

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` |
| **Doctor (JMO)** | `jmo_doc` | `doc123` |
| **Clerk** | `clerk_user` | `clerk123` |
| **Lab Staff** | `lab_tech` | `lab123` |

---

## 📁 Requirements
- **Python**: 3.8+
- **Database**: MySQL Server 8.0+
- **Python Packages**:
  - `Flask`
  - `Flask-Session`
  - `mysql-connector-python`
  - `bcrypt`
  - `python-dotenv`
