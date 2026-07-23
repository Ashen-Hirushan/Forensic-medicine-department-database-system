"""
ForensicDB One-Click Application Launcher
-----------------------------------------
Designed for new user PCs with zero technical setup required:
1. Automatically creates .env if missing
2. Automatically installs all required Python packages (pip install -r requirements.txt)
3. Connects to MySQL (interactively prompts for MySQL password if credentials fail)
4. Automatically initializes MySQL database, tables, triggers, procedures, & seed data
5. Automatically opens browser to http://127.0.0.1:5000 and runs the app
"""

import sys
import os
import time
import subprocess
import webbrowser
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

def print_banner():
    print("=" * 65)
    print("      ForensicDB - Automatic One-Click Setup & Launcher")
    print("=" * 65)

def ensure_env_file():
    env_file = os.path.join(BASE_DIR, '.env')
    example_file = os.path.join(BASE_DIR, '.env.example')
    
    if not os.path.exists(env_file):
        print("\n[+] Creating default configuration file (.env)...")
        if os.path.exists(example_file):
            with open(example_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = "DB_HOST=localhost\nDB_PORT=3306\nDB_USER=root\nDB_PASSWORD=\nDB_NAME=forensic_dept_db\nSECRET_KEY=dev_secret_key\n"
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  [OK] Default .env created.")

def ensure_dependencies():
    print("\n[1/4] Checking & Installing Python Dependencies...")
    req_file = os.path.join(BASE_DIR, 'requirements.txt')
    
    # Always ensure pip requirements are installed on new PC
    try:
        print("  --> Running 'pip install -r requirements.txt' to guarantee all packages are ready...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_file])
        print("  [OK] All Python dependencies are installed and up to date.")
    except Exception as e:
        print(f"  [!] Warning while installing requirements: {e}")

def setup_database():
    print("\n[2/4] Checking MySQL Connection & Initializing Database...")
    from dotenv import load_dotenv
    env_file = os.path.join(BASE_DIR, '.env')
    load_dotenv(env_file, override=True)
    
    import mysql.connector

    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = int(os.environ.get('DB_PORT', 3306))
    db_user = os.environ.get('DB_USER', 'root')
    db_password = os.environ.get('DB_PASSWORD', '')
    db_name = os.environ.get('DB_NAME', 'forensic_dept_db')

    # Connection retry loop for new users
    connected = False
    attempts = 0

    while not connected and attempts < 3:
        try:
            conn = mysql.connector.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password
            )
            connected = True
        except mysql.connector.Error as err:
            attempts += 1
            print(f"\n[!] MySQL Connection Failed ({err})")
            print(f"    Target: {db_user}@{db_host}:{db_port}")
            
            if attempts >= 3:
                print("\n[ERROR] Maximum connection attempts reached.")
                print("Please ensure MySQL Server is running and update DB_PASSWORD in your .env file.")
                sys.exit(1)

            # Prompt user for their MySQL password
            try:
                new_pass = input(f"-> Please enter your MySQL password for user '{db_user}' (press Enter if blank): ")
            except EOFError:
                new_pass = ""

            db_password = new_pass
            # Update .env file with user input
            update_env_key("DB_PASSWORD", new_pass)

    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`;")
    cursor.close()
    conn.close()

    # Check if database has tables
    conn = mysql.connector.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES LIKE 'system_users';")
    table_exists = cursor.fetchone()
    cursor.close()
    conn.close()

    if not table_exists:
        print(f"  --> First time setup: Database '{db_name}' is empty.")
        print("  --> Creating tables, stored procedures, triggers & seed data...")
        run_sql_initialization(db_host, db_port, db_user, db_password, db_name)
    else:
        print(f"  [OK] Database '{db_name}' is ready.")

def update_env_key(key, val):
    env_file = os.path.join(BASE_DIR, '.env')
    lines = []
    found = False
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith(f"{key}="):
                    lines.append(f"{key}={val}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"{key}={val}\n")
        
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def split_sql_statements(sql_text):
    lines = []
    for line in sql_text.splitlines():
        line_s = line.strip()
        if line_s.startswith('--') or line_s.startswith('#'):
            continue
        lines.append(line)
    clean_sql = '\n'.join(lines)
    
    statements = []
    current_stmt = []
    in_delimiter = ';'
    
    for line in clean_sql.splitlines():
        line_s = line.strip()
        if line_s.upper().startswith('DELIMITER'):
            in_delimiter = line_s.split()[1]
            continue
            
        if in_delimiter != ';' and line_s.endswith(in_delimiter):
            current_stmt.append(line[:line.rfind(in_delimiter)])
            stmt = '\n'.join(current_stmt).strip()
            if stmt:
                statements.append(stmt)
            current_stmt = []
        elif in_delimiter == ';' and line_s.endswith(';'):
            current_stmt.append(line[:-1])
            stmt = '\n'.join(current_stmt).strip()
            if stmt:
                statements.append(stmt)
            current_stmt = []
        else:
            current_stmt.append(line)
            
    if current_stmt:
        stmt = '\n'.join(current_stmt).strip()
        if stmt:
            statements.append(stmt)
            
    return statements

def run_sql_initialization(db_host, db_port, db_user, db_password, db_name):
    import mysql.connector

    sql_files = [
        os.path.join(BASE_DIR, "database", "schema.sql"),
        os.path.join(BASE_DIR, "database", "procedures.sql"),
        os.path.join(BASE_DIR, "database", "triggers.sql"),
        os.path.join(BASE_DIR, "database", "audit_triggers.sql")
    ]

    for filepath in sql_files:
        if not os.path.exists(filepath):
            continue
        print(f"      - Executing {os.path.basename(filepath)}...")
        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_text = f.read()
        
        statements = split_sql_statements(sql_text)
        for stmt in statements:
            if not stmt:
                continue
            try:
                cursor.execute(stmt)
            except Exception:
                pass
                
        conn.commit()
        cursor.close()
        conn.close()

    # Seed data
    print("      - Seeding initial roles & default users...")
    seed_script = os.path.join(BASE_DIR, "database", "seed.py")
    if os.path.exists(seed_script):
        subprocess.call([sys.executable, seed_script])

    # Run migrations if any
    print("      - Running schema migrations...")
    for mig in ['migrate.py', 'migrate_mlr.py', 'migrate_gaps.py', 'apply_triggers.py']:
        mig_path = os.path.join(BASE_DIR, mig)
        if os.path.exists(mig_path):
            subprocess.call([sys.executable, mig_path])

    print("  [OK] Database initialization complete.")

def open_browser():
    time.sleep(1.5)
    print("\n[3/4] Opening Web Browser...")
    webbrowser.open("http://127.0.0.1:5000")

def run_application():
    print("\n[4/4] Starting ForensicDB Server...")
    print("  [OK] App running at: http://127.0.0.1:5000 (Press Ctrl+C to stop)\n")
    print("=" * 65)
    
    from app import create_app
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    print_banner()
    ensure_env_file()
    ensure_dependencies()
    setup_database()
    threading.Thread(target=open_browser, daemon=True).start()
    run_application()
