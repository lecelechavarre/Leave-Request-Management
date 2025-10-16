import os, sqlite3
from utils import hash_password
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'leave_manager.db')
def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn(); cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT NOT NULL, role TEXT NOT NULL)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS leaves (id TEXT PRIMARY KEY, username TEXT NOT NULL, type TEXT, start_date TEXT, end_date TEXT, status TEXT, reason TEXT)''')
    conn.commit()
    cur.execute("SELECT COUNT(1) as c FROM users")
    row = cur.fetchone()
    if row is None or row['c'] == 0:
        # create default users without importing other modules (avoid circular imports)
        try:
            pw = hash_password('admin'); cur.execute('INSERT OR IGNORE INTO users(username,password,role) VALUES(?,?,?)', ('admin', pw, 'admin'))
            pw2 = hash_password('employee'); cur.execute('INSERT OR IGNORE INTO users(username,password,role) VALUES(?,?,?)', ('employee', pw2, 'employee'))
            conn.commit()
        except Exception:
            pass
    conn.close()

init_db()
