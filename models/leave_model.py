from models.db import get_conn
import uuid
def list_all():
    conn = get_conn(); cur = conn.cursor(); cur.execute('SELECT * FROM leaves'); rows = cur.fetchall(); conn.close()
    return [dict(r) for r in rows]
def list_for_user(username=None):
    conn = get_conn(); cur = conn.cursor()
    if username:
        cur.execute('SELECT * FROM leaves WHERE username=?', (username,))
    else:
        cur.execute('SELECT * FROM leaves')
    rows = cur.fetchall(); conn.close()
    return [dict(r) for r in rows]
def create(record):
    conn = get_conn(); cur = conn.cursor()
    lid = str(uuid.uuid4())[:8]
    cur.execute('INSERT INTO leaves(id,username,type,start_date,end_date,status,reason) VALUES (?,?,?,?,?,?,?)',
                (lid, record.get('username'), record.get('type'), record.get('start_date'), record.get('end_date'), record.get('status'), record.get('reason')))
    conn.commit(); conn.close(); record['id']=lid; return record
def update(record_id, updates):
    conn = get_conn(); cur = conn.cursor()
    keys=[]; vals=[]
    for k,v in updates.items(): keys.append(f"{k}=?"); vals.append(v)
    vals.append(record_id)
    cur.execute(f"UPDATE leaves SET {', '.join(keys)} WHERE id=?", vals)
    conn.commit(); conn.close()
    return True
def delete(record_id):
    conn = get_conn(); cur = conn.cursor(); cur.execute('DELETE FROM leaves WHERE id=?', (record_id,)); conn.commit(); conn.close(); return True
