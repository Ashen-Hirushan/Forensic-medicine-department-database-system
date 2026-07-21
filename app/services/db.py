import mysql.connector
from mysql.connector import pooling
from flask import current_app, g

db_pool = None

def init_pool(app):
    global db_pool
    if db_pool is None:
        db_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="forensic_pool",
            pool_size=10,
            pool_reset_session=True,
            host=app.config['DB_HOST'],
            port=app.config['DB_PORT'],
            database=app.config['DB_NAME'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD']
        )

def get_db():
    global db_pool
    if db_pool is None:
        raise Exception("Database pool not initialized.")
    if 'db_conn' not in g:
        g.db_conn = db_pool.get_connection()
    return g.db_conn

def close_db(e=None):
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()

def init_app(app):
    init_pool(app)
    app.teardown_appcontext(close_db)

# Utility to execute raw queries (for Views or simple selects)
def execute_query(query, params=(), fetch_all=True):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        if query.strip().upper().startswith("SELECT") or query.strip().upper().startswith("SHOW"):
            if fetch_all:
                return cursor.fetchall()
            return cursor.fetchone()
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()

# Utility to call stored procedures easily
def call_procedure(proc_name, args=()):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.callproc(proc_name, args)
        conn.commit()
        
        # Fetch results if the procedure returns any (like sp_get_monthly_statistics)
        results = []
        for result in cursor.stored_results():
            results.append(result.fetchall())
            
        if len(results) == 1:
            return results[0]
        return results
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
