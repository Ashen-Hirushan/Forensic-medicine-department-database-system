# ForensicDB - User & Installation Guide

Welcome to the **Forensic Medicine Department Database System (ForensicDB)**. This system is designed to be as easy to install and run as possible, even for non-technical users.

## 🛠️ 1. Prerequisites (For a New Computer)

Before running the application on a new computer, you only need two things installed:

1. **Python (Version 3.8 or newer)**
   - Download from: [python.org/downloads](https://www.python.org/downloads/)
   - **CRITICAL STEP**: When installing Python, make sure to check the box at the very bottom that says **"Add Python to PATH"** before clicking Install.

2. **MySQL Server (or XAMPP)**
   - The easiest way is to download XAMPP from: [apachefriends.org](https://www.apachefriends.org/index.html)
   - Open the XAMPP Control Panel and click **Start** next to MySQL.

---

## ⚙️ 2. Database Configuration (.env file)

When moving the project to a new computer, you must tell the application how to connect to that computer's database server.

1. Open the project folder.
2. Find the file named **`.env`** (if it doesn't exist, the launcher will create one for you, or you can copy `.env.example`).
3. Open the `.env` file using Notepad.
4. Update the database credentials to match your new computer's MySQL setup:
   ```ini
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_mysql_password_here
   DB_NAME=forensic_dept_db
   ```
   *(Note: If you are using XAMPP, the `DB_PASSWORD` is usually left completely blank!)*

---

## 🚀 3. How to Start the Application

1. Open the folder containing the project files.
2. Double-click the file named **`ForensicDB_Launcher.bat`**.
3. A black console window will open. The launcher will automatically:
   - Check if Python is installed.
   - Download and install all required background packages.
   - Connect to your database. (If it asks for a MySQL password, type your password and press Enter. If you use XAMPP, just press Enter to leave it blank).
   - Create all the necessary database tables and sample users.
   - Automatically open your default web browser to the login screen!
4. Then run **`ForensicDB_Launcher.bat`** file again if you are doing first time

> **Note**: Do not close the black console window while using the application. When you are done using ForensicDB for the day, simply close the black window to shut down the server.

---

## 🔑 4. Default Login Accounts

When the system is set up for the first time, it automatically creates sample accounts so you can log in immediately. 

*The password for ALL accounts is: **`securepass123`***

| Role | Username | What they can do |
|------|----------|------------------|
| **System Admin 1** | `admin1` | Full access. Can view the Audit Log, manage users, and delete user profiles. |
| **System Admin 2** | `admin2` | Full access. Can view the Audit Log, manage users, and delete user profiles. |
| **Medical Officer (JMO)** | `dr_chathula` | Can examine patients, conduct postmortems, order lab tests, and write official reports (MLEF/PMR). |
| **Department Clerk** | `clerk_nimal` | Registers new cases (Living Subjects and Cadavers) and prepares court dispatches. |
| **Lab Technician** | `lab_kamal` | Receives evidence via chain of custody, conducts tests, and uploads lab results. |

---

## 💾 5. Database Backup & Restore

To ensure you never lose important medical records, the system includes a built-in backup tool.

1. Locate the file **`backup.bat`** in the main project folder.
2. Double-click to run it.
3. You will see a menu:
   - **Type `1`** to create a fresh backup of your entire database. It will be saved as `forensic_dept_db_backup.sql`.
   - **Type `2`** to restore the database from a previous backup file.
4. Press Enter. The tool will automatically use your local database credentials to perform the operation.

---

## 📖 6. Basic Navigation

- **Dashboard**: Your home screen. Shows quick statistics (like pending cases) and gives you fast access to your most common tasks based on your role.
- **Left Sidebar Menu**: Use this to navigate between Clinical Cases, Autopsy Cases, Lab & Evidence, and Registers.
- **Top Right Menu (User Icon)**: Click here to view your profile or log out safely.

---

## 💻 7. Developer & Advanced Tools

If you are a developer or IT administrator looking to modify the system:

- **Source Code Structure**: You can review the complete file architecture in `source_code_structure.md` located in the project root.
- **Running Tests**: Run `python run_tests.py` in your terminal to execute the automated test suite and ensure all modules are functioning correctly.
- **Linting**: The codebase is formatted using `black`. We use a custom `.pylintrc` and `.vscode/settings.json` to manage warnings in modern IDEs like Visual Studio Code.

---

### ❓ Troubleshooting

- **"MySQL Connection Failed"**: Ensure that your MySQL server (via XAMPP or Workbench) is actually running.
- **"Python is not recognized"**: You likely forgot to check the "Add Python to PATH" box when installing Python. Uninstall Python and reinstall it, making sure to check that box!
