from models.db import get_conn
from utils import hash_password, verify_password

def add_user(username, password, role='employee'):
    conn = get_conn(); cur = conn.cursor()
    pw = hash_password(password)
    try:
        cur.execute('INSERT INTO users(username,password,role) VALUES(?,?,?)', (username, pw, role))
        conn.commit(); return True
    except Exception:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = get_conn(); cur = conn.cursor()
    cur.execute('SELECT username,password,role FROM users WHERE username=?', (username,))
    row = cur.fetchone(); conn.close()
    if not row: return None
    return {'username': row['username'], 'password': row['password'], 'role': row['role']}

def verify(username, password):
    u = get_user(username)
    if not u: return False
    return verify_password(password, u['password'])
