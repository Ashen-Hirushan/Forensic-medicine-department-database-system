import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'forensic_dept_db')
}

def migrate():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Add profile_picture column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE system_users ADD COLUMN profile_picture VARCHAR(255) DEFAULT 'default.png';")
            conn.commit()
            print("Successfully added profile_picture column.")
        except mysql.connector.Error as err:
            if err.errno == 1060: # Duplicate column name
                print("Column profile_picture already exists.")
            else:
                print(f"Error: {err}")
                
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == '__main__':
    migrate()
