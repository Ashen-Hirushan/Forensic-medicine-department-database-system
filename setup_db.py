import os
import subprocess
from dotenv import load_dotenv

# Load credentials from the .env file
load_dotenv()

DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'forensic_dept_db')

def run_sql_file(filepath):
    print(f"Importing {filepath}...")
    command = f'mysql -u {DB_USER} -p"{DB_PASSWORD}" {DB_NAME} < {filepath}'
    # Use shell=True for input redirection
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        # Ignore duplicate column errors from older alter scripts
        if "Duplicate column name" in result.stderr:
            print(f"  -> Note: Alterations in {filepath} already exist. Skipping.")
        else:
            print(f"  -> Error importing {filepath}: {result.stderr.strip()}")
    else:
        print(f"  -> Success.")

def run_python_script(filepath):
    print(f"Running {filepath}...")
    result = subprocess.run(['python', filepath], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  -> Error running {filepath}:\n{result.stderr.strip()}")
    else:
        # Just print the last line of the output for cleanliness
        output_lines = [line for line in result.stdout.strip().split('\n') if line]
        msg = output_lines[-1] if output_lines else "Success."
        print(f"  -> {msg}")

if __name__ == '__main__':
    print("====================================")
    print("   ForensicDB Automated Setup 🚀    ")
    print("====================================\n")
    
    # 1. Import SQL files
    print("--- Step 1: Loading SQL Schema & Triggers ---")
    sql_files = [
        "database/schema.sql",
        "database/procedures.sql",
        "database/triggers.sql",
        "database/audit_triggers.sql",
        "database/alter_mlef.sql",
        "database/alter_mlef_v2.sql",
        "database/fix_alerts.sql"
    ]
    for sql_file in sql_files:
        run_sql_file(sql_file)
    print("")

    # 2. Run Python Migrations and Seeding
    print("--- Step 2: Running Python Migrations & Seeding Data ---")
    python_scripts = [
        "migrate.py",
        "migrate_gaps.py",
        "migrate_mlr.py",
        "database/seed.py"
    ]
    for py_file in python_scripts:
        run_python_script(py_file)
        
    print("\n====================================")
    print(" Setup Complete! You can now run: ")
    print(" python run.py ")
    print("====================================")
