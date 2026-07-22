import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'forensic_dept_db')

def apply_triggers():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        cursor = conn.cursor()

        with open('database/audit_triggers.sql', 'r') as f:
            sql_script = f.read()

        # The script contains DELIMITER commands which mysql-connector-python doesn't support directly.
        # We need to split and execute manually.
        
        # Actually, it's easier to just run the mysql CLI tool via subprocess
        import subprocess
        
        cmd = f'mysql -u {DB_USER} '
        if DB_PASS:
            cmd += f'-p{DB_PASS} '
        cmd += f'{DB_NAME} < database/audit_triggers.sql'
        
        print("Running: ", cmd)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Audit triggers applied successfully!")
        else:
            print(f"Error applying triggers: {result.stderr}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    apply_triggers()
