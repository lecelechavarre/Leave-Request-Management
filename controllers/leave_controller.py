from models.db_alchemy import SessionLocal
from models.models_alchemy import Leave
from controllers.audit_controller import audit_create, audit_update, audit_delete
import uuid
def list_for(user, limit=None, offset=None):
    db = SessionLocal()
    try:
        q = db.query(Leave)
        if user.get('role') != 'admin':
            q = q.filter(Leave.username==user.get('username'))
        if offset is not None: q = q.offset(offset)
        if limit is not None: q = q.limit(limit)
        rows = q.all()
        return [dict(id=r.id, username=r.username, type=r.type, start_date=r.start_date, end_date=r.end_date, status=r.status, reason=r.reason, approved_by=r.approved_by, approved_date=r.approved_date, remarks=r.remarks) for r in rows]
    finally:
        db.close()
def count_all(user):
    db = SessionLocal()
    try:
        q = db.query(Leave)
        if user.get('role') != 'admin': q = q.filter(Leave.username==user.get('username'))
        return q.count()
    finally:
        db.close()
def create(user, payload):
    db = SessionLocal()
    try:
        lid = str(uuid.uuid4())[:8]
        rec = Leave(id=lid, username=user['username'], type=payload.get('type'), start_date=payload.get('start_date'), end_date=payload.get('end_date'), status=payload.get('status','Pending'), reason=payload.get('reason'))
        db.add(rec); db.commit(); audit_create(user['username'], lid, None, payload); return {'id': lid, 'username': rec.username, 'type': rec.type, 'start_date': rec.start_date, 'end_date': rec.end_date, 'status': rec.status}
    finally:
        db.close()
def update(user, leave_id, updates):
    db = SessionLocal()
    try:
        rec = db.query(Leave).filter(Leave.id==leave_id).first()
        if not rec: return None
        if user.get('role') != 'admin' and rec.username != user.get('username'): return None
        before = dict(id=rec.id, username=rec.username, type=rec.type, start_date=rec.start_date, end_date=rec.end_date, status=rec.status, approved_by=rec.approved_by, approved_date=rec.approved_date, remarks=rec.remarks)
        for k,v in updates.items(): setattr(rec, k, v)
        db.commit(); after = dict(id=rec.id, username=rec.username, type=rec.type, start_date=rec.start_date, end_date=rec.end_date, status=rec.status, approved_by=rec.approved_by, approved_date=rec.approved_date, remarks=rec.remarks)
        audit_update(user['username'], leave_id, before, after); return after
    finally:
        db.close()
def approve(user, leave_id, remarks=''):
    db = SessionLocal()
    try:
        rec = db.query(Leave).filter(Leave.id==leave_id).first()
        if not rec: return None
        if user.get('role') != 'admin' and user.get('role') != 'manager': return None
        before = dict(id=rec.id, status=rec.status, approved_by=rec.approved_by, approved_date=rec.approved_date, remarks=rec.remarks)
        rec.status = 'Approved'; rec.approved_by = user.get('username'); rec.approved_date = __import__('datetime').date.today().isoformat(); rec.remarks = remarks
        db.commit(); after = dict(id=rec.id, status=rec.status, approved_by=rec.approved_by, approved_date=rec.approved_date, remarks=rec.remarks)
        audit_update(user['username'], leave_id, before, after); return after
    finally:
        db.close()
def delete(user, leave_id):
    db = SessionLocal()
    try:
        rec = db.query(Leave).filter(Leave.id==leave_id).first()
        if not rec: return False
        if user.get('role') != 'admin' and rec.username != user.get('username'): return False
        before = dict(id=rec.id, username=rec.username, type=rec.type)
        db.delete(rec); db.commit(); audit_delete(user['username'], leave_id, before, None); return True
    finally:
        db.close()
